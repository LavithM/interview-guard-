import cv2
import io
import os
import tempfile

import numpy as np

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    File,
)

from pydantic import BaseModel

from app.database import SessionLocal

from app.models.database_models import (
    Interview,
    InterviewInvitation,
)

from app.services.session_manager import (
    create_session,
    get_session,
    add_features,
    add_analysis,
    end_session,
    save_report,
)

from app.services.report_service import (
    generate_report,
)

from app.services.realtime_analysis_service import (
    RealtimeAnalysisService,
)

from app.services.dataset_service import (
    DatasetService,
)

from app.services.model_feature_service import (
    ModelFeatureService,
)

from app.services.auth_dependencies import (
    require_candidate,
    require_admin,
)

from app.services.realtime_state import (
    update_analysis,
    update_window,
)


router = APIRouter(
    prefix="/interview",
    tags=["Interview"],
)


# ============================================================
# REALTIME SERVICES
# ============================================================

realtime_services = {}


def get_realtime_service(interview_id: str):
    """
    Get the realtime AI service for an interview.

    If one does not exist, create it.

    IMPORTANT:
    The previous version accidentally called this same
    function recursively.
    """

    service = realtime_services.get(
        interview_id
    )

    if service is None:

        service = RealtimeAnalysisService()

        realtime_services[
            interview_id
        ] = service

    return service


# ============================================================
# CANDIDATE AUTHORIZATION
# ============================================================

def authorize_candidate(
    interview_id: str,
    current_user,
):
    """
    Make sure the session exists and belongs to the
    authenticated candidate.
    """

    session = get_session(
        interview_id
    )

    if session is None:
        raise HTTPException(
            status_code=404,
            detail="Interview session not found",
        )

    candidate_email = (
        current_user.get(
            "username",
            "",
        )
        .lower()
        .strip()
    )

    session_email = (
        session.get(
            "email",
            "",
        )
        .lower()
        .strip()
    )

    if candidate_email != session_email:
        raise HTTPException(
            status_code=403,
            detail=(
                "You are not allowed to access this interview"
            ),
        )

    return session


# ============================================================
# DATASET SERVICES
# ============================================================

dataset_service = DatasetService()

model_feature_service = ModelFeatureService()

DATASET_FILE = (
    "dataset/interview_features.csv"
)

dataset_service.create_dataset_file(
    DATASET_FILE
)


# ============================================================
# REQUEST MODELS
# ============================================================

class InterviewStartRequest(BaseModel):
    name: str
    email: str
    role: str


class HeadPoseData(BaseModel):
    yaw: float
    pitch: float
    roll: float


class FeatureData(BaseModel):
    timestamp: float
    gaze: float
    blink: int
    head_pose: HeadPoseData
    lip_movement: float
    audio_level: float
    speech_detected: bool


# ============================================================
# LEGACY START INTERVIEW
# ============================================================

@router.post("/start")
def start_interview(
    data: InterviewStartRequest,
):
    """
    Legacy/general session creation endpoint.

    The integrated candidate flow should use:

    POST /candidate/interviews/{interview_id}/start

    so that the admin-created interview ID is preserved.
    """

    from uuid import uuid4

    interview_id = str(
        uuid4()
    )

    session = create_session(
        interview_id=interview_id,
        name=data.name,
        email=data.email,
        role=data.role,
    )

    realtime_services[
        interview_id
    ] = RealtimeAnalysisService()

    return {
        "message": "Interview session created",

        "session": session,
    }


# ============================================================
# PROCESS VIDEO FRAME
# ============================================================

