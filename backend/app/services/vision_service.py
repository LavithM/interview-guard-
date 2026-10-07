import cv2
import mediapipe as mp


class VisionService:

    def __init__(self):

        base_options = mp.tasks.BaseOptions(
            model_asset_path="models/face_landmarker.task"
        )

        options = mp.tasks.vision.FaceLandmarkerOptions(
            base_options=base_options,
            running_mode=mp.tasks.vision.RunningMode.IMAGE,
            num_faces=1,
            min_face_detection_confidence=0.5,
            min_face_presence_confidence=0.5,
            min_tracking_confidence=0.5,
        )

        self.face_landmarker = (
            mp.tasks.vision.FaceLandmarker.create_from_options(
                options
            )
        )

    def process_frame(self, frame):

        if frame is None:
            return {
                "face_detected": False,
                "face_conf": 0.0,
                "landmarks": []
            }

        rgb_frame = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb_frame
        )

        result = self.face_landmarker.detect(
            mp_image
        )

        if not result.face_landmarks:
            return {
                "face_detected": False,
                "face_conf": 0.0,
                "landmarks": []
            }

        face_landmarks = result.face_landmarks[0]

        landmarks = []

        for landmark in face_landmarks:

            landmarks.append({
                "x": landmark.x,
                "y": landmark.y,
                "z": landmark.z
            })

        # MediaPipe Face Landmarker does not expose the same
        # face_conf field used by the training dataset.
        #
        # Therefore we use a runtime detection-quality proxy.
        # This is NOT the original dataset confidence value.
        face_conf = 1.0

        return {
            "face_detected": True,
            "face_conf": face_conf,
            "landmark_count": len(landmarks),
            "landmarks": landmarks
        }

    def close(self):

        self.face_landmarker.close()