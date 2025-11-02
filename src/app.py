from llm_adapter import (
    call_gemini, WHO5_QUESTIONS, mood_history, save_mood,
    suggest_exercise, get_helplines, get_today_habits,
    mark_habit_done, get_weekly_happiness, get_wellness_insights,
    calculate_streak
)
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

from datetime import datetime, timezone, timedelta


def get_ist_time():
    """Get current time in Indian Standard Time"""
    ist = timezone(timedelta(hours=5, minutes=30))
    return datetime.now(ist).strftime("%I:%M %p")


def award_badge(badge_name, badge_emoji):
    """Award a badge if it doesn't already exist"""
   # CORRECT - This makes badges a list
    if 'badges' not in st.session_state:
        st.session_state.badges = []

    # Check if badge already exists
    existing_badges = [b['name'] for b in st.session_state.badges]

    if badge_name not in existing_badges:
        st.session_state.badges.append({
            'name': badge_name,
            'emoji': badge_emoji,
            'date': datetime.now().strftime("%Y-%m-%d")
        })
        return True  # Badge was newly awarded
    return False  # Badge already exists


# Import custom modules

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
    existing = [b for b in st.session_state.badges if b.get(
        "name") == badge_name]
    if not existing:
        new_badge = {"name": badge_name, "emoji": emoji, "date": today}
        st.session_state.badges.append(new_badge)
        save_json(BADGES_FILE, st.session_state.badges)
        return True
    return False

# ========== HELPER FUNCTION FOR SLEEP INSIGHTS ==========


def get_smart_sleep_insights(sleep_data):
    """Generate personalized sleep insights with enhanced analysis"""
    insights = []

    if not sleep_data or len(sleep_data) == 0:
        insights.append(
            "📭 No sleep logs yet. Start tracking to get personalized insights!")
        return insights

    # Extract data from recent logs (last 7)
    recent_data = sleep_data[-7:] if len(sleep_data) >= 7 else sleep_data

    durations = [entry.get("duration", 0) for entry in recent_data if entry.get(
        "duration") is not None and entry.get("duration") > 0]
    qualities = [entry.get("quality")
                 for entry in recent_data if entry.get("quality")]
    dreams_data = [entry.get("dreams") for entry in recent_data]

    if not durations:
        insights.append("📭 No complete sleep logs yet. Keep tracking!")
        return insights

    avg_duration = sum(durations) / len(durations)

    # 1. AVERAGE DURATION INSIGHT
    if avg_duration >= 7.5 and avg_duration <= 9:
        insights.append(
            f"🌟 Excellent! You averaged {avg_duration:.1f}h of sleep recently. You're in the optimal zone!")
    elif avg_duration > 9:
        insights.append(
            f"😴 You're averaging {avg_duration:.1f}h of sleep. Feeling refreshed or maybe oversleeping?")
    elif avg_duration >= 6 and avg_duration < 7.5:
        insights.append(
            f"⚠️ You averaged {avg_duration:.1f}h of sleep. Try adding 30-60 minutes for peak performance!")
    else:
        insights.append(
            f"🚨 Only {avg_duration:.1f}h average sleep! Your body needs more rest to thrive.")

    # 2. CONSISTENCY CHECK
    if len(durations) >= 3:
        duration_range = max(durations) - min(durations)
        if duration_range < 1.5:
            insights.append(
                "🎯 Your sleep schedule is super consistent! Your body loves this routine.")
        elif duration_range > 3:
            insights.append(
                "🎢 Your sleep duration is a rollercoaster! Try to stabilize for better health.")

    # 3. QUALITY ANALYSIS
    if qualities:
        quality_map = {"Poor": 1, "Fair": 2,
                       "Good": 3, "Great": 4, "Excellent": 5}
        quality_scores = [quality_map.get(q, 3)
                          for q in qualities if q in quality_map]

        if quality_scores:
            avg_quality = sum(quality_scores) / len(quality_scores)

            if avg_duration >= 7 and avg_quality < 3:
                insights.append(
                    "🤔 You're sleeping enough hours, but quality is low. Check your sleep environment!")
            elif avg_duration < 6.5 and avg_quality >= 4:
                insights.append(
                    "💎 Quality over quantity! Short sleep but high quality—you're efficient!")
            elif avg_quality >= 4:
                insights.append(
                    "✨ High sleep quality detected! You're doing something right—keep it up!")
            elif avg_quality <= 2:
                insights.append(
                    "😓 Sleep quality has been rough. Consider adjusting your pre-bed routine.")

    # 4. RECENT TREND
    if len(durations) >= 3:
        recent_trend = durations[-3:]
        trending_up = all(recent_trend[i] < recent_trend[i+1]
                          for i in range(len(recent_trend)-1))
        trending_down = all(recent_trend[i] > recent_trend[i+1]
                            for i in range(len(recent_trend)-1))

        if trending_up:
            insights.append(
                "📈 Your sleep is trending upward! Keep building this momentum!")
        elif trending_down:
            insights.append(
                "📉 Sleep is declining. What changed? Time to prioritize rest again!")

    # 5. DREAMS INSIGHT
    if dreams_data and len(dreams_data) >= 3:
        dream_count = sum(1 for d in dreams_data if d)
        dream_rate = dream_count / len(dreams_data)

        if dream_rate >= 0.7:
            insights.append(
                "🌈 You're dreaming a lot! Sign of deep REM sleep and creative processing.")
        elif dream_rate >= 0.3:
            insights.append(
                "💭 Dreams are happening occasionally. Your brain is busy at night!")
        elif dream_count == 0:
            insights.append(
                "🌑 No dreams logged recently. Not remembering or not enough REM?")

    # 6. LAST NIGHT SPECIFIC
    if len(sleep_data) >= 1:
        last_log = sleep_data[-1]
        last_duration = last_log.get("duration", 0)
        last_quality = last_log.get("quality")

        if last_duration and last_duration < 6:
            insights.append(
                "😴 Last night was short! Prioritize rest tonight for recovery.")
        elif last_duration and last_duration >= 9:
            insights.append(
                "🛌 You got plenty of sleep last night! Hope you're feeling refreshed.")

        if last_quality == "Excellent":
            insights.append(
                "🏆 Perfect quality sleep last night! You crushed it!")

    # 7. ENCOURAGEMENT
    if qualities and avg_duration >= 7:
        quality_map = {"Poor": 1, "Fair": 2,
                       "Good": 3, "Great": 4, "Excellent": 5}
        quality_scores = [quality_map.get(q, 3)
                          for q in qualities if q in quality_map]
        if quality_scores and sum(quality_scores)/len(quality_scores) >= 4:
            insights.append(
                "💪 You're a sleep champion! Keep this healthy pattern going strong!")

    return insights[:7]


# ---------- Authentication Flow ----------
if not st.session_state.nickname:
    st.markdown("<h1 style='text-align: center; color: #667eea;'>🌸 Welcome to TheraMate</h1>",
                unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #666; font-size: 1.2rem;'>Your AI Wellness Companion</p>",
                unsafe_allow_html=True)

    nickname_input = st.text_input(
        "✨ What should I call you?", key="nickname_input")

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

    import streamlit as st

# ==================================================
# 🔐 PASSWORD UTILITIES
# ==================================================
PASSWORD_FILE = Path("password.json")


def load_json(path, default=None):
    """Safely load JSON"""
    if path.exists():
        try:
            with open(path, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return default or {}
    return default or {}


def save_json(path, data):
    """Safely save JSON"""
    with open(path, "w") as f:
        json.dump(data, f, indent=4)


def hash_password(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()


def load_password_hash():
    data = load_json(PASSWORD_FILE, default={})
    if isinstance(data, dict):
        return data.get("password_hash", None)
    return None


def save_password_hash(pw_hash: str):
    save_json(PASSWORD_FILE, {"password_hash": pw_hash})


def delete_password_file():
    if PASSWORD_FILE.exists():
        PASSWORD_FILE.unlink()


# ==================================================
# 🧠 STREAMLIT AUTH SYSTEM
# ==================================================
st.set_page_config(
    page_title="TheraMate Secure Login",
    page_icon="🌸",
    layout="wide",  # ✅ fixed layout (no flicker)
)

# Initialize session state
for key, val in {
    "authenticated": False,
    "wrong_attempts": 0,
    "reset_in_progress": False,
    "just_logged_in": False,
}.items():
    if key not in st.session_state:
        st.session_state[key] = val

stored_pw_hash = load_password_hash()

# ==================================================
# 🏁 LOGIN / SETUP SCREEN
# ==================================================
if not st.session_state.authenticated:

    st.markdown("<h1 style='text-align:center;'>🔒 TheraMate Secure Login</h1>",
                unsafe_allow_html=True)
    st.divider()

    # Password setup / reset
    if stored_pw_hash is None or st.session_state.reset_in_progress:
        st.info(
            "✨ First-time setup or password reset. Please create a secure password (6+ characters).")

        new_pw = st.text_input("Enter New Password",
                               type="password", key="new_pw")
        if st.checkbox("👁 Show password", key="show_new_pw"):
            st.write(f"`{new_pw}`")

        if st.button("✅ Set Password", use_container_width=True):
            if len(new_pw) >= 6:
                save_password_hash(hash_password(new_pw))
                st.session_state.authenticated = True
                st.session_state.reset_in_progress = False
                st.session_state.wrong_attempts = 0
                st.session_state.just_logged_in = True
                st.rerun()
            else:
                st.error("❌ Password too short! Use at least 6 characters.")
        st.stop()

    # Normal login
    st.info("🌸 Please enter your password to continue.")
    pw_input = st.text_input("Password", type="password", key="pw_input")
    if st.checkbox("👁 Show password", key="show_pw"):
        st.write(f"`{pw_input}`")

    login_col, reset_col = st.columns(2)
    with login_col:
        if st.button("🔓 Login", use_container_width=True):
            if hash_password(pw_input) == stored_pw_hash:
                st.session_state.authenticated = True
                st.session_state.wrong_attempts = 0
                st.session_state.just_logged_in = True  # ✅ Added flag for timed message
                st.rerun()
            else:
                st.session_state.wrong_attempts += 1
                st.error(
                    f"❌ Incorrect password! Attempts: {st.session_state.wrong_attempts}")
                if st.session_state.wrong_attempts >= 5:
                    st.warning(
                        "⚠️ Too many wrong attempts! You may reset your password.")

    with reset_col:
        if st.button("🔁 Forgot / Reset Password", use_container_width=True):
            delete_password_file()
            st.session_state.reset_in_progress = True
            st.info("Password reset initiated. Please set a new password below.")
            st.rerun()

    st.stop()

# ==================================================
# ✅ MAIN DASHBOARD (AFTER LOGIN)
# ==================================================
if st.session_state.just_logged_in:
    success_placeholder = st.empty()
    success_placeholder.success("🎉 You are successfully logged in!")
    time.sleep(3)  # ⏳ Show for 3 seconds
    success_placeholder.empty()
    st.session_state.just_logged_in = False
    st.rerun()

# 🌸 Calm dashboard screen
st.markdown("<h2 style='text-align:center;'>Welcome to TheraMate 🌸✨</h2>",
            unsafe_allow_html=True)


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
    st.markdown(
        f"<h2 style='color: #667eea;'>👋 Hi, {st.session_state.nickname}!</h2>", unsafe_allow_html=True)

    # Hide Screen Toggle
    hide_screen_state = st.toggle(
        "🔒 Hide Screen", st.session_state.hide_screen, key="hide_toggle")
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
                # Show last 5 messages
                for msg in st.session_state.chat_history[-5:]:
                    timestamp = msg.get('timestamp', '')
                    if msg["role"] == "user":
                        st.markdown(
                            f"**You:** {msg['text']} <small style='opacity:0.7;'>{timestamp}</small>", unsafe_allow_html=True)
                    else:
                        st.markdown(
                            f"**🌸 TheraMate:** {msg['text']} <small style='opacity:0.6;'>{timestamp}</small>", unsafe_allow_html=True)

            # ✅ Use form to auto-clear input
            with st.form(key="quick_chat_form", clear_on_submit=True):
                quick_input = st.text_input(
                    "Quick message...", key="quick_chat_input", placeholder="Type your message...")
                send_quick = st.form_submit_button("Send 📤", type="primary")

            # ✅ Handle outside the form
            if send_quick and quick_input.strip():
                timestamp = get_ist_time()  # ✅ Use IST helper

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
                    "timestamp": get_ist_time()  # ✅ Use IST helper
                })
                st.rerun()


# ========== 🏠 DASHBOARD PAGE - FULLY THEME-AWARE & DYNAMIC ==========
if page == "🏠 Dashboard":
    import time
    from datetime import datetime

    # 🌈 Smart Theme Detection with Custom Theme Support (ENHANCED)
    def get_theme_colors():
        """Get theme colors with intelligent defaults and custom theme support"""
        try:
            theme_base = st.get_option("theme.base")
            theme_bg = st.get_option("theme.backgroundColor")
            theme_text = st.get_option("theme.textColor")
            theme_primary = st.get_option("theme.primaryColor")
            theme_secondary_bg = st.get_option(
                "theme.secondaryBackgroundColor")
        except:
            theme_base, theme_bg, theme_text, theme_primary, theme_secondary_bg = None, None, None, None, None

        # PRIORITY: Check custom theme in session state first
        if 'custom_theme' in st.session_state and st.session_state.get('use_custom_theme', False):
            custom = st.session_state.custom_theme
            base_mode = custom.get("base", "light")

            # Determine contrasting colors for better visibility
            is_dark = base_mode == "dark"
            default_text = "#f0f0f0" if is_dark else "#1a1a1a"
            default_subtext = "#bbb" if is_dark else "#555"
            default_bg = "#0e1117" if is_dark else "#f8f9ff"
            default_secondary_bg = "#1e2233" if is_dark else "#eef1ff"
            default_card_bg = "rgba(30,30,47,0.85)" if is_dark else "rgba(255,255,255,0.9)"
            default_card_shadow = "0 4px 15px rgba(255,255,255,0.05)" if is_dark else "0 4px 15px rgba(0,0,0,0.1)"
            default_insight_bg = "rgba(30, 34, 51, 0.7)" if is_dark else "rgba(238, 241, 255, 0.7)"

            return {
                "base": base_mode,
                "background": custom.get("backgroundColor", default_bg),
                "text": custom.get("textColor", default_text),
                "primary": custom.get("primaryColor", "#667eea"),
                "secondary_bg": custom.get("secondaryBackgroundColor", default_secondary_bg),
                "card_bg": custom.get("cardBg", default_card_bg),
                "card_shadow": custom.get("cardShadow", default_card_shadow),
                "blur_bg": "backdrop-filter: blur(10px);",
                "subtext_color": custom.get("subtextColor", default_subtext),
                "success": "#52B788",
                "warn": "#F7B801",
                "error": "#FF6B35",
                "insight_bg": custom.get("insightBg", default_insight_bg),
                "insight_border": custom.get("primaryColor", "#667eea"),
                "hover_transform": "scale(1.03)",
                "transition": "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)"
            }

        # Smart defaults based on Streamlit theme
        if not theme_base or theme_base == "light":
            return {
                "base": "light",
                "background": theme_bg or "#f8f9ff",
                "text": theme_text or "#1a1a1a",
                "primary": theme_primary or "#667eea",
                "secondary_bg": theme_secondary_bg or "#eef1ff",
                "card_bg": "rgba(255,255,255,0.9)",
                "card_shadow": "0 4px 15px rgba(0,0,0,0.1)",
                "blur_bg": "backdrop-filter: blur(10px);",
                "subtext_color": "#555",
                "success": "#52B788",
                "warn": "#F7B801",
                "error": "#FF6B35",
                "insight_bg": "rgba(238, 241, 255, 0.7)",
                "insight_border": theme_primary or "#667eea",
                "hover_transform": "scale(1.03)",
                "transition": "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)"
            }
        else:
            return {
                "base": "dark",
                "background": theme_bg or "#0e1117",
                "text": theme_text or "#f0f0f0",
                "primary": theme_primary or "#667eea",
                "secondary_bg": theme_secondary_bg or "#1e2233",
                "card_bg": "rgba(30,30,47,0.85)",
                "card_shadow": "0 4px 15px rgba(255,255,255,0.05)",
                "blur_bg": "backdrop-filter: blur(10px);",
                "subtext_color": "#bbb",
                "success": "#52B788",
                "warn": "#F7B801",
                "error": "#FF6B35",
                "insight_bg": "rgba(30, 34, 51, 0.7)",
                "insight_border": theme_primary or "#667eea",
                "hover_transform": "scale(1.03)",
                "transition": "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)"
            }

    # 💡 Dynamic Insights Generator (FIXED & ENHANCED)
    def get_dynamic_insights(score):
        """Generate personalized wellness insights based on WHO-5 score"""
        if score >= 80:
            return """🌟 **Outstanding Wellness Journey!**
            
Your mental wellbeing is in an excellent place right now! You're experiencing high levels of positive emotions and vitality. 

**Keep This Momentum:**
- Continue your current self-care routines
- Share your positive energy with others
- Document what's working well for future reference
- Consider mentoring others on their wellness journey

Remember: Even on great days, it's okay to rest and recharge. Balance is key! 🌈"""

        elif score >= 60:
            return """💪 **You're Doing Great!**
            
Your wellness indicators show you're managing well overall. There's positive momentum in your mental health journey.

**Ways to Enhance:**
- Identify what activities boost your mood most
- Build consistency in your daily wellness practices
- Connect with supportive friends or family
- Try one new relaxation technique this week

You're on a solid path. Small improvements compound over time! ✨"""

        elif score >= 40:
            return """🌱 **Room for Growth**
            
You're showing resilience, but there's opportunity to improve your overall wellbeing. This is a perfect time to focus on self-care.

**Suggested Actions:**
- Practice mindfulness for 5 minutes daily
- Ensure you're getting adequate sleep (7-9 hours)
- Engage in light physical activity
- Reach out to someone you trust
- Consider professional support if feelings persist

Every small step counts. You're worth the effort! 💚"""

        else:
            return """💖 **You Deserve Support**
            
Your responses indicate you might be experiencing some difficult emotions. Please know that it's okay to not be okay sometimes.

**Immediate Self-Care:**
- Be gentle with yourself today
- Do something that brings you comfort
- Connect with a trusted friend or family member
- Consider reaching out to a mental health professional
- Call a helpline if you need immediate support

**Crisis Resources:**
- National Suicide Prevention Lifeline: 988
- Crisis Text Line: Text HOME to 741741

You are not alone in this journey. Support is available, and things can improve. 🌸"""

    # Get current theme (this will auto-update when session_state changes)
    theme = get_theme_colors()

    # 🌸 Animated Gradient Header (ENHANCED)
    st.markdown(f"""
    <style>
    @keyframes gradientShift {{
        0% {{ background-position: 0% 50%; }}
        50% {{ background-position: 100% 50%; }}
        100% {{ background-position: 0% 50%; }}
    }}
    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(-10px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    .dashboard-header {{
        animation: fadeIn 0.6s ease-out;
    }}
    </style>
    <div class="dashboard-header" style="
        background: linear-gradient(-45deg, {theme['primary']}, #8e9eff, #a777e3, #764ba2);
        background-size: 300% 300%;
        animation: gradientShift 8s ease infinite;
        padding: 2.2rem;
        border-radius: 18px;
        text-align: center;
        color: white;
        box-shadow: 0 6px 20px rgba(102,126,234,0.4);
        margin-bottom: 2rem;
    ">
        <h1 style="font-size:2.6rem; margin-bottom:0.3rem; font-weight: 700; text-shadow: 0 2px 8px rgba(0,0,0,0.2);">🌸 TheraMate Dashboard</h1>
        <p style="font-size:1.1rem; opacity:0.95; margin:0; text-shadow: 0 1px 4px rgba(0,0,0,0.15);">Your personalized wellness companion</p>
    </div>
    """, unsafe_allow_html=True)

    # 🔹 Load Data (with auto-refresh support) - DYNAMIC
    today_habits = get_today_habits()
    completed_habits = sum(1 for h in today_habits if h.get("done"))
    total_habits = len(today_habits) if today_habits else 0

    water_data = load_json(WATER_FILE, [])
    today_str = datetime.today().strftime("%Y-%m-%d")
    today_water = next((w for w in water_data if w.get(
        "date") == today_str), {"glasses": 0})
    water_progress = today_water.get("glasses", 0)

    # Check if WHO-5 completed today
    who5_done_today = bool(
        mood_history and mood_history[-1].get("date") == today_str)

    # 📊 Three Main Cards with Dynamic Theme Colors (FULLY DYNAMIC TEXT)
    col1, col2, col3 = st.columns(3)

    # 🎯 Today's Goals Card (ALL TEXT DYNAMIC)
    with col1:
        goal_complete = sum([
            1 if who5_done_today else 0,
            1 if completed_habits == total_habits and total_habits > 0 else 0,
            1 if water_progress >= 8 else 0
        ])
        goal_percent = int((goal_complete / 3) *
                           100) if goal_complete > 0 else 0

        st.markdown(f"""
        <div style="
            {theme['blur_bg']}
            background: {theme['card_bg']};
            padding: 1.6rem;
            border-radius: 16px;
            box-shadow: {theme['card_shadow']};
            transition: {theme['transition']};
            border: 2px solid {theme['secondary_bg']};
        " onmouseover="this.style.transform='{theme['hover_transform']}'; this.style.boxShadow='0 8px 25px rgba(102,126,234,0.3)';"
          onmouseout="this.style.transform='scale(1)'; this.style.boxShadow='{theme['card_shadow']}';">
            <h3 style="color:{theme['primary']}; font-size:1.5rem; margin-top:0; margin-bottom:1rem; font-weight:700;">🎯 Today's Goals</h3>
            <p style="font-size:1rem; line-height:2; margin: 0.5rem 0;">
                <span style="color:{theme['text']}; font-weight:600; display: block; margin-bottom: 0.3rem;">
                    {'✅' if who5_done_today else '○'} <span style="color:{theme['text']};">WHO-5 Check</span>
                </span>
                <span style="color:{theme['text']}; font-weight:600; display: block; margin-bottom: 0.3rem;">
                    {'✅' if completed_habits == total_habits and total_habits > 0 else '○'} <span style="color:{theme['text']};">Habits {completed_habits}/{total_habits}</span>
                </span>
                <span style="color:{theme['text']}; font-weight:600; display: block;">
                    {'✅' if water_progress >= 8 else '○'} <span style="color:{theme['text']};">Water {water_progress}/8 glasses</span>
                </span>
            </p>
            <div style="height:12px; background:{theme['secondary_bg']}; border-radius:10px; overflow:hidden; margin-top: 1rem;">
                <div style="height:100%; width:{goal_percent}%; background:linear-gradient(90deg,{theme['primary']},#764ba2); border-radius:10px; transition: width 0.6s ease;"></div>
            </div>
            <p style="color:{theme['text']}; text-align:center; margin-top:0.7rem; font-size:1rem; font-weight:600;">{goal_percent}% Completed</p>
        </div>
        """, unsafe_allow_html=True)

    # 📈 Wellness Score Card (ALL TEXT DYNAMIC)
    with col2:
        if mood_history and len(mood_history) > 0:
            recent_scores = [m.get("score", 50) for m in mood_history[-7:]]
            wellness_score = int(sum(recent_scores) / len(recent_scores))
        else:
            wellness_score = 0

        score_color = theme["success"] if wellness_score >= 70 else theme["warn"] if wellness_score >= 50 else theme["error"]
        msg = "🌈 Excellent!" if wellness_score >= 70 else "💪 Keep it up!" if wellness_score >= 50 else "💖 Take it easy."

        st.markdown(f"""
        <div style="
            {theme['blur_bg']}
            background: {theme['card_bg']};
            padding: 1.6rem;
            border-radius: 16px;
            box-shadow: {theme['card_shadow']};
            text-align: center;
            transition: {theme['transition']};
            border: 2px solid {theme['secondary_bg']};
        " onmouseover="this.style.transform='{theme['hover_transform']}';"
          onmouseout="this.style.transform='scale(1)';">
            <h3 style="color:{theme['primary']}; font-size:1.5rem; margin-top:0; margin-bottom:0.8rem; font-weight:700;">📈 Wellness Score</h3>
            <h1 style="color:{score_color}; font-size:3rem; margin:0.5rem 0; font-weight:800; text-shadow: 0 2px 8px rgba(0,0,0,0.15);">{wellness_score}%</h1>
            <p style="color:{theme['text']}; font-size:1.1rem; margin-top:0.5rem; font-weight:600;">{msg}</p>
            <p style="color:{theme['text']}; font-size:0.9rem; margin-top:0.4rem; font-weight:500;">7-day average</p>
        </div>
        """, unsafe_allow_html=True)

    # 🏆 Achievements Card (ALL TEXT DYNAMIC)
    with col3:
        badges = len(st.session_state.badges) if hasattr(
            st.session_state, 'badges') else 0
        streak = st.session_state.streak_days if hasattr(
            st.session_state, 'streak_days') else 0
        fire = "🔥🔥🔥" if streak >= 30 else "🔥🔥" if streak >= 7 else "🔥"

        st.markdown(f"""
        <div style="
            {theme['blur_bg']}
            background: {theme['card_bg']};
            padding: 1.6rem;
            border-radius: 16px;
            box-shadow: {theme['card_shadow']};
            text-align: center;
            transition: {theme['transition']};
            border: 2px solid {theme['secondary_bg']};
        " onmouseover="this.style.transform='{theme['hover_transform']}';"
          onmouseout="this.style.transform='scale(1)';">
            <h3 style="color:{theme['primary']}; font-size:1.5rem; margin-top:0; margin-bottom:0.8rem; font-weight:700;">🏆 Achievements</h3>
            <div style="font-size:2.2rem; margin:0.8rem 0; font-weight:700;">
                <span style="color:{theme['text']};">🎖️ {badges}</span> <span style="color:{theme['text']};">|</span> <span style="color:{theme['text']};">{fire} {streak}</span>
            </div>
            <p style="color:{theme['text']}; font-size:1rem; font-weight:600;">day{'s' if streak != 1 else ''}</p>
            <p style="color:{theme['text']}; font-size:0.9rem; margin-top:0.3rem; font-weight:500;">Keep the streak alive!</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ========== WHO-5 QUESTIONNAIRE (FULLY DYNAMIC TEXT) ==========
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, {theme['card_bg']} 0%, {theme['secondary_bg']} 100%);
        padding: 2rem;
        border-radius: 16px;
        box-shadow: {theme['card_shadow']};
        border: 3px solid {theme['primary']};
        margin-bottom: 1.5rem;
    ">
        <h3 style="
            color: {theme['primary']};
            margin-top: 0;
            margin-bottom: 1rem;
            font-size: 1.8rem;
            display: flex;
            align-items: center;
            font-weight: 800;
            text-shadow: 0 2px 4px rgba(0,0,0,0.1);
        ">
            <span style="font-size: 2rem; margin-right: 0.7rem;">📝</span>
            Daily WHO-5 Wellness Check
        </h3>
        <p style="
            color: {theme['text']}; 
            font-weight: 600;
            margin-bottom: 0; 
            font-size: 1.1rem; 
            line-height: 1.7;
            padding: 0.8rem;
            background: {theme['card_bg']};
            border-radius: 10px;
            border-left: 4px solid {theme['primary']};
        ">
            Rate how you've been feeling over the <strong style="color: {theme['primary']}; font-weight: 700;">past two weeks</strong> 
            <br><span style="font-size: 1rem; color: {theme['text']}; font-weight: 500;">
            (0 = not at all | 5 = all of the time)</span>
        </p>
    </div>
    """, unsafe_allow_html=True)

    # WHO-5 Questions with Fully Dynamic Text Colors
    who5_answers = []
    for i, q in enumerate(WHO5_QUESTIONS, start=1):
        st.markdown(f"""
        <div style="
            color: {theme['text']}; 
            font-weight: 600; 
            font-size: 1.1rem;
            margin-bottom: 0.8rem;
            padding: 1rem 1.2rem;
            background: {theme['card_bg']};
            border-radius: 12px;
            border-left: 4px solid {theme['primary']};
            box-shadow: 0 2px 6px rgba(0,0,0,0.08);
            transition: {theme['transition']};
        " onmouseover="this.style.transform='translateX(5px)'; this.style.boxShadow='0 4px 12px rgba(102,126,234,0.2)';"
          onmouseout="this.style.transform='translateX(0)'; this.style.boxShadow='0 2px 6px rgba(0,0,0,0.08)';">
            <strong style="color: {theme['primary']}; font-size: 1.2rem;">{i}.</strong> <span style="color: {theme['text']};">{q}</span>
        </div>
        """, unsafe_allow_html=True)
        slider_val = st.slider(
            f"Question {i}",
            0, 5, 3,
            key=f"who5_q{i}",
            label_visibility="collapsed",
            help="0 = Not at all | 5 = All of the time"
        )
        who5_answers.append(slider_val)
        st.markdown("<div style='margin-bottom: 0.5rem;'></div>",
                    unsafe_allow_html=True)

    # Submit Button (ENHANCED)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("📊 Submit WHO-5 Assessment", type="primary", use_container_width=True):
            total = sum(who5_answers)
            percent = int((total / 25) * 100)
            today_str = datetime.today().strftime("%Y-%m-%d")

            # Update or add today's entry
            if mood_history and mood_history[-1].get("date") == today_str:
                mood_history[-1] = {"who5": who5_answers,
                                    "score": percent, "date": today_str}
            else:
                mood_history.append(
                    {"who5": who5_answers, "score": percent, "date": today_str})

            save_mood()

            st.success(f"✅ Your wellness score: **{percent}%**")

            # Award badges (if functions exist)
            try:
                if percent >= 80 and award_badge("Wellness Star", "⭐"):
                    st.balloons()
                    st.success("🎉 Badge unlocked: Wellness Star!")

                st.session_state.streak_days = calculate_streak()
                if st.session_state.streak_days >= 7 and award_badge("7-Day Streak", "🔥"):
                    st.balloons()
                    st.success("🎉 Badge unlocked: 7-Day Streak!")
            except:
                pass

            time.sleep(0.5)
            st.rerun()

    # ========== WELLNESS INSIGHTS - PREMIUM EMOTIONAL DESIGN ==========
        # ========== WELLNESS INSIGHTS - PREMIUM EMOTIONAL DESIGN ==========
    st.markdown("<br>", unsafe_allow_html=True)

    # Get latest score safely
    if mood_history and len(mood_history) > 0:
        latest_score = mood_history[-1].get("score", 50)
    else:
        latest_score = 50

    # 🌸 Enhanced Dynamic Insights with Emotional Intelligence
    def get_wellness_message(score):
        """Generate emotionally intelligent wellness messages"""
        if score >= 80:
            return {
                "headline": "You're Radiating Brilliance",
                "emoji": "✨",
                "icon": "🌟",
                "summary": "Your energy is soaring beautifully. You're in a powerful place of growth and positivity.",
                "suggestions": [
                    ("🌈", "Celebrate your wins",
                     "Take a moment to acknowledge how far you've come"),
                    ("💫", "Share your light",
                     "Your positive energy can inspire someone else today"),
                    ("📖", "Document this feeling",
                     "Write down what's working so you can return to it"),
                    ("🎯", "Set a new intention",
                     "What would you love to explore next?")
                ],
                "closing": "You're not just thriving — you're blooming into your best self. Keep shining.",
                "closing_emoji": "💖",
                "gradient_start": "#667eea",
                "gradient_end": "#a777e3",
                "glow_color": "102, 126, 234"
            }
        elif score >= 60:
            return {
                "headline": "You're Growing Beautifully",
                "emoji": "🌱",
                "icon": "💪",
                "summary": "Your heart and mind are finding their rhythm. There's real momentum in your journey.",
                "suggestions": [
                    ("✨", "Reflect on today's joys",
                     "What made you smile, even briefly?"),
                    ("🌙", "Prioritize rest",
                     "Your body and mind deserve gentle recovery"),
                    ("💬", "Connect meaningfully",
                     "Reach out to someone who brings you peace"),
                    ("🧘", "Try mindful breathing",
                     "Just 5 minutes can shift your whole day")
                ],
                "closing": "You're not just improving — you're evolving with grace. Trust the process.",
                "closing_emoji": "🌸",
                "gradient_start": "#52B788",
                "gradient_end": "#667eea",
                "glow_color": "82, 183, 136"
            }
        elif score >= 40:
            return {
                "headline": "You're Finding Your Way",
                "emoji": "🌤️",
                "icon": "🌿",
                "summary": "Some days feel harder than others, and that's completely okay. You're showing up, and that matters.",
                "suggestions": [
                    ("🕯️", "Be gentle with yourself",
                     "Treat yourself like you would a dear friend"),
                    ("🌊", "Take it slow", "Small steps forward are still progress"),
                    ("☕", "Do something comforting",
                     "A warm drink, soft music, or cozy blanket"),
                    ("🤝", "Reach out if needed",
                     "There's strength in asking for support")
                ],
                "closing": "Your journey isn't always linear, and that's beautiful. Keep going softly.",
                "closing_emoji": "💚",
                "gradient_start": "#F7B801",
                "gradient_end": "#667eea",
                "glow_color": "247, 184, 1"
            }
        else:
            return {
                "headline": "You Deserve Gentle Care",
                "emoji": "💖",
                "icon": "🌸",
                "summary": "Right now feels heavy, and I want you to know: it's okay to not be okay. You're not alone.",
                "suggestions": [
                    ("🫂", "Be extra kind to yourself",
                     "This moment doesn't define your worth"),
                    ("🌙", "Rest without guilt",
                     "Your body needs safety and comfort right now"),
                    ("💌", "Talk to someone safe",
                     "A friend, family member, or counselor who listens"),
                    ("📞", "Professional support is strength",
                     "Therapists and helplines are here for you")
                ],
                "closing": "You are worthy of support, healing, and peace. Brighter days are possible.",
                "closing_emoji": "🕊️",
                "gradient_start": "#FF6B35",
                "gradient_end": "#a777e3",
                "glow_color": "255, 107, 53",
                "crisis": True
            }

    # Get personalized message
    message = get_wellness_message(latest_score)

    # Advanced CSS with premium animations
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    @keyframes floatGlow {{
        0%, 100% {{ 
            transform: translateY(0px);
            box-shadow: 0 10px 40px rgba({message['glow_color']}, 0.2);
        }}
        50% {{ 
            transform: translateY(-5px);
            box-shadow: 0 20px 60px rgba({message['glow_color']}, 0.35);
        }}
    }}

    @keyframes shimmer {{
        0% {{ background-position: -1000px 0; }}
        100% {{ background-position: 1000px 0; }}
    }}

    @keyframes slideInLeft {{
        from {{
            opacity: 0;
            transform: translateX(-30px);
        }}
        to {{
            opacity: 1;
            transform: translateX(0);
        }}
    }}

    @keyframes pulseGlow {{
        0%, 100% {{ opacity: 0.6; }}
        50% {{ opacity: 1; }}
    }}

    .wellness-premium-card {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        background: {theme['card_bg']};
        position: relative;
        padding: 3rem;
        border-radius: 24px;
        border: 1px solid rgba({message['glow_color']}, 0.2);
        overflow: hidden;
        animation: floatGlow 4s ease-in-out infinite;
        margin-top: 2rem;
    }}

    .wellness-premium-card::before {{
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba({message['glow_color']}, 0.15) 0%, transparent 70%);
        animation: pulseGlow 6s ease-in-out infinite;
        pointer-events: none;
    }}

    .wellness-premium-card::after {{
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
        animation: shimmer 3s infinite;
    }}

    .insight-header {{
        position: relative;
        z-index: 2;
        text-align: center;
        margin-bottom: 2rem;
    }}

    .insight-icon {{
        font-size: 4rem;
        display: block;
        margin-bottom: 1rem;
        animation: pulseGlow 2s ease-in-out infinite;
        filter: drop-shadow(0 4px 12px rgba({message['glow_color']}, 0.4));
    }}

    .insight-headline {{
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, {message['gradient_start']}, {message['gradient_end']});
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0;
        letter-spacing: -0.5px;
    }}

    .insight-summary {{
        position: relative;
        z-index: 2;
        color: {theme['text']};
        font-size: 1.25rem;
        line-height: 2;
        text-align: center;
        font-weight: 500;
        margin: 2rem auto;
        max-width: 700px;
        padding: 1.5rem;
        background: {theme['secondary_bg']};
        border-radius: 16px;
        border-left: 4px solid {message['gradient_start']};
    }}

    .suggestions-title {{
        position: relative;
        z-index: 2;
        color: {theme['primary']};
        font-size: 1.5rem;
        font-weight: 700;
        margin: 2.5rem 0 1.5rem 0;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.7rem;
    }}

    .suggestions-grid {{
        position: relative;
        z-index: 2;
        display: grid;
        gap: 1.2rem;
        margin: 2rem 0;
    }}

    .suggestion-card {{
        background: {theme['secondary_bg']};
        padding: 1.5rem;
        border-radius: 16px;
        display: flex;
        align-items: flex-start;
        gap: 1.2rem;
        border: 2px solid transparent;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }}

    .suggestion-card::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
        background: linear-gradient(180deg, {message['gradient_start']}, {message['gradient_end']});
        transform: scaleY(0);
        transition: transform 0.4s ease;
    }}

    .suggestion-card:hover {{
        transform: translateX(12px) scale(1.02);
        border-color: {message['gradient_start']};
        box-shadow: 0 12px 40px rgba({message['glow_color']}, 0.25);
        background: {theme['card_bg']};
    }}

    .suggestion-card:hover::before {{
        transform: scaleY(1);
    }}

    .suggestion-emoji {{
        font-size: 2rem;
        flex-shrink: 0;
        filter: drop-shadow(0 2px 8px rgba({message['glow_color']}, 0.3));
        animation: slideInLeft 0.6s ease-out backwards;
    }}

    .suggestion-card:nth-child(1) .suggestion-emoji {{ animation-delay: 0.1s; }}
    .suggestion-card:nth-child(2) .suggestion-emoji {{ animation-delay: 0.2s; }}
    .suggestion-card:nth-child(3) .suggestion-emoji {{ animation-delay: 0.3s; }}
    .suggestion-card:nth-child(4) .suggestion-emoji {{ animation-delay: 0.4s; }}

    .suggestion-content {{
        flex: 1;
    }}

    .suggestion-title {{
        color: {theme['text']};
        font-size: 1.15rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        letter-spacing: -0.2px;
    }}

    .suggestion-description {{
        color: {theme['subtext_color']};
        font-size: 1rem;
        line-height: 1.6;
        font-weight: 500;
    }}


    
    .closing-box {{
    position: relative;
    z-index: 2;
    text-align: center;
    margin-top: 3rem;
    padding: 2rem;
    background: {theme['secondary_bg']};  /* Changed from gradient with opacity */
    border-radius: 18px;
    border: 2px solid {message['gradient_start']};
    box-shadow: 0 8px 32px rgba({message['glow_color']}, 0.2);
    }}

    .closing-text {{
        color: {theme['text']};
        font-size: 1.3rem;
        font-weight: 600;
        line-height: 1.8;
        margin: 0;
    }}

    .closing-emoji {{
        font-size: 1.8rem;
        display: inline-block;
        margin-left: 0.5rem;
        animation: pulseGlow 2s ease-in-out infinite;
    }}

    .crisis-premium {{
        position: relative;
        z-index: 2;
        margin-top: 2rem;
        padding: 2.5rem;
        border-radius: 20px;
        background: linear-gradient(135deg, #FFF9F0 0%, #FFE8D6 100%);
        border: 3px solid #D2691E;
        box-shadow: 0 12px 48px rgba(210, 105, 30, 0.2);
        animation: slideInLeft 0.8s ease-out;
    }}

    .crisis-premium-dark {{
        background: linear-gradient(135deg, rgba(139, 90, 70, 0.3) 0%, rgba(101, 67, 54, 0.4) 100%);
        backdrop-filter: blur(10px);
    }}

    .crisis-header {{
        text-align: center;
        margin-bottom: 1.5rem;
    }}

    .crisis-icon {{
        font-size: 2.5rem;
        display: block;
        margin-bottom: 0.8rem;
    }}

    .crisis-title {{
        font-size: 1.6rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: 0.5px;
    }}

    .crisis-message {{
        font-size: 1.2rem;
        line-height: 2;
        text-align: center;
        font-weight: 500;
        margin: 1.5rem 0;
        padding: 1.2rem;
        background: rgba(255, 255, 255, 0.7);
        border-radius: 12px;
    }}

    .crisis-helplines {{
        background: rgba(255, 255, 255, 0.85);
        padding: 2rem;
        border-radius: 16px;
        margin: 1.5rem 0;
        border: 2px solid #D2691E;
    }}

    .helpline-section-title {{
        font-size: 1.3rem;
        font-weight: 700;
        text-align: center;
        margin: 0 0 1.5rem 0;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.5rem;
    }}

    .helpline-item {{
        margin: 1.2rem 0;
        padding: 1rem;
        background: rgba(255, 255, 255, 0.9);
        border-radius: 12px;
        transition: all 0.3s ease;
    }}

    .helpline-item:hover {{
        transform: scale(1.02);
        box-shadow: 0 6px 24px rgba(210, 105, 30, 0.2);
    }}

    .helpline-number {{
        display: inline-block;
        font-size: 1.3rem;
        font-weight: 800;
        padding: 0.6rem 1.2rem;
        background: linear-gradient(135deg, #FF6B6B, #C2185B);
        color: white;
        border-radius: 10px;
        text-decoration: none;
        transition: all 0.3s ease;
        box-shadow: 0 4px 16px rgba(194, 24, 91, 0.3);
        margin-left: 0.5rem;
    }}

    .helpline-number:hover {{
        transform: scale(1.08) translateY(-2px);
        box-shadow: 0 8px 24px rgba(194, 24, 91, 0.4);
    }}

    .crisis-footer {{
        font-size: 1.15rem;
        text-align: center;
        font-style: italic;
        font-weight: 600;
        margin-top: 1.5rem;
        opacity: 0.95;
    }}
    </style>
    """, unsafe_allow_html=True)

    # Main premium card
    st.markdown(f"""<div class="wellness-premium-card">""",
                unsafe_allow_html=True)

    # Header with icon and headline
    st.markdown(f"""
    <div class="insight-header">
        <span class="insight-icon">{message['icon']}</span>
        <h2 class="insight-headline">{message['emoji']} {message['headline']}</h2>
    </div>
    """, unsafe_allow_html=True)

    # Summary
    st.markdown(
        f"""<p class="insight-summary">{message['summary']}</p>""", unsafe_allow_html=True)

    # Section title
    st.markdown(f"""<h3 class="suggestions-title"><span style="font-size: 1.8rem;">🌿</span> Gentle Ways Forward</h3>""", unsafe_allow_html=True)

    # Suggestions grid
    st.markdown("""<div class="suggestions-grid">""", unsafe_allow_html=True)

    for emoji, title, description in message['suggestions']:
        st.markdown(f"""
    <div class="suggestion-card">
        <div class="suggestion-emoji">{emoji}</div>
        <div class="suggestion-content">
            <div class="suggestion-title">{title}</div>
            <div class="suggestion-description">{description}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""</div>""", unsafe_allow_html=True)

    # Closing message
    st.markdown(f"""
    <div class="closing-box">
        <p class="closing-text">{message['closing']}<span class="closing-emoji">{message['closing_emoji']}</span></p>
    </div>
    """, unsafe_allow_html=True)

    # Crisis section if needed - FIXED WITH SINGLE-LINE HTML
    # Crisis section if needed - FIXED WITH PROPER THEME COLORS
    if message.get('crisis', False):
        crisis_class = "crisis-premium-dark" if theme['base'] == "dark" else ""

        # Use theme['text'] for all text to ensure visibility
        crisis_text_color = theme['text']  # Dynamic text color
        crisis_heading_color = theme['primary']  # Use primary theme color
        crisis_bg_color = theme['card_bg']  # Use card background
        crisis_secondary_bg = theme['secondary_bg']  # Use secondary background

        st.markdown(
            f"""<div class="crisis-premium {crisis_class}" style="background: {crisis_bg_color}; backdrop-filter: blur(10px);"><div class="crisis-header"><span class="crisis-icon">🤍</span><h3 class="crisis-title" style="color: {crisis_heading_color};">You're Not Alone</h3></div><p class="crisis-message" style="color: {crisis_text_color}; background: {crisis_secondary_bg};">Right now feels heavy, and I want you to know: <strong style="color: {crisis_text_color};">it's okay to not be okay.</strong><br>You matter, and help is here for you. 💙</p><div class="crisis-helplines" style="background: {crisis_secondary_bg};"><h4 class="helpline-section-title" style="color: {crisis_heading_color};">🇮🇳 Immediate Support in India</h4><div class="helpline-item" style="background: {theme['card_bg']};"><span style="color: {crisis_text_color}; font-size: 1.1rem; font-weight: 600;">☎️ <strong>AASRA Helpline</strong></span><a href="tel:+919820466726" class="helpline-number">+91-9820466726</a></div><div class="helpline-item" style="background: {theme['card_bg']};"><span style="color: {crisis_text_color}; font-size: 1.1rem; font-weight: 600;">🌿 <strong>Snehi (24×7)</strong></span><a href="tel:+919582208181" class="helpline-number">+91-9582208181</a></div><p style="color: {crisis_text_color}; font-size: 1.1rem; font-weight: 600; text-align: center; margin-top: 1.5rem;">🌐 <strong>More Resources:</strong> <a href="https://findahelpline.com" target="_blank" style="color: {theme['primary']}; text-decoration: underline; font-weight: 700;">findahelpline.com</a><span> (select India)</span></p></div><p class="crisis-footer" style="color: {crisis_text_color};">Reaching out is a sign of strength. You deserve support and care. 🌸</p></div>""", unsafe_allow_html=True)

        st.markdown("""</div>""", unsafe_allow_html=True)

    # ========== QUICK ACTIONS (FULLY DYNAMIC TEXT) ==========
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style="
        background: {theme['card_bg']};
        padding: 1.7rem;
        border-radius: 16px;
        box-shadow: {theme['card_shadow']};
        border: 2px solid {theme['secondary_bg']};
    ">
        <h3 style="color: {theme['primary']}; margin-top: 0; margin-bottom: 0.5rem; font-size: 1.4rem; font-weight: 700;">⚡ Quick Actions</h3>
        <p style="color: {theme['text']}; margin: 0; font-size: 1rem; font-weight: 500;">
            Navigate to other sections to continue your wellness journey
        </p>
    </div>
    """, unsafe_allow_html=True)


# ---------- AI CHAT PAGE ----------
elif page == "💬 AI Chat":
    st.markdown("<h1 style='color: #667eea;'>💬 Chat with TheraMate</h1>",
                unsafe_allow_html=True)

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
        user_text = st.text_input(
            "Type your message...", placeholder="How are you feeling today?")
        send_button = st.form_submit_button("Send 📤", type="primary")

    # ✅ This should be OUTSIDE the form (unindented one level)
    if send_button and user_text.strip():
        timestamp = get_ist_time()  # ✅ Use IST helper

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
            "timestamp": get_ist_time()  # ✅ Use IST helper here too
        })

        st.session_state.show_typing = False
        st.rerun()


# ========== MOOD TRACKER PAGE - FULLY FIXED & ENHANCED ==========
elif page == "📊 Mood Tracker":
    st.markdown("<h1 style='color: #667eea;'>🌈 Mood Tracker</h1>",
                unsafe_allow_html=True)

    # FIX #1: Add custom CSS for dark mode compatibility
    st.markdown("""
    <style>
        /* Universal card styling that works in ALL themes */
        .mood-note-card {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            border-left: 5px solid;
            border-radius: 15px;
            padding: 20px;
            margin: 15px 0;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease;
        }
        
        .mood-note-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
        }
        
        /* Text colors that adapt to theme */
        .mood-note-card .card-title {
            font-size: 1.1rem;
            font-weight: 600;
            margin-bottom: 8px;
            opacity: 0.95;
        }
        
        .mood-note-card .card-note {
            font-style: italic;
            margin: 10px 0;
            opacity: 0.85;
            line-height: 1.6;
        }
        
        .mood-note-card .card-time {
            font-size: 0.85rem;
            opacity: 0.7;
        }
        
        /* Mood emoji badge */
        .mood-emoji {
            font-size: 2rem;
            display: inline-block;
            margin-right: 10px;
            filter: drop-shadow(0 2px 4px rgba(0,0,0,0.2));
        }
        
        /* Stats card styling */
        .stat-highlight {
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
            padding: 15px;
            border-radius: 12px;
            text-align: center;
            margin: 10px 0;
        }
        
        /* Empty state styling */
        .empty-state {
            text-align: center;
            padding: 40px 20px;
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);
            border-radius: 20px;
            margin: 20px 0;
        }
        
        /* Animation for new entries */
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateX(-20px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }
        
        .mood-note-card {
            animation: slideIn 0.5s ease-out;
        }
    </style>
    """, unsafe_allow_html=True)

    # Mood input section with better layout
    st.markdown("### 📝 How are you feeling today?")

    # Create a more visual mood selector
    col1, col2 = st.columns([2, 1])

    with col1:
        mood_score = st.slider(
            "Rate your mood",
            0, 100, 50,
            key="mood_slider",
            help="0 = Very Low, 50 = Neutral, 100 = Excellent"
        )

    with col2:
        # FIX #2: Show live emoji feedback based on slider
        if mood_score >= 80:
            emoji_display = "😄"
            mood_label = "Excellent"
            emoji_color = "#FFD700"
        elif mood_score >= 60:
            emoji_display = "😊"
            mood_label = "Good"
            emoji_color = "#52B788"
        elif mood_score >= 40:
            emoji_display = "😐"
            mood_label = "Okay"
            emoji_color = "#F7B801"
        else:
            emoji_display = "😢"
            mood_label = "Low"
            emoji_color = "#FF6B35"

        st.markdown(f"""
        <div style='text-align: center; padding: 15px; background: {emoji_color}20; 
                    border-radius: 15px; margin-top: 5px;'>
            <div style='font-size: 3rem;'>{emoji_display}</div>
            <div style='font-weight: 600; color: {emoji_color}; font-size: 1.2rem;'>{mood_label}</div>
            <div style='font-size: 1.5rem; font-weight: 700;'>{mood_score}%</div>
        </div>
        """, unsafe_allow_html=True)

    mood_note = st.text_area(
        "Add a note (optional)",
        placeholder="What's on your mind? Share your thoughts, feelings, or what influenced your mood today...",
        height=100
    )

    # Save button with better feedback
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("💾 Save Mood Entry", type="primary", use_container_width=True):
            # ✅ Use IST for both date and time
            ist = timezone(timedelta(hours=5, minutes=30))
            today_key = datetime.now(ist).strftime("%Y-%m-%d")

            mood_entry = {
                "score": mood_score,
                "date": today_key,
                "note": mood_note.strip() if mood_note else "",
                "timestamp": get_ist_time(),  # ✅ FIXED - Use IST helper
                "emoji": emoji_display,
                "label": mood_label
            }
            mood_history.append(mood_entry)
            save_mood()

            st.success(
                f"✅ Mood saved! You're feeling {mood_label} today ({mood_score}%) {emoji_display}")

            # Update streak
            st.session_state.streak_days = calculate_streak()

            # FIX #3: Force immediate rerun to update graph and notes
            time.sleep(0.3)
            st.rerun()

            mood_history.append(mood_entry)
            save_mood()

            st.success(
                f"✅ Mood saved! You're feeling {mood_label} today ({mood_score}%) {emoji_display}")

            # Update streak
            st.session_state.streak_days = calculate_streak()

            # FIX #3: Force immediate rerun to update graph and notes
            time.sleep(0.3)
            st.rerun()

    st.markdown("---")

    # FIX #4: Mood graph with enhanced visuals and immediate updates
    st.subheader("📈 Your Mood Journey")

    col1, col2 = st.columns([3, 1])
    with col1:
        days_to_show = st.selectbox("View period", [7, 14, 30, 90], index=0)
    with col2:
        st.metric("Total Entries", len(mood_history),
                  help="All-time mood entries")

    # FIX #5: Get FRESH data from mood_history (includes just-saved entry)
    days, scores = get_weekly_happiness(days_to_show)

    if scores and any(s > 0 for s in scores):
        # FIX #6: Remove None values and handle missing data properly
        display_scores = [s if s and s > 0 else None for s in scores]

        # Filter out None values for stats calculation
        valid_scores = [s for s in display_scores if s is not None]

        if valid_scores:
            # FIX #7: Enhanced color mapping based on mood
            def get_mood_color(score):
                if score is None:
                    return '#CCCCCC'  # Gray for missing data
                if score >= 80:
                    return '#FFD700'  # Happy - Gold
                elif score >= 60:
                    return '#52B788'  # Calm - Green
                elif score >= 40:
                    return '#F7B801'  # Neutral - Orange
                else:
                    return '#FF6B35'  # Sad - Red

            colors = [get_mood_color(s) for s in display_scores]

            # Emoji mapping with None handling
            emojis = []
            for s in display_scores:
                if s is None:
                    emojis.append("")
                elif s >= 80:
                    emojis.append("😄")
                elif s >= 60:
                    emojis.append("😊")
                elif s >= 40:
                    emojis.append("😐")
                else:
                    emojis.append("😢")

            # FIX #8: Create beautiful gradient-filled chart
            fig = go.Figure()

            # Add gradient fill area
            fig.add_trace(go.Scatter(
                x=days,
                y=display_scores,
                mode='lines+markers+text',
                text=emojis,
                textposition="top center",
                textfont=dict(size=20, family="Arial"),
                line=dict(
                    color='#667eea',
                    width=4,
                    shape='spline',  # Smooth curves
                    smoothing=1.3
                ),
                marker=dict(
                    size=18,
                    color=colors,
                    line=dict(width=3, color='white'),
                    symbol='circle'
                ),
                fill='tozeroy',
                fillcolor='rgba(102, 126, 234, 0.15)',
                hovertemplate='<b>%{x}</b><br>Mood Score: %{y}%<br><extra></extra>',
                connectgaps=False  # Don't connect gaps in data
            ))

            # FIX #9: Enhanced layout with better styling
            fig.update_layout(
                title={
                    'text': "Your Happiness Journey 🌈",
                    'x': 0.5,
                    'xanchor': 'center',
                    'font': {'size': 24, 'family': 'Inter, sans-serif'}
                },
                yaxis=dict(
                    range=[0, 105],
                    title="Mood Score (%)",
                    gridcolor='rgba(102, 126, 234, 0.1)',
                    showgrid=True
                ),
                xaxis=dict(
                    title="Days",
                    gridcolor='rgba(102, 126, 234, 0.1)',
                    showgrid=True
                ),
                template="plotly_white",
                hovermode="x unified",
                font=dict(family="Inter, sans-serif"),
                plot_bgcolor='rgba(255, 255, 255, 0.02)',
                paper_bgcolor='rgba(0,0,0,0)',
                height=450,
                margin=dict(t=80, b=60, l=60, r=40)
            )

            st.plotly_chart(fig, use_container_width=True)

            # FIX #10: Stats with dynamic updates and better visuals
            st.markdown("### 📊 Period Statistics")
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                avg_score = sum(valid_scores) / len(valid_scores)
                avg_emoji = "😄" if avg_score >= 80 else "😊" if avg_score >= 60 else "😐" if avg_score >= 40 else "😢"
                st.markdown(f"""
                <div class="stat-highlight">
                    <div style='font-size: 2rem;'>{avg_emoji}</div>
                    <div style='font-size: 0.9rem; opacity: 0.7;'>Average Mood</div>
                    <div style='font-size: 1.8rem; font-weight: 700; color: #667eea;'>{avg_score:.0f}%</div>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                highest = max(valid_scores)
                st.markdown(f"""
                <div class="stat-highlight">
                    <div style='font-size: 2rem;'>🌟</div>
                    <div style='font-size: 0.9rem; opacity: 0.7;'>Best Day</div>
                    <div style='font-size: 1.8rem; font-weight: 700; color: #52B788;'>{highest}%</div>
                </div>
                """, unsafe_allow_html=True)

            with col3:
                lowest = min(valid_scores)
                st.markdown(f"""
                <div class="stat-highlight">
                    <div style='font-size: 2rem;'>💪</div>
                    <div style='font-size: 0.9rem; opacity: 0.7;'>Lowest Day</div>
                    <div style='font-size: 1.8rem; font-weight: 700; color: #FF6B35;'>{lowest}%</div>
                </div>
                """, unsafe_allow_html=True)

            with col4:
                # Calculate mood trend
                if len(valid_scores) >= 2:
                    recent_avg = sum(
                        valid_scores[-3:]) / len(valid_scores[-3:])
                    older_avg = sum(
                        valid_scores[:3]) / min(len(valid_scores), 3)
                    trend = recent_avg - older_avg
                    trend_emoji = "📈" if trend > 5 else "📉" if trend < -5 else "➡️"
                    trend_text = "Improving" if trend > 5 else "Declining" if trend < -5 else "Stable"
                else:
                    trend_emoji = "➡️"
                    trend_text = "Track More"
                    trend = 0

                st.markdown(f"""
                <div class="stat-highlight">
                    <div style='font-size: 2rem;'>{trend_emoji}</div>
                    <div style='font-size: 0.9rem; opacity: 0.7;'>Trend</div>
                    <div style='font-size: 1.2rem; font-weight: 700; color: #667eea;'>{trend_text}</div>
                </div>
                """, unsafe_allow_html=True)

            # FIX #11: Mood insights with AI-like suggestions
            st.markdown("---")
            st.markdown("### 💡 Quick Insights")

            insights = []
            if avg_score >= 75:
                insights.append(
                    "🌟 You're doing great! Your average mood is excellent this period.")
            elif avg_score >= 50:
                insights.append(
                    "😊 Your mood is generally positive. Keep up the good work!")
            else:
                insights.append(
                    "💙 Remember, tough times don't last. Consider reaching out for support.")

            if len(valid_scores) >= 7:
                recent_trend = sum(
                    valid_scores[-3:]) / 3 - sum(valid_scores[-7:-3]) / 4
                if recent_trend > 10:
                    insights.append(
                        "📈 Great news! Your mood has been improving recently.")
                elif recent_trend < -10:
                    insights.append(
                        "💪 Your mood has dipped lately. Try some wellness activities!")

            if len([s for s in valid_scores if s >= 80]) >= len(valid_scores) * 0.5:
                insights.append(
                    "🎉 Over half your days were excellent! You're thriving!")

            for insight in insights:
                st.info(insight)

        # FIX #12: Recent mood notes with FIXED dark mode display
        st.markdown("---")
        st.markdown("### 📝 Recent Mood Notes")

        # Get recent entries with notes
        recent_with_notes = [m for m in mood_history[-10:]
                             if m.get("note") and m.get("note").strip()]

        if recent_with_notes:
            # Display in reverse chronological order (newest first)
            for entry in reversed(recent_with_notes):
                score = entry.get("score", 0)
                date = entry.get("date", "Unknown")
                note = entry.get("note", "")
                timestamp = entry.get("timestamp", "")

                # Determine emoji and color
                if score >= 80:
                    emoji = "😄"
                    border_color = "#FFD700"
                elif score >= 60:
                    emoji = "😊"
                    border_color = "#52B788"
                elif score >= 40:
                    emoji = "😐"
                    border_color = "#F7B801"
                else:
                    emoji = "😢"
                    border_color = "#FF6B35"

                # FIX #13: Card that works in ALL themes (light, dark, custom)
                st.markdown(f"""
                <div class="mood-note-card" style="border-left-color: {border_color};">
                    <div class="card-title">
                        <span class="mood-emoji">{emoji}</span>
                        <strong>{date}</strong> • {score}% • {timestamp}
                    </div>
                    <div class="card-note">"{note}"</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            # FIX #14: Beautiful empty state
            st.markdown("""
            <div class="empty-state">
                <div style='font-size: 3rem; margin-bottom: 15px;'>💭</div>
                <div style='font-size: 1.2rem; font-weight: 600; margin-bottom: 10px;'>No Notes Yet</div>
                <div style='opacity: 0.7;'>Add notes to your mood entries to track your thoughts and feelings over time!</div>
            </div>
            """, unsafe_allow_html=True)

    else:
        # FIX #15: Enhanced empty state for new users
        st.markdown("""
        <div class="empty-state">
            <div style='font-size: 4rem; margin-bottom: 20px;'>🌱</div>
            <h3 style='margin-bottom: 15px;'>Start Your Mood Journey</h3>
            <p style='opacity: 0.8; max-width: 600px; margin: 0 auto;'>
                Track your emotional wellbeing and discover patterns in your mood over time.
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Instructions with visual appeal
        st.markdown("---")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("""
            ### 🎯 How to Use
            1. **Rate your mood** using the slider (0-100)
            2. **Add a note** about what's affecting your mood
            3. **Click "Save Mood"** to log your entry
            4. **Watch your journey** unfold in the graph!
            """)

        with col2:
            st.markdown("""
            ### 💡 Why Track Your Mood?
            - 🔍 **Identify patterns** in your emotional wellbeing
            - 🎯 **Understand triggers** for high and low moods
            - 📈 **Monitor progress** in your mental health journey
            - 🌟 **Celebrate wins** and recognize growth
            """)

        st.markdown("---")
        st.info("💙 Tip: Try to log your mood daily for the most accurate insights!")


# ========== WELLNESS GAMES PAGE - FULLY FIXED & ENHANCED ==========
elif page == "🎮 Wellness Games":
    st.markdown("<h1 style='color: #667eea;'>🎮 Interactive Wellness Games</h1>",
                unsafe_allow_html=True)

    game_choice = st.selectbox("Choose a game", [
        "🌬️ Breathing Exercise",
        "🤔 Would You Rather",
        "🎨 Mood Color Match",
        "✨ Gratitude Spinner",
        "😊 Emoji Mood Match",
        "🌟 Affirmation Cards",
        "🎯 Mindfulness Quiz"
    ])

    # ========== BREATHING EXERCISE - NO CHANGES (Already working correctly) ==========
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
                    st.caption(
                        "💡 Press play ▶️ on the audio above before starting the exercise")
                else:
                    st.warning(
                        "Audio file is empty. Exercise will continue without music.")

            except Exception as e:
                st.warning(
                    f"Could not load audio. Exercise will continue without music.")
        else:
            st.info(f"🎵 {audio_description} (audio file not found)")
            st.caption(
                "💡 The breathing exercise works great even without music!")

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
                timer_container.markdown(
                    f"### 🔄 Cycle {cycle + 1} of {breathing_cycles}")

                # Breathe In (4 seconds)
                instruction_container.markdown(
                    "## 🌬️ **Breathe In Slowly...**")
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
                instruction_container.markdown(
                    "## 💨 **Breathe Out Gently...**")
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

            # Save exercise data with UTF-8 encoding
            games_data = load_json(GAMES_FILE, [])
            games_data.append({
                "game": "Breathing Exercise",
                "mood": mood_type,
                "date": datetime.today().strftime("%Y-%m-%d"),
                "time": datetime.now().strftime("%H:%M:%S")
            })
            save_json(GAMES_FILE, games_data)

            # Award badge
           # ===== BREATHING EXERCISE BADGES =====
            breathing_sessions = [g for g in games_data if g.get(
                "game") == "Breathing Exercise"]
            session_count = len(breathing_sessions)

            badge_awarded = False

            # Award milestone badges
            if session_count >= 1:
                if award_badge("Calm Beginner", "🧘"):
                    badge_awarded = True

            if session_count >= 5:
                if award_badge("Breathing Pro", "🌬️"):
                    badge_awarded = True

            if session_count >= 10:
                if award_badge("Zen Master", "🌊"):
                    badge_awarded = True

            if session_count >= 25:
                if award_badge("Mindfulness Guru", "✨"):
                    badge_awarded = True

            # Show celebration if badge was awarded
            if badge_awarded:
                st.balloons()
                st.toast("🏆 New Badge Unlocked!")

            # Show progress message
            if session_count > 1:
                st.info(
                    f"🔥 You've completed {session_count} breathing sessions! Keep it up!")
            # ===== END BREATHING BADGES =====

    # ========== WOULD YOU RATHER - NO CHANGES (Already working correctly) ==========
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

        choice = st.radio(
            "Choose one:", st.session_state.wyr_current, key="wyr_radio")

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

            # Save game with UTF-8 encoding
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

    # ========== MOOD COLOR MATCH - FIXED: Message isolation ==========
    # FIX #1: Removed the markdown message that was appearing in all games
    # The message is now ONLY within this elif block
    elif game_choice == "🎨 Mood Color Match":
        st.subheader("🎨 Mood Color Match")

        # THIS MESSAGE NOW ONLY APPEARS IN MOOD COLOR MATCH GAME
        st.markdown("""
        <p style='font-size: 1.1rem; color: #666; margin-bottom: 1.5rem;'>
            <strong>Click on a color that matches your current mood!</strong> Each color represents different emotions and energy levels.
        </p>
        """, unsafe_allow_html=True)

        mood_colors = {
            "Red": "🔥 Passionate and energized!",
            "Blue": "💙 Calm and reflective.",
            "Yellow": "🌟 Cheerful and bright!",
            "Green": "🍃 Balanced and peaceful.",
            "Purple": "💜 Creative and thoughtful!",
            "Orange": "🧡 Energetic and enthusiastic!",
            "Pink": "💗 Loving and compassionate!",
            "Turquoise": "💎 Refreshed and inspired!"
        }

        color_map = {
            "Red": "#FF6B6B",
            "Blue": "#4ECDC4",
            "Yellow": "#FFD93D",
            "Green": "#52B788",
            "Purple": "#AA96DA",
            "Orange": "#FF9F45",
            "Pink": "#FF8FB1",
            "Turquoise": "#00CED1"
        }

        bg_colors = {
            "Red": "#FFE5E5",
            "Blue": "#E0F7FA",
            "Yellow": "#FFF9E5",
            "Green": "#E8F5E9",
            "Purple": "#F3E5F5",
            "Orange": "#FFF3E0",
            "Pink": "#FCE4EC",
            "Turquoise": "#E0F7FA"
        }

        # Display color cards in grid
        st.markdown("""
        <style>
            .color-card {
                padding: 1.8rem 1rem;
                border-radius: 15px;
                text-align: center;
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                cursor: pointer;
                transition: all 0.3s ease;
                margin-bottom: 1rem;
            }
            .color-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 8px 20px rgba(0,0,0,0.2);
            }
        </style>
        """, unsafe_allow_html=True)

        col1, col2, col3, col4 = st.columns(4)
        colors_list = list(mood_colors.keys())
        selected_color = None

        for i, color in enumerate(colors_list):
            with [col1, col2, col3, col4][i % 4]:
                color_hex = color_map[color]
                bg_color = bg_colors[color]

                # Display color card
                st.markdown(f"""
                <div class="color-card" style='
                    background: linear-gradient(135deg, {bg_color} 0%, #ffffff 100%);
                    border: 3px solid {color_hex};
                '>
                    <div style='font-size: 2.5rem; color: {color_hex}; margin-bottom: 0.5rem;'>⬤</div>
                    <div style='font-weight: bold; font-size: 1.2rem; color: {color_hex};'>{color}</div>
                </div>
                """, unsafe_allow_html=True)

                # Simple button below card
                if st.button(f"Select", key=f"color_btn_{color}", use_container_width=True):
                    selected_color = color

        # Show result with beautiful animation
        if selected_color:
            result_color = color_map[selected_color]
            result_bg = bg_colors[selected_color]

            st.markdown(f"""
            <style>
                @keyframes resultFadeIn {{
                    from {{ opacity: 0; transform: scale(0.9); }}
                    to {{ opacity: 1; transform: scale(1); }}
                }}
                .result-card {{
                    animation: resultFadeIn 0.5s ease-out;
                }}
            </style>
            <div class="result-card" style='
                background: linear-gradient(135deg, {result_bg} 0%, #ffffff 100%);
                padding: 2.5rem;
                border-radius: 20px;
                border-left: 6px solid {result_color};
                box-shadow: 0 8px 24px rgba(0,0,0,0.15);
                margin-top: 2rem;
            '>
                <div style='display: flex; align-items: center; gap: 1rem;'>
                    <div style='font-size: 3rem;'>⬤</div>
                    <div>
                        <h3 style='color: {result_color}; font-size: 1.8rem; margin: 0 0 0.5rem 0;'>
                            You're feeling <span style='font-weight:bold; text-decoration: underline;'>{selected_color}</span>!
                        </h3>
                        <p style='font-size: 1.3rem; color: #333; line-height: 1.6; margin: 0;'>
                            {mood_colors[selected_color]}
                        </p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.balloons()

            # FIX #2: UTF-8 encoding for saving game data
            try:
                games_data = load_json(GAMES_FILE, [])
            except:
                games_data = []

            games_data.append({
                "game": "Mood Color Match",
                "color": selected_color,
                "message": mood_colors[selected_color],
                "date": datetime.today().strftime("%Y-%m-%d"),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

            # IMPORTANT: UTF-8 encoding to handle emojis
            with open(GAMES_FILE, "w", encoding="utf-8") as f:
                json.dump(games_data, f, indent=4, ensure_ascii=False)

            # Mood suggestion based on color
            st.markdown("---")
            st.markdown("### 💡 What to do with this mood?")

            suggestions = {
                "Red": "🏃‍♀️ **Channel that energy!** Try a quick workout, dance session, or tackle a challenging task.",
                "Blue": "🧘‍♂️ **Embrace the calm.** Perfect time for meditation, reading, or journaling your thoughts.",
                "Yellow": "☀️ **Spread your joy!** Share a smile, call a friend, or do something creative.",
                "Green": "🌿 **Stay balanced.** A walk in nature or breathing exercises would be perfect right now.",
                "Purple": "🎨 **Get creative!** Paint, write, play music, or explore a new hobby.",
                "Orange": "🎉 **Ride the enthusiasm!** Start that project you've been planning or learn something new.",
                "Pink": "💌 **Share the love.** Reach out to someone you care about or practice self-compassion.",
                "Turquoise": "✨ **Stay inspired!** Watch something motivational, set new goals, or organize your space."
            }

            st.info(suggestions.get(selected_color,
                    "Keep embracing your current mood! 🌈"))

            # Show color psychology
            with st.expander("🧠 Color Psychology - Learn More"):
                psychology = {
                    "Red": "Red is associated with passion, energy, and action. It can increase heart rate and create urgency.",
                    "Blue": "Blue promotes calmness, trust, and stability. It's known to lower blood pressure and reduce anxiety.",
                    "Yellow": "Yellow stimulates mental activity and generates happiness. It's the color of optimism and joy.",
                    "Green": "Green represents balance, growth, and harmony. It's restful for the eyes and promotes relaxation.",
                    "Purple": "Purple combines the calm of blue and energy of red. It's linked to creativity and spirituality.",
                    "Orange": "Orange radiates warmth and enthusiasm. It encourages social interaction and confidence.",
                    "Pink": "Pink is calming and associated with love, kindness, and compassion. It reduces aggression.",
                    "Turquoise": "Turquoise combines the calming effects of blue with the renewal qualities of green. It promotes clarity."
                }
                st.markdown(f"**{psychology.get(selected_color, '')}**")

    # ========== GRATITUDE SPINNER - FIXED: UTF-8 encoding for save ==========
    elif game_choice == "✨ Gratitude Spinner":
        st.subheader("✨ Gratitude Spinner")
        st.markdown(
            "**Spin the wheel to discover what you're grateful for today!**")

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
            remaining_questions = [
                q for q in gratitude_questions if q not in st.session_state.gratitude_shown_questions]
            if not remaining_questions:
                st.session_state.gratitude_shown_questions = []
                remaining_questions = gratitude_questions

            st.session_state.gratitude_question = random.choice(
                remaining_questions)
            st.session_state.gratitude_shown_questions.append(
                st.session_state.gratitude_question)
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
            progress = len(
                st.session_state.gratitude_shown_questions) / len(gratitude_questions)
            st.progress(progress)
            st.markdown(f"<p style='text-align: center; color: #666; margin-top: 10px;'>✨ Spins: {st.session_state.gratitude_spin_count} | Questions explored: {len(st.session_state.gratitude_shown_questions)}/{len(gratitude_questions)}</p>",
                        unsafe_allow_html=True)

        # Reflection section
        if st.session_state.gratitude_question and not st.session_state.gratitude_spinning:
            st.markdown("---")
            st.markdown("### 📝 Your Reflection")
            st.markdown(
                "*Take a moment to reflect on this question and write your thoughts...*")

            gratitude_response = st.text_area("",
                                              placeholder="Share what you're grateful for...",
                                              key=f"gratitude_response_{st.session_state.gratitude_spin_count}",
                                              height=120)

            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                if st.button("💾 Save My Reflection", key=f"save_gratitude_{st.session_state.gratitude_spin_count}",
                             use_container_width=True):
                    if gratitude_response.strip():
                        # FIX #3: UTF-8 encoding when loading JSON
                        try:
                            with open(GAMES_FILE, "r", encoding="utf-8") as f:
                                games_data = json.load(f)
                        except (FileNotFoundError, json.JSONDecodeError):
                            games_data = []

                        games_data.append({
                            "game": "Gratitude Spinner",
                            "question": st.session_state.gratitude_question,
                            "response": gratitude_response.strip(),
                            "date": datetime.today().strftime("%Y-%m-%d")
                        })

                        # FIX #3: UTF-8 encoding when saving JSON (prevents UnicodeDecodeError)
                        with open(GAMES_FILE, "w", encoding="utf-8") as f:
                            json.dump(games_data, f, indent=4,
                                      ensure_ascii=False)

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

                        # ===== GRATITUDE JOURNAL BADGES =====
                        gratitude_count = len(gratitude_data)
                        badge_awarded = False

                        if gratitude_count >= 1:
                            if award_badge("Grateful Heart", "💖"):
                                badge_awarded = True

                        if gratitude_count >= 7:
                            if award_badge("Gratitude Week", "🌸"):
                                badge_awarded = True

                        if gratitude_count >= 30:
                            if award_badge("Positivity Pro", "✨"):
                                badge_awarded = True

                        if gratitude_count >= 100:
                            if award_badge("Gratitude Master", "🌟"):
                                badge_awarded = True

                        # Show celebration
                        if badge_awarded:
                            st.balloons()
                            st.toast("🏆 New Badge Unlocked!")
                        # ===== END GRATITUDE BADGES =====

                    else:
                        st.warning(
                            "💭 Please write your reflection before saving!")    # ========== EMOJI MOOD MATCH - NO CHANGES (Already working correctly) ==========
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
            st.session_state.emoji_questions = random.sample(
                emoji_mood_pairs, 5)
            st.session_state.emoji_answered = False
            st.session_state.emoji_selected = None
            st.session_state.emoji_options = []

        total_rounds = 5

        # Game in progress
        if st.session_state.emoji_round < total_rounds:
            current_emoji, correct_mood = st.session_state.emoji_questions[
                st.session_state.emoji_round]

            # Progress indicator with visual bar
            progress = (st.session_state.emoji_round) / total_rounds
            st.progress(progress)
            st.markdown(
                f"**Round {st.session_state.emoji_round + 1}/{total_rounds}** | 🏆 Score: {st.session_state.emoji_score}")

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
                options = [correct_mood] + \
                    random.sample(wrong_moods, min(3, len(wrong_moods)))
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
                    st.success(
                        f"✅ **Correct!** {current_emoji} represents {correct_mood}!")
                else:
                    st.error(
                        f"❌ **Not quite!** {current_emoji} represents **{correct_mood}**")

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
            score_percentage = (
                st.session_state.emoji_score / total_rounds) * 100
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
                st.markdown(
                    "### 😊 **Excellent work!** You know your emojis well!")
            elif st.session_state.emoji_score >= 3:
                st.markdown("### 👍 **Good job!** You're getting there!")
            else:
                st.markdown(
                    "### 💪 **Keep practicing!** You'll improve with each game!")

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

    # ========== AFFIRMATION CARDS - ENHANCED UX WITH ANIMATIONS ==========
    # FIX #4: Complete redesign with card shuffle, flip animations, and beautiful visuals
    elif game_choice == "🌟 Affirmation Cards":
        st.subheader("🌟 Positive Affirmation Cards")
        st.markdown(
            "**Draw a beautiful affirmation card to brighten your day!**")

        affirmations = [
            ("💖", "You are enough, just as you are.", "#FF6B9D"),
            ("🌈", "This too shall pass, better days are ahead.", "#C44569"),
            ("🌟", "Your kindness makes the world brighter.", "#FFA801"),
            ("🔥", "You are stronger than your struggles.", "#FF6348"),
            ("🌻", "Every day is a fresh start.", "#FFD93D"),
            ("💪", "You have the power to create change.", "#6C5CE7"),
            ("🌸", "You deserve love and happiness.", "#FD79A8"),
            ("✨", "Your potential is limitless.", "#A29BFE"),
            ("🦋", "You are growing and evolving beautifully.", "#74B9FF"),
            ("🌊", "Peace flows through you effortlessly.", "#00CEC9"),
            ("🎯", "You are capable of achieving your dreams.", "#0984E3"),
            ("💫", "Your presence matters to the world.", "#6C5CE7")
        ]

        # Initialize session state for card game
        if "affirmation_drawn" not in st.session_state:
            st.session_state.affirmation_drawn = False
            st.session_state.current_affirmation = None
            st.session_state.card_flipped = False

        # Card deck display (before drawing)
        if not st.session_state.affirmation_drawn:
            st.markdown("""
            <style>
                @keyframes cardFloat {
                    0%, 100% { transform: translateY(0px) rotate(-2deg); }
                    50% { transform: translateY(-10px) rotate(2deg); }
                }
                
                .card-deck {
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    margin: 40px 0;
                    perspective: 1000px;
                }
                
                .card-stack {
                    position: relative;
                    width: 280px;
                    height: 380px;
                }
                
                .deck-card {
                    position: absolute;
                    width: 280px;
                    height: 380px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    border-radius: 20px;
                    box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    cursor: pointer;
                    transition: all 0.3s ease;
                }
                
                .deck-card:nth-child(1) {
                    transform: rotate(-3deg) translateY(0px);
                    z-index: 3;
                    animation: cardFloat 3s ease-in-out infinite;
                }
                
                .deck-card:nth-child(2) {
                    transform: rotate(2deg) translateY(8px);
                    z-index: 2;
                    opacity: 0.8;
                }
                
                .deck-card:nth-child(3) {
                    transform: rotate(-1deg) translateY(16px);
                    z-index: 1;
                    opacity: 0.6;
                }
                
                .card-pattern {
                    font-size: 4rem;
                    margin-bottom: 20px;
                    filter: drop-shadow(0 5px 15px rgba(255,255,255,0.3));
                }
                
                .card-text {
                    color: white;
                    font-size: 1.8rem;
                    font-weight: 700;
                    text-shadow: 2px 2px 8px rgba(0,0,0,0.3);
                }
            </style>
            
            <div class="card-deck">
                <div class="card-stack">
                    <div class="deck-card">
                        <div class="card-pattern">🌟</div>
                        <div class="card-text">Affirmation Deck</div>
                    </div>
                    <div class="deck-card"></div>
                    <div class="deck-card"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("<p style='text-align: center; color: #666; font-size: 1.1rem; margin: 20px 0;'>✨ Click the button below to draw your card ✨</p>", unsafe_allow_html=True)

            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("🎴 Draw Your Card", type="primary", use_container_width=True, key="draw_affirmation"):
                    st.session_state.current_affirmation = random.choice(
                        affirmations)
                    st.session_state.affirmation_drawn = True
                    st.session_state.card_flipped = False
                    st.rerun()

        # Card drawn - show with flip animation
        else:
            emoji, message, color = st.session_state.current_affirmation

            if not st.session_state.card_flipped:
                # Trigger flip animation
                st.markdown("""
                <style>
                    @keyframes flipCard {
                        0% { transform: rotateY(0deg) scale(1); opacity: 0; }
                        50% { transform: rotateY(90deg) scale(1.1); opacity: 1; }
                        100% { transform: rotateY(0deg) scale(1); opacity: 1; }
                    }
                    
                    .drawn-card {
                        animation: flipCard 1s ease-out;
                    }
                </style>
                """, unsafe_allow_html=True)
                st.session_state.card_flipped = True
                time.sleep(0.5)

            # Display the drawn card with beautiful styling
            st.markdown(f"""
            <style>
                @keyframes glow {{
                    0%, 100% {{ box-shadow: 0 0 20px {color}40, 0 20px 60px rgba(0,0,0,0.3); }}
                    50% {{ box-shadow: 0 0 40px {color}80, 0 20px 60px rgba(0,0,0,0.3); }}
                }}
                
                @keyframes floatCard {{
                    0%, 100% {{ transform: translateY(0px); }}
                    50% {{ transform: translateY(-15px); }}
                }}
                
                .affirmation-card {{
                    background: linear-gradient(135deg, {color} 0%, {color}dd 100%);
                    border-radius: 25px;
                    padding: 60px 40px;
                    margin: 40px auto;
                    max-width: 500px;
                    text-align: center;
                    animation: glow 2s ease-in-out infinite, floatCard 4s ease-in-out infinite;
                    position: relative;
                    overflow: hidden;
                }}
                
                .affirmation-card::before {{
                    content: '';
                    position: absolute;
                    top: -50%;
                    left: -50%;
                    width: 200%;
                    height: 200%;
                    background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
                    animation: rotate 20s linear infinite;
                }}
                
                @keyframes rotate {{
                    from {{ transform: rotate(0deg); }}
                    to {{ transform: rotate(360deg); }}
                }}
                
                .card-emoji {{
                    font-size: 5rem;
                    margin-bottom: 30px;
                    display: block;
                    filter: drop-shadow(0 10px 20px rgba(0,0,0,0.2));
                    position: relative;
                    z-index: 1;
                }}
                
                .card-message {{
                    color: white;
                    font-size: 2rem;
                    font-weight: 600;
                    line-height: 1.6;
                    text-shadow: 3px 3px 10px rgba(0,0,0,0.3);
                    position: relative;
                    z-index: 1;
                }}
                
                .sparkles {{
                    font-size: 1.5rem;
                    margin: 30px 0 20px 0;
                    opacity: 0.9;
                }}
            </style>
            
            <div class="affirmation-card drawn-card">
                <span class="card-emoji">{emoji}</span>
                <p class="card-message">{message}</p>
                <div class="sparkles">✨ ⭐ ✨</div>
            </div>
            """, unsafe_allow_html=True)

            st.balloons()

            # Action buttons with nice spacing
            st.markdown("<div style='height: 30px;'></div>",
                        unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 Draw Another Card", type="secondary", use_container_width=True):
                    st.session_state.affirmation_drawn = False
                    st.session_state.card_flipped = False
                    st.rerun()

            with col2:
                if st.button("💾 Save This Affirmation", type="primary", use_container_width=True):
                    # Save with UTF-8 encoding
                    try:
                        with open(GAMES_FILE, "r", encoding="utf-8") as f:
                            games_data = json.load(f)
                    except (FileNotFoundError, json.JSONDecodeError):
                        games_data = []

                    games_data.append({
                        "game": "Affirmation Cards",
                        "emoji": emoji,
                        "message": message,
                        "color": color,
                        "date": datetime.today().strftime("%Y-%m-%d"),
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })

                    with open(GAMES_FILE, "w", encoding="utf-8") as f:
                        json.dump(games_data, f, indent=4, ensure_ascii=False)

                    st.success("💖 Affirmation saved to your journal!")

                    if award_badge("Positive Thinker", "🌟"):
                        st.info("🏆 Badge Unlocked: Positive Thinker!")

            # Show additional encouragement
            st.markdown("---")
            st.markdown("""
            <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                        padding: 25px; border-radius: 15px; text-align: center;'>
                <p style='color: white; font-size: 1.2rem; margin: 0; font-weight: 500;'>
                    💝 Carry this affirmation with you today. You've got this! 💝
                </p>
            </div>
            """, unsafe_allow_html=True)

    # ========== MINDFULNESS QUIZ - NO CHANGES (Already working correctly) ==========
    elif game_choice == "🎯 Mindfulness Quiz":
        st.subheader("🎯 Mindfulness Self-Assessment")
        st.markdown(
            "**Reflect on your current state of mindfulness and well-being.**")

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
            progress = (st.session_state.mindful_quiz_index + 1) / \
                len(questions)
            st.progress(progress)
            st.markdown(
                f"**Question {st.session_state.mindful_quiz_index + 1}/{len(questions)}**")

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
    st.markdown("<h1 style='color: #667eea;'>🍎 Nutrition Tracker</h1>",
                unsafe_allow_html=True)

    # Load nutrition data
    # ✅ FIXED: Ensure nutrition_data is always a list
    nutrition_data = load_json(NUTRITION_FILE, [])
    if not isinstance(nutrition_data, list):
        nutrition_data = []  # Reset to empty list if corrupted

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
        meal_type = st.selectbox("Meal Type", [
                                 "Breakfast", "Lunch", "Dinner", "Snack", "Beverage"], key="nutrition_meal_type")
        food_item = st.text_input(
            "Food item", placeholder="e.g., vada pav, biryani, banana", key="nutrition_food_input")

        # Auto-suggest as user types
        if food_item:
            suggestions = [k for k in ENHANCED_CALORIE_DB.keys()
                           if food_item.lower() in k]
            if suggestions and len(suggestions) <= 10:
                st.info(f"💡 Suggestions: {', '.join(suggestions[:5])}")

    with col2:
        portion = st.selectbox(
            "Portion Size", ["Small", "Medium", "Large"], key="nutrition_portion")
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
            protein_val = estimated_data['protein'] * \
                portion_multiplier[portion]
            carbs_val = estimated_data['carbs'] * portion_multiplier[portion]
            fat_val = estimated_data['fat'] * portion_multiplier[portion]

            st.success(
                f"✅ Found in database: ~{adjusted_cal} kcal ({portion} portion)")

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
            st.warning(
                "⚠️ Item not found in database. Please add custom entry below.")
            calories = 0

    # Custom entry option
    with st.expander("➕ Add Custom Food Item"):
        st.markdown("**Didn't find your food? Add it manually:**")
        custom_calories = st.number_input("Calories (kcal)", min_value=0, value=int(
            st.session_state.nutrition_calories), step=10, key="nutrition_custom_cal")
        custom_protein = st.number_input("Protein (g)", min_value=0.0, value=float(
            protein_val), step=0.5, key="nutrition_custom_protein")
        custom_carbs = st.number_input("Carbs (g)", min_value=0.0, value=float(
            carbs_val), step=1.0, key="nutrition_custom_carbs")
        custom_fat = st.number_input("Fat (g)", min_value=0.0, value=float(
            fat_val), step=0.5, key="nutrition_custom_fat")

        use_custom = st.checkbox(
            "Use custom values instead of database values", key="nutrition_use_custom")

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
                    "timestamp": get_ist_time()  # ✅ FIXED - Use IST helper
                }

                # ✅ FIXED: Ensure nutrition_data is a list before appending
                if not isinstance(nutrition_data, list):
                    nutrition_data = []

                nutrition_data.append(new_entry)
                save_json(NUTRITION_FILE, nutrition_data)

                st.success(
                    f"✅ {meal_type} logged: {food_item} ({calories} kcal)")

                if award_badge("Nutrition Tracker", "🍎"):
                    st.balloons()

                # Clear form
                st.session_state.nutrition_calories = 0

                time.sleep(0.5)
                st.rerun()
            else:
                st.error(
                    "⚠️ Please enter a food item and ensure calories are calculated")

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
            meal_breakdown[mtype] = meal_breakdown.get(
                mtype, 0) + meal.get("calories", 0)

        # Pie chart
        if meal_breakdown:
            fig = go.Figure(data=[go.Pie(
                labels=list(meal_breakdown.keys()),
                values=list(meal_breakdown.values()),
                hole=0.4,
                marker=dict(colors=['#667eea', '#52B788',
                            '#F7B801', '#FF6B35', '#9D4EDD'])
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
            macro_bar.update_layout(
                title="Macros (grams)", height=300, showlegend=False)
            st.plotly_chart(macro_bar, use_container_width=True)

        # Meal list
        st.markdown("### 🥄 Meals Logged Today")
        for idx, meal in enumerate(today_meals, 1):
            with st.container():
                # Create a nice card using columns
                col1, col2 = st.columns([4, 1])
                with col1:
                    # Meal header
                    st.markdown(
                        f"**#{idx} - {meal['meal_type']}** 🕐 {meal.get('timestamp', '')}")

                    # Meal description (larger text)
                    st.markdown(f"### {meal['description']}")

                    st.markdown(f"""
                     🔥 **{meal['calories']} kcal** • 
                     🍖 {meal.get('protein', 0):.1f}g Protein • 
                     🍞 {meal.get('carbs', 0):.1f}g Carbs • 
                     🥑 {meal.get('fat', 0):.1f}g Fat
                     """)

                with col2:
                    # Optional: Add delete button if you want
                    st.write("")  # Spacer
                    st.write("")  # Spacer
                    if st.button("🗑️", key=f"delete_meal_{idx}", help="Delete this meal"):
                        nutrition_data.remove(meal)
                        save_json(NUTRITION_FILE, nutrition_data)
                        st.rerun()

                # Divider between meals
                st.divider()

        # Weekly trend
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

        # Portion size
        st.caption(f"📏 Portion: {meal.get('portion', 'Medium')}")

        # Nutrition tips
        st.markdown("### 💡 Nutrition Insights")
        if total_calories < 1200:
            st.warning(
                "⚠️ Your calorie intake today is quite low. Make sure you're eating enough!")
        elif total_calories > 3000:
            st.info(
                "💡 High calorie intake today. Consider balanced portions in future meals.")
        else:
            st.success("✅ Good calorie range for the day!")

        # Protein check
        if total_protein < 50:
            st.info(
                "🍖 Try adding more protein-rich foods like eggs, dal, paneer, or chicken.")
        elif total_protein > 150:
            st.info(
                "🍖 High protein intake! Make sure you're balancing with other nutrients.")

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
    st.markdown("<h1 style='color: #667eea;'>💧 Water Intake Tracker</h1>",
                unsafe_allow_html=True)

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
                st.markdown(
                    "<p style='font-size: 2.5rem; text-align: center;'>💧</p>", unsafe_allow_html=True)
            else:
                st.markdown(
                    "<p style='font-size: 2.5rem; text-align: center; opacity: 0.3;'>🫙</p>", unsafe_allow_html=True)

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
        day_entry = next(
            (w for w in water_data if w.get("date") == date), {"glasses": 0})
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
        st.info(
            f"💧 Keep it up! {goal - current_glasses} more glasses to reach your goal.")

# ========== SLEEP TRACKER - FULLY ENHANCED & WORKING ==========
elif page == "😴 Sleep":
    st.markdown("<h1 style='color: #667eea;'>😴 Sleep Tracker</h1>",
                unsafe_allow_html=True)

    sleep_data = load_json(SLEEP_FILE, [])
    today = datetime.today().strftime("%Y-%m-%d")

    # ========== SECTION 1: LOG SLEEP ==========
    st.markdown("### 🌙 Log Your Sleep")
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        sleep_time = st.time_input(
            "🛏️ Bedtime", value=None, key="sleep_bedtime", help="What time did you go to bed?")
        wake_time = st.time_input(
            "⏰ Wake Time", value=None, key="sleep_waketime", help="What time did you wake up?")

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

            # Award badges and track if any new ones were unlocked
            badge_awarded = False

            if duration >= 7:
                if award_badge("Sleep Champion", "😴"):
                    badge_awarded = True

            if len(sleep_data) >= 5:
                if award_badge("Consistent Sleeper", "🌙"):
                    badge_awarded = True

            if duration >= 8:
                if award_badge("Sweet Dreams", "⭐"):
                    badge_awarded = True

            # Only show celebration once if any badges were awarded
            if badge_awarded:
                st.balloons()
                st.toast("🏆 New Badge Unlocked!")

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
            day_data = next(
                (s for s in sleep_data if s.get("date") == date), None)
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
            st.metric("📊 Weekly Average",
                      f"{avg_duration:.1f} hrs", help="Average sleep over last 7 days")
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

        # Generate and display insights
        insights = get_smart_sleep_insights(sleep_data)
        for insight in insights:
            st.info(insight)

        # ========== SECTION 5: DETAILED SLEEP LOGS ==========
        st.markdown("---")
        st.markdown("### 📋 Recent Sleep Logs")

        recent_entries = [s for s in sleep_data if s.get("date")][-5:]

        if recent_entries:
            for entry in reversed(recent_entries):
                quality = entry.get("quality", "Good")
                duration = entry.get("duration", 0)
                date = entry.get("date", "Unknown")
                sleep_time = entry.get("sleep_time", "N/A")
                wake_time = entry.get("wake_time", "N/A")
                has_dreams = entry.get("dreams", False)

                # Quality emoji
                quality_emojis = {
                    "Poor": "😴",
                    "Fair": "😐",
                    "Good": "😊",
                    "Great": "😄",
                    "Excellent": "⭐"
                }
                quality_emoji = quality_emojis.get(quality, "😴")

                # Duration color and label
                if duration >= 8:
                    duration_color = "#52B788"
                    duration_label = "Excellent"
                    duration_icon = "🌟"
                elif duration >= 6:
                    duration_color = "#F7B801"
                    duration_label = "Good"
                    duration_icon = "👍"
                else:
                    duration_color = "#FF6B35"
                    duration_label = "Needs Attention"
                    duration_icon = "⚠️"

                dream_text = " | 💭 Dreams" if has_dreams else ""

                with st.container():
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"**📅 {date}** {quality_emoji}")
                        st.markdown(f"🛏️ {sleep_time} → ⏰ {wake_time}")
                        st.markdown(f"**Quality:** {quality}{dream_text}")
                    with col2:
                        st.markdown(
                            f"<h2 style='color:{duration_color}; text-align:center; margin:0;'>{duration}h</h2>", unsafe_allow_html=True)
                        st.markdown(
                            f"<p style='text-align:center; color:{duration_color}; font-weight:600; margin:5px 0;'>{duration_icon} {duration_label}</p>", unsafe_allow_html=True)
                    st.markdown("---")
    else:
        st.info("📭 No sleep logs yet. Start tracking to see your history!")

        st.markdown("**💡 Quick Start Guide:**")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("**1️⃣ Log Sleep**")
            st.write("Fill in your sleep times above")
        with col2:
            st.markdown("**2️⃣ Rate Quality**")
            st.write("Choose how well you slept")
        with col3:
            st.markdown("**3️⃣ Track Progress**")
            st.write("See your sleep patterns grow")


# ========== MENTAL HEALTH HELPLINES - VERIFIED LINKS ==========

elif page == "📞 Helplines":
    st.markdown("<h1 style='color: #667eea;'>📞 Mental Health Helplines</h1>",
                unsafe_allow_html=True)

    # Safety warning
    st.error("⚠ *If you are in crisis, please contact local emergency services immediately.\n\n🚨 India Emergency: **112* | USA: *911* | UK: *999* | Australia: *000*")

    # 🌈 Custom CSS for beautiful pastel design & readability with theme support
    st.markdown("""
    <style>
        body {
            background: linear-gradient(to bottom right, #f8faff, #eef2ff);
        }
        .helpline-card {
            background-color: var(--background-color, #f7f8ff);
            color: var(--text-color, #222);
            padding: 15px 20px;
            border-radius: 16px;
            margin-bottom: 15px;
            box-shadow: 0 4px 10px rgba(102, 126, 234, 0.15);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
            border: 1px solid rgba(102, 126, 234, 0.1);
        }
        .helpline-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 6px 14px rgba(102, 126, 234, 0.25);
        }
        .helpline-card h3 {
            color: var(--primary-color, #4f46e5) !important;
            font-size: 1.15rem;
            margin-bottom: 5px;
            font-weight: 600;
        }
        .helpline-card p {
            color: var(--text-color, #222) !important;
            margin: 5px 0;
            line-height: 1.6;
        }
        .helpline-card strong {
            color: var(--text-color, #333) !important;
            font-weight: 600;
        }
        .helpline-card a {
            color: var(--link-color, #2563eb) !important;
            text-decoration: none;
            font-weight: 500;
        }
        .helpline-card a:hover {
            text-decoration: underline;
            color: var(--link-hover-color, #1e40af) !important;
        }
        
        /* Dark theme support */
        @media (prefers-color-scheme: dark) {
            .helpline-card {
                background-color: rgba(30, 30, 40, 0.8);
                color: #e0e0e0;
                border: 1px solid rgba(102, 126, 234, 0.3);
            }
            .helpline-card h3 {
                color: #8b9cfa !important;
            }
            .helpline-card p {
                color: #e0e0e0 !important;
            }
            .helpline-card strong {
                color: #f0f0f0 !important;
            }
            .helpline-card a {
                color: #6b8afd !important;
            }
            .helpline-card a:hover {
                color: #8b9cfa !important;
            }
        }
        
        /* Streamlit theme color inheritance */
        [data-testid="stMarkdownContainer"] .helpline-card {
            background-color: var(--background-color);
            color: var(--text-color);
        }
        
        hr {
            border: 0;
            height: 1px;
            background: var(--secondary-background-color, #ddd);
            margin: 1rem 0;
        }
        label {
            color: var(--text-color, #333) !important;
            font-weight: 600;
        }
        .stSelectbox label {
            color: var(--text-color, #444) !important;
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Complete helplines database with VERIFIED working websites
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
            },
            {
                "name": "NIMHANS Helpline",
                "number": "080-46110007",
                "hours": "Mon-Sat 9AM-5PM",
                "website": "nimhans.ac.in"
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
                    "name": "SAHAI - Suicide Prevention Helpline",
                    "number": "080-25497777 / 9886444075",
                    "hours": "10AM-5:30PM, Mon-Sat",
                    "website": "Contact via phone"
                },
                {
                    "name": "NIMHANS Centre for Well-being",
                    "number": "080-46110007 / 080-26685948",
                    "hours": "Mon-Sat 9AM-5PM",
                    "website": "nimhans.ac.in"
                },
                {
                    "name": "Mitram Foundation",
                    "number": "080-25722573 / 9019708133",
                    "hours": "10AM-4PM Daily",
                    "website": "Contact via phone"
                }
            ],
            "Tamil Nadu": [
                {
                    "name": "Sneha Foundation Chennai",
                    "number": "044-24640050 / 044-24640060",
                    "hours": "24/7",
                    "website": "snehaindia.org"
                }
            ],

            "West Bengal": [
                {
                    "name": "Lifeline Foundation Kolkata",
                    "number": "033-24637401 / 033-24637432",
                    "hours": "10AM-6PM Daily",
                    "website": "Contact via phone for support"
                }
            ],
            "Gujarat": [
                {
                    "name": "Sanjivani Society",
                    "number": "079-26300222",
                    "hours": "24/7",
                    "website": "Contact via phone for support"
                }
            ],
            "Telangana": [
                {
                    "name": "Roshni Trust",
                    "number": "040-66202000 / 040-66202001",
                    "hours": "11AM-9PM, Mon-Sat",
                    "website": "Contact via phone for support"
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
                    "name": "SAHAI Bangalore",
                    "number": "080-25497777 / 9886444075",
                    "hours": "10AM-5:30PM, Mon-Sat",
                    "website":  "Contact via phone"
                },
                {
                    "name": "NIMHANS Centre for Well-being",
                    "number": "080-46110007 / 080-26685948",
                    "hours": "Mon-Sat 9AM-5PM",
                    "website": "nimhans.ac.in"
                },
                {
                    "name": "Mitram Foundation",
                    "number": "080-25722573 / 9019708133",
                    "hours": "10AM-4PM Daily",
                    "website": "Contact via phone"
                }
            ],
            "Chennai": [
                {
                    "name": "Sneha Chennai",
                    "number": "044-24640050 / 044-24640060",
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
                    "name": "Fortis Mental Health Helpline",
                    "number": "8376804102",
                    "hours": "24/7",
                    "website": "Contact via phone"


                }
            ],
            "Kolkata": [
                {
                    "name": "Lifeline Foundation Kolkata",
                    "number": "033-24637401 / 033-24637432",
                    "hours": "10AM-6PM Daily",
                    "website": "Contact via phone for support"
                }
            ],
            "Hyderabad": [
                {
                    "name": "Roshni Trust Hyderabad",
                    "number": "040-66202000 / 040-66202001",
                    "hours": "11AM-9PM, Mon-Sat",
                    "website": "Contact via phone for support"
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
            if h['website'].startswith('Contact'):
                website_html = f"<p><strong>🔗 Info:</strong> {h['website']}</p>"
            else:
                website_html = f"<p><strong>🔗 Website:</strong> <a href='https://{h['website']}' target='_blank'>https://{h['website']}</a></p>"

            st.markdown(f"""
            <div class="helpline-card">
                <h3>🧩 Helpline Name: {h['name']}</h3>
                <p><strong>📞 Contact:</strong> {h['number']}</p>
                <p><strong>⏰ Hours:</strong> {h['hours']}</p>
                {website_html}
            </div>
            """, unsafe_allow_html=True)

    elif region == "🏛 State-specific":
        st.markdown("### 🏛 State-specific Helplines")
        st.info("📍 Select your state to view local mental health helplines")

        state = st.selectbox(
            "Choose your state",
            ["Maharashtra", "Karnataka", "Tamil Nadu",
                "West Bengal", "Gujarat", "Telangana"],
            key="helpline_state"
        )

        if state in HELPLINES_DATA["state_specific"]:
            st.markdown(f"#### {state} Mental Health Resources")
            helplines = HELPLINES_DATA["state_specific"][state]

            for h in helplines:
                if h['website'].startswith('Contact'):
                    website_html = f"<p><strong>🔗 Info:</strong> {h['website']}</p>"
                else:
                    website_html = f"<p><strong>🔗 Website:</strong> <a href='https://{h['website']}' target='_blank'>https://{h['website']}</a></p>"

                st.markdown(f"""
                <div class="helpline-card">
                    <h3>🧩 Helpline Name: {h['name']}</h3>
                    <p><strong>📞 Contact:</strong> {h['number']}</p>
                    <p><strong>⏰ Hours:</strong> {h['hours']}</p>
                    {website_html}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info(
                f"💡 No specific helplines listed for {state} yet. Please use India-wide helplines above.")

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
                if h['website'].startswith('Contact'):
                    website_html = f"<p><strong>🔗 Info:</strong> {h['website']}</p>"
                else:
                    website_html = f"<p><strong>🔗 Website:</strong> <a href='https://{h['website']}' target='_blank'>https://{h['website']}</a></p>"

                st.markdown(f"""
                <div class="helpline-card">
                    <h3>🧩 Helpline Name: {h['name']}</h3>
                    <p><strong>📞 Contact:</strong> {h['number']}</p>
                    <p><strong>⏰ Hours:</strong> {h['hours']}</p>
                    {website_html}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info(
                f"💡 No specific helplines listed for {city} yet. Please use India-wide or state-specific helplines.")

    # Additional resources
    st.markdown("---")
    st.markdown("### 💡 Additional Resources")
    st.info("""
    *Remember:*
    - 🆘 In an emergency, always call *112* (India) or your local emergency number
    - 💙 You are not alone - help is available
    - 🤝 Talking to someone can make a real difference
    - 🏥 Consider visiting a mental health professional for ongoing support
    - 📱 Save these numbers in your phone for quick access
    """)