@router.post("/{interview_id}/frame")
async def process_interview_frame(
    interview_id: str,
    file: UploadFile = File(...),
    current_user=Depends(require_candidate),
):
    """
    Receive candidate video frames.

    AI analysis is performed server-side.

    IMPORTANT:
    The candidate receives only an acknowledgement.
    AI analysis is NOT returned.
    """

    session = authorize_candidate(
        interview_id,
        current_user,
    )

    if session.get("status") != "active":
        raise HTTPException(
            status_code=400,
            detail="Interview session is not active",
        )

    service = get_realtime_service(
        interview_id
    )

    image_bytes = await file.read()

    if not image_bytes:
        raise HTTPException(
            status_code=400,
            detail="Empty image file",
        )

    image_array = np.frombuffer(
        image_bytes,
        dtype=np.uint8,
    )

    frame = cv2.imdecode(
        image_array,
        cv2.IMREAD_COLOR,
    )

    if frame is None:
        raise HTTPException(
            status_code=400,
            detail="Invalid image",
        )

    # --------------------------------------------------------
    # AI analysis happens here
    # --------------------------------------------------------

    result = service.process_video_frame(
        frame
    )

    # --------------------------------------------------------
    # Store realtime state
    # --------------------------------------------------------

    update_analysis(
        interview_id,
        result,
    )

    # --------------------------------------------------------
    # Candidate receives NO analysis
    # --------------------------------------------------------

    return {
        "message": "Frame received",

        "interview_id": interview_id,

        "status": "received",
    }


# ============================================================
# PROCESS AUDIO
# ============================================================

@router.post("/{interview_id}/audio")
async def process_interview_audio(
    interview_id: str,
    file: UploadFile = File(...),
    current_user=Depends(require_candidate),
):
    """
    Receive candidate microphone audio.

    AI processing remains server-side.
    """

    session = authorize_candidate(
        interview_id,
        current_user,
    )

    if session.get("status") != "active":
        raise HTTPException(
            status_code=400,
            detail="Interview session is not active",
        )

    service = get_realtime_service(
        interview_id
    )

    audio_bytes = await file.read()

    if not audio_bytes:
        raise HTTPException(
            status_code=400,
            detail="Empty audio file",
        )

    import soundfile as sf

    try:

        audio, sample_rate = sf.read(
            io.BytesIO(audio_bytes),
            dtype="float32",
        )

    except Exception:

        raise HTTPException(
            status_code=400,
            detail="Invalid audio file",
        )

    if len(audio.shape) > 1:

        audio = np.mean(
            audio,
            axis=1,
        )

    result = service.process_audio(
        audio,
        sample_rate,
    )

    update_analysis(
        interview_id,
        result,
    )

    return {
        "message": "Audio received",

        "interview_id": interview_id,

        "status": "received",
    }


# ============================================================
# PROCESS SPEECH
# ============================================================

@router.post("/{interview_id}/speech")
async def process_interview_speech(
    interview_id: str,
    file: UploadFile = File(...),
    current_user=Depends(require_candidate),
):
    """
    Receive speech audio and run speech analysis.

    The candidate does NOT receive the transcription or
    AI analysis.
    """

    session = authorize_candidate(
        interview_id,
        current_user,
    )

    if session.get("status") != "active":
        raise HTTPException(
            status_code=400,
            detail="Interview session is not active",
        )

    service = get_realtime_service(
        interview_id
    )

    audio_bytes = await file.read()

    if not audio_bytes:
        raise HTTPException(
            status_code=400,
            detail="Empty audio file",
        )

    temporary_path = None

    try:

        with tempfile.NamedTemporaryFile(
            suffix=".wav",
            delete=False,
        ) as temporary_file:

            temporary_file.write(
                audio_bytes
            )

            temporary_path = (
                temporary_file.name
            )

        result = service.process_speech(
            temporary_path
        )

        # Store internally
        update_analysis(
            interview_id,
            result,
        )

        # IMPORTANT:
        # Do not return "result" to candidate.

        return {
            "message": "Speech received",

            "interview_id": interview_id,

            "status": "received",
        }

    except Exception as error:

        print(
            "Speech analysis failed:",
            str(error),
        )

        raise HTTPException(
            status_code=500,
            detail="Speech analysis failed",
        )

    finally:

        if (
            temporary_path is not None
            and os.path.exists(
                temporary_path
            )
        ):

            os.remove(
                temporary_path
            )


