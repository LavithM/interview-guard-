import cv2

from app.services.hand_detection_service import HandDetectionService


service = HandDetectionService()

camera = cv2.VideoCapture(0)

print("Camera started.")
print("Show your hand to the camera.")
print("Press Q to quit.")

while True:
    success, frame = camera.read()

    if not success:
        print("Could not read camera.")
        break

    result = service.process_frame(frame)

    print(result)

    cv2.putText(
        frame,
        f"Hands: {result['hand_count']}",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        2,
    )

    cv2.imshow("InterviewGuard Hand Test", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

camera.release()
cv2.destroyAllWindows()
service.close()
