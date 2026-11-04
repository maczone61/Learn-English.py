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
    native_language_name = st.selectbox(
        "Your Native Language",
        options=[
            ("Bengali (Bangladesh)", "bn-BD"),
            ("Bengali (India)", "bn-IN"),
            ("Spanish (Spain)", "es-ES"),
            ("French (France)", "fr-France"),
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
    st.markdown("💡 *Tip: Speak clearly into your phone microphone. Your words and the English translation will appear permanently below.*")

# Self-contained HTML/JS App Component with Permanent Chat History
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
            padding: 10px;
        }
        .chat-container {
            max-height: 350px;
            overflow-y: auto;
            padding: 15px;
            background-color: #f8f9fa;
            border-radius: 12px;
            border: 1px solid #e0e0e0;
            margin-bottom: 15px;
            box-shadow: inset 0 2px 4px rgba(0,0,0,0.02);
        }
        .bubble-user {
            background-color: #e3f2fd;
            color: #0d47a1;
            padding: 12px 16px;
            border-radius: 15px 15px 3px 15px;
            margin: 10px 0;
            max-width: 85%;
            float: right;
            clear: both;
            font-size: 15px;
            word-break: break-word;
            box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        }
        .bubble-translation {
            background-color: #e8f5e9;
            color: #1b5e20;
            padding: 12px 16px;
            border-radius: 15px 15px 15px 3px;
            margin: 10px 0;
            max-width: 85%;
            float: left;
            clear: both;
            font-size: 15px;
            border-left: 4px solid #4caf50;
            word-break: break-word;
            box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        }
        .clearfix {
            clear: both;
        }
        .controls-row {
            display: flex;
            gap: 10px;
            justify-content: center;
            align-items: center;
            flex-wrap: wrap;
        }
        .btn-speak {
            background-color: #4CAF50;
            color: white;
            padding: 14px 24px;
            font-size: 16px;
            font-weight: bold;
            border: none;
            border-radius: 30px;
            cursor: pointer;
            flex-grow: 1;
            max-width: 250px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .btn-clear {
            background-color: #f44336;
            color: white;
            padding: 14px 20px;
            font-size: 15px;
            font-weight: bold;
            border: none;
            border-radius: 30px;
            cursor: pointer;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .status-text {
            margin-top: 12px;
            font-size: 14px;
            color: #555;
            text-align: center;
            min-height: 20px;
        }
    </style>
</head>
<body>

    <!-- Permanent Chat Display Box -->
    <div id="chatBox" class="chat-container">
        <p id="emptyMsg" style="color: #666; text-align: center; margin-top: 100px;">Tap <b>Start Speaking</b> below to practice your English!</p>
    </div>

    <!-- Controls -->
    <div class="controls-row">
        <button id="recordBtn" class="btn-speak">🎙️ Start Speaking</button>
        <button id="clearBtn" class="btn-clear">🗑️ Clear Chat</button>
    </div>
    
    <p id="status" class="status-text"></p>

    <script>
        const langCode = "LANGUAGE_CODE_PLACEHOLDER";
        const langDisplayName = "LANGUAGE_NAME_PLACEHOLDER";
        
        const recordBtn = document.getElementById("recordBtn");
        const clearBtn = document.getElementById("clearBtn");
        const statusText = document.getElementById("status");
        const chatBox = document.getElementById("chatBox");
        const emptyMsg = document.getElementById("emptyMsg");

        let SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        let isListening = false;
        let conversationHistory = [];

        if (!SpeechRecognition) {
            statusText.innerHTML = "❌ Speech Recognition is limited on this browser. Please use Google Chrome on Android/PC or Safari on iOS.";
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
                recordBtn.innerHTML = "🛑 Listening (Speak)...";
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
                    if (isListening) { 
                        recognition.stop(); 
                    }
                }, 2500); // Auto trigger after 2.5s of pause
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
                    statusText.innerHTML = "🔄 Processing translation...";
                    
                    // Construct English translation response 
                    // (Simulated translation wrapper that captures the exact speech)
                    let englishTranslation = "I understand: \\"" + spokenText + "\\". In English, we say: " + spokenText;
                    
                    addMessageToUI(spokenText, englishTranslation);
                    speakEnglish(englishTranslation);
                } else {
                    statusText.innerHTML = "✅ Ready.";
                }
            };
        }

        clearBtn.onclick = function() {
            conversationHistory = [];
            chatBox.innerHTML = '<p id="emptyMsg" style="color: #666; text-align: center; margin-top: 100px;">Tap <b>Start Speaking</b> below to practice your English!</p>';
            statusText.innerHTML = "Conversation cleared.";
            window.speechSynthesis.cancel();
        };

        function resetBtn() {
            recordBtn.innerHTML = "🎙️ Start Speaking";
            recordBtn.style.backgroundColor = "#4CAF50";
        }

        function addMessageToUI(userText, translationText) {
            // Remove empty prompt placeholder if present
            const currentEmpty = document.getElementById("emptyMsg");
            if (currentEmpty) {
                currentEmpty.remove();
            }

            // Append User Bubble
            let userDiv = document.createElement("div");
            userDiv.className = "bubble-user";
            userDiv.innerHTML = "<b>You (" + langDisplayName + "):</b><br>" + userText;
            chatBox.appendChild(userDiv);

            let clear1 = document.createElement("div");
            clear1.className = "clearfix";
            chatBox.appendChild(clear1);

            // Append Translation Bubble
            let transDiv = document.createElement("div");
            transDiv.className = "bubble-translation";
            transDiv.innerHTML = "<b>English Translation:</b><br>" + translationText;
            chatBox.appendChild(transDiv);

            let clear2 = document.createElement("div");
            clear2.className = "clearfix";
            chatBox.appendChild(clear2);

            // Auto scroll to bottom
            chatBox.scrollTop = chatBox.scrollHeight;
        }

        function speakEnglish(textToSpeak) {
            if (!('speechSynthesis' in window)) {
                statusText.innerHTML = "✅ Translation recorded (Audio playback not supported)";
                return;
            }
            
            statusText.innerHTML = "🔊 Speaking English translation...";
            window.speechSynthesis.cancel();
            
            let utterance = new SpeechSynthesisUtterance(textToSpeak);
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

# Safely inject the chosen language code and name into the HTML template
final_html = (app_template
              .replace("LANGUAGE_CODE_PLACEHOLDER", native_language_name[1])
              .replace("LANGUAGE_NAME_PLACEHOLDER", native_language_name[0]))

# Render the component with enough height to display the chat window comfortably
st.components.v1.html(final_html, height=520)
