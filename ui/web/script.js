const API_URL = 'http://127.0.0.1:5000';

// DOM
const chatMessages = document.getElementById('chatMessages');
const sonarOuter   = document.getElementById('sonarOuter');
const chatInput    = document.getElementById('chatInput');
const sendBtn      = document.getElementById('sendBtn');
const clearBtn     = document.getElementById('clearBtn');

// Avatar / GIF elements
const listeningGif = document.getElementById('listeningGif');
const speakingGif  = document.getElementById('speakingGif');
const thinkingGif  = document.getElementById('thinkingGif');
const listenPulse  = document.getElementById('listenPulse');

// HUD elements
const statusLabel  = document.getElementById('statusLabel');
const hudMode      = document.getElementById('hudMode');
const hudLang      = document.getElementById('hudLang');
const hudConn      = document.getElementById('hudConn');
const wakeLabel    = document.getElementById('wakeLabel');

// ── Status management ──
function showStatus(status) {
    [listeningGif, speakingGif, thinkingGif].forEach(el => el.style.display = 'none');
    if (sonarOuter) sonarOuter.classList.remove('listening');
    listenPulse.classList.remove('active');
    statusLabel.className = 'id-status';

    if (status === 'wake') {
        statusLabel.textContent = 'WAITING';
        statusLabel.classList.add('wake');
        hudMode.textContent = 'WAKE WORD';
        hudMode.style.color = 'var(--muted)';
        if (wakeLabel) { wakeLabel.textContent = 'SAY "HEY FRIDAY"'; wakeLabel.style.color = 'var(--muted)'; }

    }
    // Replace the showStatus gif lines with safe    versions:
    if (listeningGif) listeningGif.style.display =   (status === 'listening') ? 'block' : 'none';
    if (speakingGif)  speakingGif.style.display  =   (status === 'speaking')  ? 'block' : 'none';
    if (thinkingGif)  thinkingGif.style.display  =   (status === 'thinking')  ? 'block' : 'none'; 
}

// ── Message rendering ──
function addMessage(text, isUser) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user' : 'assistant'}`;

    const avatarEl = document.createElement('div');
    avatarEl.className = 'msg-avatar';
    avatarEl.innerHTML = isUser
        ? '<i class="fas fa-user"></i>'
        : '<i class="fas fa-robot"></i>';

    const msgBody  = document.createElement('div');
    msgBody.className = 'msg-body';

    const bubble = document.createElement('div');
    bubble.className = 'bubble';
    bubble.textContent = text;

    const time = document.createElement('div');
    time.className = 'time';
    time.textContent = new Date().toLocaleTimeString([], { hour:'2-digit', minute:'2-digit' });

    msgBody.appendChild(bubble);
    msgBody.appendChild(time);
    messageDiv.appendChild(avatarEl);
    messageDiv.appendChild(msgBody);
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function showTyping() {
    const div = document.createElement('div');
    div.className = 'message assistant typing';
    div.id = 'typingIndicator';
    div.innerHTML = `
        <div class="msg-avatar"><i class="fas fa-robot"></i></div>
        <div class="msg-body">
            <div class="bubble">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
        </div>`;
    chatMessages.appendChild(div);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function removeTyping() {
    const el = document.getElementById('typingIndicator');
    if (el) el.remove();
}

function updateLangHUD(language) {
    hudLang.textContent = language === 'hi' ? 'HI' : 'EN';
}

// ── SSE — real-time events from always-on voice pipeline ──
function connectSSE() {
    const es = new EventSource(`${API_URL}/api/stream`);

    es.addEventListener('status', e => {
        const { status } = JSON.parse(e.data);
        showStatus(status);
        hudConn.textContent = 'ACTIVE';
    });

    es.addEventListener('transcript', e => {
        const { text, is_command } = JSON.parse(e.data);
        // Only show wake word echo as a subtle system note, command as full bubble
        if (is_command) {
            addMessage(text, true);
            showTyping();
            
        }
    });

    es.addEventListener('message', e => {
        const { response, language } = JSON.parse(e.data);
        removeTyping();
        addMessage(response, false);
        updateLangHUD(language);
    });

    es.onerror = () => {
        hudConn.textContent = 'OFFLINE';
        showStatus('idle');
        // Reconnect after 3s
        es.close();
        setTimeout(connectSSE, 3000);
    };

    es.onopen = () => {
        hudConn.textContent = 'ACTIVE';
        console.log('[Friday] SSE connected');
    };
}

// ── Text chat ──
async function sendMessage(message) {
    if (!message.trim()) return;
    addMessage(message, true);
    chatInput.value = '';
    showTyping();
    showStatus('thinking');

    try {
        const res  = await fetch(`${API_URL}/api/chat`, {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify({ message })
        });
        const data = await res.json();
        removeTyping();
        showStatus('idle');
        addMessage(data.response, false);
        updateLangHUD(data.language);
    } catch (err) {
        removeTyping();
        addMessage('⚠ Backend offline. Run: python backend/app.py', false);
        hudConn.textContent = 'OFFLINE';
    }
}

// ── Clear chat ──
async function clearChat() {
    try { await fetch(`${API_URL}/api/clear`, { method: 'POST' }); } catch (e) {}
    chatMessages.innerHTML = '';
    addMessage('Chat cleared. Say "Hey Friday" to wake me up, yaar!', false);
}

// ── Events ──
sendBtn.addEventListener('click',  () => sendMessage(chatInput.value));
chatInput.addEventListener('keydown', e => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(chatInput.value); }
});
clearBtn.addEventListener('click', clearChat);

// ── Boot ──
showStatus('wake');
connectSSE();
console.log('[Friday] UI loaded. Listening for "Hey Friday"...');