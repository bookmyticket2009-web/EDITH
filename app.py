import os
from flask import Flask, request, jsonify, render_template_string
import requests

app = Flask(__name__)

# ==========================================
# 🧠 EXTRACTING CONFIGURATION FROM ENVIRONMENT VARIABLES
# ==========================================
# On Railway, add your Ollama public link inside the dashboard variables: OLLAMA_URL
OLLAMA_HOST_API = os.getenv("OLLAMA_URL", "http://YOUR_OLLAMA_CLOUD_IP:11434/api/chat")
MODEL_NAME = "llama3.1:8b"

CHATBOT_UI_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>E.D.I.T.H. Cloud Hub</title>
    <style>
        body { background-color: #0d1117; color: #c9d1d9; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 0; padding: 0; display: flex; flex-direction: column; height: 100vh; }
        .chat-header { background: #161b22; padding: 15px; text-align: center; border-bottom: 1px solid #30363d; color: #58a6ff; font-weight: bold; letter-spacing: 1px; }
        .chat-box { flex: 1; padding: 15px; overflow-y: auto; display: flex; flex-direction: column; gap: 10px; }
        .msg { max-width: 80%; padding: 10px 14px; border-radius: 15px; font-size: 15px; line-height: 1.4; word-wrap: break-word; }
        .user-msg { background: #1f6feb; color: #fff; align-self: flex-end; border-bottom-right-radius: 2px; }
        .edith-msg { background: #21262d; color: #c9d1d9; align-self: flex-start; border-bottom-left-radius: 2px; border: 1px solid #30363d; }
        .iot-status { font-size: 11px; color: #8b949e; text-align: center; padding: 4px; background: #161b22; }
        .input-area { padding: 10px; background: #161b22; border-top: 1px solid #30363d; display: flex; gap: 8px; }
        input { flex: 1; background: #0d1117; border: 1px solid #30363d; border-radius: 20px; padding: 10px 15px; color: #fff; font-size: 15px; outline: none; }
        input:focus { border-color: #58a6ff; }
        .send-btn { background: #238636; border: none; color: white; border-radius: 50%; width: 40px; height: 40px; font-weight: bold; cursor: pointer; display: flex; align-items: center; justify-content: center; font-size: 18px; }
    </style>
</head>
<body>
    <div class="chat-header">E.D.I.T.H. CLOUD SYSTEM MATRIX</div>
    <div class="iot-status" id="iotBar">E.D.I.T.H. Core: Operational Node</div>
    <div class="chat-box" id="chatBox">
        <div class="msg edith-msg">Cloud instance verified. બોલો, શુ કામ છે? (Systems synced. Speak your directive.)</div>
    </div>
    <div class="input-area">
        <input type="text" id="userInput" placeholder="Message E.D.I.T.H. (Gujlish)..." onkeypress="handleKeyPress(event)">
        <button class="send-btn" onclick="sendMessage()">➔</button>
    </div>
    <script>
        const chatBox = document.getElementById('chatBox');
        function appendMessage(text, isUser) {
            const msgDiv = document.createElement('div');
            msgDiv.className = `msg ${isUser ? 'user-msg' : 'edith-msg'}`;
            msgDiv.innerText = text;
            chatBox.appendChild(msgDiv);
            chatBox.scrollTop = chatBox.scrollHeight;
        }
        function handleKeyPress(e) { if (e.key === 'Enter') sendMessage(); }
        function sendMessage() {
            const input = document.getElementById('userInput');
            const query = input.value.trim();
            if (!query) return;
            appendMessage(query, true);
            input.value = '';
            fetch('/chat-stream', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: query })
            })
            .then(res => res.json())
            .then(data => {
                appendMessage(data.reply, false);
                if(data.iot_action) {
                    document.getElementById('iotBar').innerText = "Cloud Directive Generated: " + data.iot_action;
                }
            })
            .catch(() => { appendMessage("Neural connection link disrupted.", false); });
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(CHATBOT_UI_HTML)

@app.route('/chat-stream', methods=['POST'])
def cloud_chat():
    data = request.json or {}
    user_input = data.get("message", "")
    
    system_rules = (
        "You are E.D.I.T.H., an autonomous personal companion system like Jarvis. "
        "You communicate in a fluid blend of Gujarati and English (Gujlish). "
        "Keep responses punchy, witty, and highly helpful regarding studies and exam preparation parameters."
    )
    
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": system_rules},
            {"role": "user", "content": user_input}
        ],
        "stream": False
    }
    
    iot_flag = None
    lowered_input = user_input.lower()
    
    # Cloud AI intercepts intentions and signals hardware execution requirements
    if "study" in lowered_input or "ભણવા" in lowered_input or "tv bandh" in lowered_input:
        iot_flag = "POWER_OFF_JIO"

    try:
        response = requests.post(OLLAMA_HOST_API, json=payload, timeout=20)
        edith_reply = response.json()['message']['content']
        return jsonify({"reply": edith_reply, "iot_action": iot_flag})
    except Exception as e:
        return jsonify({"reply": f"Ollama cloud link failed: {str(e)}", "iot_action": None}), 500

if __name__ == '__main__':
    # Railway passes its target ports dynamically via environment variables
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
  
