import requests


BASE_URL = "http://127.0.0.1:8000"


print("\nSTARTING INTERVIEW")

response = requests.post(
    f"{BASE_URL}/interview/start",
    json={
        "name": "Object Detection Test",
        "email": "object@test.com",
        "role": "Software Engineer",
    }
)

print("Status:", response.status_code)

data = response.json()

interview_id = data[
    "session"
]["interview_id"]

print(
    "Interview ID:",
    interview_id
)


print("\nSENDING CAMERA FRAME")

with open(
    "test_face.jpg",
    "rb"
) as image_file:

    response = requests.post(
        f"{BASE_URL}/interview/{interview_id}/frame",
        files={
            "file": (
                "test_face.jpg",
                image_file,
                "image/jpeg"
            )
        }
    )

print(
    "Status:",
    response.status_code
)

result = response.json()

analysis = result["analysis"]

print("\nFACE")
print(
    "Face detected:",
    analysis.get(
        "face_detected"
    )
)

print("\nOBJECT DETECTION")

object_result = analysis.get(
    "object_detection",
    {}
)

print(
    "Person count:",
    object_result.get(
        "person_count"
    )
)

print(
    "Objects:"
)

for obj in object_result.get(
    "objects",
    []
):

    print(
        " -",
        obj["class"],
        "confidence:",
        obj["confidence"]
    )


print("\nBUILDING WINDOW")

response = requests.post(
    f"{BASE_URL}/interview/{interview_id}/window"
)

print(
    "Status:",
    response.status_code
)

window = response.json()["window"]

print(
    "\nWindow object detection:"
)

print(
    window.get(
        "object_detection"
    )
)


print("\nENDING INTERVIEW")

response = requests.post(
    f"{BASE_URL}/interview/{interview_id}/end"
)

print(
    "Status:",
    response.status_code
)

print("\nTEST COMPLETE")