import cv2

from app.services.vision_service import VisionService
from app.services.blink_service import BlinkService


vision = VisionService()
blink = BlinkService()

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


blink_result = blink.calculate(
    vision_result["landmarks"]
)


print("Blink analysis:")
print(
    "Left EAR:",
    blink_result["left_ear"]
)

print(
    "Right EAR:",
    blink_result["right_ear"]
)

print(
    "Average EAR:",
    blink_result["average_ear"]
)

print(
    "Blink:",
    blink_result["blink"]
)


vision.close()