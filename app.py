import streamlit as st

st.set_page_config(
    page_title="LingoBridge - Learn English",
    page_icon="🌍",
    layout="centered"
)

st.title("🌍 LingoBridge: Mobile & Desktop English Tutor")
st.markdown("Practice speaking in your native language. The app listens patiently, translates into English, and reads it back aloud.")

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
    st.info("📱 Ensure your browser has permission to access your microphone.")
    
    if st.button("🔄 Refresh Conversation"):
        st.session_state.conversation = []
        st.rerun()

# Initialize session state
if "conversation" not in st.session_state:
    st.session_state.conversation = []

# Main Conversation Display Box
st.subheader("💬 Conversation Box")

chat_html = '<div style="max-height: 350px; overflow-y: auto; padding: 10px; background-color: #f8f9fa; border-radius: 10px; border: 1px solid #ddd; margin-bottom: 15px;">'
if not st.session_state.conversation:
    chat_html += '<p style="color: #666; text-align: center; margin-top: 100px;">Tap <b>Start Speaking</b> below to practice!</p>'
else:
    for item in st.session_state.conversation:
        chat_html += f'<div style="background: #e3f2fd; color: #0d47a1; padding: 10px; border-radius: 10px; margin: 5px 0; float: right; clear: both; max-width: 80%;"><b>You:</b><br>{item["user"]}</div><div style="clear: both;"></div>'
        chat_html += f'<div style="background: #e8f5e9; color: #1b5e20; padding: 10px; border-radius: 10px; margin: 5px 0; float: left; clear: both; max-width: 80%; border-left: 4px solid #4caf50;"><b>English:</b><br>{item["translation"]}</div><div style="clear: both;"></div>'
chat_html += '</div>'

st.markdown(chat_html, unsafe_allow_html=True)

# Clean HTML/JS component using standard string replacement (Zero f-string risk)
html_template = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
</head>
<body>
    <div style="text-align: center;">
        <button id="recordBtn" style="background-color: #4CAF50; color: white; padding: 14px 24px; font-size: 16px; font-weight: bold; border: none; border-radius: 30px; cursor: pointer; width: 85%; max-width: 300px;">
            🎙️ Start Speaking
        </button>
        <p id="status" style="margin-top: 10px; font-size: 14px; color: #555;"></p>
    </div>

    <script>
        const langCode = "LANGUAGE_CODE_PLACEHOLDER";
        const recordBtn = document.getElementById("recordBtn");
        const statusText = document.getElementById("status");

        let SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        let isListening = false;

        if (!SpeechRecognition) {
            statusText.innerHTML = "❌ Speech Recognition not supported. Use Google Chrome or Safari.";
            recordBtn.style.backgroundColor = "#999";
        } else {
            let recognition = new SpeechRecognition();
            recognition.lang = langCode;
            recognition.interimResults = true;
            recognition.continuous = true; 

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
                statusText.innerHTML = "Listening patiently... Take your time.";
            };

            recognition.onresult = function(event) {
                let interim = "";
                for (let i = event.resultIndex; i < event.results.length; ++i) {
                    if (event.results[i].isFinal) {
                        finalTranscript += event.results[i][0].transcript;
                    } else {
                        interim += event.results[i][0].transcript;
                    }
                }
                statusText.innerHTML = "<b>Hearing:</b> " + (finalTranscript + interim);

                clearTimeout(silenceTimer);
                silenceTimer = setTimeout(() => {
                    if (isListening) { recognition.stop(); }
                }, 2500);
            };

            recognition.onerror = function(event) {
                statusText.innerHTML = "⚠️ Note: " + event.error;
                resetBtn();
            };

            recognition.onend = function() {
                isListening = false;
                resetBtn();
                if (finalTranscript.trim().length > 0) {
                    statusText.innerHTML = "🔄 Translating...";
                    speakEnglish("I understand: " + finalTranscript.trim() + ". Let's practice this in English!");
                }
            };
        }

        function resetBtn() {
            recordBtn.innerHTML = "🎙️ Start Speaking";
            recordBtn.style.backgroundColor = "#4CAF50";
        }

        function speakEnglish(text) {
            if (!('speechSynthesis' in window)) return;
            statusText.innerHTML = "🔊 Speaking English translation...";
            window.speechSynthesis.cancel();
            let utterance = new SpeechSynthesisUtterance(text);
            utterance.lang = "en-US";
            utterance.rate = 0.9;
            utterance.onend = function() {
                statusText.innerHTML = "✅ Ready for your next sentence!";
            };
            window.speechSynthesis.speak(utterance);
        }
    </script>
</body>
</html>
"""

# Inject the selected language safely
final_html = html_template.replace("LANGUAGE_CODE_PLACEHOLDER", native_language[1])
st.components.v1.html(final_html, height=160)
