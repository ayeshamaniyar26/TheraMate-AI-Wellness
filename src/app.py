# app.py

# Safe Streamlit rerun
from streamlit.runtime.scriptrunner.script_runner import RerunException
from streamlit.runtime.scriptrunner import get_script_run_ctx

def rerun():
    ctx = get_script_run_ctx()
    if ctx is None:
        raise RuntimeError("Cannot get Streamlit context")
    raise RerunException(ctx)



import streamlit as st
from datetime import datetime
import random
import time
import json
from pathlib import Path
import matplotlib.pyplot as plt
import plotly.express as px

from llm_adapter import (
    call_gemini, WHO5_QUESTIONS, mood_history, save_mood,
    suggest_exercise, get_helplines, get_today_habits,
    mark_habit_done, get_weekly_happiness
)
# ---------- Page Config ----------
#st.set_page_config(page_title="TheraMate - Your friendly AI therapy companion", layout="wide")
#st.title("💬 TheraMate — Your friendly AI therapy companion")
#st.write("Confidential and empathetic chatbot powered by AI.")

# ---------- Safe rerun function ----------
from streamlit.runtime.scriptrunner.script_runner import RerunException
from streamlit.runtime.scriptrunner import get_script_run_ctx

def rerun():
    ctx = get_script_run_ctx()
    if ctx is None:
        raise RuntimeError("Cannot get Streamlit context")
    raise RerunException(ctx)

# ---------- User Nickname & Privacy ----------
# ---------- Entry Gate: Nickname + PIN + Consent ----------
import hashlib
import streamlit as st
import time

# Helper to hash pin
def hash_pin(pin: str) -> str:
    return hashlib.sha256(pin.encode()).hexdigest()

# Default stored PIN (replace with dynamic storage if needed)
STORED_PIN_HASH = hash_pin("1234")  # Example default PIN (set to "1234")

# --- Nickname ---
if "nickname" not in st.session_state or not st.session_state.nickname:
    st.title("💬 TheraMate — Your friendly AI therapy companion")

    nickname_input = st.text_input("✨ What should I call you today?", key="nickname_input")
    
    if st.button("Save Nickname"):
        if nickname_input.strip():
            st.session_state.nickname = nickname_input.strip()
            st.success(f"Welcome, {st.session_state.nickname}! 💛")
            st.balloons()
            time.sleep(1)
            st.rerun()
        else:
            st.error("Please enter a valid nickname 💡")
    st.stop()

# --- Consent Agreement ---
if "consent" not in st.session_state:
    st.warning("🔒 This is a **confidential self-care space**.\n\n"
               "⚠️ No medical advice is provided.\n"
               "💙 If you ever feel unsafe, please reach out to a crisis helpline immediately.")

    agree = st.checkbox("I understand and want to continue 💙")
    if st.button("Confirm & Continue"):
        if agree:
            st.session_state.consent = True
            st.success("Thank you for trusting this space 🌈")
            time.sleep(1)
            st.rerun()
        else:
            st.error("You must agree before continuing.")
    st.stop()

# --- PIN Protection (Optional) ---
if "authenticated" not in st.session_state:
    st.subheader("🔑 Unlock Your SafeMind Session")
    pin_input = st.text_input("Enter your 4-digit PIN (default: 1234)", type="password")
    
    if st.button("Unlock"):
        if hash_pin(pin_input) == STORED_PIN_HASH:
            st.session_state.authenticated = True
            st.success("✅ Access granted — your safe space is open.")
            time.sleep(1)
            st.rerun()
        else:
            st.error("❌ Incorrect PIN. Please try again.")
    st.stop()

# ---------- After this point, load your main chatbot/dashboard ----------
st.markdown(f"👋 Hello, **{st.session_state.nickname}**! Welcome back to your safe space 💛")

# ---------------- Session State ----------------
if "history" not in st.session_state:
    st.session_state.history = []

# Optional: One-time welcome message
if "welcomed" in st.session_state and st.session_state.welcomed:
    st.info("💡 Tip: Use the chat below to talk with your AI companion, track moods, or play mini-games!")
    # Remove 'welcomed' so it doesn’t show again
    del st.session_state.welcomed

# ---------------- WHO-5 Questionnaire ----------------
st.header("📝 Daily WHO-5 Questionnaire")
who5_answers = []
for i, q in enumerate(WHO5_QUESTIONS, start=1):
    slider_val = st.slider(f"{i}. {q}", 0, 5, 3, key=f"q{i}")
    who5_answers.append(slider_val)

