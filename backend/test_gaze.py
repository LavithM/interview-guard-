import cv2

from app.services.vision_service import VisionService
from app.services.gaze_service import GazeService


vision = VisionService()
gaze = GazeService()

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


gaze_result = gaze.calculate(
    vision_result["landmarks"]
)


print("Gaze analysis:")
print(
    "Horizontal:",
    gaze_result["horizontal"]
)

print(
    "Vertical:",
    gaze_result["vertical"]
)

print(
    "Gaze score:",
    gaze_result["gaze_score"]
)


vision.close()
