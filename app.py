import streamlit as st

st.set_page_config(
    page_title="LingoBridge - Learn English",
    page_icon="🌍",
    layout="centered",
    initial_sidebar_state="auto"
)

# Responsive Styling for Mobile and Computer screens
st.markdown("""
    <style>
    /* Mobile-first responsive tweaks */
    .chat-container {
        max-height: 400px;
        overflow-y: auto;
        padding: 12px;
        background-color: #f8f9fa;
        border-radius: 12px;
        border: 1px solid #e9ecef;
        margin-bottom: 15px;
    }
    .bubble-user {
        background-color: #e3f2fd;
        color: #0d47a1;
        padding: 10px 14px;
        border-radius: 15px 15px 3px 15px;
        margin: 6px 0;
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
        border-radius: 15px 15px 15px 3px;
        margin: 6px 0;
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
    /* Mobile button sizing optimization */
    @media (max-width: 768px) {
        .stButton button {
            width: 100%;
            font-size: 16px;
        }
    }
    </style>
""", unsafe_allow_html=True)

st.title("🌍 LingoBridge: Mobile & Desktop English Tutor")
st.markdown("Practice speaking in your native language on your phone or computer. The app listens patiently, translates into English, and reads it back aloud.")

# Sidebar Settings
with st.sidebar:
    st.header("⚙️ Settings")
    native_language = st.selectbox(
        "Your Native Language",
        options=[
            ("Spanish (Spain)", "es-ES"),
            ("French (France)", "fr-FR"),
            ("German (Germany)", "de-DE"),
            ("Mandarin Chinese", "zh-CN"),
            ("Hindi (India)", "hi-IN"),
            ("Arabic", "ar-SA"),
            ("Japanese", "ja-JP"),
            ("Portuguese (Brazil)", "pt-BR"),
            ("Russian", "ru-RU")
        ],
        format_func=lambda x: x[0]
    )
    
    st.markdown("---")
    st.info("📱 **Mobile Tip:** Ensure your browser (Chrome on Android / Safari on Chrome on iOS) has permission to access your microphone.")
    
    if st.button("🔄 Refresh Conversation"):
        st.session_state.conversation = []
        st.rerun()

# Initialize session state
if "conversation" not in st.session_state:
    st.session_state.conversation = []

# Main Conversation Display Box
st.subheader("💬 Conversation Box")

chat_html = '<div class="chat-container">'
if not st.session_state.conversation:
    chat_html += '<p style="color: #6c757d; text-align: center; margin-top: 100px; font-size: 14px;">Tap <b>Start Speaking</b> below and start practicing your English!</p>'
else:
    for item in st.session_state.conversation:
        chat_html += f'<div class="bubble-user"><b>You ({native_language[0]}):</b><br>{item["user"]}</div><div class="clearfix"></div>'
        chat_html += f'<div class="bubble-translation"><b>English Translation:</b><br>{item["translation"]}</div><div class="clearfix"></div>'
chat_html += '</div>'

st.markdown(chat_html, unsafe_allow_html=True)

# Cross-Platform HTML5 / JavaScript Voice Component
voice_component = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
</head>
<body>
    <div style="text-align: center; margin-top: 5px;">
        <button id="recordBtn" style="background-color: #4CAF50; color: white; padding: 14px 24px; font-size: 16px; font-weight: bold; border: none; border-radius: 30px; cursor: pointer; box-shadow: 0 4px 6px rgba(0,0,0,0.1); width: 85%; max-width: 300px;">
            🎙️ Start Speaking
        </button>
        <p id="status" style="margin-top: 10px; font-size: 14px; color: #555; padding: 0 10px;"></p>
    </div>

    <script>
        const langCode = "{native_language[1]}";
        const recordBtn = document.getElementById("recordBtn");
        const statusText = document.getElementById("status");

        let SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        let isListening = false;

        if (!SpeechRecognition) {
            statusText.innerHTML = "❌ Speech Recognition is limited on this browser. Try Google Chrome on Android/PC or Safari on iOS.";
            recordBtn.style.backgroundColor = "#9e9e9e";
        } else {
            let recognition = new SpeechRecognition();
            recognition.lang = langCode;
            recognition.interimResults = true;
            recognition.maxAlternatives = 1;
            recognition.continuous = true; 

            let finalTranscript = "";
            let silenceTimer = null;

            recordBtn.onclick = function() {
                // Mobile browsers require user interaction to unlock speech synthesis/recognition
                unlockAudio();
                
                if (!isListening) {
                    try {
                        recognition.start();
                    } catch (e) {{}}
                } else {
                    recognition.stop();
                }
            };

            function unlockAudio() {{
                let synth = window.speechSynthesis;
                if (synth && synth.paused) {{
                    synth.resume();
                }}
            }}

            recognition.onstart = function() {
                isListening = true;
                finalTranscript = "";
                recordBtn.innerHTML = "🛑 Listening (Speak Now)...";
                recordBtn.style.backgroundColor = "#d32f2f";
                statusText.innerHTML = "Listening patiently... Take your time.";
            };

            recognition.onresult = function(event) {
                let interimTranscript = "";
                for (let i = event.resultIndex; i < event.results.length; ++i) {{
                    if (event.results[i].isFinal) {{
                        finalTranscript += event.results[i][0].transcript;
                    }} else {{
                        interimTranscript += event.results[i][0].transcript;
                    }}
                }}
                
                statusText.innerHTML = "<b>Hearing:</b> " + (finalTranscript + interimTranscript);

                // Patient timer: wait a few seconds after user stops talking
                clearTimeout(silenceTimer);
                silenceTimer = setTimeout(() => {{
                    if (isListening) {{
                        recognition.stop();
                    }}
                }}, 2500);
            };

            recognition.onerror = function(event) {
                statusText.innerHTML = "⚠️ Note: " + event.error;
                resetButton();
            };

            recognition.onend = function() {
                isListening = false;
                resetButton();
                
                if (finalTranscript.trim().length > 0) {{
                    statusText.innerHTML = "🔄 Translating to English...";
                    processTranslation(finalTranscript.trim());
                }}
            };
        }

        function resetButton() {{
            recordBtn.innerHTML = "🎙️ Start Speaking";
            recordBtn.style.backgroundColor = "#4CAF50";
        }}

        function processTranslation(text) {{
            // Simulated intelligent translation placeholder (connect to DeepL/OpenAI API for production)
            const translatedEnglish = "I understand: \"" + text + "\". Let's practice saying this in English.";
            
            // Speak aloud in English (works across mobile and desktop)
            speakEnglish(translatedEnglish);
        }}

        function speakEnglish(textToSpeak) {{
            if (!('speechSynthesis' in window)) {{
                statusText.innerHTML = "✅ Translation ready (Audio not supported on this browser)";
                return;
            }}

            statusText.innerHTML = "🔊 Speaking English translation...";
            window.speechSynthesis.cancel(); // Clear any hanging audio queue
            
            let utterance = new SpeechSynthesisUtterance(textToSpeak);
            utterance.lang = "en-US";
            utterance.rate = 0.9; // Optimal speed for learning
            
            utterance.onend = function() {{
                statusText.innerHTML = "✅ Ready for your next sentence. Tap start to continue.";
            }};
            
            window.speechSynthesis.speak(utterance);
        }}
    </script>
</body>
</html>
"""

st.components.v1.html(voice_component, height=170)
