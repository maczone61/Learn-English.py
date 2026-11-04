import streamlit as st

st.set_page_config(
    page_title="LingoBridge - Learn English",
    page_icon="🌍",
    layout="centered"
)

st.title("🌍 LingoBridge: AI-Powered Voice Tutor")
st.markdown("Speak any sentence in your native language. The app translates it into English instantly, displays it permanently, and reads it aloud.")

# Language Selector at the top
native_language_name = st.selectbox(
    "🗣️ Select Your Native Language (আপনার মাতৃভাষা নির্বাচন করুন)",
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

# Self-contained HTML/JS component handling Universal Translation & Permanent Chat locally (Zero mobile reload bugs)
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
            border-radius: 12px;
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
            border-radius: 12px;
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
        .btn-clear {
            background-color: #f44336;
            color: white;
            padding: 10px 20px;
            font-size: 14px;
            font-weight: bold;
            border: none;
            border-radius: 20px;
            cursor: pointer;
            margin-top: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
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

    <!-- Permanent Chat Box -->
    <div id="chatBox" class="chat-container">
        <p id="emptyMsg" style="color: #666; text-align: center; margin-top: 80px;">Tap <b>Start Speaking</b> below to practice your English!</p>
    </div>

    <!-- Controls -->
    <div class="controls">
        <button id="recordBtn" class="btn-speak">🎙️ Start Speaking</button><br>
        <button id="clearBtn" class="btn-clear">🗑️ Clear Chat</button>
        <p id="status" class="status-text"></p>
    </div>

    <script>
        const langCode = "LANGUAGE_CODE_PLACEHOLDER";
        const langName = "LANGUAGE_NAME_PLACEHOLDER";
        
        const recordBtn = document.getElementById("recordBtn");
        const clearBtn = document.getElementById("clearBtn");
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
                unlockAudio();
                if (!isListening) {
                    try { recognition.start(); } catch(e) {}
                } else {
                    recognition.stop();
                }
            };

            clearBtn.onclick = function() {
                chatBox.innerHTML = '<p id="emptyMsg" style="color: #666; text-align: center; margin-top: 80px;">Tap <b>Start Speaking</b> below to practice your English!</p>';
                statusText.innerHTML = "Conversation cleared.";
                window.speechSynthesis.cancel();
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
                    statusText.innerHTML = "🔄 Translating any sentence...";
                    translateAndProcess(spokenText);
                } else {
                    statusText.innerHTML = "✅ Ready.";
                }
            };
        }

        function translateAndProcess(text) {
            // Universal API Translation for ANY sentence in ANY language
            const apiURL = `https://api.mymemory.translated.net/get?q=${encodeURIComponent(text)}&langpair=${langCode}|en`;
            
            fetch(apiURL)
                .then(response => response.json())
                .then(data => {
                    let translation = data.responseData && data.responseData.translatedText 
                        ? data.responseData.translatedText 
                        : "I understand: " + text;
                    
                    appendMessage(langName, text, translation);
                    speakEnglish(translation);
                })
                .catch(error => {
                    let fallbackTranslation = "I understand: " + text;
                    appendMessage(langName, text, fallbackTranslation);
                    speakEnglish(fallbackTranslation);
                });
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
            statusText.innerHTML = "🔊 Speaking English translation...";
        }

        function speakEnglish(text) {
            if (!('speechSynthesis' in window)) {
                statusText.innerHTML = "✅ Done! (Audio not supported)";
                return;
            }
            
            window.speechSynthesis.cancel();
            let utterance = new SpeechSynthesisUtterance(text);
            utterance.lang = "en-US";
            utterance.rate = 0.95;
            
            utterance.onend = function() {
                statusText.innerHTML = "✅ Ready for your next sentence!";
            };
            
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

st.components.v1.html(final_html, height=580)
