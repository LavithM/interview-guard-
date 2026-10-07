from ultralytics import YOLO


class ObjectDetectionService:

    def __init__(self):

        self.model = YOLO(
            "yolo11n.pt"
        )

    def process_frame(self, frame):

        if frame is None:
            return {
                "person_count": 0,
                "maximum_person_count": 0,
                "person_count_above_one": False,
                "mobile_phone_detected": False,
                "mobile_phone_detections": 0,
                "mobile_phone_confidence": 0.0,
                "objects": [],
            }

        results = self.model(
            frame,
            verbose=False
        )

        objects = []

        person_count = 0
        phone_count = 0
        maximum_phone_confidence = 0.0

        for result in results:

            if result.boxes is None:
                continue

            for box in result.boxes:

                class_id = int(
                    box.cls[0].item()
                )

                confidence = float(
                    box.conf[0].item()
                )

                class_name = (
                    self.model.names[class_id]
                )

                x1, y1, x2, y2 = (
                    box.xyxy[0].tolist()
                )

                objects.append({
                    "class": class_name,
                    "confidence": round(
                        confidence,
                        4
                    ),
                    "bbox": [
                        round(x1, 2),
                        round(y1, 2),
                        round(x2, 2),
                        round(y2, 2),
                    ],
                })

                if class_name == "person":

                    person_count += 1

                if class_name == "cell phone":

                    phone_count += 1

                    maximum_phone_confidence = max(
                        maximum_phone_confidence,
                        confidence
                    )

        return {
            "person_count": person_count,

            "maximum_person_count": person_count,

            "person_count_above_one": (
                person_count > 1
            ),

            "mobile_phone_detected": (
                phone_count > 0
            ),

            "mobile_phone_detections": phone_count,

            "mobile_phone_confidence": round(
                maximum_phone_confidence,
                4
            ),

            "objects": objects,
        }