if st.button("Submit WHO-5"):
    total = sum(who5_answers)
    percent = int((total / 25) * 100)
    today_str = datetime.today().strftime("%Y-%m-%d")
    mood_history.append({"who5": who5_answers, "score": percent, "date": today_str})
    save_mood()
    st.success(f"✅ Your WHO-5 score: {percent}%")


# ---------------- Exercise Suggestion ----------------
st.header("🏃 Suggested Mindfulness / Relaxation Exercise")
if st.button("Suggest Exercise"):
    last_score = mood_history[-1]["score"] if mood_history else None
    exercise = suggest_exercise(last_score)
    st.success(exercise)

# ---------------- Chat Section ----------------
st.header("💬 Chat ")
user_input = st.text_input("Type your message here:", key="chat_input")
if st.button("Send Message"):
    if user_input.strip():
        st.session_state.history.append({"role": "user", "text": user_input})
        reply = call_gemini(user_input)
        st.session_state.history.append({"role": "assistant", "text": reply})

# ---------------- Display Conversation ----------------
for msg in st.session_state.history:
    if msg["role"] == "user":
        st.markdown(f"**You:** {msg['text']}")
    else:
        st.markdown(f"**SafeMind:** {msg['text']}")

# ---------------- Helplines ----------------
HELPLINES_FILE = Path("helplines.json")
with open(HELPLINES_FILE, "r", encoding="utf-8") as f:
    helplines_data = json.load(f)

st.header("📞 Helplines / Crisis Support")
st.warning(helplines_data.get("safety_note", ""))

# India-wide helplines
st.subheader("🌏 India-wide Helplines")
for h in helplines_data["helplines"].get("india_wide", []):
    st.info(f"**{h['name']}**\n📞 {h['number']}\n🗂 {', '.join(h['category'])}\n🗣 {', '.join(h['language'])}\n💡 {h['notes']}")

# State-specific helplines
for state, entries in helplines_data["helplines"].get("state_specific", {}).items():
    st.subheader(f"🏙️ {state} Helplines")
    for h in entries:
        st.info(f"**{h['name']}**\n📞 {h['number']}\n🗂 {', '.join(h['category'])}\n🗣 {', '.join(h['language'])}\n💡 {h['notes']}")

# City-specific helplines
for city, entries in helplines_data["helplines"].get("city_specific", {}).items():
    st.subheader(f"🏘️ {city} Helplines")
    for h in entries:
        st.info(f"**{h['name']}**\n📞 {h['number']}\n🗂 {', '.join(h['category'])}\n🗣 {', '.join(h['language'])}\n💡 {h['notes']}")

# ---------------- Daily Habit Tracker ----------------
st.header("✅ Daily Habit Tracker")
today_habits = get_today_habits()
for idx, h in enumerate(today_habits):
    key = f"habit_{h['habit_id']}_{datetime.today().strftime('%Y%m%d')}_{idx}"
    done = st.checkbox(h["habit_name"], value=h["done"], key=key)
    if done and not h["done"]:
        mark_habit_done(h["habit_id"])

# ---------------- Weekly Happiness Graph ----------------
days, scores = get_weekly_happiness()
if any(scores):
    fig = px.line(x=days, y=scores, markers=True, text=scores, title="🌟 Your Mood Journey This Week",
                  labels={"x": "Day", "y": "Happiness Score (0-100)"})
    fig.update_traces(line_color="royalblue", line_width=3, marker=dict(size=12, color="orange"), textposition="top center")
    fig.update_layout(template="plotly_white", yaxis=dict(range=[0, 100]), font=dict(size=16),
                      title=dict(x=0.5, xanchor="center", font=dict(size=24, color="darkblue")),
                      margin=dict(l=30, r=30, t=70, b=30), hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)

    avg_score = sum(scores) / len(scores)
    if avg_score >= 70:
        st.success("💖 Amazing! You’ve had a really positive week 🌈 Keep it up!")
    elif avg_score >= 40:
        st.info("🌤️ Some ups and downs — totally normal! Stay consistent 💪")
    else:
        st.warning("🌧️ Looks like it’s been tough. Remember: small steps count 💙")
else:
    st.info("No mood data available yet. Record your moods to see your happiness journey 📈")

# ---------------- Mini-games ----------------
st.header("🎮 Mind Games & Activities")

# ---------- Games Storage ----------
GAMES_FILE = Path("games.json")
if GAMES_FILE.exists():
    games_history = json.loads(GAMES_FILE.read_text(encoding="utf-8"))
