import streamlit as st
import os
from textwrap import dedent

st.set_page_config(page_title="Voice Chatbot", layout="centered")

# 🌊 Full-screen gradient background + centered white block
st.markdown("""
    <style>
        html, body, [data-testid="stAppViewContainer"] {
            height: 600px;
            margin: 0;
            padding: 0;
            background: linear-gradient(135deg, #b3e5fc 0%, #e0f7fa 40%, #ffffff 100%);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }

        [data-testid="stHeader"], [data-testid="stToolbar"] {
            display: none;
        }

        .block-container {
            padding-top: 0 !important;
            padding-bottom: 0 !important;
        }

        # .voice-card {
        #     background: white;
        #     border-radius: 20px;
        #     padding: 30px;
        #     box-shadow: 0 8px 32px rgba(2,136,209,0.15);
        #     width: 700px;
        #     height: 600px;
        #     margin: 60px auto;
        #     text-align: center;
        #     display: flex;
        #     flex-direction: column;
        #     justify-content: center;
        # }

        .voice-card h1 {
            color: #015a8a;
            font-size: 2rem;
            margin-bottom: 20px;
        }

        .voice-card p {
            font-size: 1.1rem;
            color: #163a47;
        }

        footer {
            margin-top: 24px;
            color: #666;
            font-size: 0.9rem;
            text-align: center;
            background: transparent;
        }
    </style>
""", unsafe_allow_html=True)

backend_default = os.getenv("BACKEND_URL", "http://localhost:8000/chat")

# ⬜ Centered white card for voice bot
st.markdown('<div class="voice-card">', unsafe_allow_html=True)
# st.markdown("## 🎤 Voice Chatbot")
st.markdown("Click once to Start Recording, again to Stop. The recording plays back, then processes, and the response is shown below.")

# 🎙️ HTML Recorder
template = dedent("""
<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial; margin: 0; padding: 8px; }
    .recorder { background: white; padding:16px; border-radius:10px; text-align:center; }
    button { background:#0288d1; color:white; border:none; padding:10px 18px; border-radius:8px; font-size:16px; cursor:pointer }
    #status { margin-top:12px; color:#0288d1 }
    #response {
  margin-top: 16px;
  text-align: center;
  max-width: 720px;
  margin-left: auto;
  margin-right: auto;
  font-size: 1.1rem;
  color: #163a47;
  background: rgba(255,255,255,0.88);
  border-radius: 12px;
  box-shadow: 0 4px 18px rgba(2,136,209,0.06);
  padding: 16px 20px;
}

  </style>
</head>
<body>
  <div class="recorder">
    <h2>🎤 Voice Chatbot</h2>
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

    // ✅ Clear previous response and audio
    responseDiv.innerHTML = '';
    responseAudio.style.display = 'none';
    responseAudio.src = '';
    status.style.display = 'none';

  
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];

        mediaRecorder.ondataavailable = e => audioChunks.push(e.data);

        mediaRecorder.onstop = async () => {
          const blob = new Blob(audioChunks, { type: 'audio/webm' });

          const url = URL.createObjectURL(blob);
          responseAudio.src = url; responseAudio.style.display = 'block';
          responseAudio.play();
          status.style.display = 'block'; status.textContent = 'Playing your recording...';

          responseAudio.onended = async () => {
            status.textContent = 'Processing...';
            responseAudio.style.display = 'none'; responseAudio.src = '';

            const formData = new FormData();
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
st.components.v1.html(html, height=700, scrolling=True)

st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("Developed with ❤️ by Lakshmi Kumari.")
