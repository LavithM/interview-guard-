from pathlib import Path
import re

BACKEND = Path(__file__).resolve().parent
INTERVIEW = BACKEND / "app" / "api" / "interview.py"
MAIN = BACKEND / "app" / "main.py"


def add_import(text, needle, addition):
    if addition.strip() in text:
        return text
    if needle not in text:
        raise RuntimeError(f"Could not find import anchor: {needle}")
    return text.replace(needle, needle + addition, 1)


text = INTERVIEW.read_text(encoding="utf-8")

# FastAPI dependencies used by the candidate/admin authorization.
if "    Depends," not in text:
    text = text.replace("    APIRouter,\n", "    APIRouter,\n    Depends,\n", 1)

# Keep existing auth imports if present; otherwise add them.
if "from app.services.auth_dependencies import" not in text:
    anchor = "from app.services.model_feature_service import (\n    ModelFeatureService\n)\n"
    text = add_import(
        text,
        anchor,
        "\nfrom app.services.auth_dependencies import require_candidate, require_admin\n",
    )
else:
    if "require_admin" not in text.split("from app.services.auth_dependencies import", 1)[1].split("\n\n", 1)[0]:
        text = text.replace(
            "from app.services.auth_dependencies import (\n    require_candidate,\n)",
            "from app.services.auth_dependencies import (\n    require_candidate,\n    require_admin,\n)",
            1,
        )

if "from app.services.realtime_state import" not in text:
    anchor = "from app.services.auth_dependencies import require_candidate, require_admin\n"
    if anchor in text:
        text = add_import(
            text,
            anchor,
            "from app.services.realtime_state import update_analysis, update_window\n",
        )
    else:
        text = add_import(
            text,
            "from app.services.auth_dependencies import (\n    require_candidate,\n    require_admin,\n)\n",
            "from app.services.realtime_state import update_analysis, update_window\n",
        )

# Recreate realtime service after FastAPI restart when the DB interview is still active.
if "def get_realtime_service(" not in text:
    anchor = "realtime_services = {}\n"
    helper = '''\n\ndef get_realtime_service(interview_id: str):\n    service = realtime_services.get(interview_id)\n    if service is None:\n        service = RealtimeAnalysisService()\n        realtime_services[interview_id] = service\n    return service\n\n\ndef authorize_candidate(interview_id: str, current_user):\n    session = get_session(interview_id)\n    if session is None:\n        raise HTTPException(status_code=404, detail="Interview session not found")\n\n    candidate_email = current_user.get("username", "").lower().strip()\n    interview_email = session["email"].lower().strip()\n\n    if candidate_email != interview_email:\n        raise HTTPException(status_code=403, detail="You are not allowed to access this interview")\n\n    return session\n'''
    text = text.replace(anchor, anchor + helper, 1)

# Use the recovery helper in processing endpoints. Do not alter pop() at interview end.
text = text.replace(
    "service = realtime_services.get(\n        interview_id\n    )",
    "service = get_realtime_service(\n        interview_id\n    )",
)

# Protect candidate processing endpoints if the current file doesn't already do so.
patterns = {
    "async def process_interview_frame": r"(async def process_interview_frame\(\n    interview_id: str,\n)(    file: UploadFile = File\(\.\.\.\)\n\):)",
    "async def process_interview_audio": r"(async def process_interview_audio\(\n    interview_id: str,\n)(    file: UploadFile = File\(\.\.\.\)\n\):)",
    "async def process_interview_speech": r"(async def process_interview_speech\(\n    interview_id: str,\n)(    file: UploadFile = File\(\.\.\.\)\n\):)",
    "def build_interview_window": r"(def build_interview_window\(\n    interview_id: str)(\n\):)",
    "def add_interview_features": r"(def add_interview_features\(\n    interview_id: str,\n    data: FeatureData,\n)(\n):)",
    "def finish_interview": r"(def finish_interview\(\n    interview_id: str)(\n):)",
}

for name, pattern in patterns.items():
    if name not in text:
        continue
    start = text.find(name)
    next_section = text.find("# --------------------------------------------------", start + 20)
    block_end = next_section if next_section != -1 else len(text)
    block = text[start:block_end]
    if "Depends(require_candidate)" not in block:
        block = re.sub(
            pattern,
            lambda m: m.group(1) + "    current_user=Depends(require_candidate),\n" + m.group(2),
            block,
            count=1,
        )
        if "current_user=Depends(require_candidate)" in block:
            text = text[:start] + block + text[block_end:]

