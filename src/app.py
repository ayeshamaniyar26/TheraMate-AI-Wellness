import streamlit as st
import json
from pathlib import Path
from datetime import datetime, timedelta
import time
import random
import hashlib
import plotly.graph_objects as go
import requests
from io import BytesIO
import base64
from datetime import datetime, timedelta
import plotly.graph_objects as go


# Import custom modules
from llm_adapter import (
    call_gemini, WHO5_QUESTIONS, mood_history, save_mood,
    suggest_exercise, get_helplines, get_today_habits,
    mark_habit_done, get_weekly_happiness, get_wellness_insights,
    calculate_streak
)

# ---------- Page Config ----------
st.set_page_config(
    page_title="TheraMate - AI Wellness Companion",
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------- Enhanced CSS ----------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    * { font-family: 'Inter', sans-serif; }
    
    .main {
        background: linear-gradient(135deg, #E8F5E9 0%, #E1F5FE 50%, #F3E5F5 100%);
    }
    
    /* Floating Quick Chat - FIXED */
    .floating-chat-container {
        position: fixed;
        bottom: 30px;
        right: 30px;
        z-index: 9999;
    }
    
    .quick-chat-btn {
        width: 60px;
        height: 60px;
        border-radius: 50%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        box-shadow: 0 8px 24px rgba(102, 126, 234, 0.4);
        cursor: pointer;
        font-size: 24px;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.3s ease;
        animation: pulse-btn 2s infinite;
    }
    
    .quick-chat-btn:hover {
        transform: scale(1.1) translateY(-5px);
        box-shadow: 0 12px 32px rgba(102, 126, 234, 0.6);
    }
    
    @keyframes pulse-btn {
        0%, 100% { box-shadow: 0 8px 24px rgba(102, 126, 234, 0.4); }
        50% { box-shadow: 0 8px 32px rgba(102, 126, 234, 0.7); }
    }
    
    .quick-chat-panel {
        position: fixed;
        bottom: 100px;
        right: 30px;
        width: 350px;
        height: 500px;
        background: white;
        border-radius: 20px;
        box-shadow: 0 12px 48px rgba(0,0,0,0.15);
        z-index: 9998;
        display: flex;
        flex-direction: column;
        animation: slideUp 0.4s ease-out;
    }
    
    @keyframes slideUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Hide Screen Overlay - FIXED */
    .hide-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        z-index: 99999;
        display: flex;
        align-items: center;
        justify-content: center;
        animation: fadeIn 0.3s ease-in;
    }
    
    .hide-content {
        text-align: center;
        color: white;
    }
    
    .hide-icon {
        font-size: 5rem;
        animation: pulse 2s infinite;
        margin-bottom: 20px;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 0.6; transform: scale(1); }
        50% { opacity: 1; transform: scale(1.15); }
    }
    
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    /* Chat Messages */
    .chat-message {
        padding: 1.2rem;
        border-radius: 18px;
        margin: 0.8rem 0;
        animation: slideIn 0.4s ease-out;
        box-shadow: 0 2px 12px rgba(0,0,0,0.08);
    }
    
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        margin-left: 15%;
        text-align: right;
    }
    
    .assistant-message {
        background: white;
        color: #1D3557;
        margin-right: 15%;
    }
    
    @keyframes slideIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Typing Indicator */
    .typing-indicator {
        display: inline-block;
        padding: 10px 20px;
        background: white;
        border-radius: 18px;
        margin-right: 15%;
        box-shadow: 0 2px 12px rgba(0,0,0,0.08);
    }
    
    .typing-dot {
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #667eea;
        margin: 0 3px;
        animation: typingBounce 1.4s infinite ease-in-out;
    }
    
    .typing-dot:nth-child(2) { animation-delay: 0.2s; }
    .typing-dot:nth-child(3) { animation-delay: 0.4s; }
    
    @keyframes typingBounce {
        0%, 60%, 100% { transform: translateY(0); }
        30% { transform: translateY(-10px); }
    }
    
    /* Badge System */
    .badge {
        display: inline-block;
        padding: 10px 18px;
        border-radius: 25px;
        margin: 8px 5px;
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        font-size: 0.95rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        animation: badgePop 0.6s cubic-bezier(0.68, -0.55, 0.265, 1.55);
    }
    
    @keyframes badgePop {
        0% { transform: scale(0) rotate(-180deg); opacity: 0; }
        100% { transform: scale(1) rotate(0); opacity: 1; }
    }
    
    /* Wellness Cards */
    .wellness-card {
        background: white;
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.08);
        margin: 1.5rem 0;
        transition: all 0.3s ease;
        border-left: 4px solid transparent;
    }
    
    .wellness-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 8px 28px rgba(0,0,0,0.12);
        border-left-color: #667eea;
    }
    
    /* Progress Bar */
    .progress-container {
        background: #e0e0e0;
        border-radius: 15px;
        height: 12px;
        overflow: hidden;
        margin: 10px 0;
    }
    
    .progress-bar {
        background: linear-gradient(90deg, #52B788 0%, #40916C 100%);
        height: 100%;
        transition: width 0.6s ease;
        border-radius: 15px;
    }
    
    /* Smooth Transitions */
    .stButton button {
        transition: all 0.3s ease;
        border-radius: 12px;
        font-weight: 500;
    }
    
    .stButton button:hover {
        transform: scale(1.05);
        box-shadow: 0 4px 16px rgba(0,0,0,0.2);
    }
    
    /* Helpline Cards */
    .helpline-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border-left: 5px solid #667eea;
        transition: all 0.3s ease;
    }
    
    .helpline-card:hover {
        transform: translateX(8px);
        box-shadow: 0 4px 16px rgba(0,0,0,0.15);
    }
    
    /* Spinner Animation */
    .spinner {
        width: 200px;
        height: 200px;
        margin: 30px auto;
        border: 10px solid #e0e0e0;
        border-top: 10px solid #667eea;
        border-radius: 50%;
        animation: spin 2s linear;
    }
    
    @keyframes spin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
</style>
""", unsafe_allow_html=True)

# ---------- Helper Functions ----------
def hash_pin(pin: str) -> str:
    return hashlib.sha256(pin.encode()).hexdigest()

STORED_PIN_HASH = hash_pin("1234")

def load_json(filepath: Path, default=None):
    if filepath.exists():
        try:
            return json.loads(filepath.read_text(encoding="utf-8"))
        except:
            return default or []
    return default or []

def save_json(filepath: Path, data):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_audio_base64(file_path):
    """Convert audio file to base64 for embedding"""
    try:
        with open(file_path, "rb") as f:
            audio_bytes = f.read()
        return base64.b64encode(audio_bytes).decode()
    except:
        return None

# ---------- File Paths ----------
BADGES_FILE = Path("badges.json")
NUTRITION_FILE = Path("nutrition.json")
WATER_FILE = Path("water_log.json")
SLEEP_FILE = Path("sleep_log.json")
GAMES_FILE = Path("games.json")
HELPLINES_FILE = Path("helplines.json")

# ---------- Session State ----------
if "nickname" not in st.session_state:
    st.session_state.nickname = ""
if "consent" not in st.session_state:
    st.session_state.consent = False
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "hide_screen" not in st.session_state:
    st.session_state.hide_screen = False
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "badges" not in st.session_state:
    st.session_state.badges = load_json(BADGES_FILE, [])
if "streak_days" not in st.session_state:
    st.session_state.streak_days = calculate_streak()
if "show_typing" not in st.session_state:
    st.session_state.show_typing = False
if "quick_chat_open" not in st.session_state:
    st.session_state.quick_chat_open = False
if "current_page" not in st.session_state:
    st.session_state.current_page = "🏠 Dashboard"

def award_badge(badge_name, emoji):
    """Award a new badge"""
    today = datetime.today().strftime("%Y-%m-%d")
    existing = [b for b in st.session_state.badges if b.get("name") == badge_name]
    if not existing:
        new_badge = {"name": badge_name, "emoji": emoji, "date": today}
        st.session_state.badges.append(new_badge)
        save_json(BADGES_FILE, st.session_state.badges)
        return True
    return False

# ---------- Authentication Flow ----------
if not st.session_state.nickname:
    st.markdown("<h1 style='text-align: center; color: #667eea;'>🌸 Welcome to TheraMate</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #666; font-size: 1.2rem;'>Your AI Wellness Companion</p>", unsafe_allow_html=True)
    
    nickname_input = st.text_input("✨ What should I call you?", key="nickname_input")
    
    if st.button("Continue", type="primary", use_container_width=True):
        if nickname_input.strip():
            st.session_state.nickname = nickname_input.strip()
            st.balloons()
            time.sleep(0.3)
            st.rerun()
        else:
            st.error("Please enter a valid nickname 💡")
    st.stop()

if not st.session_state.consent:
    st.warning("🔒 **Privacy & Safety Notice**\n\n"
               "✓ Confidential self-care space\n"
               "✓ No medical advice provided\n"
               "✓ In crisis? Contact emergency services immediately")
    
    agree = st.checkbox("I understand and want to continue 💙")
    if st.button("Confirm & Continue", type="primary", use_container_width=True):
        if agree:
            st.session_state.consent = True
            st.success("Welcome to your safe space 🌈")
            time.sleep(0.3)
            st.rerun()
        else:
            st.error("Please agree to continue")
    st.stop()

if not st.session_state.authenticated:
    st.subheader("🔑 Secure Access")
    pin_input = st.text_input("Enter PIN (default: 1234)", type="password")
    
    if st.button("Unlock", type="primary", use_container_width=True):
        if hash_pin(pin_input) == STORED_PIN_HASH:
            st.session_state.authenticated = True
            st.success("✅ Welcome back!")
            time.sleep(0.3)
            st.rerun()
        else:
            st.error("❌ Incorrect PIN")
    st.stop()

# ---------- Hide Screen Mode - FIXED ----------
if st.session_state.hide_screen:
    st.markdown("""
    <div class="hide-overlay">
        <div class="hide-content">
            <div class="hide-icon">🔒</div>
            <h1>Screen Locked</h1>
            <p style='font-size: 1.2rem; margin-top: 20px;'>Your data is safe and private</p>
            <p style='opacity: 0.8; margin-top: 10px;'>Toggle "Hide Screen" in sidebar to return</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Keep sidebar functional during hide
    with st.sidebar:
        if st.toggle("🔒 Hide Screen", st.session_state.hide_screen, key="hide_toggle_active"):
            st.session_state.hide_screen = True
        else:
            st.session_state.hide_screen = False
            st.rerun()
    st.stop()

# ---------- Sidebar ----------
with st.sidebar:
    st.markdown(f"<h2 style='color: #667eea;'>👋 Hi, {st.session_state.nickname}!</h2>", unsafe_allow_html=True)
    
    # Hide Screen Toggle
    hide_screen_state = st.toggle("🔒 Hide Screen", st.session_state.hide_screen, key="hide_toggle")
    if hide_screen_state != st.session_state.hide_screen:
        st.session_state.hide_screen = hide_screen_state
        st.rerun()
    
    st.divider()
    
    # Navigation
    page = st.radio(
        "Navigate",
        ["🏠 Dashboard", "💬 AI Chat", "📊 Mood Tracker", "🎮 Wellness Games", 
         "🍎 Nutrition", "💧 Water", "😴 Sleep",  "📞 Helplines"],
        index=["🏠 Dashboard", "💬 AI Chat", "📊 Mood Tracker", "🎮 Wellness Games", 
               "🍎 Nutrition", "💧 Water", "😴 Sleep", "📞 Helplines"].index(st.session_state.current_page),
        label_visibility="collapsed"
    )
    st.session_state.current_page = page
    
    st.divider()
    
    # Streak Display
    if st.session_state.streak_days > 0:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #FF6B35 0%, #F7B801 100%); 
                    padding: 15px; border-radius: 15px; text-align: center; color: white;'>
            <h2 style='margin: 0;'>🔥 {st.session_state.streak_days}</h2>
            <p style='margin: 5px 0 0 0;'>Day Streak!</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Badges
    if st.session_state.badges:
        st.markdown("### 🏆 Your Badges")
        for badge in st.session_state.badges[-4:]:
            st.markdown(f"<div class='badge'>{badge['emoji']} {badge['name']}</div>", 
                       unsafe_allow_html=True)

