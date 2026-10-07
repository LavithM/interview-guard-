import cv2

from app.services.visual_feature_service import VisualFeatureService


visual = VisualFeatureService()

image = cv2.imread("test_face.jpg")

if image is None:
    print("ERROR: test_face.jpg could not be loaded.")
    visual.close()
    exit()


result = visual.process_frame(image)


print("Visual feature result:")
print("----------------------")

print("Face detected:", result["face_detected"])
print("Blink:", result["blink"])
print("Gaze:", result["gaze"])

print("Head pose:")
print("  Yaw:", result["head_pose"]["yaw"])
print("  Pitch:", result["head_pose"]["pitch"])
print("  Roll:", result["head_pose"]["roll"])

print("Lip movement:", result["lip_movement"])


visual.close()
