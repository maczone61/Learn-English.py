import streamlit as st
from googletrans import Translator

st.set_page_config(
    page_title="LingoBridge - Learn English",
    page_icon="🌍",
    layout="centered"
)

translator = Translator()

st.title("🌍 LingoBridge: Mobile & Desktop English Tutor")
st.markdown("আপনার মাতৃভাষায় কথা বলুন। অ্যাপটি মনোযোগ সহকারে শুনবে, ইংরেজিতে অনুবাদ করবে এবং স্থায়ীভাবে কনভার্সেশন বক্সে দেখাবে।")

# Initialize session state for conversation history
if "conversation" not in st.session_state:
    st.session_state.conversation = []

# Sidebar Settings
with st.sidebar:
    st.header("⚙️ সেটিংস")
    native_language_name = st.selectbox(
        "আপনার মাতৃভাষা (Native Language)",
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
    
    st.markdown("---")
    st.info("📱 আপনার ব্রাউজারে মাইক্রোফোনের অনুমতি নিশ্চিত করুন।")
    
    if st.button("🗑️ চ্যাট মুছে ফেলুন (Clear Chat)"):
        st.session_state.conversation = []
        st.rerun()

# Main Conversation Display Box (Placed prominently at the top)
st.subheader("💬 কনভার্সেশন বক্স (Conversation Box)")

chat_container = st.container(height=350)
with chat_container:
    if not st.session_state.conversation:
        st.markdown('<p style="color: #666; text-align: center; margin-top: 100px;">নিচে <b>Start Speaking</b> এ ট্যাপ করে আপনার অনুশীলন শুরু করুন!</p>', unsafe_allow_html=True)
    else:
        for item in st.session_state.conversation:
            st.markdown(f'<div style="background: #e3f2fd; color: #0d47a1; padding: 12px 16px; border-radius: 15px 15px 3px 15px; margin: 10px 0; float: right; clear: both; max-width: 85%;"><b>আপনি ({native_language_name[0]}):</b><br>{item["user"]}</div><div style="clear: both;"></div>', unsafe_allow_html=True)
            st.markdown(f'<div style="background: #e8f5e9; color: #1b5e20; padding: 12px 16px; border-radius: 15px 15px 15px 3px; margin: 10px 0; float: left; clear: both; max-width: 85%; border-left: 4px solid #4caf50;"><b>ইংরেজি অনুবাদ (English Translation):</b><br>{item["translation"]}</div><div style="clear: both;"></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Handle text input passed back from Javascript securely
if "spoken_text" in st.query_params:
    raw_speech = st.query_params["spoken_text"]
    if raw_speech and (not st.session_state.conversation or st.session_state.conversation[-1]["user"] != raw_speech):
        try:
            translation = translator.translate(raw_speech, dest='en')
            translated_text = translation.text
        except Exception:
            # Fallback if translation API times out
            translated_text = f"I understand: {raw_speech}"
            
        st.session_state.conversation.append({"user": raw_speech, "translation": translated_text})
        st.query_params.clear()
        st.rerun()

# HTML/JS Voice Component positioned below the conversation box
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
            statusText.innerHTML = "❌ এই ব্রাউজারে স্পিচ রিকগনিশন সীমিত। গুগল ক্রোম বা সাফারি ব্যবহার করুন।";
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
                recordBtn.innerHTML = "🛑 শুনছি (Listening)...";
                recordBtn.style.backgroundColor = "#d32f2f";
                statusText.innerHTML = "ধীরে ধীরে স্পষ্ট করে বলুন...";
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
                statusText.innerHTML = "<b>শোনা হচ্ছে:</b> " + (finalTranscript || interim);

                clearTimeout(silenceTimer);
                silenceTimer = setTimeout(() => {
                    if (isListening) { recognition.stop(); }
                }, 3000);
            };

            recognition.onerror = function(event) {
                statusText.innerHTML = "⚠️ ত্রুটি: " + event.error;
                resetBtn();
            };

            recognition.onend = function() {
                isListening = false;
                resetBtn();
                let spokenText = finalTranscript.trim();
                if (spokenText.length > 0) {
                    statusText.innerHTML = "🔄 অনুবাদ ও চ্যাট আপডেট করা হচ্ছে...";
                    
                    // Send to Streamlit backend
                    const url = new URL(window.parent.location.href);
                    url.searchParams.set("spoken_text", spokenText);
                    window.parent.location.href = url.toString();
                } else {
                    statusText.innerHTML = "✅ প্রস্তুত।";
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