# ============================================================
# BUILD FEATURE WINDOW
# ============================================================

@router.post("/{interview_id}/window")
def build_interview_window(
    interview_id: str,
    current_user=Depends(require_candidate),
):
    """
    Build a feature window on the backend.

    The candidate receives only confirmation.
    """

    session = authorize_candidate(
        interview_id,
        current_user,
    )

    if session.get("status") != "active":
        raise HTTPException(
            status_code=400,
            detail="Interview session is not active",
        )

    service = get_realtime_service(
        interview_id
    )

    window = service.build_feature_window()

    # --------------------------------------------------------
    # Realtime state for admin
    # --------------------------------------------------------

    update_window(
        interview_id,
        window,
    )

    # --------------------------------------------------------
    # Save complete feature window
    # --------------------------------------------------------

    updated_session = add_features(
        interview_id,
        window,
    )

    # --------------------------------------------------------
    # Save important AI analysis
    # --------------------------------------------------------

    add_analysis(
        interview_id,
        {
            "fusion": window.get(
                "fusion",
                {},
            ),

            "model_prediction": window.get(
                "model_prediction",
                {},
            ),

            "model_features": window.get(
                "model_features",
                {},
            ),
        },
    )

    # --------------------------------------------------------
    # Candidate gets only acknowledgement
    # --------------------------------------------------------

    return {
        "message": "Feature window received",

        "interview_id": interview_id,

        "status": "received",

        "total_feature_windows": len(
            updated_session.get(
                "features",
                [],
            )
        ),
    }


# ============================================================
# MANUAL FEATURE ENDPOINT
# ============================================================

@router.post("/{interview_id}/features")
def add_interview_features(
    interview_id: str,
    data: FeatureData,
    current_user=Depends(require_candidate),
):
    """
    Receive manually supplied feature data.

    The candidate receives only confirmation.
    """

    session = authorize_candidate(
        interview_id,
        current_user,
    )

    if session.get("status") != "active":
        raise HTTPException(
            status_code=400,
            detail="Interview session is not active",
        )

    features = data.model_dump()

    updated_session = add_features(
        interview_id,
        features,
    )

    return {
        "message": "Features received",

        "interview_id": interview_id,

        "status": "received",

        "total_feature_windows": len(
            updated_session.get(
                "features",
                [],
            )
        ),
    }


# ============================================================
# END INTERVIEW
# ============================================================