# ---------- Quick Chat Floating Button - FIXED ----------
if page != "💬 AI Chat":
    # Create a container at the bottom for the chat button
    quick_chat_placeholder = st.empty()
    
    with quick_chat_placeholder.container():
        col1, col2 = st.columns([5, 1])
        with col2:
            if st.button("💬", key="quick_chat_btn", help="Quick Chat", use_container_width=True):
                st.session_state.quick_chat_open = not st.session_state.quick_chat_open
                st.rerun()
    
    # Show quick chat panel
    if st.session_state.quick_chat_open:
        with st.expander("💬 Quick Chat", expanded=True):
            # Mini chat interface
            mini_chat_container = st.container()
            with mini_chat_container:
                for msg in st.session_state.chat_history[-5:]:  # Show last 5 messages
                    if msg["role"] == "user":
                        st.markdown(f"**You:** {msg['text']}")
                    else:
                        st.markdown(f"**🌸 TheraMate:** {msg['text']}")
            
            quick_input = st.text_input("Quick message...", key="quick_chat_input")
            if st.button("Send", key="quick_send", type="primary"):
                if quick_input.strip():
                    timestamp = datetime.now().strftime("%I:%M %p")
                    st.session_state.chat_history.append({
                        "role": "user",
                        "text": quick_input.strip(),
                        "timestamp": timestamp
                    })
                    
                    context = {
                        "mood_score": mood_history[-1].get("score") if mood_history else None,
                        "streak": st.session_state.streak_days
                    }
                    reply = call_gemini(quick_input.strip(), context)
                    
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "text": reply,
                        "timestamp": timestamp
                    })
                    st.rerun()


# ========== DASHBOARD PAGE - FIXED FOR DARK MODE ========== 
if page == "🏠 Dashboard":
    st.markdown("<h1 style='color: #667eea;'>🌸 TheraMate Dashboard</h1>", unsafe_allow_html=True)
    
    # Dynamic Goals
    today_habits = get_today_habits()
    completed_habits = sum(1 for h in today_habits if h.get("done"))
    
    water_data = load_json(WATER_FILE, [])
    today_str = datetime.today().strftime("%Y-%m-%d")
    today_water = next((w for w in water_data if w.get("date") == today_str), {"glasses": 0})
    water_progress = today_water.get("glasses", 0)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="wellness-card" style="background-color: #ffffff; color: #2d3748;">
            <h3 style="color: #667eea;">🎯 Today's Goals</h3>
            <p style="color: #2d3748;">✓ WHO-5 Wellness Check<br>
            ✓ Habits: {completed_habits}/{len(today_habits)}<br>
            ✓ Water: {water_progress}/8 glasses<br>
            ✓ Chat Check-in</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        wellness_score = 0
        if mood_history:
            recent_moods = [m.get("score", 50) for m in mood_history[-7:]]
            wellness_score = int(sum(recent_moods) / len(recent_moods))
        
        score_color = "#52B788" if wellness_score >= 70 else "#F7B801" if wellness_score >= 50 else "#FF6B35"
        
        st.markdown(f"""
        <div class="wellness-card" style="background-color: #ffffff; color: #2d3748;">
            <h3 style="color: #667eea;">📈 Wellness Score</h3>
            <h2 style="color: {score_color};">{wellness_score}%</h2>
            <p style="color: #2d3748;">{'Great progress!' if wellness_score >= 70 else 'Keep going!' if wellness_score >= 50 else 'Be gentle with yourself'}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="wellness-card" style="background-color: #ffffff; color: #2d3748;">
            <h3 style="color: #667eea;">🏆 Achievements</h3>
            <p style="color: #2d3748;">{len(st.session_state.badges)} badges earned<br>
            {st.session_state.streak_days} day streak 🔥</p>
        </div>
        """, unsafe_allow_html=True)
    
    # WHO-5 Questionnaire
    st.markdown("### 📝 Daily WHO-5 Wellness Check")
    who5_answers = []
    for i, q in enumerate(WHO5_QUESTIONS, start=1):
        slider_val = st.slider(f"{q}", 0, 5, 3, key=f"who5_q{i}")
        who5_answers.append(slider_val)
    
    if st.button("Submit WHO-5", type="primary"):
        total = sum(who5_answers)
        percent = int((total / 25) * 100)
        today_str = datetime.today().strftime("%Y-%m-%d")
        mood_history.append({"who5": who5_answers, "score": percent, "date": today_str})
        save_mood()
        st.success(f"✅ Your wellness score: {percent}%")
        
        # Award badges
        if percent >= 80 and award_badge("Wellness Star", "⭐"):
            st.balloons()
        
        st.session_state.streak_days = calculate_streak()
        if st.session_state.streak_days >= 7 and award_badge("7-Day Streak", "🔥"):
            st.balloons()
        
        time.sleep(0.5)
        st.rerun()
    
    # FIXED: Dynamic Wellness Insights - NOW VISIBLE IN DARK MODE
    st.markdown("### 💡 Your Wellness Insights")
    
    # Get LATEST score (from most recent entry or just submitted)
    latest_score = 0
    if mood_history:
        latest_entry = mood_history[-1]
        latest_score = latest_entry.get("score", 50)
    
    # DYNAMIC INSIGHTS BASED ON CURRENT SCORE
    def get_dynamic_insights(score):
        """Generate insights that change based on score"""
        insights = []
        
        # Main wellness message (changes based on score)
        if score >= 90:
            insights.append("🌟 Exceptional wellbeing! You're radiating positive energy today!")
        elif score >= 80:
            insights.append("😊 You're in a wonderful state of mind! Keep nurturing this positivity.")
        elif score >= 70:
            insights.append("💚 Feeling good! Your emotional balance is strong today.")
        elif score >= 60:
            insights.append("🌤️ You're doing okay. Small steps forward make a big difference.")
        elif score >= 50:
            insights.append("💛 Mixed feelings are normal. Be kind to yourself as you navigate today.")
        elif score >= 40:
            insights.append("🌥️ It's been a bit tough. Remember, it's okay to have difficult days.")
        elif score >= 30:
            insights.append("💙 You're going through a challenging time. Reach out for support when needed.")
        else:
            insights.append("🫂 This feels really hard right now. Please consider talking to someone who can help.")
        
        # Add context from recent trend
        if len(mood_history) >= 3:
            recent_scores = [m.get("score", 50) for m in mood_history[-3:]]
            trend = recent_scores[-1] - recent_scores[0]
            
            if trend > 10:
                insights.append("📈 Positive trend: Your mood has been improving over recent entries!")
            elif trend < -10:
                insights.append("📉 You've had some ups and downs. Consider what might help you feel better.")
            else:
                insights.append("➡️ Your mood has been relatively stable recently.")
        
        # Add encouragement based on streak
        if st.session_state.streak_days >= 7:
            insights.append(f"🔥 Amazing! You've maintained a {st.session_state.streak_days}-day wellness streak!")
        elif st.session_state.streak_days >= 3:
            insights.append(f"⭐ Great consistency with your {st.session_state.streak_days}-day streak!")
        
        # Specific suggestions based on score range
        if score < 50:
            insights.append("💡 Try: Take 5 deep breaths, drink water, or reach out to a friend.")
        elif score < 70:
            insights.append("💡 Try: A short walk, listening to uplifting music, or journaling your thoughts.")
        else:
            insights.append("💡 Keep it going: Continue the activities that make you feel this good!")
        
        return "\n\n".join(insights)
    
    dynamic_insight = get_dynamic_insights(latest_score)
    
    # FIXED: Custom styled box with GUARANTEED visible text
    st.markdown(f"""
    <div style="background-color: #f0f4ff; 
                padding: 25px; 
                border-radius: 12px; 
                border-left: 5px solid #667eea;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                margin-top: 20px;">
        <div style="color: #1a1a2e; 
                    font-size: 16px; 
                    line-height: 1.8;
                    white-space: pre-line;">{dynamic_insight}</div>
    </div>
    """, unsafe_allow_html=True)

# ---------- AI CHAT PAGE ----------
elif page == "💬 AI Chat":
    st.markdown("<h1 style='color: #667eea;'>💬 Chat with TheraMate</h1>", unsafe_allow_html=True)
    
    # Chat container
    chat_container = st.container()
    
    with chat_container:
        for msg in st.session_state.chat_history:
            timestamp = msg.get('timestamp', '')
            if msg["role"] == "user":
                st.markdown(f"""
                <div class="chat-message user-message">
                    <strong>You:</strong> {msg['text']}<br>
                    <small style='opacity: 0.7;'>{timestamp}</small>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="chat-message assistant-message">
                    <strong>🌸 TheraMate:</strong> {msg['text']}<br>
                    <small style='opacity: 0.6;'>{timestamp}</small>
                </div>
                """, unsafe_allow_html=True)
    
    # Typing indicator
    if st.session_state.show_typing:
        st.markdown("""
        <div class="typing-indicator">
            <span class="typing-dot"></span>
            <span class="typing-dot"></span>
            <span class="typing-dot"></span>
        </div>
        """, unsafe_allow_html=True)
    
    # Chat input
    with st.form(key="chat_form", clear_on_submit=True):
        user_text = st.text_input("Type your message...", placeholder="How are you feeling today?")
        send_button = st.form_submit_button("Send 📤", type="primary")
    
    if send_button and user_text.strip():
        timestamp = datetime.now().strftime("%I:%M %p")
        
        st.session_state.chat_history.append({
            "role": "user",
            "text": user_text.strip(),
            "timestamp": timestamp
        })
        
        st.session_state.show_typing = True
        st.rerun()
    
    if st.session_state.show_typing:
        # Get context
        context = {
            "mood_score": mood_history[-1].get("score") if mood_history else None,
            "streak": st.session_state.streak_days
        }
        
        reply = call_gemini(st.session_state.chat_history[-1]["text"], context)
        
        st.session_state.chat_history.append({
            "role": "assistant",
            "text": reply,
            "timestamp": timestamp
        })
        
        st.session_state.show_typing = False
        st.rerun()




