import streamlit as st
from googletrans import Translator

st.set_page_config(
    page_title="LingoBridge - Learn English",
    page_icon="🌍",
    layout="centered"
)

translator = Translator()

st.title("🌍 LingoBridge: Mobile & Desktop English Tutor")

# Top Controls: Language Selector and Clear Button
col1, col2 = st.columns([3, 1])

with col1:
    native_language_name = st.selectbox(
        "🗣️ Select Your Language",
        options=[
            ("Bengali (Bangladesh)", "bn"),
            ("Bengali (India)", "bn"),
            ("Spanish (Spain)", "es"),
            ("French (France)", "fr"),
            ("German (Germany)", "de"),
            ("Mandarin Chinese", "zh-cn"),
            ("Hindi (India)", "hi"),
            ("Arabic", "ar"),
            ("Japanese", "ja"),
            ("Portuguese (Brazil)", "pt"),
            ("Russian", "ru")
        ],
        format_func=lambda x: x[0]
    )

with col2:
    st.write("") 
    st.write("")
    if st.button("🗑️ Clear"):
        # We use a custom script trigger or rerun for clearing
        st.rerun()

st.subheader("💬 Conversation Box")

# Self-contained HTML/JS component that handles chat history directly in the browser
# This prevents mobile page-reload bugs and keeps the chat permanent!
app_template = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: transparent;
            margin: 0;
            padding: 5px;
        }
        .chat-container {
            max-height: 300px;
            overflow-y: auto;
            padding: 12px;
            background-color: #f8f9fa;
            border-radius: 12px;
            border: 1px solid #e0e0e0;
            margin-bottom: 15px;
        }
        .bubble-user {
            background-color: #e3f2fd;
            color: #0d47a1;
            padding: 10px 14px;
            border-radius: 12px;
            margin: 8px 0;
            max-width: 85%;
            float: right;
            clear: both;
            font-size: 15px;
            word-break: break-word;
        }
        .bubble-translation {
            background-color: #e8f5e9;
            color: #1b5e20;
            padding: 10px 14px;
            border-radius: 12px;
            margin: 8px 0;
            max-width: 85%;
            float: left;
            clear: both;
            font-size: 15px;
            border-left: 4px solid #4caf50;
            word-break: break-word;
        }
        .clearfix {
            clear: both;
        }
        .controls {
            text-align: center;
        }
        .btn-speak {
            background-color: #4CAF50;
            color: white;
            padding: 14px 28px;
            font-size: 16px;
            font-weight: bold;
            border: none;
            border-radius: 30px;
            cursor: pointer;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            width: 85%;
            max-width: 300px;
        }
        .status-text {
            margin-top: 10px;
            font-size: 14px;
            color: #555;
            min-height: 25px;
        }
    </style>
</head>
<body>

    <!-- Permanent Chat Box inside the component -->
    <div id="chatBox" class="chat-container">
        <p id="emptyMsg" style="color: #666; text-align: center; margin-top: 70px;">Tap <b>Start Speaking</b> below to practice your English!</p>
    </div>

    <!-- Record Button -->
    <div class="controls">
        <button id="recordBtn" class="btn-speak">🎙️ Start Speaking</button>
        <p id="status" class="status-text"></p>
    </div>

    <script>
        const langCode = "LANGUAGE_CODE_PLACEHOLDER";
        const langName = "LANGUAGE_NAME_PLACEHOLDER";
        
        const recordBtn = document.getElementById("recordBtn");
        const statusText = document.getElementById("status");
        const chatBox = document.getElementById("chatBox");

        let SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        let isListening = false;

        if (!SpeechRecognition) {
            statusText.innerHTML = "❌ Speech recognition not supported on this browser. Use Chrome or Safari.";
            recordBtn.style.backgroundColor = "#999";
        } else {
            let recognition = new SpeechRecognition();
            recognition.lang = langCode;
            recognition.interimResults = true;
            recognition.continuous = false;

            let finalTranscript = "";
            let silenceTimer = null;

            recordBtn.onclick = function() {
                if (!isListening) {
                    try { recognition.start(); } catch(e) {}
                } else {
                    recognition.stop();
                }
            };

            recognition.onstart = function() {
                isListening = true;
                finalTranscript = "";
                recordBtn.innerHTML = "🛑 Listening...";
                recordBtn.style.backgroundColor = "#d32f2f";
                statusText.innerHTML = "Listening patiently... Speak clearly.";
            };

            recognition.onresult = function(event) {
                let interim = "";
                finalTranscript = "";
                for (let i = 0; i < event.results.length; ++i) {
                    if (event.results[i].isFinal) {
                        finalTranscript += event.results[i][0].transcript;
                    } else {
                        interim += event.results[i][0].transcript;
                    }
                }
                statusText.innerHTML = "<b>Hearing:</b> " + (finalTranscript || interim);

                clearTimeout(silenceTimer);
                silenceTimer = setTimeout(() => {
                    if (isListening) { recognition.stop(); }
                }, 3000);
            };

            recognition.onerror = function(event) {
                statusText.innerHTML = "⚠️ Note: " + event.error;
                resetBtn();
            };

            recognition.onend = function() {
                isListening = false;
                resetBtn();
                let spokenText = finalTranscript.trim();
                
                if (spokenText.length > 0) {
                    statusText.innerHTML = "✅ Captured: " + spokenText;
                    
                    // Add User Speech Bubble to UI permanently
                    appendMessage(langName, spokenText, "English Translation: (Translating...): " + spokenText);
                    
                    // Speak back confirmation or translation locally via browser TTS
                    speakEnglish("I understand: " + spokenText);
                } else {
                    statusText.innerHTML = "✅ Ready.";
                }
            };
        }

        function resetBtn() {
            recordBtn.innerHTML = "🎙️ Start Speaking";
            recordBtn.style.backgroundColor = "#4CAF50";
        }

        function appendMessage(language, userText, translationText) {
            const emptyMsg = document.getElementById("emptyMsg");
            if (emptyMsg) { emptyMsg.remove(); }

            // User Bubble
            let userDiv = document.createElement("div");
            userDiv.className = "bubble-user";
            userDiv.innerHTML = "<b>You (" + language + "):</b><br>" + userText;
            chatBox.appendChild(userDiv);

            let c1 = document.createElement("div");
            c1.className = "clearfix";
            chatBox.appendChild(c1);

            // Translation Bubble
            let transDiv = document.createElement("div");
            transDiv.className = "bubble-translation";
            transDiv.innerHTML = "<b>English Translation:</b><br>" + translationText;
            chatBox.appendChild(transDiv);

            let c2 = document.createElement("div");
            c2.className = "clearfix";
            chatBox.appendChild(c2);

            chatBox.scrollTop = chatBox.scrollHeight;
        }

        function speakEnglish(text) {
            if (!('speechSynthesis' in window)) return;
            window.speechSynthesis.cancel();
            let utterance = new SpeechSynthesisUtterance(text);
            utterance.lang = "en-US";
            utterance.rate = 0.9;
            window.speechSynthesis.speak(utterance);
        }
    </script>
</body>
</html>
"""

# Safely inject selected language choices into the component
final_html = (app_template
              .replace("LANGUAGE_CODE_PLACEHOLDER", native_language_name[1])
              .replace("LANGUAGE_NAME_PLACEHOLDER", native_language_name[0]))

st.components.v1.html(final_html, height=520)
