# app.py
import json
from pathlib import Path

# ---------- Load Helpline Data ----------
import json
import os

def load_helplines():
    file_path = os.path.join(os.path.dirname(_file_), "helplines.json")
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


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
    st.warning("🔒 This is a *confidential self-care space*.\n\n"
               "⚠ No medical advice is provided.\n"
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
st.markdown(f"👋 Hello, *{st.session_state.nickname}*! Welcome back to your safe space 💛")

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
st.header("💬 Chat with TheraMate")

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "chat_input" not in st.session_state:
    st.session_state.chat_input = ""

# Input form to avoid double execution on button press
with st.form(key="chat_form", clear_on_submit=True):
    user_text = st.text_input(
        "Type your message here:",
        value=st.session_state.chat_input,
        placeholder="Ask me anything..."
    )
    send_button = st.form_submit_button("Send")

if send_button and user_text.strip():
    # Add user message
    st.session_state.chat_history.append({"role": "user", "text": user_text.strip()})

    # Get AI reply
    reply = call_gemini(user_text.strip())
    st.session_state.chat_history.append({"role": "assistant", "text": reply})

# Display chat history with calm, minimalist styling
for msg in st.session_state.chat_history:
    if msg["role"] == "user":
        st.markdown(
            f"""
            <div style="
                background-color:#E0F7FA; 
                color:#004D40;
                padding:12px; 
                border-radius:12px; 
                margin:6px 0; 
                font-family:sans-serif;
                max-width:80%;
            ">
                <b>You:</b> {msg['text']}
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f"""
            <div style="
                background-color:#F1F8E9; 
                color:#33691E;
                padding:12px; 
                border-radius:12px; 
                margin:6px 0; 
                font-family:sans-serif;
                max-width:80%;
            ">
                <b>TheraMate:</b> {msg['text']}
            </div>
            """,
            unsafe_allow_html=True
        )


# ---------------- Helpline Resources ----------------
import streamlit as st
import json

# Load helplines data
def load_helplines():
    # Replace this with the actual JSON if loading from a file:
    helplines_json = """
    {
      "safety_note": "⚠ Safety First: If you are in immediate danger or having suicidal thoughts, please contact your local emergency services immediately.",
      "helplines": {
        "india_wide": [
          {
            "name": "AASRA Foundation",
            "number": "+91 9820466726",
            "category": ["Suicide Prevention", "24x7 Support"],
            "language": ["English", "Hindi"],
            "notes": "Confidential, free support"
          },
          {
            "name": "Vandrevala Foundation",
            "number": "1860 266 2345",
            "category": ["Mental Health Support", "Counseling", "24x7 Support"],
            "language": ["English", "Hindi"],
            "notes": "Free, confidential"
          }
        ],
        "state_specific": {
          "Maharashtra": [
            {
              "name": "Mumbai Suicide Prevention Helpline",
              "number": "022 2754 6669",
              "category": ["Suicide Prevention"],
              "language": ["Marathi", "Hindi", "English"],
              "notes": "Local support, free"
            }
          ],
          "Karnataka": [
            {
              "name": "NIMHANS Helpline",
              "number": "080 4611 0007",
              "category": ["Counseling", "Mental Health Support"],
              "language": ["Kannada", "English"],
              "notes": "Expert support, free"
            }
          ],
          "Tamil Nadu": [
            {
              "name": "Sneha Suicide Prevention Centre",
              "number": "044 2464 0050",
              "category": ["Suicide Prevention", "Counseling"],
              "language": ["Tamil", "English"],
              "notes": "24x7 support, confidential"
            }
          ],
          "Kerala": [
            {
              "name": "Maithri Helpline",
              "number": "0484 2540530",
              "category": ["Emotional Support", "Counseling"],
              "language": ["Malayalam", "English"],
              "notes": "Free listening service"
            }
          ],
          "West Bengal": [
            {
              "name": "Lifeline Foundation",
              "number": "033 40447437",
              "category": ["Suicide Prevention", "Mental Health Support"],
              "language": ["Bengali", "English"],
              "notes": "Confidential support"
            }
          ]
        },
        "city_specific": {
          "Delhi": [
            {
              "name": "Delhi Mental Health Helpline",
              "number": "+91 011 2338 9999",
              "category": ["Counseling", "24x7 Support"],
              "language": ["Hindi", "English"],
              "notes": "Local government initiative, free"
            }
          ],
          "Mumbai": [
            {
              "name": "iCall Mumbai Helpline",
              "number": "9152987821",
              "category": ["Mental Health Support", "Counseling"],
              "language": ["Hindi", "English", "Marathi"],
              "notes": "TISS initiative, free and confidential"
            }
          ],
          "Bengaluru": [
            {
              "name": "Sahai Helpline",
              "number": "080 25497777",
              "category": ["Counseling", "Mental Health Support"],
              "language": ["Kannada", "English"],
              "notes": "Runs 10am–8pm daily"
            }
          ],
          "Chennai": [
            {
              "name": "Sneha Chennai Helpline",
              "number": "044 2464 0050",
              "category": ["Suicide Prevention", "Counseling"],
              "language": ["Tamil", "English"],
              "notes": "24/7 confidential emotional support"
            }
          ]
        }
      }
    }
    """
    return json.loads(helplines_json)

# Main Streamlit App
helplines_data = load_helplines()

st.subheader("📞 Mental Health Helplines")
st.info(helplines_data["safety_note"])

# Dropdown for helpline category
option = st.selectbox(
    "Choose Helpline Category:",
    ["India-wide", "State-specific", "City-specific"]
)

# India-wide helplines
if option == "India-wide":
    st.write("### India-wide Helplines")
    for entry in helplines_data["helplines"]["india_wide"]:
        with st.container():
            st.markdown(f"{entry['name']}")
            st.write(f"📞 {entry['number']}")
            st.write(f"🗂 {', '.join(entry['category'])}")
            st.write(f"🌐 {', '.join(entry['language'])}")
            st.caption(entry["notes"])
            st.divider()

# State-specific helplines
elif option == "State-specific":
    state = st.selectbox(
        "Select a State:",
        list(helplines_data["helplines"]["state_specific"].keys())
    )
    st.write(f"### 🏙 Helplines in {state}")
    for hotline in helplines_data["helplines"]["state_specific"][state]:
        with st.container():
            st.markdown(f"{hotline['name']}")
            st.write(f"📞 {hotline['number']}")
            st.write(f"🗂 {', '.join(hotline['category'])}")
            st.write(f"🌐 {', '.join(hotline['language'])}")
            st.caption(hotline["notes"])
            st.divider()

# City-specific helplines
elif option == "City-specific":
    city = st.selectbox(
        "Select a City:",
        list(helplines_data["helplines"]["city_specific"].keys())
    )
    st.write(f"### 🌆 Helplines in {city}")
    for hotline in helplines_data["helplines"]["city_specific"][city]:
        with st.container():
            st.markdown(f"{hotline['name']}")
            st.write(f"📞 {hotline['number']}")
            st.write(f"🗂 {', '.join(hotline['category'])}")
            st.write(f"🌐 {', '.join(hotline['language'])}")
            st.caption(hotline["notes"])
            st.divider()
import streamlit as st
import json
from datetime import datetime, timedelta
from pathlib import Path
import plotly.graph_objects as go
import random

# ----------------- File Paths -----------------
HABITS_FILE = Path("habits.json")
MOOD_FILE = Path("mood_data.json")
JOURNAL_FILE = Path("journal.json")
GAMES_FILE = Path("games.json")

# ----------------- Helper Functions -----------------
def load_scores():
    if MOOD_FILE.exists():
        return json.loads(MOOD_FILE.read_text(encoding="utf-8"))
    return {}

def save_score(date_str, score):
    scores = load_scores()
    scores[date_str] = score
    with open(MOOD_FILE, "w", encoding="utf-8") as f:
        json.dump(scores, f, indent=2, ensure_ascii=False)

def load_journal():
    if JOURNAL_FILE.exists():
        return json.loads(JOURNAL_FILE.read_text(encoding="utf-8"))
    return []

def save_journal(entry):
    journal_data = load_journal()
    # Remove old entry for today
    journal_data = [d for d in journal_data if d.get("date") != entry["date"]]
    journal_data.append(entry)
    with open(JOURNAL_FILE, "w", encoding="utf-8") as f:
        json.dump(journal_data, f, indent=2, ensure_ascii=False)

def load_games():
    if GAMES_FILE.exists():
        return json.loads(GAMES_FILE.read_text(encoding="utf-8"))
    return []

def save_game_entry(entry):
    games_history = load_games()
    games_history.append(entry)
    with open(GAMES_FILE, "w", encoding="utf-8") as f:
        json.dump(games_history, f, indent=2, ensure_ascii=False)

def get_weekly_happiness(days_back=7):
    today = datetime.today()
    scores = load_scores()
    days = [(today - timedelta(days=i)).strftime("%a %d") for i in reversed(range(days_back))]
    values = []
    for i in reversed(range(days_back)):
        date_key = (today - timedelta(days=i)).strftime("%Y-%m-%d")
        if date_key in scores:
            values.append(scores[date_key])
        elif i == 0:
            values.append(50)  # default today
        else:
            values.append(None)
    return days, values

# ----------------- Daily Habit Tracker -----------------
st.header("✅ Daily Habit Tracker")

# Example: replace with actual function fetching user habits
def get_today_habits():
    if HABITS_FILE.exists():
        return json.loads(HABITS_FILE.read_text(encoding="utf-8"))
    return [
        {"habit_id": 1, "habit_name": "Drink water", "done": False},
        {"habit_id": 2, "habit_name": "Exercise", "done": False},
        {"habit_id": 3, "habit_name": "Meditate", "done": False},
    ]

def mark_habit_done(habit_id):
    today_habits = get_today_habits()
    for h in today_habits:
        if h["habit_id"] == habit_id:
            h["done"] = True
    with open(HABITS_FILE, "w", encoding="utf-8") as f:
        json.dump(today_habits, f, indent=2, ensure_ascii=False)

today_habits = get_today_habits()
for idx, h in enumerate(today_habits):
    key = f"habit_{h['habit_id']}{datetime.today().strftime('%Y%m%d')}{idx}"
    done = st.checkbox(h["habit_name"], value=h.get("done", False), key=key)
    if done and not h.get("done", False):
        mark_habit_done(h["habit_id"])






# ----------------- Daily Mood Input -----------------
st.subheader("📝 Record Today's Mood")
today_key = datetime.today().strftime("%Y-%m-%d")

if "today_score" not in st.session_state:
    scores = load_scores()
    st.session_state["today_score"] = scores.get(today_key, 50)

st.session_state["today_score"] = st.slider(
    "How are you feeling today? (0=lowest, 100=highest)",
    0, 100, st.session_state["today_score"]
)

if st.button("💾 Save Today's Mood"):
    save_score(today_key, st.session_state["today_score"])
    st.success("✅ Mood saved! Graph updated below.")

# ----------------- Mood Graph -----------------
st.header("🌈 Your Mood Tracker")

# Select number of days to display
option_days = st.selectbox("Select number of days to view:", [7, 14, 30], index=0)
days, scores = get_weekly_happiness(option_days)

# Replace None with 0 and apply emojis/colors
display_scores = [s if s is not None else 0 for s in scores]
emojis = ["😢" if s < 40 else "😐" if s < 70 else "😄" for s in display_scores]
colors = ["red" if s < 40 else "orange" if s < 70 else "green" for s in display_scores]

# Plotly Figure
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=days,
    y=display_scores,
    mode="lines+markers+text",
    text=emojis,
    textposition="top center",
    line=dict(color="royalblue", width=3),
    marker=dict(size=14, color=colors, line=dict(width=2, color="darkblue"))
))

# Shaded reference area
fig.add_trace(go.Scatter(
    x=days + days[::-1],
    y=[100]*len(days) + [0]*len(days),
    fill='toself',
    fillcolor='rgba(173, 216, 230, 0.2)',
    line=dict(color='rgba(255,255,255,0)'),
    hoverinfo="skip",
    showlegend=False
))

fig.update_layout(
    title=dict(
        text="🌟 Your Happiness Journey",
        x=0.5,
        xanchor="center",
        font=dict(size=24, color="darkblue")
    ),
    yaxis=dict(title="Happiness Score (0-100)", range=[0, 100]),
    xaxis=dict(title="Day"),
    template="plotly_white",
    font=dict(size=16),
    margin=dict(l=40, r=40, t=80, b=40),
    hovermode="x unified"
)

st.plotly_chart(fig, use_container_width=True)


# ----------------- Insights -----------------
valid_scores = [s for s in scores if s is not None]
if valid_scores:
    avg_score = sum(valid_scores)/len(valid_scores)
    max_score = max(valid_scores)
    min_score = min(valid_scores)
    today_score = valid_scores[-1]

    st.markdown(f"*Today's Mood Score:* {today_score} {emojis[-1]}")
    st.markdown(f"*Average Score:* {avg_score:.1f}")
    st.markdown(f"*Highest Score:* {max_score}")
    st.markdown(f"*Lowest Score:* {min_score}")

    if avg_score >= 70:
        st.success("💖 Amazing! You’ve had a really positive period 🌈 Keep it up!")
    elif avg_score >= 40:
        st.info("🌤 Some ups and downs — totally normal! Stay consistent 💪")
    else:
        st.warning("🌧 It’s been tough. Remember: small steps count 💙")
else:
    st.info("No mood data yet. Record your moods to see your happiness journey 📈")

# ---------------- Would You Rather ----------------
wyr_choices = [
    ("🌍 Travel to space 🚀", "🌊 Explore the deep sea"),
    ("🎶 Always hear music", "🎨 Always see art"),
    ("📚 Read minds", "🔮 See the future"),
    ("🐶 Talk to animals", "🕊 Fly like a bird"),
    ("🍫 Unlimited chocolate", "🍕 Unlimited pizza"),
    ("💤 Sleep 12 hrs/day", "⚡ Never need sleep again"),
]

# Initialize session state
if "wyr_current" not in st.session_state:
    st.session_state.wyr_current = random.choice(wyr_choices)
    st.session_state.wyr_submitted = False
    st.session_state.wyr_feedback = ""
    st.session_state.wyr_choice = None
import random
from datetime import datetime
import streamlit as st

# ---------- Would You Rather ----------
wyr_choices = [
    ("🌍 Travel to space 🚀", "🌊 Explore the deep sea"),
    ("🎶 Always hear music", "🎨 Always see art"),
    ("📚 Read minds", "🔮 See the future"),
    ("🐶 Talk to animals", "🕊 Fly like a bird"),
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

        # Dynamic responses depending on the choice
        feedback_map = {
            "🌍 Travel to space 🚀": "🚀 Wow! You're a true explorer, aiming for the stars!",
            "🌊 Explore the deep sea": "🌊 Deep dive! You love mysteries and hidden worlds.",
            "🎶 Always hear music": "🎶 Music feeds your soul — such a beautiful choice!",
            "🎨 Always see art": "🎨 Artistic vibes! You see beauty in everything.",
            "📚 Read minds": "🧠 Powerful! You value understanding people deeply.",
            "🔮 See the future": "🔮 Future sight! You like to plan ahead and dream big.",
            "🐶 Talk to animals": "🐾 Aww! You must be kind and connected to nature.",
            "🕊 Fly like a bird": "🕊 Freedom seeker! You love adventure and open skies.",
            "🍫 Unlimited chocolate": "🍫 Sweet tooth! You know how to enjoy life’s pleasures.",
            "🍕 Unlimited pizza": "🍕 Pizza lover — you’re all about comfort and happiness!",
            "💤 Sleep 12 hrs/day": "😴 Rest is luxury! You love peace and relaxation.",
            "⚡ Never need sleep again": "⚡ Energy boost! You want to maximize every moment."
        }

        st.session_state.wyr_feedback = feedback_map.get(
            st.session_state.wyr_choice,
            f"✨ Great pick! *{st.session_state.wyr_choice}* really shows your vibe today."
        )

        # Save the game entry
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
    if st.button("Next Question ➡"):
        st.session_state.wyr_current = random.choice(wyr_choices)
        st.session_state.wyr_submitted = False
        st.session_state.wyr_feedback = ""
        st.session_state.wyr_choice = None
        st.rerun()


# ---------- Relaxation Challenge ----------
import streamlit as st
import time

st.title("🌬 Quick Relaxation Challenge")

st.subheader("✨ Breathing Exercise")

st.write("Follow this calming 3-cycle breathing exercise:")

if st.button("Start Breathing 🧘", key="breathing_start_btn"):
    for i in range(3):
        st.markdown("### 🌬 Breathe In... (4s)")
        time.sleep(4)
        st.markdown("### 😌 Hold... (2s)")
        time.sleep(2)
        st.markdown("### 💨 Breathe Out... (4s)")
        time.sleep(4)
        if i < 2:
            st.write("---")
    st.success("💙 Great job! Feeling calmer already 🌈")


#---------- Squish the Cute Critters Game ----------

import streamlit as st
import streamlit.components.v1 as components

st.title("🪲 Squish the Cute Critters")

st.write("Click the floating critters to squish them! Pop 7 to complete the game.")

critters_game_html = """
<!DOCTYPE html>
<html>
<head>
<style>
  body {
      margin:0;
      background: radial-gradient(circle, #fbc2eb, #a6c1ee);
      overflow:hidden;
      height:500px;
  }
  .critters {
      position:absolute;
      cursor:pointer;
      font-size:32px;
      transition: transform 0.2s ease-out;
      user-select:none;
  }
  #message {
      position:absolute;
      top:40%;
      left:50%;
      transform:translate(-50%,-50%);
      font-size:28px;
      font-weight:bold;
      color:white;
      display:none;
      text-shadow: 2px 2px 5px #000;
      text-align:center;
  }
</style>
</head>
<body>
  <div id="message">🎉 You squished 7 critters! Feeling playful & happy 💖</div>
  <script>
    let crittersPopped = 0;
    const crittersArr = ["🐞","🐛","🐝","🦋","🐌","🐜","🦗"];

    function createCritter() {
        let c = document.createElement("div");
        c.className = "critters";
        c.innerHTML = crittersArr[Math.floor(Math.random()*crittersArr.length)];
        c.style.left = Math.random()*window.innerWidth + "px";
        c.style.top = Math.random()*400 + "px";

        c.onclick = function(){
            if(crittersPopped < 7){
                crittersPopped++;
                c.style.transform = "scale(0)";
                setTimeout(()=>c.remove(),200);
            }
            if(crittersPopped === 7){
                setTimeout(()=>{document.getElementById("message").style.display="block";},500);
            }
        };

        document.body.appendChild(c);
        setTimeout(()=>c.remove(),5000); // remove if not clicked
    }

    setInterval(createCritter, 700); // spawn critters continuously
  </script>
</body>
</html>
"""

# Display the game
components.html(critters_game_html, height=500, scrolling=False)


# ---------- Emoji Mood Match ----------
st.subheader("💫 Emoji Mood Match")

MOTIVATIONAL_QUOTES = {
    "😊": "Keep smiling, your joy is contagious 🌟",
    "😢": "It's okay to feel down 💙 Brighter days are coming 🌈",
    "😡": "Take a deep breath 😌 You are stronger than your anger 💪",
    "😴": "Rest is productive 🌙 Recharge and shine tomorrow ☀",
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





# ---------- Session Summary & Closing ----------
import streamlit as st
from datetime import datetime
from pathlib import Path
import json
import random

# ------------------ Initialize games_history ------------------
if "games_history" not in st.session_state:
    summary_file = Path("daily_summary.json")
    if summary_file.exists():
        st.session_state.games_history = json.loads(summary_file.read_text(encoding="utf-8"))
    else:
        st.session_state.games_history = []

games_history = st.session_state.games_history


st.subheader("🪞 Your Daily Reflection & Mini-Insights")

# Get today's date
today_str = datetime.today().strftime("%Y-%m-%d")

# Check if any games/mood entries exist
todays_entries = st.session_state.get("games_history", [])
todays_entries = [e for e in todays_entries if e.get("date") == today_str]

if todays_entries:
    st.markdown(f"✨ You completed **{len(todays_entries)} activities** today. Great job! 🎉")
    
    # Mood insights
    moods = [e.get("mood_score") for e in todays_entries if "mood_score" in e]
    if moods:
        avg_mood = sum(moods)/len(moods)
        if avg_mood >= 70:
            st.success("😄 Your mood was mostly positive today. Keep the energy flowing!")
        elif avg_mood >= 40:
            st.warning("😐 Your mood was mixed today. Try a short breathing exercise.")
        else:
            st.error("😢 Today was tough. Remember to be gentle with yourself 💖")
    
    # Random reflection prompts
    reflections = [
        "🌱 You took time for self-care today. That’s progress!",
        "💡 Remember small wins are still wins. Celebrate them!",
        "🌈 Keep noticing your feelings. Awareness is growth.",
        "🕊 Even one positive action today matters. You did it!"
    ]
    st.markdown(f"💬 **Reflection:** {random.choice(reflections)}")
    
else:
    st.info("No activities recorded today. Play a game or reflect in your journal 🌟")



# ---------------- Closing Messages ----------------
closing_messages = [
    "💙 <b>Thank you for taking care of yourself today.</b><br>Remember: even tiny steps count 🌱",
    "🌟 <b>Session complete!</b><br>Take a deep breath, unclench your shoulders, and smile 🙂",
    "🌈 <b>You showed up today — that’s brave.</b><br>Tomorrow is a new chance to shine 🌞",
    "🕊 <b>Healing takes time.</b><br>Be gentle with yourself, you are doing better than you think 💖",
    "🔥 <b>You are stronger than you realize.</b><br>Carry this strength into the rest of your day 💪"
]
final_note = random.choice(closing_messages)

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

# ---------------- Save Session Summary ----------------

from pathlib import Path
import json
from datetime import datetime

# Initialize games_history if not present
if "games_history" not in st.session_state:
    st.session_state.games_history = []

today_str = datetime.today().strftime("%Y-%m-%d")

# Example: collect today’s activities (replace this with your actual entries)
todays_entries = [
    {"date": today_str, "game": "Mood Color Match", "mood_score": 75},
    {"date": today_str, "game": "Would You Rather", "choice": "Option 1"}
]

if st.button("💾 Save Session"):
    summary_file = Path("daily_summary.json")

    # Load existing summaries if file exists
    if summary_file.exists():
        all_summaries = json.loads(summary_file.read_text(encoding="utf-8"))
    else:
        all_summaries = []

    # Remove any previous entry for today
    all_summaries = [s for s in all_summaries if s.get("date") != today_str]

    # Add today’s entries
    all_summaries.extend(todays_entries)

    # Save back to JSON
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(all_summaries, f, indent=2, ensure_ascii=False)

    # Update session state
    st.session_state.games_history = all_summaries
    st.success(f"✅ Your session for {today_str} has been saved successfully!")