# Candidate authorization after session lookup.
for name in [
    "async def process_interview_frame",
    "async def process_interview_audio",
    "async def process_interview_speech",
    "def build_interview_window",
    "def add_interview_features",
    "def finish_interview",
]:
    start = text.find(name)
    if start == -1:
        continue
    next_section = text.find("# --------------------------------------------------", start + 20)
    block_end = next_section if next_section != -1 else len(text)
    block = text[start:block_end]
    if "authorize_candidate(" not in block:
        anchor = "    session = get_session(\n        interview_id\n    )\n"
        if anchor in block:
            block = block.replace(
                anchor,
                anchor + "\n    authorize_candidate(interview_id, current_user)\n",
                1,
            )
            text = text[:start] + block + text[block_end:]

# Save the latest AI outputs for the admin WebSocket.
if "update_analysis(interview_id, result)" not in text:
    text = text.replace(
        "    result = service.process_video_frame(\n        frame\n    )\n",
        "    result = service.process_video_frame(\n        frame\n    )\n\n    update_analysis(interview_id, result)\n",
        1,
    )
    text = text.replace(
        "    result = service.process_audio(\n        audio,\n        sample_rate\n    )\n",
        "    result = service.process_audio(\n        audio,\n        sample_rate\n    )\n\n    update_analysis(interview_id, result)\n",
        1,
    )
    text = text.replace(
        "        result = service.process_speech(\n            temporary_path\n        )\n",
        "        result = service.process_speech(\n            temporary_path\n        )\n\n        update_analysis(interview_id, result)\n",
        1,
    )

# Store the latest feature window.
if "update_window(interview_id, window)" not in text:
    text = text.replace(
        "    window = service.build_feature_window()\n",
        "    window = service.build_feature_window()\n\n    update_window(interview_id, window)\n",
        1,
    )

# Candidate must not receive raw AI analysis or feature windows.
for func_name in [
    "async def process_interview_frame",
    "async def process_interview_audio",
    "async def process_interview_speech",
]:
    start = text.find(func_name)
    if start == -1:
        continue
    end = text.find("# --------------------------------------------------", start + 20)
    if end == -1:
        end = len(text)
    block = text[start:end]
    block = block.replace(
        '        "analysis":\n            result\n',
        '        "status":\n            "received"\n',
    )
    block = block.replace(
        '        "analysis":\n            result,\n',
        '        "status":\n            "received",\n',
    )
    text = text[:start] + block + text[end:]

# Window endpoint should return acknowledgement only and use the updated session count.
start = text.find("def build_interview_window")
if start != -1:
    end = text.find("# --------------------------------------------------", start + 20)
    block = text[start:end if end != -1 else len(text)]
    block = block.replace(
        "    add_features(\n        interview_id,\n        window\n    )",
        "    updated_session = add_features(\n        interview_id,\n        window\n    )",
        1,
    )
    block = block.replace(
        '        "window":\n            window,\n\n        "total_feature_windows":\n            len(\n                session["features"]\n            ),',
        '        "status":\n            "received",\n\n        "total_feature_windows":\n            len(updated_session["features"]),',
        1,
    )
    text = text[:start] + block + text[end if end != -1 else len(text):]

# GET /interview/{id} and /dataset are admin-only.
if "def get_interview(" in text:
    text = text.replace(
        "def get_interview(\n    interview_id: str\n):",
        "def get_interview(\n    interview_id: str,\n    current_user=Depends(require_admin),\n):",
        1,
    )
if "def save_interview_window_to_dataset(" in text:
    text = text.replace(
        "def save_interview_window_to_dataset(\n    interview_id: str,\n    label: int,\n):",
        "def save_interview_window_to_dataset(\n    interview_id: str,\n    label: int,\n    current_user=Depends(require_admin),\n):",
        1,
    )

# Candidate must not receive the final report.
text = text.replace(
    '    return {\n\n        "message":\n            "Interview completed",\n\n        "report":\n            report,\n    }',
    '    return {\n\n        "message":\n            "Interview completed",\n\n        "interview_id":\n            interview_id,\n\n        "status":\n            "completed",\n    }',
    1,
)

INTERVIEW.write_text(text, encoding="utf-8")

# Add the new routers to FastAPI.
main = MAIN.read_text(encoding="utf-8")
if "from app.api.live import router as live_router" not in main:
    main = main.replace(
        "from app.api.candidate import router as candidate_router\n",
        "from app.api.candidate import router as candidate_router\nfrom app.api.live import router as live_router\nfrom app.api.admin_live_routes import router as admin_live_router\n",
        1,
    )
if "app.include_router(live_router)" not in main:
    main = main.replace(
        "app.include_router(candidate_router)\n",
        "app.include_router(candidate_router)\napp.include_router(admin_live_router)\napp.include_router(live_router)\n",
        1,
    )
MAIN.write_text(main, encoding="utf-8")

print("Live InterviewGuard backend patch applied successfully.")