else:
    games_history = []

def save_game_entry(entry):
    games_history.append(entry)
    with open(GAMES_FILE, "w", encoding="utf-8") as f:
        json.dump(games_history, f, indent=2, ensure_ascii=False)


# ---------- Would You Rather ----------
# ---------- Would You Rather ----------
wyr_choices = [
    ("🌍 Travel to space 🚀", "🌊 Explore the deep sea"),
    ("🎶 Always hear music", "🎨 Always see art"),
    ("📚 Read minds", "🔮 See the future"),
    ("🐶 Talk to animals", "🕊️ Fly like a bird"),
    ("🍫 Unlimited chocolate", "🍕 Unlimited pizza"),
    ("💤 Sleep 12 hrs/day", "⚡ Never need sleep again"),
]

# Initialize session state
if "wyr_current" not in st.session_state:
    st.session_state.wyr_current = random.choice(wyr_choices)
    st.session_state.wyr_submitted = False
    st.session_state.wyr_feedback = ""
    st.session_state.wyr_choice = None

st.subheader("🤔 Would You Rather")
choice = st.radio("Choose one:", st.session_state.wyr_current, key="wyr_radio")
st.session_state.wyr_choice = choice

# Submit choice
if st.button("Submit Choice") and not st.session_state.wyr_submitted:
    if st.session_state.wyr_choice:
        st.session_state.wyr_submitted = True
        amazing_lines = [
            f"🌟 Choosing **{st.session_state.wyr_choice}** shows your adventurous spirit!",
            f"💖 Wow! **{st.session_state.wyr_choice}** truly reflects what excites you.",
            f"✨ Great pick! Sometimes **{st.session_state.wyr_choice}** is exactly what we need to dream bigger.",
            f"🌈 Love it! **{st.session_state.wyr_choice}** says a lot about your vibe today."
        ]
        st.session_state.wyr_feedback = random.choice(amazing_lines)

        save_game_entry({
            "game": "Would You Rather",
            "question": st.session_state.wyr_current,
            "choice": st.session_state.wyr_choice,
            "date": datetime.today().strftime("%Y-%m-%d")
        })

# Show feedback
if st.session_state.wyr_feedback:
    st.success(st.session_state.wyr_feedback)
    # Next question button
    if st.button("Next Question ➡️"):
        st.session_state.wyr_current = random.choice(wyr_choices)
        st.session_state.wyr_submitted = False
        st.session_state.wyr_feedback = ""
        st.session_state.wyr_choice = None
        rerun()  # custom rerun function to refresh the page


# ---------- Relaxation Challenge ----------
import streamlit as st
import time

# ---------- Quick Relaxation Challenge ----------
st.subheader("🌬️ Quick Relaxation Challenge")

relax_choice = st.radio(
    "Pick a relaxation game:", 
    ["✨ Breathing Exercise", "🎈 Pop Stress Bubbles"]
)

# Breathing Exercise
if relax_choice == "✨ Breathing Exercise":
    st.write("Follow the guided breathing for 3 cycles...")
    if st.button("Start Breathing"):
        for i in range(3):
            st.write("🌬️ Breathe In... (4s)")
            time.sleep(4)  # fixed typo: e.sleep -> time.sleep
            
            st.write("😌 Hold... (2s)")
            time.sleep(2)
            
            st.write("💨 Breathe Out... (4s)")
            time.sleep(4)
        st.success("💙 Well done! Feeling calmer already.")

# Pop Stress Bubbles
elif relax_choice == "🎈 Pop Stress Bubbles":
    if "bubbles" not in st.session_state:
        st.session_state.bubbles = 5  # initialize bubbles

    st.write(f"Pop the bubbles! Remaining: {st.session_state.bubbles}")

    if st.button("Pop a Bubble 🎈"):
        if st.session_state.bubbles > 0:
            st.session_state.bubbles -= 1
            if st.session_state.bubbles == 0:
                st.success("🎉 You popped all the stress bubbles! Relaxed and refreshed 💖")
        else:
            st.info("All bubbles popped! Restart to play again.")

    if st.button("Restart Game 🔄"):
        st.session_state.bubbles = 5
        st.info("Game restarted! 🎈 Pop away!")

st.markdown("---")

# ---------- Emoji Mood Match ----------
st.subheader("💫 Emoji Mood Match")

