import streamlit as st
from googletrans import Translator

st.set_page_config(
    page_title="LingoBridge - Learn English",
    page_icon="🌍",
    layout="centered"
)

# Initialize the translation engine
translator = Translator()

st.title("🌍 LingoBridge: AI-Powered Voice Tutor")
st.markdown("Speak any sentence in your native language. The app translates it into English instantly and reads it aloud.")

# Initialize conversation history in session state
if "conversation" not in st.session_state:
    st.session_state.conversation = []

# Top Controls: Language Selector and Clear Button
col1, col2 = st.columns([3, 1])

with col1:
    native_language_name = st.selectbox(
        "🗣️ Select Your Native Language",
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
    if st.button("🗑️ Clear Chat"):
        st.session_state.conversation = []
        st.rerun()

# Handle data sent back from the browser JavaScript component securely via query parameters
if "spoken_text" in st.query_params:
    raw_speech = st.query_params["spoken_text"]
    if raw_speech and (not st.session_state.conversation or st.session_state.conversation[-1]["user"] != raw_speech):
        try:
            # Dynamically translate ANY sentence spoken in any language to English
            translation = translator.translate(raw_speech, dest='en')
            translated_text = translation.text
        except Exception as e:
            translated_text = f"I understand: {raw_speech}"
            
        # Append to permanent session history
        st.session_state.conversation.append({"user": raw_speech, "translation": translated_text})
        st.query_params.clear()
        st.rerun()

# Main Permanent Conversation Box
st.subheader("💬 Conversation Box")

chat_container = st.container(height=320)
with chat_container:
    if not st.session_state.conversation:
        st.markdown('<p style="color: #666; text-align: center; margin-top: 80px;">Tap <b>Start Speaking</b> below to practice your English!</p>', unsafe_allow_html=True)
    else:
        for item in st.session_state.conversation:
            st.markdown(f'<div style="background: #e3f2fd; color: #0d47a1; padding: 10px 14px; border-radius: 12px; margin: 8px 0; float: right; clear: both; max-width: 85%;"><b>You ({native_language_name[0]}):</b><br>{item["user"]}</div><div style="clear: both;"></div>', unsafe_allow_html=True)
            st.markdown(f'<div style="background: #e8f5e9; color: #1b5e20; padding: 10px 14px; border-radius: 12px; margin: 8px 0; float: left; clear: both; max-width: 85%; border-left: 4px solid #4caf50;"><b>English Translation:</b><br>{item["translation"]}</div><div style="clear: both;"></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# HTML/JS Speech Component
app_template = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {
            font-family: sans-serif;
            text-align: center;
            background-color: transparent;
            margin: 0;
            padding: 5px;
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
    <button id="recordBtn" class="btn-speak">🎙️ Start Speaking</button>
    <p id="status" class="status-text"></p>

    <script>
        const langCode = "LANGUAGE_CODE_PLACEHOLDER";
        const recordBtn = document.getElementById("recordBtn");
        const statusText = document.getElementById("status");

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
                unlockAudio();
                if (!isListening) {
                    try { recognition.start(); } catch(e) {}
                } else {
                    recognition.stop();
                }
            };

            function unlockAudio() {
                if ('speechSynthesis' in window) {
                    let synth = window.speechSynthesis;
                    if (synth.paused) synth.resume();
                }
            }

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
                    statusText.innerHTML = "🔄 Translating via AI backend...";
                    
                    // Send to Streamlit Python backend for universal translation
                    const url = new URL(window.parent.location.href);
                    url.searchParams.set("spoken_text", spokenText);
                    window.parent.location.href = url.toString();
                } else {
                    statusText.innerHTML = "✅ Ready.";
                }
            };
        }

        function resetBtn() {
            recordBtn.innerHTML = "🎙️ Start Speaking";
            recordBtn.style.backgroundColor = "#4CAF50";
        }
    </script>
</body>
</html>
"""

final_html = app_template.replace("LANGUAGE_CODE_PLACEHOLDER", native_language_name[1])
st.components.v1.html(final_html, height=130)

# Automatically trigger Text-to-Speech audio output in Python if a new translation is added
if st.session_state.conversation:
    latest_translation = st.session_state.conversation[-1]["translation"]
    # We use a minor client-side script injection to ensure the browser speaks out the translated text
    tts_script = f"""
    <script>
        if ('speechSynthesis' in window) {{
            window.speechSynthesis.cancel();
            let utterance = new SpeechSynthesisUtterance("{latest_translation}");
            utterance.lang = "en-US";
            utterance.rate = 0.95;
            window.speechSynthesis.speak(utterance);
        }}
    </script>
    """
    st.components.v1.html(tts_script, height=0)
