import cv2

from app.services.vision_service import VisionService
from app.services.head_pose_service import HeadPoseService


vision = VisionService()
head_pose = HeadPoseService()

image = cv2.imread("test_face.jpg")

if image is None:
    print("ERROR: test_face.jpg could not be loaded.")
    vision.close()
    exit()


height, width = image.shape[:2]

vision_result = vision.process_frame(image)

if not vision_result["face_detected"]:
    print("No face detected.")
    vision.close()
    exit()


pose_result = head_pose.calculate(
    vision_result["landmarks"],
    width,
    height,
)


print("Head pose:")
print("Yaw:", pose_result["yaw"])
print("Pitch:", pose_result["pitch"])
print("Roll:", pose_result["roll"])


vision.close()