MOTIVATIONAL_QUOTES = {
    "😊": "Keep smiling, your joy is contagious 🌟",
    "😢": "It's okay to feel down 💙 Brighter days are coming 🌈",
    "😡": "Take a deep breath 😌 You are stronger than your anger 💪",
    "😴": "Rest is productive 🌙 Recharge and shine tomorrow ☀️",
    "🤔": "Curiosity keeps the mind alive 🔍 Keep exploring 💫",
}

emojis = list(MOTIVATIONAL_QUOTES.keys())
picked_mood = st.radio("Pick the emoji that matches your mood:", emojis, key="mood_match")

if st.button("Submit Mood"):
    quote = MOTIVATIONAL_QUOTES.get(
        picked_mood, 
        "🌟 Keep going, you’re doing great!"
    )
    st.success(quote)

st.markdown("---")

# ---------- Positive Affirmations ----------
st.subheader("🌟 Positive Affirmation Cards")
AFFIRMATIONS = [
    "💖 You are enough, just as you are.",
    "🌈 This too shall pass, better days are ahead.",
    "🌟 Your kindness makes the world brighter.",
    "🔥 You are stronger than your struggles.",
    "🌻 Every day is a fresh start.",
]
if st.button("Draw a Card 🎴"):
    affirmation = random.choice(AFFIRMATIONS)
    st.success(affirmation)
# ---------- Mood Color Match ----------
st.subheader("🎨 Mood Color Match")

mood_colors = {
    "Red": "🔥 Passionate and energized!",
    "Blue": "💙 Calm and reflective.",
    "Yellow": "🌟 Cheerful and bright!",
    "Green": "🍃 Balanced and peaceful.",
    "Purple": "💜 Creative and thoughtful.",
    "Orange": "🧡 Energetic and enthusiastic!"
}

picked_color = st.radio("Pick a color that matches your mood today:", list(mood_colors.keys()), key="mood_color")

if st.button("Submit Color Mood"):
    st.success(f"{mood_colors[picked_color]}")
    save_game_entry({
        "game": "Mood Color Match",
        "color": picked_color,
        "date": datetime.today().strftime("%Y-%m-%d")
    })

st.subheader("📔 Daily Micro-Journal")
journal_prompts = [
    "What made you smile today?",
    "Name one thing you learned today.",
    "Describe a small victory you had today.",
    "Write one thing you want to let go of."
]

prompt_today = random.choice(journal_prompts)
st.write(f"📌 Prompt: {prompt_today}")
journal_entry = st.text_area("Your reflection:", key="journal_input")
if st.button("Save Journal Entry"):
    if journal_entry.strip():
        st.success("✅ Reflection saved!")
        save_game_entry({
            "game": "Daily Micro-Journal",
            "prompt": prompt_today,
            "response": journal_entry,
            "date": datetime.today().strftime("%Y-%m-%d")
        })



# ---------- Game History ----------
st.subheader("📜 Your Game History")
if games_history:
    for entry in reversed(games_history[-20:]):
        if entry["game"] == "Would You Rather":
            st.info(
                f"🤔 **{entry['game']}** ({entry['date']})\n"
                f"Q: {entry['question'][0]} OR {entry['question'][1]}\n"
                f"👉 You chose: **{entry['choice']}**"
            )
        elif entry["game"] == "Gratitude Spinner":
            st.success(f"🌸 Gratitude shared on {entry['date']}")
else:
    st.info("No history yet. Play a game and your reflections will appear here 🌟")

# ---------- Session Ending ----------
st.markdown("---")  # separator

closing_messages = [
    "💙 <b>Thank you for taking care of yourself today.</b><br>Remember: even tiny steps count 🌱",
    "🌟 <b>Session complete!</b><br>Take a deep breath, unclench your shoulders, and smile 🙂",
    "🌈 <b>You showed up today — that’s brave.</b><br>Tomorrow is a new chance to shine 🌞",
    "🕊️ <b>Healing takes time.</b><br>Be gentle with yourself, you are doing better than you think 💖",
    "🔥 <b>You are stronger than you realize.</b><br>Carry this strength into the rest of your day 💪"
]

import random
final_note = random.choice(closing_messages)

# Big styled text for emphasis
st.markdown(
    f"""
    <div style="text-align: center; 
                background-color: #f0f8ff; 
                padding: 20px; 
                border-radius: 15px; 
                border: 2px solid #87CEFA;">
        <h2 style="color:#1E90FF;">{final_note}</h2>
    </div>
    """,
    unsafe_allow_html=True
)
