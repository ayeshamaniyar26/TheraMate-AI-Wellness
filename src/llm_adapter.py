import json
from pathlib import Path
from google import genai
import random
from datetime import datetime, timedelta

# ---------- Local Storage Paths ----------
SESSION_FILE = Path("session_history.json")
MOOD_FILE = Path("mood.json")
HELPLINES_FILE = Path("helplines.json")
HABITS_FILE = Path("habits.json")

# ---------- Gemini Client ----------
client = genai.Client()  # Reads GEMINI_API_KEY from environment variable

# ---------- Load Session & Mood ----------
session_history = json.loads(SESSION_FILE.read_text(encoding="utf-8")) if SESSION_FILE.exists() else []
mood_history = json.loads(MOOD_FILE.read_text(encoding="utf-8")) if MOOD_FILE.exists() else []

# ---------- System Prompt ----------
SYSTEM_PROMPT = (
    "You are a supportive and empathetic mental wellness assistant. "
    "Always respond gently and encouragingly. "
    "Do not give medical advice; if crisis keywords are detected, respond with resources only."
)

# ---------- Gemini Chat ----------
def call_gemini(user_input: str) -> str:
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for entry in session_history:
        messages.append({"role": "user", "content": entry["user"]})
        messages.append({"role": "assistant", "content": entry["assistant"]})
    messages.append({"role": "user", "content": user_input})

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=messages[-1]["content"]
    )
    assistant_reply = response.text.strip()

    session_history.append({"user": user_input, "assistant": assistant_reply})
    save_session()
    return assistant_reply

def save_session():
    with open(SESSION_FILE, "w", encoding="utf-8") as f:
        json.dump(session_history, f, indent=2, ensure_ascii=False)

def save_mood():
    with open(MOOD_FILE, "w", encoding="utf-8") as f:
        json.dump(mood_history, f, indent=2, ensure_ascii=False)

# ---------- WHO-5 ----------
WHO5_QUESTIONS = [
    
    "I have felt calm and relaxed.",
    "I woke up feeling fresh and rested.",
    "My daily life has been filled with things that interest me.",
    "I felt connected to others today.", 
    "I was able to focus on tasks without distraction."  
]

# ---------- Adaptive Exercise Suggestions ----------
EXERCISE_CATEGORIES = {
    "relaxation": [
        "NHS Breathing: inhale 4s, hold 7s, exhale 8s x5",
        "5-4-3-2-1 Grounding",
        "Listen to calming music for 5 minutes",
        "Progressive muscle relaxation",
        "Light stretching",
        "Warm tea break for 5 mins",
        "Guided meditation"
    ],
    "mindfulness": [
        "Journaling: write down 3 things you are grateful for",
        "Mindful walk for 10 minutes",
        "Meditation: 10 minutes guided",
        "Observe a natural object mindfully",
        "Mindful eating: eat slowly",
        "Body scan meditation",
        "Listen to ambient sounds"
    ],
    "energy": [
        "Pomodoro Focus: 25 min work + 5 min break",
        "Quick stretches: jumping jacks & squats",
        "2-min energizing walk",
        "5-min brisk walk/stairs",
        "Push-ups & sit-ups",
        "Dance to upbeat music",
        "Open window, deep breaths & stretch"
    ]
}

def suggest_exercise(who5_score=None):
    if who5_score is None:
        category = random.choice(list(EXERCISE_CATEGORIES.keys()))
    elif who5_score < 50:
        category = "relaxation"
    elif who5_score <= 75:
        category = "mindfulness"
    else:
        category = "energy"
    exercise = random.choice(EXERCISE_CATEGORIES[category])
    return f"💡 Suggested ({category.title()}) exercise: {exercise}"

# ---------- Helplines ----------
helplines = json.loads(HELPLINES_FILE.read_text(encoding="utf-8")) if HELPLINES_FILE.exists() else []

def get_helplines():
    if not helplines:
        return "No helplines available."
    return "\n".join([f"{h['name']}: {h['number']}" for h in helplines])

# ---------- Habit Tracker ----------
# ---------- Habit Tracker ----------
if HABITS_FILE.exists():
    with open(HABITS_FILE, "r", encoding="utf-8") as f:
        habits = json.load(f)
else:
    habits = [
        {"habit_id": 1, "habit_name": "Meditation"},
        {"habit_id": 2, "habit_name": "Exercise"},
        {"habit_id": 3, "habit_name": "Journaling"},
        {"habit_id": 4, "habit_name": "Mindful Breathing"},
        {"habit_id": 5, "habit_name": "Stretching"}
    ]
    for h in habits:
        h["records"] = []
    with open(HABITS_FILE, "w", encoding="utf-8") as f:
        json.dump(habits, f, indent=2)

# ✅ Ensure unique habits (no duplicates by name)
seen = set()
unique_habits = []
for h in habits:
    if h["habit_name"] not in seen:
        seen.add(h["habit_name"])
        if "records" not in h:
            h["records"] = []
        unique_habits.append(h)
habits = unique_habits
with open(HABITS_FILE, "w", encoding="utf-8") as f:
    json.dump(habits, f, indent=2)


def get_today_date():
    return datetime.today().strftime("%Y-%m-%d")


def get_today_habits():
    """Return today's habits, ensuring only one record per habit per day."""
    global habits
    today = get_today_date()
    today_habits = []

    for h in habits:
        # Ensure records key exists
        if "records" not in h:
            h["records"] = []

        # Find today's record
        record = next((r for r in h["records"] if r["date"] == today), None)
        if record:
            today_habits.append({
                "habit_id": h["habit_id"],
                "habit_name": h["habit_name"],
                "done": record["done"]
            })
        else:
            new_record = {"date": today, "done": False}
            h["records"].append(new_record)
            today_habits.append({
                "habit_id": h["habit_id"],
                "habit_name": h["habit_name"],
                "done": False
            })

    # Save back to file
    with open(HABITS_FILE, "w", encoding="utf-8") as f:
        json.dump(habits, f, indent=2)

    return today_habits


def mark_habit_done(habit_id: int):
    """Mark the given habit as done for today."""
    global habits
    today = get_today_date()

    for h in habits:
        if h["habit_id"] == habit_id:
            for r in h.get("records", []):
                if r["date"] == today:
                    r["done"] = True
                    break
            else:
                # If no record for today, create one
                h["records"].append({"date": today, "done": True})
            break

    # Save back to file
    with open(HABITS_FILE, "w", encoding="utf-8") as f:
        json.dump(habits, f, indent=2)


# ---------- Weekly Happiness ----------
def get_weekly_happiness(past_days=7):
    today = datetime.today()
    week_ago = today - timedelta(days=past_days)
    weekly_scores = []
    weekly_days = []

    for m in mood_history:
        date_str = m.get("date", "")
        if not date_str:
            continue
        try:
            entry_date = datetime.strptime(date_str, "%Y-%m-%d")
            if entry_date >= week_ago:
                weekly_scores.append(m.get("score", 0))
                weekly_days.append(entry_date.strftime("%a"))
        except ValueError:
            continue

    # Generate continuous list of days
    days = [(week_ago + timedelta(days=i)).strftime("%a") for i in range(past_days)]
    scores = []
    for d in days:
        if d in weekly_days:
            idx = weekly_days.index(d)
            scores.append(weekly_scores[idx])
        else:
            scores.append(0)
    return days, scores