@router.post("/{interview_id}/end")
def finish_interview(
    interview_id: str,
    current_user=Depends(require_candidate),
):
    """
    Finish the interview.

    This:

    1. Saves remaining realtime data
    2. Generates the final report
    3. Saves the report
    4. Marks database interview completed
    5. Marks invitation completed
    6. Removes realtime service
    7. Returns only a safe completion message
    """

    # --------------------------------------------------------
    # Verify candidate session
    # --------------------------------------------------------

    session = authorize_candidate(
        interview_id,
        current_user,
    )

    if session.get("status") != "active":
        raise HTTPException(
            status_code=400,
            detail=(
                "Interview session is already completed"
            ),
        )

    service = get_realtime_service(
        interview_id
    )

    # --------------------------------------------------------
    # Save remaining realtime data
    # --------------------------------------------------------

    if service is not None:

        try:

            final_window = (
                service.build_feature_window()
            )

            has_final_data = (
                final_window.get(
                    "visual_samples",
                    0,
                ) > 0

                or final_window.get(
                    "audio_samples",
                    0,
                ) > 0

                or final_window.get(
                    "speech_samples",
                    0,
                ) > 0

                or final_window.get(
                    "object_samples",
                    0,
                ) > 0
            )

            if has_final_data:

                add_features(
                    interview_id,
                    final_window,
                )

                add_analysis(
                    interview_id,
                    {
                        "fusion": final_window.get(
                            "fusion",
                            {},
                        ),

                        "model_prediction": (
                            final_window.get(
                                "model_prediction",
                                {},
                            )
                        ),

                        "model_features": (
                            final_window.get(
                                "model_features",
                                {},
                            )
                        ),
                    },
                )

        except Exception as error:

            print(
                "Final feature window error:",
                str(error),
            )

    # --------------------------------------------------------
    # End session-manager session
    # --------------------------------------------------------

    session = end_session(
        interview_id
    )

    # --------------------------------------------------------
    # Generate final report
    # --------------------------------------------------------

    report = generate_report(
        session
    )

    # --------------------------------------------------------
    # Save final report
    # --------------------------------------------------------

    save_report(
        interview_id,
        report,
    )

    # --------------------------------------------------------
    # Update SQLite interview status
    # --------------------------------------------------------

    db = SessionLocal()

    try:

        interview = (
            db.query(Interview)
            .filter(
                Interview.interview_id
                == interview_id
            )
            .first()
        )

        if interview is not None:

            interview.status = "completed"

            # Use current UTC time
            interview.ended_at = (
                __import__(
                    "datetime"
                ).datetime.now(
                    __import__(
                        "datetime"
                    ).timezone.utc
                )
            )

        # ----------------------------------------------------
        # Update invitation status
        # ----------------------------------------------------

        if interview is not None:

            invitation = (
                db.query(
                    InterviewInvitation
                )
                .filter(
                    InterviewInvitation.interview_id
                    == interview.id
                )
                .first()
            )

            if invitation is not None:

                invitation.status = "completed"

        db.commit()

    except Exception:

        db.rollback()
        raise

    finally:

        db.close()

    # --------------------------------------------------------
    # Remove realtime service
    # --------------------------------------------------------

    realtime_service = (
        realtime_services.pop(
            interview_id,
            None,
        )
    )

    if realtime_service is not None:

        try:
            realtime_service.close()
        except Exception as error:
            print(
                "Realtime service close error:",
                str(error),
            )

    # --------------------------------------------------------
    # Candidate receives NO report
    # --------------------------------------------------------

    return {
        "message": "Interview completed",

        "interview_id": interview_id,

        "status": "completed",
    }


# ============================================================
# ADMIN: GET INTERVIEW SESSION
# ============================================================

@router.get("/{interview_id}")
def get_interview(
    interview_id: str,
    current_user=Depends(require_admin),
):
    """
    Admin-only endpoint.

    The admin can see the complete server-side session.
    """

    session = get_session(
        interview_id
    )

    if session is None:
        raise HTTPException(
            status_code=404,
            detail="Interview session not found",
        )

    return {
        "session": session,
    }


# ============================================================
# SAVE INTERVIEW WINDOWS TO DATASET
# ============================================================

@router.post("/{interview_id}/dataset")
def save_interview_window_to_dataset(
    interview_id: str,
    label: int,
    current_user=Depends(require_admin),
):
    """
    Admin-only dataset labeling endpoint.
    """

    session = get_session(
        interview_id
    )

    if session is None:
        raise HTTPException(
            status_code=404,
            detail="Interview session not found",
        )

    if label not in [0, 1]:
        raise HTTPException(
            status_code=400,
            detail="Label must be 0 or 1",
        )

    features = session.get(
        "features",
        [],
    )

    if not features:
        raise HTTPException(
            status_code=400,
            detail="No feature windows available",
        )

    saved_count = 0

    for window in features:

        model_features = (
            model_feature_service.extract(
                window
            )
        )

        dataset_service.append_sample(
            file_path=DATASET_FILE,
            features=model_features,
            label=label,
        )

        saved_count += 1

    return {
        "message": (
            "Interview windows added to dataset"
        ),

        "interview_id": interview_id,

        "label": label,

        "windows_saved": saved_count,

        "dataset_file": DATASET_FILE,
    }