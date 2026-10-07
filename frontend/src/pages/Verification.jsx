import { useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import "./Verification.css";

function Verification() {
  const navigate = useNavigate();

  const videoRef = useRef(null);
  const canvasRef = useRef(null);

  const [cameraStream, setCameraStream] = useState(null);
  const [photo, setPhoto] = useState(null);
  const [idImage, setIdImage] = useState(null);
  const [error, setError] = useState("");
  const [photoMessage, setPhotoMessage] = useState("");

  const startCamera = async () => {
    try {
      setError("");
      setPhotoMessage("");

      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 1280 },
          height: { ideal: 720 },
          facingMode: "user",
        },
        audio: false,
      });

      videoRef.current.srcObject = stream;
      setCameraStream(stream);

    } catch (err) {
      console.error(err);
      setError(
        "Camera access is required for identity verification."
      );
    }
  };

  const takePhoto = () => {
    const video = videoRef.current;
    const canvas = canvasRef.current;

    if (!video || !canvas) return;

    if (video.videoWidth === 0 || video.videoHeight === 0) {
      setError(
        "Camera is not ready. Please wait a moment and try again."
      );
      return;
    }

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    const context = canvas.getContext("2d");

    context.drawImage(
      video,
      0,
      0,
      canvas.width,
      canvas.height
    );

    const image = canvas.toDataURL("image/jpeg", 0.9);

    setPhoto(image);

    setPhotoMessage(
      "Photo captured. Face verification will be added next."
    );

    setError("");
  };

  const retakePhoto = () => {
    setPhoto(null);
    setPhotoMessage("");
    setError("");
  };

  const handleIdUpload = (event) => {
    const file = event.target.files[0];

    if (!file) return;

    if (!file.type.startsWith("image/")) {
      setError(
        "Please upload a valid image of your government ID."
      );
      return;
    }

    if (file.size > 5 * 1024 * 1024) {
      setError(
        "Government ID image must be less than 5 MB."
      );
      return;
    }

    setError("");

    const reader = new FileReader();

    reader.onload = () => {
      setIdImage(reader.result);
    };

    reader.readAsDataURL(file);
  };

  const continueVerification = () => {
    if (!photo) {
      setError("Please take your photo first.");
      return;
    }

    if (!idImage) {
      setError("Please upload your government ID.");
      return;
    }

    if (cameraStream) {
      cameraStream.getTracks().forEach((track) => {
        track.stop();
      });

      setCameraStream(null);
    }

    // Temporarily store verification data.
    // Later this will be securely sent to the backend.
    window.candidatePhoto = photo;
    window.candidateIdImage = idImage;

    // Go to Ready page
    navigate("/ready");
  };

  return (
    <div className="verification-page">

      <div className="verification-card">

        <h1>Identity Verification</h1>

        <p className="verification-description">
          Before starting the interview, verify your identity.
        </p>

        {/* CANDIDATE PHOTO */}

        <div className="verification-section">

          <h2>1. Candidate Photo</h2>

          <p>
            Position your face clearly inside the centre guide.
          </p>

          <div className="verification-camera">

            {photo ? (
              <img
                src={photo}
                alt="Candidate"
              />
            ) : (
              <>
                <video
                  ref={videoRef}
                  autoPlay
                  muted
                  playsInline
                />

                {cameraStream && (
                  <div className="face-guide">
                    <div className="face-oval"></div>
                    <p>Place your face here</p>
                  </div>
                )}
              </>
            )}

          </div>

          <canvas
            ref={canvasRef}
            style={{ display: "none" }}
          />

          {!cameraStream && !photo && (
            <button
              type="button"
              onClick={startCamera}
            >
              OPEN CAMERA
            </button>
          )}

          {cameraStream && !photo && (
            <button
              type="button"
              onClick={takePhoto}
            >
              TAKE PHOTO
            </button>
          )}

          {photo && (
            <button
              type="button"
              onClick={retakePhoto}
            >
              RETAKE PHOTO
            </button>
          )}

          {photoMessage && (
            <p className="photo-message">
              {photoMessage}
            </p>
          )}

        </div>

        {/* GOVERNMENT ID */}

        <div className="verification-section">

          <h2>2. Government ID</h2>

          <p>
            Upload a clear picture of your government-issued ID.
          </p>

          <label className="upload-button">

            {idImage
              ? "CHANGE ID IMAGE"
              : "UPLOAD GOVERNMENT ID"}

            <input
              type="file"
              accept="image/jpeg,image/png,image/webp"
              onChange={handleIdUpload}
              hidden
            />

          </label>

          {idImage && (
            <img
              className="id-preview"
              src={idImage}
              alt="Government ID"
            />
          )}

        </div>

        {error && (
          <p className="verification-error">
            {error}
          </p>
        )}

        <button
          className="continue-verification"
          onClick={continueVerification}
        >
          CONTINUE
        </button>

      </div>

    </div>
  );
}

export default Verification;