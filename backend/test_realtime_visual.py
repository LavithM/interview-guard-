import cv2

from app.services.realtime_visual_service import (
    RealtimeVisualService
)


image_path = "test_face.jpg"

frame = cv2.imread(image_path)

if frame is None:
    print("Could not load test_face.jpg")
    exit()


service = RealtimeVisualService()


result = service.process_frame(frame)


print()
print("Real-time visual result:")
print("------------------------")

print("Face detected:", result["face_detected"])

if result["face_detected"]:

    print("Blink:", result["blink"])

    print("Gaze:", result["gaze"])

    print("Head pose:")
    print(
        "  Yaw:",
        result["head_pose"]["yaw"]
    )

    print(
        "  Pitch:",
        result["head_pose"]["pitch"]
    )

    print(
        "  Roll:",
        result["head_pose"]["roll"]
    )

    print(
        "Lip movement:",
        result["lip_movement"]
    )


service.close()
