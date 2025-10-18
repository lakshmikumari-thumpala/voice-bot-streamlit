import streamlit as st
import os
from textwrap import dedent

st.set_page_config(page_title="Voice Chatbot", layout="centered")

# 🌊 Styling and Layout
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

# 🌐 Backend Endpoint
backend_default = os.getenv("BACKEND_URL", "https://voice-bot-1-zwwg.onrender.com/chat")

# Voice Bot Card
st.markdown('<div class="voice-card">', unsafe_allow_html=True)
st.markdown("""
<div style="
    text-align: center; 
    background: rgba(255, 255, 255, 0.8); 
    border-radius: 12px; 
    box-shadow: 0 2px 8px rgba(2,136,209,0.08); 
    padding: 12px 16px; 
    margin: 15px auto; 
    max-width: 600px;
    line-height: 1.6;
    color: #015a8a;
    font-size: 1.05rem;">
    🎙️ Click once to <b>Start Recording</b>, again to <b>Stop</b>.<br>
    🔁 Your recording stays visible to replay anytime.<br>
    🧹 Starting a new recording clears the previous one.
</div>
""", unsafe_allow_html=True)


# 🎙️ HTML Recorder + Updated JavaScript
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
    audio { width: 100%; margin-top: 10px; border-radius: 10px; }
  </style>
</head>
<body>
  <div class="recorder">
    <h2>🎤 Voice Chatbot</h2>
    <button id="recordButton">Start Recording</button>
    <div id="status" style="display:none;"></div>
    <div id="audioContainer"></div>
    <div id="response"></div>
  </div>

  <script>
    const backend = '__BACKEND_URL__';
    const recordButton = document.getElementById('recordButton');
    const status = document.getElementById('status');
    const responseDiv = document.getElementById('response');
    const audioContainer = document.getElementById('audioContainer');

    let mediaRecorder;
    let audioChunks = [];
    let isRecording = false;

    recordButton.addEventListener('click', async () => {
      if (isRecording) {
        mediaRecorder.stop();
        recordButton.textContent = 'Start Recording';
        isRecording = false;
        return;
      }

      // Clear previous audios and response
      audioContainer.innerHTML = '';
      responseDiv.innerHTML = '';
      status.style.display = 'none';

      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];

        mediaRecorder.ondataavailable = e => audioChunks.push(e.data);

        mediaRecorder.onstop = async () => {
          const blob = new Blob(audioChunks, { type: 'audio/webm' });
          const url = URL.createObjectURL(blob);

          // 🎧 User recorded audio
          const userAudio = document.createElement('audio');
          userAudio.src = url;
          userAudio.controls = true;
          userAudio.style.display = 'block';
          audioContainer.appendChild(userAudio);
          userAudio.play();

          status.style.display = 'block';
          status.textContent = 'Processing...';

          const formData = new FormData();
          formData.append('audio', blob, 'recording.webm');

          try {
            const res = await fetch(backend, { method: 'POST', body: formData });
            const data = await res.json();

            responseDiv.innerHTML = data.response || 'No response';

            if (data.audio_base64) {
              const binary = atob(data.audio_base64);
              const bytes = new Uint8Array(binary.length);
              for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i);
              const audioBlob = new Blob([bytes], { type: 'audio/mp3' });
              const audioUrl = URL.createObjectURL(audioBlob);

              // 🎧 Bot response audio
              const botLabel = document.createElement('div');
              botLabel.innerHTML = "<b>🤖 Bot Reply:</b>";
              botLabel.style.marginTop = '10px';
              botLabel.style.color = '#015a8a';

              const botAudio = document.createElement('audio');
              botAudio.src = audioUrl;
              botAudio.controls = true;
              botAudio.style.display = 'block';

              audioContainer.appendChild(botLabel);
              audioContainer.appendChild(botAudio);
            }

            status.style.display = 'none';
          } catch (err) {
            status.textContent = 'Error contacting backend: ' + err.message;
          }
        };

        mediaRecorder.start();
        isRecording = true;
        recordButton.textContent = 'Stop Recording';
        status.style.display = 'block';
        status.textContent = 'Recording...';
      } catch (err) {
        status.style.display = 'block';
        status.textContent = 'Microphone access denied or not available.';
      }
    });
  </script>
</body>
</html>
""")

# Inject backend URL dynamically
html = template.replace('__BACKEND_URL__', backend_default)
st.components.v1.html(html, height=720, scrolling=True)

st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("Developed with ❤️ by **Lakshmi Kumari**.")
