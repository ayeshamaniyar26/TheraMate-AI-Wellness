import streamlit as st
import time
from datetime import datetime

def render_typing_indicator():
    """Show typing animation"""
    st.markdown("""
    <div style="padding: 10px;">
        <span style="animation: blink 1.5s infinite;">●</span>
        <span style="animation: blink 1.5s infinite 0.2s;">●</span>
        <span style="animation: blink 1.5s infinite 0.4s;">●</span>
    </div>
    <style>
    @keyframes blink {
        0%, 100% { opacity: 0.3; }
        50% { opacity: 1; }
    }
    </style>
    """, unsafe_allow_html=True)

def render_floating_chat():
    """Render floating chat widget"""
    if st.session_state.get("show_floating_chat", False):
        st.markdown("""
        <div style="
            position: fixed;
            bottom: 80px;
            right: 20px;
            width: 350px;
            height: 400px;
            background: white;
            border-radius: 15px;
            box-shadow: 0 8px 30px rgba(0,0,0,0.3);
            z-index: 999;
            padding: 15px;
        ">
            <h4>💬 Quick Chat</h4>
            <p>Chat interface here...</p>
        </div>
        """, unsafe_allow_html=True)

def render_hide_screen_toggle():
    """Toggle hide screen mode"""
    return st.toggle("🔒 Hide Screen Mode", False)

def render_badge_system(badges):
    """Display user badges"""
    if badges:
        st.markdown("### 🏆 Your Achievements")
        cols = st.columns(min(len(badges), 4))
        for idx, badge in enumerate(badges):
            with cols[idx % 4]:
                st.markdown(f"""
                <div class="badge">
                    <span style="font-size: 2rem;">{badge['emoji']}</span>
                    <br>{badge['name']}
                </div>
                """, unsafe_allow_html=True)

def show_notification(message, type="success"):
    """Show animated notification"""
    if type == "success":
        st.success(message)
    elif type == "info":
        st.info(message)
    elif type == "warning":
        st.warning(message)
    
def render_progress_bar(current, total, label="Progress"):
    """Render custom progress bar"""
    percentage = int((current / total) * 100) if total > 0 else 0
    st.markdown(f"""
    <div style="margin: 10px 0;">
        <small>{label}: {current}/{total}</small>
        <div class="progress-bar">
            <div class="progress-fill" style="width: {percentage}%;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_streak_badge(days):
    """Display streak badge"""
    if days >= 7:
        emoji = "🔥"
        color = "#FF6B35"
    elif days >= 3:
        emoji = "⚡"
        color = "#F7B801"
    else:
        emoji = "✨"
        color = "#00A8E8"
    
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, {color} 0%, {color}88 100%);
        color: white;
        padding: 15px;
        border-radius: 15px;
        text-align: center;
        margin: 10px 0;
    ">
        <h2>{emoji} {days} Day Streak!</h2>
        <p>Keep up the amazing work!</p>
    </div>
    """, unsafe_allow_html=True)

def render_wellness_tip():
    """Show random wellness tip"""
    tips = [
        "💧 Remember to drink water regularly!",
        "🌿 Take a 5-minute break to stretch",
        "😊 Smile! It releases endorphins",
        "🌙 Good sleep is essential for wellness",
        "🎵 Music can improve your mood instantly"
    ]
    import random
    tip = random.choice(tips)
    st.info(f"💡 **Wellness Tip:** {tip}")

def render_mood_emoji_selector():
    """Interactive mood selector with emojis"""
    moods = {
        "😊": "Happy",
        "😌": "Calm",
        "😢": "Sad",
        "😰": "Anxious",
        "😴": "Tired",
        "😡": "Angry"
    }
    
    st.markdown("### How are you feeling?")
    cols = st.columns(6)
    
    selected_mood = None
    for idx, (emoji, label) in enumerate(moods.items()):
        with cols[idx]:
            if st.button(emoji, key=f"mood_{emoji}"):
                selected_mood = label
    
    return selected_mood

def render_animated_header(text, emoji="🌸"):
    """Render animated header"""
    st.markdown(f"""
    <h1 style="
        text-align: center;
        color: #6B9BD1;
        animation: fadeIn 1s ease-in;
    ">
        {emoji} {text}
    </h1>
    <style>
    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(-20px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    </style>
    """, unsafe_allow_html=True)

def render_card(title, content, emoji="✨"):
    """Render a modern card component"""
    st.markdown(f"""
    <div class="wellness-card">
        <h3>{emoji} {title}</h3>
        <p>{content}</p>
    </div>
    """, unsafe_allow_html=True)