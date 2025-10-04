import streamlit as st
import os
from textwrap import dedent

st.set_page_config(page_title="Voice Chatbot", layout="centered")


backend_default = os.getenv("BACKEND_URL", "http://localhost:8000/chat")

st.markdown("**Instructions:** Allow microphone access when prompted. Click *Start Recording*, speak, then *Stop*. The recording plays back, then it will be sent to your backend and the response shown below the recorder.")

template = dedent("""
<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial; margin: 0; padding: 8px; }
    .recorder { background: linear-gradient(135deg,#e0f7fa 0%,#b3e5fc 40%,#fff 100%); padding:16px; border-radius:10px; text-align:center; }
    button { background:#0288d1; color:white; border:none; padding:10px 18px; border-radius:8px; font-size:16px; cursor:pointer }
    #status { margin-top:12px; color:#0288d1 }
    #response { margin-top:16px; text-align:left; max-width:720px; margin-left:auto; margin-right:auto }
  </style>
</head>
<body>
  <div class="recorder">
    <h3>🎤 Voice Chatbot </h3>
    <button id="recordButton">Start Recording</button>
    <div id="status" style="display:none;"></div>
    <audio id="responseAudio" controls style="display:none; width:100%; margin-top:12px"></audio>
    <div id="response"></div>
  </div>

  <script>
    const backend = '__BACKEND_URL__';
    const recordButton = document.getElementById('recordButton');
    const status = document.getElementById('status');
    const responseDiv = document.getElementById('response');
    const responseAudio = document.getElementById('responseAudio');

    let mediaRecorder; let audioChunks = []; let isRecording = false;

    recordButton.addEventListener('click', async () => {
      if (isRecording) {
        mediaRecorder.stop();
        recordButton.textContent = 'Start Recording';
        isRecording = false;
        return;
      }

      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];

        mediaRecorder.ondataavailable = e => audioChunks.push(e.data);

        mediaRecorder.onstop = async () => {
          const blob = new Blob(audioChunks, { type: 'audio/webm' });

          // Play back
          const url = URL.createObjectURL(blob);
          responseAudio.src = url; responseAudio.style.display = 'block';
          responseAudio.play();
          status.style.display = 'block'; status.textContent = 'Playing your recording...';

          responseAudio.onended = async () => {
            status.textContent = 'Processing...';
            responseAudio.style.display = 'none'; responseAudio.src = '';

            const formData = new FormData();
            // send as wav filename (server converts if needed)
            formData.append('audio', blob, 'recording.webm');

            try {
              const res = await fetch(backend, { method: 'POST', body: formData });
              const contentType = res.headers.get('content-type') || '';
              if (contentType.includes('audio')) {
                const audioBlob = await res.blob();
                const audioUrl = URL.createObjectURL(audioBlob);
                responseAudio.src = audioUrl; responseAudio.style.display = 'block'; responseAudio.play();
                status.textContent = 'Audio response received';
                responseDiv.innerHTML = '';
              } else {
                try {
                  const data = await res.json();
                  responseDiv.innerHTML = data.response || 'No response';
                } catch (err) {
                  const raw = await res.text(); responseDiv.textContent = raw || 'No response';
                }
                status.style.display = 'none';
              }
            } catch (err) {
              status.textContent = 'Error contacting backend: ' + err.message;
            }
          };
        };

        mediaRecorder.start();
        isRecording = true; recordButton.textContent = 'Stop Recording';
        status.style.display = 'block'; status.textContent = 'Recording...';
      } catch (err) {
        status.style.display = 'block'; status.textContent = 'Microphone access denied or not available.';
      }
    });
  </script>
</body>
</html>
""")

html = template.replace('__BACKEND_URL__', backend_default)

st.components.v1.html(html, height=520)

st.markdown("---")
st.caption("This app embeds the recorder as an HTML component and sends audio to the backend URL above. For easier deployment on Streamlit Cloud, make sure `requirements.txt` includes `streamlit`.")
