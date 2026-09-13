from flask import Flask, render_template, jsonify, request, send_file
import cv2
import numpy as np
import base64
from gtts import gTTS
from io import BytesIO

app = Flask(__name__)


# =========================================================
# FACE DETECTOR
# =========================================================

face_detector = cv2.CascadeClassifier(
    cv2.data.haarcascades +
    "haarcascade_frontalface_default.xml"
)


# =========================================================
# SMILE DETECTOR
# =========================================================

smile_detector = cv2.CascadeClassifier(
    cv2.data.haarcascades +
    "haarcascade_smile.xml"
)


# =========================================================
# EYE DETECTOR
# =========================================================

eye_detector = cv2.CascadeClassifier(
    cv2.data.haarcascades +
    "haarcascade_eye.xml"
)


# =========================================================
# HOME PAGE
# =========================================================

@app.route("/")
def home():
    return render_template("index.html")


# =========================================================
# ANALYZE IMAGE
# =========================================================

@app.route("/analyze", methods=["POST"])
def analyze():

    try:

        # -------------------------------------------------
        # GET IMAGE
        # -------------------------------------------------

        data = request.json["image"]

        image_data = base64.b64decode(
            data.split(",")[1]
        )

        image_array = np.frombuffer(
            image_data,
            np.uint8
        )

        frame = cv2.imdecode(
            image_array,
            cv2.IMREAD_COLOR
        )

        if frame is None:

            return jsonify({
                "error": "Could not read image"
            }), 400


        # =================================================
        # GRAYSCALE
        # =================================================

        gray = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2GRAY
        )


        # =================================================
        # FACE DETECTION
        # =================================================

        faces = face_detector.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(50, 50)
        )


        expression = "no face"


        # =================================================
        # EXPRESSION DETECTION
        # =================================================

        if len(faces) > 0:

            # Use first face

            x, y, w, h = faces[0]

            face_gray = gray[
                y:y + h,
                x:x + w
            ]


            # -------------------------------------------------
            # SMILE DETECTION
            # -------------------------------------------------

            smiles = smile_detector.detectMultiScale(
                face_gray,
                scaleFactor=1.7,
                minNeighbors=20,
                minSize=(25, 25)
            )


            # -------------------------------------------------
            # EYE DETECTION
            # -------------------------------------------------

            eyes = eye_detector.detectMultiScale(
                face_gray,
                scaleFactor=1.1,
                minNeighbors=8,
                minSize=(20, 20)
            )


            # =================================================
            # EXPRESSION DECISION
            # =================================================

            if len(smiles) > 0:

                expression = "smiling"

            elif len(eyes) >= 2:

                expression = "surprised"

            elif len(eyes) == 0:

                expression = "closed_eyes"

            else:

                expression = "neutral"


        # =================================================
        # NO HAND DETECTION
        # =================================================

        gesture = "none"


        # =================================================
        # SEND RESULT
        # =================================================

        return jsonify({

            "expression": expression,

            "gesture": gesture

        })


    except Exception as e:

        print("ERROR:", e)

        return jsonify({

            "error": str(e)

        }), 500


# =========================================================
# MALAYALAM TEXT-TO-SPEECH
# =========================================================

@app.route("/speak", methods=["POST"])
def speak():

    try:

        data = request.json

        text = data["text"]

        audio = BytesIO()

        tts = gTTS(
            text=text,
            lang="ml",
            slow=False
        )

        tts.write_to_fp(audio)

        audio.seek(0)

        return send_file(
            audio,
            mimetype="audio/mpeg"
        )


    except Exception as e:

        print("VOICE ERROR:", e)

        return jsonify({

            "error": str(e)

        }), 500


# =========================================================
# START SERVER
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )