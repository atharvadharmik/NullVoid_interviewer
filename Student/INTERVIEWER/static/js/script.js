let recordingCount=0;
let noFaceDetectedCount = 0;
// console.log(initial_response)
//TIMER AT TOP///////////////////////////////////////////////////




// AI VOICE////////////////////////////////////////////
function speakText() {
  var questionElement = document.getElementById("questionText");
  toSend=questionElement.textContent
  if(toSend==''){
    console.log("Empty Q")
    return
  }
  console.log('test3')
  fetch('/synthesize', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      "text": toSend
  })
})
.then(response => response.blob())
.then(blob => {
    const audio = new Audio(URL.createObjectURL(blob));
    console.log('test4')
    audio.play();
});
}



// NEXT QUESTION////////////////////////////////////////////////////////////////////////
document.addEventListener("DOMContentLoaded", function() {
    var nextQuestionButton = document.getElementById("nextQuestion");
    var questionElement = document.getElementById("questionText");
    const recordBtn = document.getElementById('recordBtn');
    const transcriptDisplay = document.getElementById('transcriptDisplay');
    var timerElement = document.getElementById("timer");
    var timerInterval;  // Variable to store the timer interval
  
    
    // NextQuestion /////////////////////////////////////////////
    function fetchNextQuestion() {
      nextQuestionButton.disabled=true
        fetch("/get_next_question", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                "transcript": transcriptDisplay.value
            })
        })
        .then(response => response.json())
        .then(data => {
            questionElement.innerHTML = data.next_question;
            nextQuestionButton.disabled = data.completed;  // Disable button if interview completed
            transcriptDisplay.value = '';  // Empty the transcriptDisplay
            recordBtn.disabled = false;   // Enable the recordBtn
            recordingCount=0
            speakQuestion()
            resetTimer()
            if (data.completed) {
                // Trigger data transfer and deletion on the server
                fetch('/transfer_data', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ number: noFaceDetectedCount })
                })
                .then(response => response.json())
                .then(data => {
                    console.log(data.message);
                });
                
                transcriptDisplay.value="PLEASE EXIT THE TEST USING THE BUTTON ON BOTTOM RIGHT"
            }
        });
    }
  
  
/// Question Speaker ///////////////////////////////////////////////////////////
        function speakQuestion() {
        nextQuestionButton.disabled=true;
        recordBtn.disabled=true;
        console.log('test1');
        speakText();
        console.log('test2');
        nextQuestionButton.disabled=false;
        recordBtn.disabled=false;
        }
        speakQuestion()


// Timer Function /////////////////////////////////////////////////

    function startTimer() {
        var seconds = 180;
        timerInterval = setInterval(function() {
            seconds--;
            if (seconds < 0) {
                fetchNextQuestion();
                console.log("HERE");
                resetTimer();  // Automatically click "Next Question" button when timer hits 0
            } else {
                timerElement.textContent = `${Math.floor(seconds / 60)}:${(seconds % 60).toString().padStart(2, '0')}`;
            }
        }, 1000);
    }
    function resetTimer() {
        clearInterval(timerInterval);
        timerElement.textContent = "00:01:00";
        startTimer();
    }

    startTimer()
// Adds ///////////////////////////////////////////////////////  
    nextQuestionButton.addEventListener("click", fetchNextQuestion);
  });

  
// RECORDING FUNCTION ////////////////////////////////////////////////////////////////////////

let mediaRecorder;
let recordedChunks = [];
let isRecording = false;
const recordButton = document.getElementById('recordBtn');
const nextBtn = document.getElementById('nextQuestion');

function toggleRecording() {
    if (!isRecording) {
        navigator.mediaDevices.getUserMedia({ audio: true })
            .then(stream => {
                mediaRecorder = new MediaRecorder(stream);

                mediaRecorder.ondataavailable = event => {
                    if (event.data.size > 0) {
                        recordedChunks.push(event.data);
                    }
                };

                mediaRecorder.onstop = () => {
                    const audioBlob = new Blob(recordedChunks, { type: 'audio/wav' });

                    // Send the audio data to the server
                    fetch('/upload', {
                        method: 'POST',
                        body: audioBlob
                    })
                    .then(response => response.json())
                    .then(data => {
                        console.log(data.message);
                        displayTranscript(data.transcript);  // Display the transcript on the page
                    })
                    .catch(error => {
                        console.error('Error uploading audio:', error);
                    });

                    recordButton.textContent = 'Record Answer'; // Change button text back
                    nextBtn.disabled=false;
                };

                recordButton.textContent = 'Recording...';
                nextBtn.disabled=true;
                recordedChunks = [];
                mediaRecorder.start();
                isRecording = true;
            })
            .catch(error => {
                console.error('Error accessing microphone:', error);
            });
    } else {
        mediaRecorder.stop();
        isRecording = false;
    }

    recordingCount++;
    if (recordingCount >= 2) {
      recordButton.disabled = true;
    }
}

function displayTranscript(transcript) {
  const transcriptDisplay = document.getElementById('transcriptDisplay');
  transcriptDisplay.value = transcript; 
}


/////////////////////////////////////////////////////////////////////////////////////////////////
// Camera Panel

const video = document.getElementById("video");
const isScreenSmall = window.matchMedia("(max-width: 700px)");


/****Loading the model ****/
Promise.all([
  faceapi.nets.ssdMobilenetv1.loadFromUri("/static/models"),
]).then(startVideo);

function startVideo() {
  navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => {
      video.srcObject = stream;
      video.play(); // Start video playback
    })
    .catch(err => console.error(err));
}

/****Fixing the video with based on size size  ****/

function screenResize(isScreenSmall) {
  if (isScreenSmall.matches) {
    video.style.width = "100%"; // Adjust this as needed
  } else {
    video.style.width = "auto";
  }
}
/****Event Listeiner for the video****/
video.addEventListener("playing", () => {
//   const canvas = faceapi.createCanvasFromMedia(video);

//   const displaySize = { width: video.videoWidth, height: video.videoHeight };
//   faceapi.matchDimensions(canvas, displaySize);

  async function animate() {
    requestAnimationFrame(animate);
    try {
      const detections = await faceapi.detectSingleFace(video, new faceapi.SsdMobilenetv1Options());
      
    //   canvas.getContext("2d").clearRect(0, 0, canvas.width, canvas.height);

      if (detections) {
        // const resizedDetections = faceapi.resizeResults(detections, displaySize);
        // Draw facial landmarks using faceapi.draw.drawFaceLandmarks

      } else {
        noFaceDetectedCount++;
      }
    } catch (error) {
      console.error("Error during face detection:", error);
    }

  }

  animate();
});



/////////////////EXIT BUTTON/////////////////////////
function exitTest() {
  fetch("/exit_test", {
      method: "POST",
      headers: {
          "Content-Type": "application/json"
      }
  })
  .then(response => response.json())
  .then(data => {
      if (data.completed) {
           
              // Trigger data transfer and deletion on the server
              fetch('/transfer_data', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ number: noFaceDetectedCount })
            })
            .then(response => response.json())
            .then(data => {
                console.log(data.message);
            });

            // Display a pop-up message using window.alert
            window.alert("Congratulations on completing the interview!! Click OK to exit.");
            // Terminate the app after the user clicks OK
            window.location.href = "static/over.html"; // You can also close the browser window here
            // window.open("{{ url_for('static', filename='over.html') }}", "_blank");
            // window.location.href = "/terminate";

      }
  });
}
