import cv2

from app.services.vision_service import VisionService


vision = VisionService()

image = cv2.imread("test_face.jpg")

if image is None:
    print("ERROR: test_face.jpg was not found.")

    vision.close()
    exit()


result = vision.process_frame(image)


print("Vision result:")
print("Face detected:", result["face_detected"])


if result["face_detected"]:

    print(
        "Landmarks:",
        result["landmark_count"]
    )


vision.close()