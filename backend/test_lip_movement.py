import cv2

from app.services.vision_service import VisionService
from app.services.lip_movement_service import LipMovementService


vision = VisionService()
lip_movement = LipMovementService()

image = cv2.imread("test_face.jpg")

if image is None:
    print("ERROR: test_face.jpg could not be loaded.")
    vision.close()
    exit()


vision_result = vision.process_frame(image)

if not vision_result["face_detected"]:
    print("No face detected.")
    vision.close()
    exit()


result = lip_movement.calculate(
    vision_result["landmarks"]
)


print("Lip movement:")
print("Mouth open:", result["mouth_open"])
print("Lip movement:", result["lip_movement"])


vision.close()
