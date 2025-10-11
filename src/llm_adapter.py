import json
import os
from pathlib import Path
from datetime import datetime, timedelta
import random

# Import Gemini - FIXED VERSION
try:
    import google.generativeai as genai
    from dotenv import load_dotenv
    load_dotenv()
    
    # Configure Gemini with API key
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        genai.configure(api_key=api_key)
        print("✅ Gemini API configured successfully")
    else:
        print("⚠️ Warning: GEMINI_API_KEY not found in .env file")
except ImportError:
    print("⚠️ Warning: google-generativeai not installed")
    genai = None

# ---------- File Paths ----------
SESSION_FILE = Path("session_history.json")
MOOD_FILE = Path("mood.json")
HELPLINES_FILE = Path("helplines.json")
HABITS_FILE = Path("habits.json")

# ---------- Data Loading ----------
def load_json(filepath, default=None):
    """Load JSON file with error handling"""
    try:
        if filepath.exists():
            return json.loads(filepath.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
    return default or []

def save_json(filepath, data):
    """Save JSON file with error handling"""
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving {filepath}: {e}")

# Load data
session_history = load_json(SESSION_FILE, [])
mood_history = load_json(MOOD_FILE, [])
habits = load_json(HABITS_FILE, [
    {"habit_id": 1, "habit_name": "Meditation", "records": []},
    {"habit_id": 2, "habit_name": "Exercise", "records": []},
    {"habit_id": 3, "habit_name": "Journaling", "records": []},
    {"habit_id": 4, "habit_name": "Mindful Breathing", "records": []},
    {"habit_id": 5, "habit_name": "Stretching", "records": []}
])

# ---------- System Prompt ----------
SYSTEM_PROMPT = """You are TheraMate, a warm, empathetic, and supportive AI wellness companion. Your role is to:

1. **Listen actively** - Show genuine interest in the user's feelings and experiences
2. **Respond with empathy** - Validate emotions without judgment
3. **Encourage wellness** - Suggest healthy coping strategies and self-care
4. **Detect crisis** - If you notice severe distress, suicidal thoughts, or self-harm indicators, immediately recommend professional help and crisis helplines
5. **Stay supportive** - Use warm, gentle language with appropriate emojis 🌸💙
6. **Be concise** - Keep responses thoughtful but not overwhelming (2-4 sentences typically)

Important guidelines:
- You are NOT a medical professional and cannot diagnose or treat conditions
- For serious concerns, always recommend professional help
- Focus on emotional support, validation, and wellness tips
- Use a friendly, conversational tone
- Ask follow-up questions to show care
- Celebrate small wins and progress

Crisis keywords to watch for: suicide, kill myself, self-harm, end it all, no point living, etc.
If detected, respond with care and immediately suggest helplines."""

# ---------- WHO-5 Questions ----------
WHO5_QUESTIONS = [
    "I have felt cheerful and in good spirits",
    "I have felt calm and relaxed",
    "I have felt active and vigorous",
    "I woke up feeling fresh and rested",
    "My daily life has been filled with things that interest me"
]

# ---------- Gemini Chat Function - COMPLETELY FIXED ----------
def call_gemini(user_input: str, context: dict = None) -> str:
    """
    Call Gemini AI for response
    
    Args:
        user_input: User's message
        context: Optional context (mood score, streak, etc.)
    
    Returns:
        AI response string
    """
    
    if not genai:
        return "⚠️ AI service unavailable. Please install google-generativeai: pip install google-generativeai"
    
    if not os.getenv("GEMINI_API_KEY"):
        return "⚠️ Please add your GEMINI_API_KEY to the .env file. Get it from: https://aistudio.google.com/app/apikey"
    
    try:
        # Build context string
        context_str = ""
        if context:
            if context.get('mood_score'):
                context_str += f"\n[User's recent mood score: {context['mood_score']}/100]"
            if context.get('streak'):
                context_str += f"\n[User's wellness streak: {context['streak']} days]"
        
        # Build conversation history
        history_str = ""
        recent_history = session_history[-5:] if len(session_history) > 5 else session_history
        for entry in recent_history:
            if isinstance(entry, dict):
                history_str += f"User: {entry.get('user', '')}\n"
                history_str += f"Assistant: {entry.get('assistant', '')}\n"
        
        # Combine into full prompt
        full_prompt = f"{SYSTEM_PROMPT}\n{context_str}\n\nRecent conversation:\n{history_str}\nUser: {user_input}\n\nAssistant:"
        
        # Call Gemini - FIXED API CALL
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        response = model.generate_content(full_prompt)
        
        assistant_reply = response.text.strip()
        
        # Check for crisis keywords
        crisis_keywords = ['suicide', 'kill myself', 'self-harm', 'end it all', 'no point living', 'want to die']
        if any(keyword in user_input.lower() for keyword in crisis_keywords):
            assistant_reply += "\n\n🚨 I'm concerned about what you're sharing. Please reach out to a crisis helpline immediately - they're available 24/7 and can provide real support. You can find helplines in the 📞 Helplines section."
        
        # Save to history
        session_history.append({
            "user": user_input,
            "assistant": assistant_reply,
            "timestamp": datetime.now().isoformat()
        })
        save_session()
        
        return assistant_reply
        
    except Exception as e:
        print(f"Error calling Gemini: {e}")
        return f"I'm having trouble connecting right now. Please try again in a moment. 💙"

def save_session():
    """Save session history"""
    save_json(SESSION_FILE, session_history)

def save_mood():
    """Save mood history"""
    save_json(MOOD_FILE, mood_history)

# ---------- Calculate Streak - FIXED NAME ----------
def calculate_streak():
    """Calculate current wellness streak"""
    if not mood_history:
        return 0
    
    # Sort mood history by date (most recent first)
    sorted_moods = sorted(
        [m for m in mood_history if "date" in m],
        key=lambda x: datetime.strptime(x["date"], "%Y-%m-%d"),
        reverse=True
    )
    
    if not sorted_moods:
        return 0
    
    streak = 1
    today = datetime.today().date()
    last_date = datetime.strptime(sorted_moods[0]["date"], "%Y-%m-%d").date()
    
    # Check if the most recent entry is today or yesterday
    days_diff = (today - last_date).days
    if days_diff > 1:
        return 0  # Streak broken
    
    # Count consecutive days backwards
    for i in range(1, len(sorted_moods)):
        current_date = datetime.strptime(sorted_moods[i]["date"], "%Y-%m-%d").date()
        prev_date = datetime.strptime(sorted_moods[i-1]["date"], "%Y-%m-%d").date()
        
        # Check if dates are consecutive
        if (prev_date - current_date).days == 1:
            streak += 1
        else:
            break
    
    return streak

# ---------- Exercise Suggestions ----------
EXERCISE_CATEGORIES = {
    "relaxation": [
        "🌬️ 4-7-8 Breathing: Inhale 4s, hold 7s, exhale 8s (repeat 5 times)",
        "🧘 5-4-3-2-1 Grounding: Name 5 things you see, 4 you feel, 3 you hear, 2 you smell, 1 you taste",
        "🎵 Listen to calming music for 5 minutes",
        "💆 Progressive muscle relaxation: Tense and release each muscle group",
        "🌿 Light stretching for 5 minutes",
        "☕ Take a mindful tea/water break",
        "🎧 Guided meditation for 10 minutes"
    ],
    "mindfulness": [
        "📝 Journal 3 things you're grateful for today",
        "🚶 Mindful walk: Focus on each step and breath",
        "🧘 10-minute guided meditation",
        "🍃 Observe nature: Study a flower or tree mindfully",
        "🍽️ Mindful eating: Eat one thing very slowly, savoring each bite",
        "🛀 Body scan meditation: Notice sensations from head to toe",
        "🎶 Listen to ambient sounds with full attention"
    ],
    "energy": [
        "⏰ Pomodoro: 25 min focused work + 5 min break",
        "🏃 Quick cardio: 20 jumping jacks + 10 squats",
        "🚶 2-minute energizing walk outside",
        "🏃 5-minute brisk walk or climb stairs",
        "💪 10 push-ups and 15 sit-ups",
        "💃 Dance to an upbeat song",
        "🪟 Open a window, take 10 deep breaths, stretch arms"
    ]
}

def suggest_exercise(who5_score=None):
    """Suggest exercise based on WHO-5 score"""
    if who5_score is None:
        category = random.choice(list(EXERCISE_CATEGORIES.keys()))
    elif who5_score < 50:
        category = "relaxation"
    elif who5_score <= 75:
        category = "mindfulness"
    else:
        category = "energy"
    
    exercise = random.choice(EXERCISE_CATEGORIES[category])
    return f"💡 {category.title()} exercise: {exercise}"

# ---------- Helplines ----------
def get_helplines():
    """Get helpline information"""
    helplines_data = load_json(HELPLINES_FILE, {})
    if not helplines_data:
        return "Helplines data not available. Please check helplines.json file."
    
    output = "🆘 Mental Health Helplines:\n\n"
    output += helplines_data.get("safety_note", "") + "\n\n"
    
    india_wide = helplines_data.get("helplines", {}).get("india_wide", [])
    for h in india_wide[:3]:  # Show first 3
        if isinstance(h, dict):
            output += f"📞 {h.get('name', 'N/A')}: {h.get('number', 'N/A')}\n"
    
    return output

# ---------- Habit Tracker ----------
def get_today_date():
    """Get today's date string"""
    return datetime.today().strftime("%Y-%m-%d")

def get_today_habits():
    """Get today's habit checklist"""
    global habits
    today = get_today_date()
    today_habits = []
    
    for h in habits:
        if "records" not in h:
            h["records"] = []
        
        record = next((r for r in h["records"] if r.get("date") == today), None)
        
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
    
    save_json(HABITS_FILE, habits)
    return today_habits

def mark_habit_done(habit_id: int):
    """Mark habit as complete"""
    global habits
    today = get_today_date()
    
    for h in habits:
        if h["habit_id"] == habit_id:
            for r in h.get("records", []):
                if r["date"] == today:
                    r["done"] = True
                    break
            else:
                h["records"].append({"date": today, "done": True})
            break
    
    save_json(HABITS_FILE, habits)

# ---------- Weekly Happiness ----------
def get_weekly_happiness(days_back=7):
    """Get mood data for the past N days"""
    today = datetime.today()
    days = []
    scores = []
    
    for i in range(days_back):
        date = today - timedelta(days=days_back - 1 - i)
        date_str = date.strftime("%Y-%m-%d")
        day_label = date.strftime("%a")
        
        # Find mood entry for this date
        entry = next((m for m in mood_history if m.get("date") == date_str), None)
        
        days.append(day_label)
        scores.append(entry.get("score", 0) if entry else 0)
    
    return days, scores

# ---------- Wellness Insights ----------
def get_wellness_insights():
    """Generate insights based on recent data"""
    if not mood_history:
        return "Start logging your mood to see insights! 📊"
    
    recent_moods = [m.get("score", 50) for m in mood_history[-7:]]
    avg_mood = sum(recent_moods) / len(recent_moods)
    
    insights = []
    
    if avg_mood >= 80:
        insights.append("🌟 You're doing amazing! Your mood has been consistently positive.")
    elif avg_mood >= 60:
        insights.append("😊 You're maintaining good emotional balance. Keep it up!")
    elif avg_mood >= 40:
        insights.append("🌤️ Some ups and downs this week. That's normal - be gentle with yourself.")
    else:
        insights.append("💙 It's been challenging lately. Remember to reach out for support when needed.")
    
    # Habit insights
    today_habits = get_today_habits()
    completed = sum(1 for h in today_habits if h.get("done"))
    if completed >= 3:
        insights.append(f"✅ Great job completing {completed} habits today!")
    
    # Streak insight
    streak = calculate_streak()
    if streak >= 7:
        insights.append(f"🔥 Amazing {streak}-day streak! You're building great wellness habits!")
    
    return "\n".join(insights)