# ========== MOOD TRACKER PAGE - GRAPH UPDATES IMMEDIATELY ========== 
elif page == "📊 Mood Tracker":
    st.markdown("<h1 style='color: #667eea;'>🌈 Mood Tracker</h1>", unsafe_allow_html=True)
    
    # Mood input
    st.subheader("📝 How are you feeling today?")
    mood_score = st.slider("Rate your mood (0-100)", 0, 100, 50, key="mood_slider")
    
    mood_note = st.text_area("Add a note (optional)", placeholder="What's on your mind?")
    
    if st.button("Save Mood", type="primary"):
        today_key = datetime.today().strftime("%Y-%m-%d")
        mood_entry = {
            "score": mood_score,
            "date": today_key,
            "note": mood_note,
            "timestamp": datetime.now().strftime("%I:%M %p")
        }
        mood_history.append(mood_entry)
        save_mood()
        st.success("✅ Mood saved!")
        
        st.session_state.streak_days = calculate_streak()
        
        # FIXED: Force immediate rerun to update graph
        time.sleep(0.5)
        st.rerun()
    
    # Mood graph - UPDATES IMMEDIATELY AFTER SAVE
    st.subheader("📈 Your Mood Journey")
    days_to_show = st.selectbox("View period", [7, 14, 30], index=0)
    
    # FIXED: Get FRESH data from mood_history (includes just-saved entry)
    days, scores = get_weekly_happiness(days_to_show)
    
    # Show current count
    st.caption(f"Total mood entries: {len(mood_history)}")
    
    if scores and any(s != 0 for s in scores):
        # FIXED: Remove None values properly
        display_scores = [s if s > 0 else 50 for s in scores]
        
        # FIXED: Color mapping based on mood (happy=yellow, sad=blue, stressed=red, calm=green)
        def get_mood_color(score):
            if score >= 80:
                return '#FFD700'  # Happy - Yellow/Gold
            elif score >= 60:
                return '#52B788'  # Calm - Green
            elif score >= 40:
                return '#F7B801'  # Neutral - Orange
            else:
                return '#FF6B35'  # Sad/Stressed - Red
        
        colors = [get_mood_color(s) for s in display_scores]
        
        # Emoji mapping
        emojis = []
        for s in display_scores:
            if s >= 80:
                emojis.append("😄")  # Happy
            elif s >= 60:
                emojis.append("😊")  # Calm
            elif s >= 40:
                emojis.append("😐")  # Neutral
            else:
                emojis.append("😢")  # Sad
        
        fig = go.Figure()
        
        # FIXED: Use colors array properly (no None values)
        fig.add_trace(go.Scatter(
            x=days, 
            y=display_scores,
            mode='lines+markers+text',
            text=emojis,
            textposition="top center",
            textfont=dict(size=18),
            line=dict(color='#667eea', width=4, shape='spline'),
            marker=dict(
                size=16, 
                color=colors,  # FIXED: Use color array directly
                line=dict(width=2, color='white')
            ),
            fill='tozeroy',
            fillcolor='rgba(102, 126, 234, 0.2)',
            hovertemplate='<b>%{x}</b><br>Mood: %{y}%<extra></extra>'
        ))
        
        fig.update_layout(
            title="Your Happiness Journey 🌈",
            yaxis=dict(range=[0, 105], title="Mood Score"),
            xaxis=dict(title="Day"),
            template="plotly_white",
            hovermode="x unified",
            font=dict(family="Inter"),
            plot_bgcolor='rgba(232, 245, 233, 0.3)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Stats - FIXED with real-time data
        col1, col2, col3 = st.columns(3)
        with col1:
            avg_score = sum(display_scores) / len(display_scores)
            st.metric("Average", f"{avg_score:.0f}%", help="Your average mood this period")
        with col2:
            st.metric("Highest", f"{max(display_scores)}%", help="Your best day")
        with col3:
            st.metric("Lowest", f"{min(display_scores)}%", help="Your lowest day")
        
        # Show recent mood notes
        st.markdown("---")
        st.subheader("📝 Recent Mood Notes")
        recent_with_notes = [m for m in mood_history[-5:] if m.get("note")]
        
        if recent_with_notes:
            for entry in reversed(recent_with_notes):
                score = entry.get("score", 0)
                emoji = "😄" if score >= 80 else "😊" if score >= 60 else "😐" if score >= 40 else "😢"
                st.markdown(f"""
                <div class="wellness-card">
                    <strong>{entry.get('date')} {emoji} ({score}%)</strong><br>
                    <em>"{entry.get('note')}"</em><br>
                    <small>{entry.get('timestamp', '')}</small>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("💡 Add notes to your mood entries to track your thoughts over time!")
        
    else:
        st.info("Start tracking your mood to see your journey! 🌱")
        st.markdown("""
        ### 💡 How to use:
        1. Rate your current mood (0-100)
        2. Add an optional note about what's affecting your mood
        3. Click "Save Mood"
        4. Your graph will update instantly!
        
        Track daily to see patterns and trends in your emotional wellbeing.
        """)

# ========== WELLNESS GAMES PAGE - UPDATED ==========
elif page == "🎮 Wellness Games":
    st.markdown("<h1 style='color: #667eea;'>🎮 Interactive Wellness Games</h1>", unsafe_allow_html=True)
    
    game_choice = st.selectbox("Choose a game", [
        "🌬️ Breathing Exercise",
        "🤔 Would You Rather",
        "🎨 Mood Color Match",
        "✨ Gratitude Spinner",
        "😊 Emoji Mood Match",
        "🌟 Affirmation Cards", 
        "🎯 Mindfulness Quiz"
    ])
    if game_choice == "🌬️ Breathing Exercise":
        st.subheader("🌬️ Guided Breathing with Music")
        
        # Create audio folder if it doesn't exist
        audio_folder = Path("audio")
        if not audio_folder.exists():
            audio_folder.mkdir(parents=True, exist_ok=True)
        
        # Mood selection
        mood_type = st.radio(
            "How are you feeling right now?",
            ["Calm", "Stressed", "Energetic"],
            horizontal=True
        )
        
        # Audio mapping with better descriptions
        audio_map = {
            "Calm": ("audio/ocean_waves.mp3", "🌊 Gentle ocean waves"),
            "Stressed": ("audio/soft_piano.mp3", "🎹 Soothing piano melody"),
            "Energetic": ("audio/upbeat_ambient.mp3", "✨ Uplifting ambient sounds")
        }
        
        audio_file = Path(audio_map[mood_type][0])
        audio_description = audio_map[mood_type][1]
        
        # Display audio player if available
        if audio_file.exists():
            st.info(f"🎵 {audio_description}")
            try:
                with open(audio_file, 'rb') as f:
                    audio_bytes = f.read()
                
                if len(audio_bytes) > 0:
                    st.audio(audio_bytes, format='audio/mp3', start_time=0)
                    st.caption("💡 Press play ▶️ on the audio above before starting the exercise")
                else:
                    st.warning("Audio file is empty. Exercise will continue without music.")
                    
            except Exception as e:
                st.warning(f"Could not load audio. Exercise will continue without music.")
        else:
            st.info(f"🎵 {audio_description} (audio file not found)")
            st.caption("💡 The breathing exercise works great even without music!")
        
        # Breathing pattern info
        with st.expander("ℹ️ About this breathing technique"):
            st.write("""
            **Box Breathing Technique**
            
            This simple technique helps:
            - 🧘 Reduce stress and anxiety
            - 🎯 Improve focus and concentration
            - 💆 Promote instant relaxation
            - 😌 Calm your nervous system
            
            **Pattern:** (4 seconds each)
            - Breathe in for 4 seconds
            - Hold for 4 seconds
            - Breathe out for 4 seconds
            - Hold for 4 seconds
            
            Just 3 cycles = 48 seconds of mindfulness!
            """)
        
        st.write("")  # Spacing
        
        # Start button
        if st.button("🌬️ Start Breathing Exercise", type="primary", key="breathing_start", use_container_width=True):
            
            # Create containers for smooth updates
            timer_container = st.empty()
            progress_container = st.empty()
            instruction_container = st.empty()
            
            breathing_cycles = 3
            total_steps = breathing_cycles * 16  # 4 + 4 + 4 + 4 = 16 seconds per cycle
            current_step = 0
            
            for cycle in range(breathing_cycles):
                # Cycle header
                timer_container.markdown(f"### 🔄 Cycle {cycle + 1} of {breathing_cycles}")
                
                # Breathe In (4 seconds)
                instruction_container.markdown("## 🌬️ **Breathe In Slowly...**")
                for i in range(4):
                    current_step += 1
                    progress_container.progress(current_step / total_steps)
                    time.sleep(1)
                
                # Hold (4 seconds)
                instruction_container.markdown("## 🤲 **Hold Your Breath...**")
                for i in range(4):
                    current_step += 1
                    progress_container.progress(current_step / total_steps)
                    time.sleep(1)
                
                # Breathe Out (4 seconds)
                instruction_container.markdown("## 💨 **Breathe Out Gently...**")
                for i in range(4):
                    current_step += 1
                    progress_container.progress(current_step / total_steps)
                    time.sleep(1)
                
                # Rest (4 seconds)
                instruction_container.markdown("## 😌 **Rest & Relax...**")
                for i in range(4):
                    current_step += 1
                    progress_container.progress(current_step / total_steps)
                    time.sleep(1)
            
            # Completion
            progress_container.progress(1.0)
            timer_container.markdown("### ✅ Complete!")
            instruction_container.success("""
            ## 🌟 Excellent Work!
            
            You've completed your breathing exercise. Take a moment to notice how you feel now.
            
            Regular practice makes it easier! 💙
            """)
            
            st.balloons()
            
            # Save exercise data
            games_data = load_json(GAMES_FILE, [])
            games_data.append({
                "game": "Breathing Exercise",
                "mood": mood_type,
                "date": datetime.today().strftime("%Y-%m-%d"),
                "time": datetime.now().strftime("%H:%M:%S")
            })
            save_json(GAMES_FILE, games_data)
            
            # Award badge
            if award_badge("Mindful Breather", "🌬️"):
                st.success("🏆 Badge Unlocked: Mindful Breather!")
            
            # Show streak if multiple sessions
            breathing_sessions = [g for g in games_data if g.get("game") == "Breathing Exercise"]
            if len(breathing_sessions) > 1:
                st.info(f"🔥 You've completed {len(breathing_sessions)} breathing sessions! Keep it up!")
                
    
    elif game_choice == "🤔 Would You Rather":    
        st.subheader("🤔 Would You Rather")
        
        if "wyr_current" not in st.session_state:
            wyr_choices = [
                ("🌍 Travel to space 🚀", "🌊 Explore the deep sea"),
                ("🎶 Always hear music", "🎨 Always see art"),
                ("📚 Read minds", "🔮 See the future"),
                ("🐶 Talk to animals", "🕊️ Fly like a bird"),
                ("🍫 Unlimited chocolate", "🍕 Unlimited pizza"),
                ("💤 Sleep 12 hrs/day", "⚡ Never need sleep"),
                ("🏖️ Beach vacation forever", "🏔️ Mountain retreat forever"),
                ("📱 No internet for a year", "🚗 No car for a year"),
                ("🎭 Be invisible", "⏰ Freeze time"),
                ("🌟 Be famous", "💰 Be wealthy"),
                ("🎸 Master any instrument", "🗣️ Speak all languages"),
                ("🔄 Undo past mistakes", "👁️ See your future")
            ]
            st.session_state.wyr_current = random.choice(wyr_choices)
            st.session_state.wyr_submitted = False
        
        choice = st.radio("Choose one:", st.session_state.wyr_current, key="wyr_radio")
        
        if st.button("Submit Choice", type="primary") and not st.session_state.wyr_submitted:
            st.session_state.wyr_submitted = True
            
            feedback_map = {
                "🌍 Travel to space 🚀": "🚀 You're an explorer at heart!",
                "🌊 Explore the deep sea": "🌊 You love mysteries!",
                "🎶 Always hear music": "🎶 Music feeds your soul!",
                "🎨 Always see art": "🎨 You appreciate beauty!",
                "📚 Read minds": "🧠 Understanding is your power!",
                "🔮 See the future": "🔮 You're a dreamer!",
                "🐶 Talk to animals": "🐾 You're kind and connected!",
                "🕊️ Fly like a bird": "🕊️ Freedom is your calling!",
                "🍫 Unlimited chocolate": "🍫 Sweet life choice!",
                "🍕 Unlimited pizza": "🍕 Comfort food champion!",
                "💤 Sleep 12 hrs/day": "😴 Rest is sacred!",
                "⚡ Never need sleep": "⚡ Maximum productivity!",
                "🏖️ Beach vacation forever": "🏖️ You love tranquility!",
                "🏔️ Mountain retreat forever": "🏔️ You seek peace in nature!",
                "📱 No internet for a year": "📚 You value real connections!",
                "🚗 No car for a year": "🚶 You embrace simplicity!",
                "🎭 Be invisible": "👻 You value privacy!",
                "⏰ Freeze time": "⏱️ You cherish moments!",
                "🌟 Be famous": "✨ You love the spotlight!",
                "💰 Be wealthy": "💎 You value security!",
                "🎸 Master any instrument": "🎵 Music is your passion!",
                "🗣️ Speak all languages": "🌍 You're a connector!",
                "🔄 Undo past mistakes": "🔙 You learn from experience!",
                "👁️ See your future": "🔮 You plan ahead!"
            }
            
            st.success(feedback_map.get(choice, "✨ Great choice!"))
            
            # Save game
            games_data = load_json(GAMES_FILE, [])
            games_data.append({
                "game": "Would You Rather",
                "question": list(st.session_state.wyr_current),
                "choice": choice,
                "date": datetime.today().strftime("%Y-%m-%d")
            })
            save_json(GAMES_FILE, games_data)
        
        if st.session_state.get("wyr_submitted", False):
            if st.button("Next Question ➡️", type="primary"):
                del st.session_state.wyr_current
                del st.session_state.wyr_submitted
                st.rerun()
    
    elif game_choice == "🎨 Mood Color Match":
        st.subheader("🎨 Mood Color Match")
        
        mood_colors = {
            "Red": "🔥 Passionate and energized!",
            "Blue": "💙 Calm and reflective.",
            "Yellow": "🌟 Cheerful and bright!",
            "Green": "🍃 Balanced and peaceful.",
            "Purple": "💜 Creative and thoughtful.",
            "Orange": "🧡 Energetic and enthusiastic!",
            "Pink": "💗 Loving and compassionate!",
            "Turquoise": "💎 Refreshed and inspired!"
        }
        
        col1, col2, col3, col4 = st.columns(4)
        colors_list = list(mood_colors.keys())
        
        selected_color = None
        for i, color in enumerate(colors_list):
            with [col1, col2, col3, col4][i % 4]:
                color_map = {
                    "Red": "#FF6B6B", "Blue": "#4ECDC4", "Yellow": "#FFE66D",
                    "Green": "#95E1D3", "Purple": "#AA96DA", "Orange": "#FCBF49",
                    "Pink": "#F8B5C1", "Turquoise": "#83E8E2"
                }
                if st.button(f"{color}", key=f"color_{color}", use_container_width=True):
                    selected_color = color
        
        if selected_color:
            st.markdown(f"<h3 style='color: {color_map[selected_color]};'>{mood_colors[selected_color]}</h3>", unsafe_allow_html=True)
            
            games_data = load_json(GAMES_FILE, [])
            games_data.append({
                "game": "Mood Color Match",
                "color": selected_color,
                "date": datetime.today().strftime("%Y-%m-%d")
            })
            save_json(GAMES_FILE, games_data)
            
    # ========== GRATITUDE SPINNER - SPINNING WHEEL ANIMATION ==========
    elif game_choice == "✨ Gratitude Spinner":
        st.subheader("✨ Gratitude Spinner")
        st.markdown("**Spin the wheel to discover what you're grateful for today!**")
        
        # Gratitude questions pool
        gratitude_questions = [
            "💙 What made you smile today?",
            "🌟 Who in your life are you most thankful for?",
            "🌈 What's a simple pleasure you're grateful for?",
            "🎁 What positive thing happened recently?",
            "🏡 What aspect of your home brings you comfort?",
            "🌻 What in nature makes you feel peaceful?",
            "💪 What strength or skill are you proud of?",
            "📚 What knowledge or lesson are you grateful to have learned?",
            "🎵 What sound or song brings you joy?",
            "☕ What small daily ritual makes your day better?",
            "👥 What act of kindness have you experienced?",
            "🌅 What moment today are you thankful for?",
            "💖 What about yourself are you grateful for?",
            "🍽️ What meal or food brought you happiness?",
            "😊 What memory makes you feel warm inside?"
        ]
        
        # Initialize session state
        if "gratitude_question" not in st.session_state:
            st.session_state.gratitude_question = None
            st.session_state.gratitude_shown_questions = []
            st.session_state.gratitude_spinning = False
            st.session_state.gratitude_spin_count = 0
        
        # Spinning animation
        if st.session_state.gratitude_spinning:
            st.markdown("""
            <style>
                @keyframes spinWheel {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(1440deg); }
                }
                
                .spinner-wheel {
                    width: 200px;
                    height: 200px;
                    margin: 30px auto;
                    border-radius: 50%;
                    background: conic-gradient(
                        from 0deg,
                        #FF6B6B 0deg 45deg,
                        #4ECDC4 45deg 90deg,
                        #FFE66D 90deg 135deg,
                        #95E1D3 135deg 180deg,
                        #F38181 180deg 225deg,
                        #AA96DA 225deg 270deg,
                        #FCBAD3 270deg 315deg,
                        #A8E6CF 315deg 360deg
                    );
                    border: 8px solid white;
                    box-shadow: 0 8px 32px rgba(0,0,0,0.15);
                    animation: spinWheel 2s cubic-bezier(0.17, 0.67, 0.12, 0.99);
                    position: relative;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }
                
                .spinner-center {
                    width: 80px;
                    height: 80px;
                    background: white;
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 2.5rem;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                }
                
                .spinning-text {
                    text-align: center;
                    font-size: 1.3rem;
                    color: #667eea;
                    font-weight: 600;
                    margin-top: 20px;
                    animation: pulse 1s ease-in-out infinite;
                }
                
                @keyframes pulse {
                    0%, 100% { opacity: 1; }
                    50% { opacity: 0.5; }
                }
            </style>
            
            <div class="spinner-wheel">
                <div class="spinner-center">✨</div>
            </div>
            <div class="spinning-text">🎯 Spinning...</div>
            """, unsafe_allow_html=True)
            
            # Simulate spinning delay
            import time
            time.sleep(2)
            
            # Get a new question
            remaining_questions = [q for q in gratitude_questions if q not in st.session_state.gratitude_shown_questions]
            if not remaining_questions:
                st.session_state.gratitude_shown_questions = []
                remaining_questions = gratitude_questions
            
            st.session_state.gratitude_question = random.choice(remaining_questions)
            st.session_state.gratitude_shown_questions.append(st.session_state.gratitude_question)
            st.session_state.gratitude_spinning = False
            st.session_state.gratitude_spin_count += 1
            st.rerun()
        
        # Display the wheel (static when not spinning)
        if not st.session_state.gratitude_spinning:
            st.markdown("""
            <style>
                .static-wheel {
                    width: 200px;
                    height: 200px;
                    margin: 30px auto;
                    border-radius: 50%;
                    background: conic-gradient(
                        from 0deg,
                        #FF6B6B 0deg 45deg,
                        #4ECDC4 45deg 90deg,
                        #FFE66D 90deg 135deg,
                        #95E1D3 135deg 180deg,
                        #F38181 180deg 225deg,
                        #AA96DA 225deg 270deg,
                        #FCBAD3 270deg 315deg,
                        #A8E6CF 315deg 360deg
                    );
                    border: 8px solid white;
                    box-shadow: 0 8px 32px rgba(0,0,0,0.15);
                    position: relative;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }
                
                .wheel-center {
                    width: 80px;
                    height: 80px;
                    background: white;
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 2.5rem;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                }
            </style>
            
            <div class="static-wheel">
                <div class="wheel-center">✨</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Display current question with beautiful card
        if st.session_state.gratitude_question and not st.session_state.gratitude_spinning:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        border-radius: 20px; padding: 30px; margin: 20px 0;
                        text-align: center; box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
                        animation: fadeIn 0.8s ease-in;">
                <p style="color: white; font-size: 1.6rem; font-weight: 600; 
                          line-height: 1.6; margin: 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.2);">
                    {st.session_state.gratitude_question}
                </p>
            </div>
            
            <style>
                @keyframes fadeIn {{
                    from {{ opacity: 0; transform: translateY(20px); }}
                    to {{ opacity: 1; transform: translateY(0); }}
                }}
            </style>
            """, unsafe_allow_html=True)
        
        # Spin button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🎡 Spin the Wheel", type="primary", use_container_width=True, 
                        key="gratitude_spin", disabled=st.session_state.gratitude_spinning):
                st.session_state.gratitude_spinning = True
                st.rerun()
        
        # Progress tracker
        if st.session_state.gratitude_spin_count > 0:
            progress = len(st.session_state.gratitude_shown_questions) / len(gratitude_questions)
            st.progress(progress)
            st.markdown(f"<p style='text-align: center; color: #666; margin-top: 10px;'>✨ Spins: {st.session_state.gratitude_spin_count} | Questions explored: {len(st.session_state.gratitude_shown_questions)}/{len(gratitude_questions)}</p>", 
                       unsafe_allow_html=True)
        
        # Reflection section
        if st.session_state.gratitude_question and not st.session_state.gratitude_spinning:
            st.markdown("---")
            st.markdown("### 📝 Your Reflection")
            st.markdown("*Take a moment to reflect on this question and write your thoughts...*")
            
            gratitude_response = st.text_area("", 
                                              placeholder="Share what you're grateful for...",
                                              key=f"gratitude_response_{st.session_state.gratitude_spin_count}",
                                              height=120)
            
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                if st.button("💾 Save My Reflection", key=f"save_gratitude_{st.session_state.gratitude_spin_count}", 
                           use_container_width=True):
                    if gratitude_response.strip():
                        games_data = load_json(GAMES_FILE, [])
                        games_data.append({
                            "game": "Gratitude Spinner",
                            "question": st.session_state.gratitude_question,
                            "response": gratitude_response.strip(),
                            "date": datetime.today().strftime("%Y-%m-%d")
                        })
                        save_json(GAMES_FILE, games_data)
                        
                        # Show cheerful messages
                        cheerful_messages = [
                            "✨ Beautiful! Your gratitude has been saved!",
                            "🌟 Wonderful reflection! Thank you for sharing!",
                            "💖 Lovely thoughts! Your gratitude journal is growing!",
                            "🌈 Amazing! Keep embracing gratitude!",
                            "🎉 Fantastic! Your positive energy is inspiring!",
                            "💫 Gorgeous reflection! Stay grateful!",
                            "🌸 Beautiful words! Your heart is full of grace!"
                        ]
                        st.success(random.choice(cheerful_messages))
                        st.balloons()
                        
                        if award_badge("Grateful Heart", "✨"):
                            st.info("🏆 Badge Unlocked: Grateful Heart!")
                    else:
                        st.warning("💭 Please write your reflection before saving!")
    

    # ========== EMOJI MOOD MATCH - IMPROVED WITH BETTER STATE MANAGEMENT ==========
    elif game_choice == "😊 Emoji Mood Match":
        st.subheader("😊 Emoji Mood Match Game")
        st.markdown("**Match the emoji to the correct mood!**")
        
        # Emoji-Mood pairs
        emoji_mood_pairs = [
            ("😊", "Happy"),
            ("😢", "Sad"),
            ("😡", "Angry"),
            ("😰", "Anxious"),
            ("😴", "Tired"),
            ("🤩", "Excited"),
            ("😌", "Calm"),
            ("🥳", "Celebrating"),
            ("😔", "Disappointed"),
            ("😍", "Loving")
        ]
        
        # Initialize game state
        if "emoji_round" not in st.session_state:
            st.session_state.emoji_round = 0
            st.session_state.emoji_score = 0
            st.session_state.emoji_questions = random.sample(emoji_mood_pairs, 5)
            st.session_state.emoji_answered = False
            st.session_state.emoji_selected = None
            st.session_state.emoji_options = []
        
        total_rounds = 5
        
        # Game in progress
        if st.session_state.emoji_round < total_rounds:
            current_emoji, correct_mood = st.session_state.emoji_questions[st.session_state.emoji_round]
            
            # Progress indicator with visual bar
            progress = (st.session_state.emoji_round) / total_rounds
            st.progress(progress)
            st.markdown(f"**Round {st.session_state.emoji_round + 1}/{total_rounds}** | 🏆 Score: {st.session_state.emoji_score}")
            
            # Display emoji with cool animation
            st.markdown(f"""
            <style>
                @keyframes bounce {{
                    0%, 100% {{ transform: translateY(0) scale(1); }}
                    50% {{ transform: translateY(-20px) scale(1.1); }}
                }}
                
                @keyframes fadeIn {{
                    from {{ opacity: 0; transform: scale(0.5); }}
                    to {{ opacity: 1; transform: scale(1); }}
                }}
                
                .emoji-display {{
                    text-align: center;
                    font-size: 8rem;
                    margin: 40px 0;
                    animation: bounce 2s ease-in-out infinite;
                    filter: drop-shadow(0 10px 20px rgba(0,0,0,0.2));
                }}
                
                .mood-button {{
                    padding: 15px 30px;
                    font-size: 1.2rem;
                    font-weight: 600;
                    border-radius: 15px;
                    border: 3px solid #667eea;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    cursor: pointer;
                    transition: all 0.3s ease;
                    margin: 10px;
                }}
                
                .mood-button:hover {{
                    transform: translateY(-5px);
                    box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
                }}
            </style>
            
            <div class="emoji-display">
                {current_emoji}
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("### 🤔 What mood does this emoji represent?")
            
            # Generate options once per round
            if not st.session_state.emoji_options or len(st.session_state.emoji_options) == 0:
                all_moods = [mood for _, mood in emoji_mood_pairs]
                wrong_moods = [m for m in all_moods if m != correct_mood]
                options = [correct_mood] + random.sample(wrong_moods, min(3, len(wrong_moods)))
                random.shuffle(options)
                st.session_state.emoji_options = options
            else:
                options = st.session_state.emoji_options
            
            # Display buttons in a grid
            cols = st.columns(2)
            
            for i, option in enumerate(options):
                with cols[i % 2]:
                    button_type = "secondary"
                    button_label = option
                    
                    if st.session_state.emoji_answered and st.session_state.emoji_selected == option:
                        if option == correct_mood:
                            button_label = f"✅ {option}"
                        else:
                            button_label = f"❌ {option}"
                    
                    if st.button(button_label, key=f"emoji_option_{st.session_state.emoji_round}_{i}", 
                               use_container_width=True, type=button_type):
                        if not st.session_state.emoji_answered:
                            st.session_state.emoji_selected = option
                            st.session_state.emoji_answered = True
                            
                            if option == correct_mood:
                                st.session_state.emoji_score += 1
                            
                            st.rerun()
            
            # Show feedback after answer
            if st.session_state.emoji_answered:
                st.markdown("---")
                if st.session_state.emoji_selected == correct_mood:
                    st.success(f"✅ **Correct!** {current_emoji} represents {correct_mood}!")
                else:
                    st.error(f"❌ **Not quite!** {current_emoji} represents **{correct_mood}**")
                
                col1, col2, col3 = st.columns([1, 1, 1])
                with col2:
                    if st.button("Next Round ➡️", type="primary", key="emoji_next", use_container_width=True):
                        st.session_state.emoji_round += 1
                        st.session_state.emoji_answered = False
                        st.session_state.emoji_selected = None
                        st.session_state.emoji_options = []
                        st.rerun()
        
        # Game completed
        else:
            st.success(f"🎉 **Game Complete!**")
            
            # Score display with visual flair
            score_percentage = (st.session_state.emoji_score / total_rounds) * 100
            st.markdown(f"""
            <div style="text-align: center; padding: 40px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        border-radius: 20px; margin: 20px 0; color: white;">
                <h1 style="font-size: 4rem; margin: 0;">🏆</h1>
                <h2 style="margin: 20px 0;">Your Score</h2>
                <h1 style="font-size: 3rem; margin: 0;">{st.session_state.emoji_score}/{total_rounds}</h1>
                <p style="font-size: 1.5rem; margin-top: 10px;">{score_percentage:.0f}% Correct</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Feedback based on score
            if st.session_state.emoji_score == total_rounds:
                st.balloons()
                st.markdown("### 🌟 **Perfect Score!** You're an emoji expert!")
                if award_badge("Emoji Master", "😊"):
                    st.success("🏆 Badge unlocked: Emoji Master!")
            elif st.session_state.emoji_score >= 4:
                st.markdown("### 😊 **Excellent work!** You know your emojis well!")
            elif st.session_state.emoji_score >= 3:
                st.markdown("### 👍 **Good job!** You're getting there!")
            else:
                st.markdown("### 💪 **Keep practicing!** You'll improve with each game!")
            
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                if st.button("🔄 Play Again", type="primary", key="emoji_restart", use_container_width=True):
                    del st.session_state.emoji_round
                    del st.session_state.emoji_score
                    del st.session_state.emoji_questions
                    del st.session_state.emoji_answered
                    del st.session_state.emoji_selected
                    del st.session_state.emoji_options
                    st.rerun()
    
    # ========== AFFIRMATION CARDS - NO CHANGES ==========
    elif game_choice == "🌟 Affirmation Cards":
        st.subheader("🌟 Positive Affirmation Cards")
        
        affirmations = [
            "💖 You are enough, just as you are.",
            "🌈 This too shall pass, better days are ahead.",
            "🌟 Your kindness makes the world brighter.",
            "🔥 You are stronger than your struggles.",
            "🌻 Every day is a fresh start.",
            "💪 You have the power to create change.",
            "🌸 You deserve love and happiness.",
            "✨ Your potential is limitless.",
            "🦋 You are growing and evolving beautifully.",
            "🌊 Peace flows through you effortlessly.",
            "🎯 You are capable of achieving your dreams.",
            "💫 Your presence matters to the world."
        ]
        
        if st.button("Draw a Card 🎴", type="primary"):
            affirmation = random.choice(affirmations)
            st.markdown(f"""
            <div class="wellness-card" style="text-align: center; font-size: 1.5rem; padding: 3rem; 
                 background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;
                 box-shadow: 0 12px 40px rgba(102, 126, 234, 0.4);">
                {affirmation}
            </div>
            """, unsafe_allow_html=True)
            st.balloons()
    
    # ========== MINDFULNESS QUIZ - EXPANDED (10 QUESTIONS) ==========
    elif game_choice == "🎯 Mindfulness Quiz":
        st.subheader("🎯 Mindfulness Self-Assessment")
        st.markdown("**Reflect on your current state of mindfulness and well-being.**")
        
        # Expanded questions (10 total)
        questions = [
            {
                "q": "How calm do you feel right now?",
                "options": ["Very calm", "Somewhat calm", "Neutral", "A bit anxious", "Very anxious"],
                "type": "rating"
            },
            {
                "q": "How often do you practice mindfulness or meditation?",
                "options": ["Daily", "Few times a week", "Once a week", "Rarely", "Never"],
                "type": "frequency"
            },
            {
                "q": "When you're stressed, how do you usually respond?",
                "options": ["Take deep breaths", "Talk to someone", "Distract myself", "Feel overwhelmed", "Ignore it"],
                "type": "coping"
            },
            {
                "q": "How present do you feel in the current moment?",
                "options": ["Fully present", "Mostly present", "Somewhat distracted", "Mind wandering", "Very distracted"],
                "type": "awareness"
            },
            {
                "q": "How well do you sleep most nights?",
                "options": ["Very well", "Pretty well", "Okay", "Poorly", "Very poorly"],
                "type": "wellbeing"
            },
            {
                "q": "How connected do you feel to your emotions?",
                "options": ["Very connected", "Quite connected", "Neutral", "Somewhat disconnected", "Very disconnected"],
                "type": "emotional"
            },
            {
                "q": "How often do you feel grateful for things in your life?",
                "options": ["Always", "Often", "Sometimes", "Rarely", "Never"],
                "type": "gratitude"
            },
            {
                "q": "How balanced does your life feel right now?",
                "options": ["Very balanced", "Mostly balanced", "Neutral", "Somewhat unbalanced", "Very unbalanced"],
                "type": "balance"
            },
            {
                "q": "How do you feel about your ability to handle challenges?",
                "options": ["Very confident", "Confident", "Neutral", "Not very confident", "Not confident at all"],
                "type": "resilience"
            },
            {
                "q": "After this reflection, how much better do you feel?",
                "options": ["Much better", "Somewhat better", "About the same", "Slightly worse", "Much worse"],
                "type": "outcome"
            }
        ]
        
        # Initialize quiz state
        if "mindful_quiz_index" not in st.session_state:
            st.session_state.mindful_quiz_index = 0
            st.session_state.mindful_answers = []
        
        # Quiz in progress
        if st.session_state.mindful_quiz_index < len(questions):
            current_q = questions[st.session_state.mindful_quiz_index]
            
            # Progress bar
            progress = (st.session_state.mindful_quiz_index + 1) / len(questions)
            st.progress(progress)
            st.markdown(f"**Question {st.session_state.mindful_quiz_index + 1}/{len(questions)}**")
            
            # Display question
            st.markdown(f"### {current_q['q']}")
            
            # Answer options
            answer = st.radio("Choose your answer:", current_q['options'], 
                            key=f"mindful_q{st.session_state.mindful_quiz_index}")
            
            if st.button("Next ➡️", type="primary", key=f"mindful_next_{st.session_state.mindful_quiz_index}"):
                st.session_state.mindful_answers.append({
                    "question": current_q['q'],
                    "answer": answer,
                    "type": current_q['type']
                })
                st.session_state.mindful_quiz_index += 1
                st.rerun()
        
        # Quiz completed - Show results
        else:
            st.success("🎉 Assessment Complete!")
            st.balloons()
            
            # Calculate wellness score
            positive_responses = 0
            for ans in st.session_state.mindful_answers:
                if ans['answer'] in ["Very calm", "Daily", "Take deep breaths", "Fully present", 
                                    "Very well", "Very connected", "Always", "Very balanced", 
                                    "Very confident", "Much better"]:
                    positive_responses += 1
                elif ans['answer'] in ["Somewhat calm", "Few times a week", "Talk to someone", 
                                      "Mostly present", "Pretty well", "Quite connected", 
                                      "Often", "Mostly balanced", "Confident", "Somewhat better"]:
                    positive_responses += 0.5
            
            score_percentage = (positive_responses / len(questions)) * 100
            
            # Display result
            st.markdown(f"### Your Mindfulness Score: {score_percentage:.0f}%")
            
            # Personalized feedback
            if score_percentage >= 80:
                st.markdown("""
                ### 🌟 Excellent Mindfulness!
                You're in a great mental space! You practice mindfulness regularly and are very aware of your emotions and surroundings. Keep up this wonderful routine!
                """)
                if award_badge("Mindfulness Master", "🧠"):
                    st.success("🏆 Badge unlocked: Mindfulness Master!")
            elif score_percentage >= 60:
                st.markdown("""
                ### 😊 You're Feeling More Balanced!
                You have a good foundation of mindfulness. With a bit more practice and consistency, you'll feel even better. Consider adding daily meditation or breathing exercises.
                """)
            elif score_percentage >= 40:
                st.markdown("""
                ### 💙 Room for Growth
                You're on the right path, but there's space to improve your mindfulness. Try starting with 5 minutes of meditation daily and practice being present in small moments.
                """)
            else:
                st.markdown("""
                ### 🌱 Start Your Journey
                Mindfulness is a skill that develops over time. Begin with simple breathing exercises, and be patient with yourself. Every small step counts!
                """)
            
            # Show summary of answers
            with st.expander("📊 View Your Responses"):
                for i, ans in enumerate(st.session_state.mindful_answers, 1):
                    st.markdown(f"**{i}. {ans['question']}**")
                    st.markdown(f"*Your answer:* {ans['answer']}")
                    st.markdown("---")
            
            # Restart button
            if st.button("Take Assessment Again 🔄", type="primary"):
                del st.session_state.mindful_quiz_index
                del st.session_state.mindful_answers
                st.rerun()







# ========== NUTRITION TRACKER - FULLY WORKING ==========
elif page == "🍎 Nutrition":
    st.markdown("<h1 style='color: #667eea;'>🍎 Nutrition Tracker</h1>", unsafe_allow_html=True)
    
    # Load nutrition data
    nutrition_data = load_json(NUTRITION_FILE, [])
    today = datetime.today().strftime("%Y-%m-%d")
    
    # Enhanced calorie database with Indian foods
    ENHANCED_CALORIE_DB = {
        # Fruits
        "banana": {"cal": 105, "protein": 1.3, "carbs": 27, "fat": 0.4},
        "apple": {"cal": 95, "protein": 0.5, "carbs": 25, "fat": 0.3},
        "orange": {"cal": 62, "protein": 1.2, "carbs": 15, "fat": 0.2},
        "mango": {"cal": 99, "protein": 1.4, "carbs": 25, "fat": 0.6},
        "grapes": {"cal": 104, "protein": 1.1, "carbs": 27, "fat": 0.2},
        "watermelon": {"cal": 30, "protein": 0.6, "carbs": 8, "fat": 0.2},
        "papaya": {"cal": 43, "protein": 0.5, "carbs": 11, "fat": 0.1},
        
        # Vegetables & Grains
        "rice": {"cal": 206, "protein": 4.3, "carbs": 45, "fat": 0.4},
        "roti": {"cal": 71, "protein": 3, "carbs": 15, "fat": 0.4},
        "chapati": {"cal": 71, "protein": 3, "carbs": 15, "fat": 0.4},
        "naan": {"cal": 262, "protein": 8.7, "carbs": 45, "fat": 5.1},
        "paratha": {"cal": 300, "protein": 7, "carbs": 40, "fat": 12},
        "potato": {"cal": 163, "protein": 4.3, "carbs": 37, "fat": 0.2},
        "aloo": {"cal": 163, "protein": 4.3, "carbs": 37, "fat": 0.2},
        
        # Indian Dishes
        "dosa": {"cal": 133, "protein": 2.5, "carbs": 20, "fat": 4.3},
        "idli": {"cal": 58, "protein": 2, "carbs": 11, "fat": 0.5},
        "vada": {"cal": 217, "protein": 4, "carbs": 24, "fat": 12},
        "samosa": {"cal": 252, "protein": 4, "carbs": 34, "fat": 11},
        "pakora": {"cal": 180, "protein": 3, "carbs": 18, "fat": 10},
        "biryani": {"cal": 290, "protein": 6, "carbs": 43, "fat": 10},
        "dal": {"cal": 115, "protein": 7, "carbs": 20, "fat": 0.8},
        "paneer": {"cal": 265, "protein": 18, "carbs": 3.6, "fat": 20},
        "chole": {"cal": 164, "protein": 8.9, "carbs": 27, "fat": 2.6},
        "rajma": {"cal": 127, "protein": 8.7, "carbs": 23, "fat": 0.5},
        "khichdi": {"cal": 144, "protein": 4.5, "carbs": 23, "fat": 3.5},
        "poha": {"cal": 180, "protein": 3, "carbs": 35, "fat": 3},
        "upma": {"cal": 120, "protein": 3, "carbs": 21, "fat": 3},
        "pav bhaji": {"cal": 400, "protein": 8, "carbs": 55, "fat": 15},
        "vada pav": {"cal": 286, "protein": 7, "carbs": 42, "fat": 10},
        "pani puri": {"cal": 45, "protein": 1, "carbs": 9, "fat": 1},
        "panipuri": {"cal": 45, "protein": 1, "carbs": 9, "fat": 1},
        "bhel puri": {"cal": 160, "protein": 4, "carbs": 30, "fat": 4},
        "chaat": {"cal": 200, "protein": 5, "carbs": 35, "fat": 6},
        
        # Proteins
        "chicken": {"cal": 165, "protein": 31, "carbs": 0, "fat": 3.6},
        "egg": {"cal": 78, "protein": 6.3, "carbs": 0.6, "fat": 5.3},
        "fish": {"cal": 206, "protein": 22, "carbs": 0, "fat": 12},
        "tofu": {"cal": 144, "protein": 15, "carbs": 3, "fat": 9},
        "salmon": {"cal": 206, "protein": 22, "carbs": 0, "fat": 13},
        
        # Dairy
        "milk": {"cal": 149, "protein": 7.7, "carbs": 12, "fat": 8},
        "yogurt": {"cal": 100, "protein": 5.7, "carbs": 7.7, "fat": 5},
        "curd": {"cal": 98, "protein": 11, "carbs": 4.7, "fat": 4.3},
        "dahi": {"cal": 98, "protein": 11, "carbs": 4.7, "fat": 4.3},
        "cheese": {"cal": 113, "protein": 7, "carbs": 0.9, "fat": 9},
        "butter": {"cal": 102, "protein": 0.1, "carbs": 0, "fat": 11.5},
        "ghee": {"cal": 112, "protein": 0, "carbs": 0, "fat": 12.7},
        
        # Fast Food & Snacks
        "pizza": {"cal": 285, "protein": 12, "carbs": 36, "fat": 10},
        "burger": {"cal": 354, "protein": 17, "carbs": 30, "fat": 18},
        "fries": {"cal": 312, "protein": 3.4, "carbs": 41, "fat": 15},
        "sandwich": {"cal": 250, "protein": 10, "carbs": 30, "fat": 8},
        "pasta": {"cal": 200, "protein": 7, "carbs": 40, "fat": 1},
        "noodles": {"cal": 221, "protein": 7, "carbs": 43, "fat": 2.6},
        "maggi": {"cal": 205, "protein": 5, "carbs": 30, "fat": 7},
        
        # Sweets & Desserts
        "gulab jamun": {"cal": 175, "protein": 2, "carbs": 28, "fat": 7},
        "jalebi": {"cal": 150, "protein": 1, "carbs": 30, "fat": 3},
        "rasgulla": {"cal": 186, "protein": 4, "carbs": 29, "fat": 6},
        "kheer": {"cal": 200, "protein": 5, "carbs": 32, "fat": 6},
        "halwa": {"cal": 250, "protein": 3, "carbs": 40, "fat": 10},
        "ladoo": {"cal": 186, "protein": 3, "carbs": 27, "fat": 8},
        "barfi": {"cal": 210, "protein": 4, "carbs": 30, "fat": 9},
        "chocolate": {"cal": 235, "protein": 2.2, "carbs": 29, "fat": 13},
        "cake": {"cal": 257, "protein": 2.9, "carbs": 36, "fat": 12},
        "ice cream": {"cal": 207, "protein": 3.5, "carbs": 24, "fat": 11},
        
        # Beverages
        "tea": {"cal": 30, "protein": 0.5, "carbs": 7, "fat": 0.3},
        "chai": {"cal": 50, "protein": 1, "carbs": 9, "fat": 1.5},
        "coffee": {"cal": 2, "protein": 0.3, "carbs": 0, "fat": 0},
        "lassi": {"cal": 150, "protein": 6, "carbs": 22, "fat": 4},
        "juice": {"cal": 110, "protein": 1, "carbs": 26, "fat": 0.3},
        
        # Nuts & Seeds
        "almonds": {"cal": 164, "protein": 6, "carbs": 6, "fat": 14},
        "cashew": {"cal": 157, "protein": 5, "carbs": 9, "fat": 12},
        "peanuts": {"cal": 161, "protein": 7, "carbs": 4.6, "fat": 14},
        "walnuts": {"cal": 185, "protein": 4.3, "carbs": 4, "fat": 18.5}
    }
    
    # Function to search food in database
    def search_food(food_name):
        """Search for food in database with fuzzy matching"""
        food_lower = food_name.lower().strip()
        
        # Direct match
        if food_lower in ENHANCED_CALORIE_DB:
            return ENHANCED_CALORIE_DB[food_lower]
        
        # Partial match
        for key in ENHANCED_CALORIE_DB.keys():
            if key in food_lower or food_lower in key:
                return ENHANCED_CALORIE_DB[key]
        
        return None
    
    # Initialize session state for form
    if "nutrition_calories" not in st.session_state:
        st.session_state.nutrition_calories = 0
    
    # UI: Food Entry Form
    st.subheader("📝 Log Today's Meals")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        meal_type = st.selectbox("Meal Type", ["Breakfast", "Lunch", "Dinner", "Snack", "Beverage"], key="nutrition_meal_type")
        food_item = st.text_input("Food item", placeholder="e.g., vada pav, biryani, banana", key="nutrition_food_input")
        
        # Auto-suggest as user types
        if food_item:
            suggestions = [k for k in ENHANCED_CALORIE_DB.keys() if food_item.lower() in k]
            if suggestions and len(suggestions) <= 10:
                st.info(f"💡 Suggestions: {', '.join(suggestions[:5])}")
    
    with col2:
        portion = st.selectbox("Portion Size", ["Small", "Medium", "Large"], key="nutrition_portion")
        portion_multiplier = {"Small": 0.75, "Medium": 1.0, "Large": 1.5}
    
    # Lookup and estimate
    estimated_data = None
    calories = 0
    protein_val = 0
    carbs_val = 0
    fat_val = 0
    
    if food_item:
        estimated_data = search_food(food_item)
        
        if estimated_data:
            base_cal = estimated_data["cal"]
            adjusted_cal = int(base_cal * portion_multiplier[portion])
            protein_val = estimated_data['protein'] * portion_multiplier[portion]
            carbs_val = estimated_data['carbs'] * portion_multiplier[portion]
            fat_val = estimated_data['fat'] * portion_multiplier[portion]
            
            st.success(f"✅ Found in database: ~{adjusted_cal} kcal ({portion} portion)")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Calories", f"{adjusted_cal}")
            with col2:
                st.metric("Protein", f"{protein_val:.1f}g")
            with col3:
                st.metric("Carbs", f"{carbs_val:.1f}g")
            with col4:
                st.metric("Fat", f"{fat_val:.1f}g")
            
            calories = adjusted_cal
            st.session_state.nutrition_calories = calories
        else:
            st.warning("⚠️ Item not found in database. Please add custom entry below.")
            calories = 0
    
    # Custom entry option
    with st.expander("➕ Add Custom Food Item"):
        st.markdown("**Didn't find your food? Add it manually:**")
        custom_calories = st.number_input("Calories (kcal)", min_value=0, value=int(st.session_state.nutrition_calories), step=10, key="nutrition_custom_cal")
        custom_protein = st.number_input("Protein (g)", min_value=0.0, value=float(protein_val), step=0.5, key="nutrition_custom_protein")
        custom_carbs = st.number_input("Carbs (g)", min_value=0.0, value=float(carbs_val), step=1.0, key="nutrition_custom_carbs")
        custom_fat = st.number_input("Fat (g)", min_value=0.0, value=float(fat_val), step=0.5, key="nutrition_custom_fat")
        
        use_custom = st.checkbox("Use custom values instead of database values", key="nutrition_use_custom")
        
        if use_custom:
            calories = custom_calories
            protein_val = custom_protein
            carbs_val = custom_carbs
            fat_val = custom_fat
            st.success("✅ Using custom nutrition values")
    
    # Add meal button
    if st.button("➕ Add Meal", type="primary", use_container_width=True, key="nutrition_add_meal"):
        if food_item.strip() and calories > 0:
            new_entry = {
                "date": today,
                "meal_type": meal_type,
                "description": food_item.strip(),
                "calories": calories,
                "protein": round(protein_val, 1),
                "carbs": round(carbs_val, 1),
                "fat": round(fat_val, 1),
                "portion": portion,
                "timestamp": datetime.now().strftime("%I:%M %p")
            }
            
            nutrition_data.append(new_entry)
            save_json(NUTRITION_FILE, nutrition_data)
            
            st.success(f"✅ {meal_type} logged: {food_item} ({calories} kcal)")
            
            if award_badge("Nutrition Tracker", "🍎"):
                st.balloons()
            
            # Clear form
            st.session_state.nutrition_calories = 0
            
            time.sleep(0.5)
            st.rerun()
        else:
            st.error("⚠️ Please enter a food item and ensure calories are calculated")
    
    # Today's nutrition summary
    st.markdown("---")
    st.subheader("📊 Today's Nutrition Summary")
    
    today_meals = [m for m in nutrition_data if m.get("date") == today]
    
    if today_meals:
        total_calories = sum(m.get("calories", 0) for m in today_meals)
        total_protein = sum(m.get("protein", 0) for m in today_meals)
        total_carbs = sum(m.get("carbs", 0) for m in today_meals)
        total_fat = sum(m.get("fat", 0) for m in today_meals)
        
        # Metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Calories", f"{total_calories} kcal")
        with col2:
            st.metric("Protein", f"{total_protein:.1f}g")
        with col3:
            st.metric("Carbs", f"{total_carbs:.1f}g")
        with col4:
            st.metric("Fat", f"{total_fat:.1f}g")
        
        # Additional stats
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Meals Logged", len(today_meals))
        with col2:
            avg_cal = total_calories / len(today_meals) if today_meals else 0
            st.metric("Avg per Meal", f"{avg_cal:.0f} kcal")
        
        # Calorie breakdown by meal type
        st.markdown("### 🍽️ Calorie Breakdown")
        
        meal_breakdown = {}
        for meal in today_meals:
            mtype = meal.get("meal_type", "Other")
            meal_breakdown[mtype] = meal_breakdown.get(mtype, 0) + meal.get("calories", 0)
        
        # Pie chart
        if meal_breakdown:
            fig = go.Figure(data=[go.Pie(
                labels=list(meal_breakdown.keys()),
                values=list(meal_breakdown.values()),
                hole=0.4,
                marker=dict(colors=['#667eea', '#52B788', '#F7B801', '#FF6B35', '#9D4EDD'])
            )])
            fig.update_layout(
                title="Calories by Meal Type",
                showlegend=True,
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Macronutrient breakdown
        st.markdown("### 🥗 Macronutrient Distribution")
        col1, col2 = st.columns(2)
        
        with col1:
            # Pie chart for macros
            macro_fig = go.Figure(data=[go.Pie(
                labels=['Protein', 'Carbs', 'Fat'],
                values=[total_protein * 4, total_carbs * 4, total_fat * 9],
                marker=dict(colors=['#FF6B35', '#F7B801', '#667eea'])
            )])
            macro_fig.update_layout(title="Macro Calories", height=300)
            st.plotly_chart(macro_fig, use_container_width=True)
        
        with col2:
            # Bar chart for grams
            macro_bar = go.Figure(data=[
                go.Bar(name='Grams', x=['Protein', 'Carbs', 'Fat'], 
                       y=[total_protein, total_carbs, total_fat],
                       marker_color=['#FF6B35', '#F7B801', '#667eea'])
            ])
            macro_bar.update_layout(title="Macros (grams)", height=300, showlegend=False)
            st.plotly_chart(macro_bar, use_container_width=True)
        
        # Meal list
        st.markdown("### 📋 Today's Meals")
        for idx, meal in enumerate(today_meals, 1):
            st.markdown(f"""
            <div class="wellness-card">
                <strong>#{idx} - {meal['meal_type']}</strong> 🕐 {meal.get('timestamp', '')}<br>
                <h4 style="color: #667eea; margin: 10px 0;">{meal['description']}</h4>
                <p style="margin: 5px 0;">
                    🔥 {meal['calories']} kcal | 🍖 {meal.get('protein', 0):.1f}g P | 
                    🍞 {meal.get('carbs', 0):.1f}g C | 🥑 {meal.get('fat', 0):.1f}g F<br>
                    📏 {meal.get('portion', 'Medium')} portion
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        # Weekly trend
        st.markdown("---")
        st.markdown("### 📈 Weekly Calorie Trend")
        
        week_data = {}
        for i in range(7):
            date = (datetime.today() - timedelta(days=6-i)).strftime("%Y-%m-%d")
            day_meals = [m for m in nutrition_data if m.get("date") == date]
            week_data[date] = sum(m.get("calories", 0) for m in day_meals)
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=list(week_data.keys()),
            y=list(week_data.values()),
            marker_color='#52B788',
            text=list(week_data.values()),
            textposition='outside'
        ))
        fig.add_hline(y=2000, line_dash="dash", line_color="orange",
                     annotation_text="Recommended Daily (2000 kcal)")
        fig.update_layout(
            title="Daily Calorie Intake (Last 7 Days)",
            yaxis_title="Calories (kcal)",
            xaxis_title="Date",
            template="plotly_white",
            showlegend=False,
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Nutrition tips
        st.markdown("### 💡 Nutrition Insights")
        if total_calories < 1200:
            st.warning("⚠️ Your calorie intake today is quite low. Make sure you're eating enough!")
        elif total_calories > 3000:
            st.info("💡 High calorie intake today. Consider balanced portions in future meals.")
        else:
            st.success("✅ Good calorie range for the day!")
        
        # Protein check
        if total_protein < 50:
            st.info("🍖 Try adding more protein-rich foods like eggs, dal, paneer, or chicken.")
        elif total_protein > 150:
            st.info("🍖 High protein intake! Make sure you're balancing with other nutrients.")
        
    else:
        st.info("📝 No meals logged today. Start tracking your nutrition!")
        
        # Show sample foods
        st.markdown("### 💡 Popular Foods")
        popular_foods = [
            "🥘 vada pav", "🍛 biryani", "🥞 dosa", "🍚 idli", "🥟 samosa", 
            "🧀 paneer", "🍲 dal", "🫓 roti", "🍕 pizza", "🍔 burger",
            "🍌 banana", "🥭 mango", "🍎 apple", "🥚 egg", "🥛 milk"
        ]
        
        cols = st.columns(5)
        for idx, food in enumerate(popular_foods):
            with cols[idx % 5]:
                st.markdown(f"**{food}**")

# ========== WATER TRACKER - FULLY WORKING ==========
elif page == "💧 Water":
    st.markdown("<h1 style='color: #667eea;'>💧 Water Intake Tracker</h1>", unsafe_allow_html=True)
    
    water_data = load_json(WATER_FILE, [])
    today = datetime.today().strftime("%Y-%m-%d")
    
    # Find or create today's entry
    today_entry = next((w for w in water_data if w.get("date") == today), None)
    if not today_entry:
        today_entry = {"date": today, "glasses": 0, "goal": 8}
        water_data.append(today_entry)
        save_json(WATER_FILE, water_data)
    
    current_glasses = today_entry.get("glasses", 0)
    goal = today_entry.get("goal", 8)
    
    st.subheader(f"💦 Today's Progress: {current_glasses}/{goal} glasses")
    
    # Progress bar
    progress = min(current_glasses / goal, 1.0)
    st.markdown(f"""
    <div class="progress-container">
        <div class="progress-bar" style="width: {progress * 100}%;"></div>
    </div>
    """, unsafe_allow_html=True)
    
    # Visual glasses
    cols = st.columns(8)
    for i in range(8):
        with cols[i]:
            if i < current_glasses:
                st.markdown("<p style='font-size: 2.5rem; text-align: center;'>💧</p>", unsafe_allow_html=True)
            else:
                st.markdown("<p style='font-size: 2.5rem; text-align: center; opacity: 0.3;'>🫙</p>", unsafe_allow_html=True)
    
    # Buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("➕ Add Glass", type="primary", key="water_add"):
            for entry in water_data:
                if entry.get("date") == today:
                    entry["glasses"] = min(entry.get("glasses", 0) + 1, 20)
                    break
            save_json(WATER_FILE, water_data)
            
            # Award badge if goal reached
            if current_glasses + 1 >= goal:
                if award_badge("Hydration Hero", "💧"):
                    st.balloons()
            
            time.sleep(0.2)
            st.rerun()
    
    with col2:
        if st.button("➖ Remove Glass", key="water_remove"):
            for entry in water_data:
                if entry.get("date") == today:
                    entry["glasses"] = max(entry.get("glasses", 0) - 1, 0)
                    break
            save_json(WATER_FILE, water_data)
            time.sleep(0.2)
            st.rerun()
    
    with col3:
        if st.button("🔄 Reset Today", key="water_reset"):
            for entry in water_data:
                if entry.get("date") == today:
                    entry["glasses"] = 0
                    break
            save_json(WATER_FILE, water_data)
            time.sleep(0.2)
            st.rerun()
    
    # Weekly trend
    st.markdown("---")
    st.markdown("### 📊 Weekly Water Intake")
    
    week_data = {}
    for i in range(7):
        date = (datetime.today() - timedelta(days=6-i)).strftime("%Y-%m-%d")
        day_entry = next((w for w in water_data if w.get("date") == date), {"glasses": 0})
        week_data[date] = day_entry.get("glasses", 0)
    
    if any(week_data.values()):
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=list(week_data.keys()),
            y=list(week_data.values()),
            marker_color='#4ECDC4',
            text=list(week_data.values()),
            textposition='outside'
        ))
        fig.add_hline(y=8, line_dash="dash", line_color="orange",
                     annotation_text="Daily Goal (8 glasses)")
        fig.update_layout(
            title="Daily Water Intake (Last 7 Days)",
            yaxis_title="Glasses",
            xaxis_title="Date",
            template="plotly_white",
            showlegend=False,
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Tips
    st.markdown("### 💡 Hydration Tips")
    if current_glasses < 4:
        st.warning("⚠️ You're behind on water! Try setting hourly reminders.")
    elif current_glasses >= goal:
        st.success("🎉 Amazing! You've hit your water goal for today!")
    else:
        st.info(f"💧 Keep it up! {goal - current_glasses} more glasses to reach your goal.")



 # ========== SLEEP TRACKER - FULLY ENHANCED & WORKING ==========
elif page == "😴 Sleep":
    st.markdown("<h1 style='color: #667eea;'>😴 Sleep Tracker</h1>", unsafe_allow_html=True)
    
    sleep_data = load_json(SLEEP_FILE, [])
    today = datetime.today().strftime("%Y-%m-%d")
    
    # ========== SECTION 1: LOG SLEEP ==========
    st.markdown("### 🌙 Log Your Sleep")
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        sleep_time = st.time_input("🛏️ Bedtime", value=None, key="sleep_bedtime", help="What time did you go to bed?")
        wake_time = st.time_input("⏰ Wake Time", value=None, key="sleep_waketime", help="What time did you wake up?")
    
    with col2:
        sleep_quality = st.select_slider(
            "⭐ Sleep Quality",
            options=["Poor", "Fair", "Good", "Great", "Excellent"],
            value="Good",
            key="sleep_quality"
        )
        dreams = st.checkbox("💭 Had vivid dreams?", key="sleep_dreams")
    
    if st.button("💾 Log Sleep", type="primary", key="sleep_log_btn", use_container_width=True):
        if sleep_time and wake_time:
            from datetime import datetime as dt
            sleep_dt = dt.combine(dt.today(), sleep_time)
            wake_dt = dt.combine(dt.today(), wake_time)
            
            # Handle overnight sleep
            if wake_dt < sleep_dt:
                wake_dt += timedelta(days=1)
            
            duration = (wake_dt - sleep_dt).total_seconds() / 3600
            
            sleep_data.append({
                "date": today,
                "sleep_time": sleep_time.strftime("%I:%M %p"),
                "wake_time": wake_time.strftime("%I:%M %p"),
                "duration": round(duration, 1),
                "quality": sleep_quality,
                "dreams": dreams
            })
            save_json(SLEEP_FILE, sleep_data)
            st.success(f"✅ Logged {duration:.1f} hours of sleep!")
            
            # Award badge for good sleep (7+ hours)
            if duration >= 7:
                if award_badge("Sleep Champion", "😴"):
                    st.balloons()
                    st.success("🏆 Badge unlocked: Sleep Champion!")
            
            time.sleep(0.5)
            st.rerun()
        else:
            st.error("⚠️ Please enter both bedtime and wake time")
    
    # ========== SECTION 2: SLEEP SUMMARY & INSIGHTS ==========
    if sleep_data:
        st.markdown("---")
        st.markdown("### 📊 Your Sleep Summary")
        
        # Get last 7 days of sleep data
        recent_sleep = []
        for i in range(7):
            date = (datetime.today() - timedelta(days=6-i)).strftime("%Y-%m-%d")
            day_data = next((s for s in sleep_data if s.get("date") == date), None)
            recent_sleep.append({
                "date": date,
                "day": (datetime.today() - timedelta(days=6-i)).strftime("%a"),
                "duration": day_data.get("duration", 0) if day_data else 0
            })
        
        # Calculate weekly average
        durations = [s["duration"] for s in recent_sleep if s["duration"] > 0]
        avg_duration = sum(durations) / len(durations) if durations else 0
        
        # Display average with emoji
        def get_sleep_emoji(hours):
            if hours >= 8:
                return "😴 Excellent!"
            elif hours >= 6:
                return "😊 Good!"
            elif hours >= 4:
                return "😐 Fair"
            else:
                return "😢 Poor"
        
        # Metrics row
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📊 Weekly Average", f"{avg_duration:.1f} hrs", help="Average sleep over last 7 days")
        with col2:
            quality_emoji = get_sleep_emoji(avg_duration)
            st.metric("⭐ Sleep Quality", quality_emoji)
        with col3:
            total_nights = len([s for s in recent_sleep if s["duration"] > 0])
            st.metric("📅 Nights Logged", f"{total_nights}/7")
        
        # ========== SECTION 3: SLEEP CHART (LAST 7 DAYS) ==========
        st.markdown("#### 📈 Sleep Duration Trend (Last 7 Days)")
        
        # Create bar chart with Plotly
        days = [s["day"] for s in recent_sleep]
        sleep_hours = [s["duration"] for s in recent_sleep]
        
        # Color based on duration
        colors = []
        for h in sleep_hours:
            if h >= 8:
                colors.append('#52B788')  # Green - Excellent
            elif h >= 6:
                colors.append('#F7B801')  # Yellow - Good
            elif h > 0:
                colors.append('#FF6B35')  # Red - Poor
            else:
                colors.append('#E0E0E0')  # Gray - No data
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=days,
            y=sleep_hours,
            marker_color=colors,
            text=[f"{h:.1f}h" if h > 0 else "" for h in sleep_hours],
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>Sleep: %{y:.1f} hours<extra></extra>'
        ))
        
        # Add reference lines
        fig.add_hline(y=7, line_dash="dash", line_color="green", 
                     annotation_text="Recommended Min (7h)", 
                     annotation_position="right")
        fig.add_hline(y=9, line_dash="dash", line_color="orange",
                     annotation_text="Recommended Max (9h)",
                     annotation_position="right")
        
        fig.update_layout(
            yaxis=dict(range=[0, max(sleep_hours + [10])], title="Hours"),
            xaxis=dict(title="Day of Week"),
            template="plotly_white",
            showlegend=False,
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
# ========== SECTION 4: SMART SLEEP INSIGHTS ==========
        st.markdown("#### 💡 Your Sleep Insights")

        def get_sleep_insights(avg_hours):
            """Generate personalized sleep insights"""
            insights = []

            # Main insight based on average
            if avg_hours < 6:
                insights.append("😴 **You might need more rest.** Aim for 7–9 hours of sleep per night for optimal health.")
                insights.append("💡 **Tip:** Try setting a consistent bedtime and avoid screens 1 hour before sleep.")
            elif avg_hours >= 6 and avg_hours < 8:
                insights.append("😊 **Good sleep routine! Keep it up.** You're getting a healthy amount of sleep.")
                insights.append("💡 **Tip:** Maintain this routine for consistent energy levels throughout the day.")
            else:  # >= 8 hours
                insights.append("🌟 **You're well-rested and recharged!** Excellent sleep habits!")
                insights.append("💡 **Tip:** Keep up this great routine and you'll continue feeling energized.")

            # Consistency insight
            if len(durations) >= 5:
                variance = max(durations) - min(durations)
                if variance > 3:
                    insights.append("⏰ **Consistency matters:** Your sleep duration varies significantly. Try to maintain a regular schedule.")
                else:
                    insights.append("✅ **Great consistency:** Your sleep schedule is stable!")

            # Recent trend
            if len(durations) >= 3:
                recent_trend = durations[-1] - durations[-3]
                if recent_trend > 1:
                    insights.append("📈 **Improving:** Your sleep duration has increased recently. Keep it up!")
                elif recent_trend < -1:
                    insights.append("📉 **Declining:** Your sleep has decreased lately. Consider prioritizing rest.")

            return insights

        insights = get_sleep_insights(avg_duration)

        for insight in insights:
            st.info(insight)

        # ========== SECTION 5: DETAILED SLEEP LOGS (FIXED) ==========
        st.markdown("---")
        st.markdown("### 📋 Recent Sleep Logs")

        # Show last 5 entries
        recent_entries = [s for s in sleep_data if s.get("date")][-5:]

        if recent_entries:
            for entry in reversed(recent_entries):
                quality = entry.get("quality", "Good")
                duration = entry.get("duration", 0)

                # Quality emoji
                quality_emojis = {
                    "Poor": "😴", "Fair": "😐", "Good": "😊",
                    "Great": "😄", "Excellent": "⭐"
                }
                quality_emoji = quality_emojis.get(quality, "😴")

                # Duration color
                if duration >= 8:
                    duration_color = "#52B788"
                elif duration >= 6:
                    duration_color = "#F7B801"
                else:
                    duration_color = "#FF6B35"
                
                # Dream indicator
                dream_text = " | 💭 Dreams" if entry.get("dreams") else ""

                # Render clean card using wellness-card CSS class
                st.markdown(f"""
                <div class="wellness-card">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <div>
                            <strong>📅 {entry['date']}</strong> {quality_emoji}<br>
                            <span style="color:#666;">🛏️ {entry.get('sleep_time')} → ⏰ {entry.get('wake_time')}</span>
                        </div>
                        <div style="text-align:right;">
                            <h2 style="color:{duration_color}; margin:0;">{duration}h</h2>
                            <small>{quality}{dream_text}</small>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No sleep logs yet. Start tracking to see your history!")

        # ========== SECTION 6: SLEEP TIPS ==========
        st.markdown("---")
        st.markdown("### 🌙 Sleep Better Tips")

        tips_cols = st.columns(2)

        with tips_cols[0]:
            st.markdown("""
            **🕐 Timing:**
            - Go to bed at the same time daily  
            - Wake up at the same time (even weekends)  
            - Avoid naps after 3 PM  

            **🌡️ Environment:**
            - Keep room cool (60–67°F)  
            - Use blackout curtains  
            - Reduce noise with white noise  
            """)

        with tips_cols[1]:
            st.markdown("""
            **📱 Before Bed:**
            - No screens 1 hour before sleep  
            - Avoid caffeine after 2 PM  
            - Try relaxation techniques  

            **🧘 Relaxation:**
            - Deep breathing exercises  
            - Progressive muscle relaxation  
            - Reading a book  
            """)

    # ========== FIRST-TIME USER MESSAGE ==========
    if not sleep_data:
        st.info("""
        ### 🌙 Start Tracking Your Sleep

        Good sleep is essential for mental and physical wellbeing. Track your sleep to:
        - 📊 See patterns in your sleep duration  
        - 💡 Get personalized insights  
        - 🏆 Earn badges for healthy sleep habits  
        - 📈 Monitor your progress over time  

        **Log your first sleep entry above to get started!**
        """)

        st.markdown("---")
        st.markdown("#### 💤 Why Sleep Matters")

        benefits_cols = st.columns(3)

        with benefits_cols[0]:
            st.markdown("""
            **🧠 Mental Health**
            - Improves mood  
            - Reduces anxiety  
            - Better focus  
            """)

        with benefits_cols[1]:
            st.markdown("""
            **💪 Physical Health**
            - Boosts immunity  
            - Aids recovery  
            - Increases energy  
            """)

        with benefits_cols[2]:
            st.markdown("""
            **⭐ Performance**
            - Better memory  
            - Enhanced creativity  
            - Sharper thinking  
            """)

    # ========== FOOTER ==========
    st.markdown("---")
    st.markdown("""
    <div style='text-align:center; color:#666; padding:20px;'>
        <p>💙 TheraMate - Your AI Wellness Companion</p>
        <p style='font-size:0.9rem;'>This is a supportive tool, not a replacement for professional help.</p>
    </div>
    """, unsafe_allow_html=True)
    

# ========== MENTAL HEALTH HELPLINES - ENHANCED ==========
elif page == "📞 Helplines":
    st.markdown("<h1 style='color: #667eea;'>📞 Mental Health Helplines</h1>", unsafe_allow_html=True)
    
    # Safety warning
    st.error("⚠️ **If you are in crisis, please contact local emergency services immediately.**\n\n🚨 India Emergency: **112** | USA: **911** | UK: **999** | Australia: **000**")
    
    st.markdown("---")
    
    # Complete helplines database
    HELPLINES_DATA = {
        "international": [
            {
                "country": "🇺🇸 USA",
                "name": "988 Suicide & Crisis Lifeline",
                "number": "988",
                "hours": "24/7",
                "website": "988lifeline.org"
            },
            {
                "country": "🇺🇸 USA",
                "name": "Crisis Text Line",
                "number": "Text HOME to 741741",
                "hours": "24/7",
                "website": "crisistextline.org"
            },
            {
                "country": "🇬🇧 UK",
                "name": "Samaritans",
                "number": "116 123",
                "hours": "24/7",
                "website": "samaritans.org"
            },
            {
                "country": "🇬🇧 UK",
                "name": "Mind Infoline",
                "number": "0300 123 3393",
                "hours": "Mon-Fri 9AM-6PM",
                "website": "mind.org.uk"
            },
            {
                "country": "🇦🇺 Australia",
                "name": "Lifeline",
                "number": "13 11 14",
                "hours": "24/7",
                "website": "lifeline.org.au"
            },
            {
                "country": "🇦🇺 Australia",
                "name": "Beyond Blue",
                "number": "1300 22 4636",
                "hours": "24/7",
                "website": "beyondblue.org.au"
            },
            {
                "country": "🇨🇦 Canada",
                "name": "Crisis Services Canada",
                "number": "1-833-456-4566",
                "hours": "24/7",
                "website": "crisisservicescanada.ca"
            },
            {
                "country": "🇨🇦 Canada",
                "name": "Kids Help Phone",
                "number": "1-800-668-6868",
                "hours": "24/7",
                "website": "kidshelpphone.ca"
            }
        ],
        "india_wide": [
            {
                "name": "Vandrevala Foundation",
                "number": "1860 2662 345 / 1800 2333 330",
                "hours": "24/7",
                "website": "vandrevalafoundation.com"
            },
            {
                "name": "AASRA",
                "number": "91-22-27546669",
                "hours": "24/7",
                "website": "aasra.info"
            },
            {
                "name": "iCall - TISS",
                "number": "9152987821",
                "hours": "Mon-Sat 8AM-10PM",
                "website": "icallhelpline.org"
            },
            {
                "name": "Sneha Foundation",
                "number": "044-24640050",
                "hours": "24/7",
                "website": "snehaindia.org"
            },
            {
                "name": "Mann Talks",
                "number": "8686139139",
                "hours": "24/7",
                "website": "manntalks.org"
            },
            {
                "name": "Fortis Stress Helpline",
                "number": "8376804102",
                "hours": "24/7",
                "website": "fortishealthcare.com"
            },
            {
                "name": "Sumaitri",
                "number": "011-23389090",
                "hours": "2PM-10PM Daily",
                "website": "sumaitri.net"
            },
            {
                "name": "Parivarthan",
                "number": "7676602602",
                "hours": "Mon-Fri 10AM-6PM",
                "website": "parivarthan.org"
            }
        ],
        "state_specific": {
            "Maharashtra": [
                {
                    "name": "Connecting NGO",
                    "number": "9922001122 / 9922004305",
                    "hours": "12PM-8PM Daily",
                    "website": "connectingngo.org"
                },
                {
                    "name": "Mpower 1on1",
                    "number": "1800-1208-20050",
                    "hours": "Mon-Fri 9AM-6PM",
                    "website": "mpowerminds.com"
                }
            ],
            "Karnataka": [
                {
                    "name": "Sahai",
                    "number": "080-25497777",
                    "hours": "10AM-6PM Daily",
                    "website": "sahai.co.in"
                },
                {
                    "name": "NIMHANS Helpline",
                    "number": "080-46110007",
                    "hours": "Mon-Sat 9AM-5PM",
                    "website": "nimhans.ac.in"
                }
            ],
            "Tamil Nadu": [
                {
                    "name": "Sneha Foundation Chennai",
                    "number": "044-24640050",
                    "hours": "24/7",
                    "website": "snehaindia.org"
                },
                {
                    "name": "Roshni Trust",
                    "number": "040-66202000",
                    "hours": "11AM-9PM Daily",
                    "website": "roshnihelpline.org"
                }
            ],
            "Delhi": [
                {
                    "name": "Sumaitri Delhi",
                    "number": "011-23389090",
                    "hours": "2PM-10PM Daily",
                    "website": "sumaitri.net"
                },
                {
                    "name": "VIMHANS Helpline",
                    "number": "011-26692941",
                    "hours": "Mon-Fri 9AM-5PM",
                    "website": "vimhans.in"
                }
            ],
            "West Bengal": [
                {
                    "name": "Lifeline Foundation",
                    "number": "033-24637401",
                    "hours": "10AM-6PM Daily",
                    "website": "lifelinekolkata.org"
                }
            ],
            "Gujarat": [
                {
                    "name": "Sanjivani Society",
                    "number": "079-26300222",
                    "hours": "24/7",
                    "website": "sanjivanisociety.org"
                }
            ]
        },
        "city_specific": {
            "Mumbai": [
                {
                    "name": "Connecting NGO Mumbai",
                    "number": "9922001122",
                    "hours": "12PM-8PM Daily",
                    "website": "connectingngo.org"
                },
                {
                    "name": "iCall Mumbai",
                    "number": "9152987821",
                    "hours": "Mon-Sat 8AM-10PM",
                    "website": "icallhelpline.org"
                }
            ],
            "Bangalore": [
                {
                    "name": "Sahai Bangalore",
                    "number": "080-25497777",
                    "hours": "10AM-6PM Daily",
                    "website": "sahai.co.in"
                },
                {
                    "name": "NIMHANS",
                    "number": "080-46110007",
                    "hours": "Mon-Sat 9AM-5PM",
                    "website": "nimhans.ac.in"
                }
            ],
            "Chennai": [
                {
                    "name": "Sneha Chennai",
                    "number": "044-24640050",
                    "hours": "24/7",
                    "website": "snehaindia.org"
                }
            ],
            "Delhi": [
                {
                    "name": "Sumaitri Delhi",
                    "number": "011-23389090",
                    "hours": "2PM-10PM Daily",
                    "website": "sumaitri.net"
                },
                {
                    "name": "VIMHANS",
                    "number": "011-26692941",
                    "hours": "Mon-Fri 9AM-5PM",
                    "website": "vimhans.in"
                }
            ],
            "Kolkata": [
                {
                    "name": "Lifeline Foundation Kolkata",
                    "number": "033-24637401",
                    "hours": "10AM-6PM Daily",
                    "website": "lifelinekolkata.org"
                }
            ],
            "Hyderabad": [
                {
                    "name": "Roshni Trust Hyderabad",
                    "number": "040-66202000",
                    "hours": "11AM-9PM Daily",
                    "website": "roshnihelpline.org"
                }
            ]
        }
    }
    
    # Single Filter - Region Only
    st.markdown("### 🔍 Filter by Region")
    region = st.selectbox(
        "Select your region to view mental health helplines",
        ["🌍 International", "🇮🇳 India-wide", "🏛 State-specific", "🏙 City-specific"],
        key="helpline_region"
    )
    
    st.markdown("---")
    
    # Display helplines based on region
    if region == "🌍 International":
        st.markdown("### 🌍 International Helplines")
        st.info("Mental health support services available worldwide")
        
        helplines = HELPLINES_DATA["international"]
        
        for h in helplines:
            st.markdown(f"""
            <div class="helpline-card">
                <h3>🧩 {h['country']} - {h['name']}</h3>
                <p><strong>📞 Contact:</strong> {h['number']}</p>
                <p><strong>⏰ Hours:</strong> {h['hours']}</p>
                <p><strong>🔗 Website:</strong> <a href="https://{h['website']}" target="_blank">{h['website']}</a></p>
            </div>
            """, unsafe_allow_html=True)
    
    elif region == "🇮🇳 India-wide":
        st.markdown("### 🇮🇳 India-wide Helplines")
        st.info("National mental health support services available across India")
        
        helplines = HELPLINES_DATA["india_wide"]
        
        for h in helplines:
            st.markdown(f"""
            <div class="helpline-card">
                <h3>🧩 Helpline Name: {h['name']}</h3>
                <p><strong>📞 Contact:</strong> {h['number']}</p>
                <p><strong>⏰ Hours:</strong> {h['hours']}</p>
                <p><strong>🔗 Website:</strong> <a href="https://{h['website']}" target="_blank">https://{h['website']}</a></p>
            </div>
            """, unsafe_allow_html=True)
    
    elif region == "🏛 State-specific":
        st.markdown("### 🏛 State-specific Helplines")
        st.info("📍 Select your state to view local mental health helplines")
        
        state = st.selectbox(
            "Choose your state",
            ["Maharashtra", "Karnataka", "Tamil Nadu", "Delhi", "West Bengal", "Gujarat"],
            key="helpline_state"
        )
        
        if state in HELPLINES_DATA["state_specific"]:
            st.markdown(f"#### {state} Mental Health Resources")
            helplines = HELPLINES_DATA["state_specific"][state]
            
            for h in helplines:
                st.markdown(f"""
                <div class="helpline-card">
                    <h3>🧩 Helpline Name: {h['name']}</h3>
                    <p><strong>📞 Contact:</strong> {h['number']}</p>
                    <p><strong>⏰ Hours:</strong> {h['hours']}</p>
                    <p><strong>🔗 Website:</strong> <a href="https://{h['website']}" target="_blank">https://{h['website']}</a></p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info(f"💡 No specific helplines listed for {state} yet. Please use India-wide helplines above.")
    
    else:  # City-specific
        st.markdown("### 🏙 City-specific Helplines")
        st.info("🏙 Select your city to view local mental health resources")
        
        city = st.selectbox(
            "Choose your city",
            ["Mumbai", "Bangalore", "Chennai", "Delhi", "Kolkata", "Hyderabad"],
            key="helpline_city"
        )
        
        if city in HELPLINES_DATA["city_specific"]:
            st.markdown(f"#### {city} Mental Health Resources")
            helplines = HELPLINES_DATA["city_specific"][city]
            
            for h in helplines:
                st.markdown(f"""
                <div class="helpline-card">
                    <h3>🧩 Helpline Name: {h['name']}</h3>
                    <p><strong>📞 Contact:</strong> {h['number']}</p>
                    <p><strong>⏰ Hours:</strong> {h['hours']}</p>
                    <p><strong>🔗 Website:</strong> <a href="https://{h['website']}" target="_blank">https://{h['website']}</a></p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info(f"💡 No specific helplines listed for {city} yet. Please use India-wide or state-specific helplines.")
    
    # Additional resources
    st.markdown("---")
    st.markdown("### 💡 Additional Resources")
    st.info("""
    **Remember:**
    - 🆘 In an emergency, always call **112** (India) or your local emergency number
    - 💙 You are not alone - help is available
    - 🤝 Talking to someone can make a real difference
    - 🏥 Consider visiting a mental health professional for ongoing support
    """)