const camera = document.getElementById("camera");
const status = document.getElementById("status");

let lastExpression = "";
let speaking = false;


// =====================================================
// AUDIO FILES
// =====================================================

const audioFiles = {

    neutral:
        "/static/audio/aare.mpeg",

    smiling:
        "/static/audio/produce.mpeg",

    surprised:
        "/static/audio/youagain.mpeg",

    closed_eyes:
        "/static/audio/thamara.mpeg"
};


// =====================================================
// CAMERA
// =====================================================

async function startCamera() {

    try {

        const stream =
            await navigator.mediaDevices.getUserMedia({

                video: true,

                audio: false

            });


        camera.srcObject = stream;


        status.textContent =
            "Camera ready. Look into the mirror...";


        startDetection();


    } catch (error) {

        console.error(
            "Camera error:",
            error
        );


        status.textContent =
            "Please allow camera access.";

    }
}


// =====================================================
// PLAY AUDIO
// =====================================================

function playAudio(expression) {

    if (speaking) {

        return;

    }


    const audioFile =
        audioFiles[expression];


    if (!audioFile) {

        return;

    }


    speaking = true;


    const audio =
        new Audio(audioFile);


    audio.onended = () => {

        speaking = false;

    };


    audio.onerror = (error) => {

        console.error(
            "Audio playback error:",
            error
        );

        speaking = false;

    };


    audio.play().catch(error => {

        console.error(
            "Could not play audio:",
            error
        );

        speaking = false;

    });
}


// =====================================================
// DETECTION
// =====================================================

function startDetection() {

    const canvas =
        document.createElement("canvas");


    const context =
        canvas.getContext("2d");


    setInterval(async () => {

        // Camera not ready
        if (
            camera.videoWidth === 0 ||
            camera.videoHeight === 0
        ) {

            return;

        }


        // Don't start another audio
        // while audio is playing.

        if (speaking) {

            return;

        }


        // Set canvas size

        canvas.width =
            camera.videoWidth;

        canvas.height =
            camera.videoHeight;


        // Copy camera frame

        context.drawImage(

            camera,

            0,
            0,

            canvas.width,
            canvas.height

        );


        // Convert to JPEG

        const image =
            canvas.toDataURL(
                "image/jpeg"
            );


        try {

            // Send image to Flask

            const response =
                await fetch(
                    "/analyze",
                    {

                        method: "POST",

                        headers: {

                            "Content-Type":
                                "application/json"

                        },

                        body: JSON.stringify({

                            image: image

                        })

                    }
                );


            const result =
                await response.json();


            const expression =
                result.expression;


            // =================================================
            // DISPLAY
            // =================================================

            let expressionText;


            if (
                expression === "smiling"
            ) {

                expressionText =
                    "😄 Smile detected!";

            }

            else if (
                expression === "surprised"
            ) {

                expressionText =
                    "😮 Surprise detected!";

            }

            else if (
                expression === "closed_eyes"
            ) {

                expressionText =
                    "😴 Eyes closed!";

            }

            else if (
                expression === "neutral"
            ) {

                expressionText =
                    "😐 Neutral detected!";

            }

            else {

                expressionText =
                    "👀 Look into the mirror...";

            }


            status.textContent =
                expressionText;


            // =================================================
            // PLAY AUDIO WHEN EXPRESSION CHANGES
            // =================================================

            if (
                expression !== lastExpression
                &&
                (
                    expression === "neutral" ||
                    expression === "smiling" ||
                    expression === "surprised" ||
                    expression === "closed_eyes"
                )
            ) {

                playAudio(expression);

            }


            // Save current expression

            lastExpression =
                expression;


        }

        catch (error) {

            console.error(
                "Detection error:",
                error
            );

        }

    }, 1500);
}


// =====================================================
// START
// =====================================================

startCamera();