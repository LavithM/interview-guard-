import cv2

from app.services.object_detection_service import (
    ObjectDetectionService
)


def main():

    detector = ObjectDetectionService()

    camera = cv2.VideoCapture(0)

    if not camera.isOpened():

        print("ERROR: Could not open camera.")

        return

    print()
    print("Camera started.")
    print("Show yourself to the camera.")
    print("Show a mobile phone to test phone detection.")
    print("Press Q to quit.")
    print()

    while True:

        success, frame = camera.read()

        if not success:

            print("ERROR: Could not read camera frame.")

            break

        result = detector.process_frame(
            frame
        )

        print(
            "\r"
            f"People: {result['person_count']} | "
            f"Phone: {result['mobile_phone_detected']} | "
            f"Phone count: {result['mobile_phone_detections']} | "
            f"Phone confidence: {result['mobile_phone_confidence']:.2f}",
            end="",
            flush=True
        )

        cv2.imshow(
            "InterviewGuard Object Detection Test",
            frame
        )

        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):

            break

    camera.release()

    cv2.destroyAllWindows()

    print()
    print()
    print("Camera test finished.")


if __name__ == "__main__":
    main()