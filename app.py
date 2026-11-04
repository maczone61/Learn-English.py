import streamlit as st
from googletrans import Translator

st.set_page_config(
    page_title="LingoBridge - Learn English",
    page_icon="🌍",
    layout="centered"
)

translator = Translator()

st.title("🌍 LingoBridge: Mobile & Desktop English Tutor")
st.markdown("আপনার মাতৃভাষায় কথা বলুন। অ্যাপটি মনোযোগ সহকারে শুনবে, ইংরেজিতে অনুবাদ করবে এবং আপনাকে শোনাবে।")

# Initialize session state for conversation history
if "conversation" not in st.session_state:
    st.session_state.conversation = []

# Sidebar Settings
with st.sidebar:
    st.header("⚙️ সেটিংস")
    native_language_name = st.selectbox(
        "আপনার মাতৃভাষা (Native Language)",
        options=[
            ("Bengali (Bangladesh)", "bn-BD"),
            ("Bengali (India)", "bn-IN"),
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
    st.info("📱 আপনার ব্রাউজারে মাইক্রোফোনের অনুমতি নিশ্চিত করুন।")
    
    if st.button("🗑️ চ্যাট মুছে ফেলুন (Clear)"):
        st.session_state.conversation = []
        st.rerun()

# Handle data sent back from JavaScript component
if "user_speech" in st.query_params:
    u_text = st.query_params["user_speech"]
    if u_text and (not st.session_state.conversation or st.session_state.conversation[-1]["user"] != u_text):
        try:
            # Translate to English using Google Translate
            translation_obj = translator.translate(u_text, dest='en')
            t_text = translation_obj.text
        except Exception as e:
            t_text = f"Translation error: {e}"
        
        st.session_state.conversation.append({"user": u_text, "translation": t_text})
    st.query_params.clear()

# Main Conversation Display Box
st.subheader("💬 কনভার্সেশন বক্স")

chat_container = st.container()
with chat_container:
    if not st.session_state.conversation:
        st.markdown('<p style="color: #666; text-align: center; margin-top: 50px;">নিচে <b>Start Speaking</b> এ ট্যাপ করে আপনার অনুশীলন শুরু করুন!</p>', unsafe_allow_html=True)
    else:
        for item in st.session_state.conversation:
            st.markdown(f'<div style="background: #e3f2fd; color: #0d47a1; padding: 12px 16px; border-radius: 15px 15px 3px 15px; margin: 10px 0; float: right; clear: both; max-width: 85%;"><b>আপনি ({native_language_name[0]}):</b><br>{item["user"]}</div><div style="clear: both;"></div>', unsafe_allow_html=True)
            st.markdown(f'<div style="background: #e8f5e9; color: #1b5e20; padding: 12px 16px; border-radius: 15px 15px 15px 3px; margin: 10px 0; float: left; clear: both; max-width: 85%; border-left: 4px solid #4caf50;"><b>ইংরেজি অনুবাদ (English Translation):</b><br>{item["translation"]}</div><div style="clear: both;"></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# HTML/JS Voice Component (Fixed repetition bug)
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
            padding: 10px;
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
            margin-top: 12px;
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
            statusText.innerHTML = "❌ এই ব্রাউজারে স্পিচ রিকগনিশন সীমিত। দয়া করে গুগল ক্রোম বা সাফারি ব্যবহার করুন।";
            recordBtn.style.backgroundColor = "#999";
        } else {
            let recognition = new SpeechRecognition();
            recognition.lang = langCode;
            recognition.interimResults = true;
            recognition.continuous = false; // Set to false to prevent duplication loops

            let finalTranscript = "";
            let silenceTimer = null;

            recordBtn.onclick = function() {
                if (!isListening) {
                    try { 
                        recognition.start(); 
                    } catch(e) {}
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
                finalTranscript = ""; // Reset to prevent text accumulation/duplication
                
                for (let i = 0; i < event.results.length; ++i) {
                    if (event.results[i].isFinal) {
                        finalTranscript += event.results[i][0].transcript;
                    } else {
                        interim += event.results[i][0].transcript;
                    }
                }
                statusText.innerHTML = "<b>শোনা যাচ্ছে:</b> " + (finalTranscript || interim);

                clearTimeout(silenceTimer);
                silenceTimer = setTimeout(() => {
                    if (isListening) { 
                        recognition.stop(); 
                    }
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
                    statusText.innerHTML = "🔄 ইংরেজিতে অনুবাদ করা হচ্ছে...";
                    sendDataToStreamlit(spokenText);
                } else {
                    statusText.innerHTML = "✅ প্রস্তুত।";
                }
            };
        }

        function resetBtn() {
            recordBtn.innerHTML = "🎙️ Start Speaking";
            recordBtn.style.backgroundColor = "#4CAF50";
        }

        function sendDataToStreamlit(userSpeech) {
            const url = new URL(window.parent.location.href);
            url.searchParams.set("user_speech", userSpeech);
            window.parent.location.href = url.toString();
        }
    </script>
</body>
</html>
"""

final_html = app_template.replace("LANGUAGE_CODE_PLACEHOLDER", native_language_name[1])
st.components.v1.html(final_html, height=120)
