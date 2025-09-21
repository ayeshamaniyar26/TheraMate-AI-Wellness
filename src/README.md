# 🌱 TheraMate - Your Friendly AI Therapy Companion

TheraMate is an **AI-powered mental wellness web app** built with **Streamlit**.  
It helps users improve their mental health through **interactive features**, including:  
- A chatbot for emotional support 🤖  
- Mood tracking with visual graphs 🌈  
- Fun relaxation & self-care exercises 🎮  
- Personalized journaling and gratitude reflection 📓  
- Access to verified mental health helplines ☎️  

Designed to be **simple, calming, and user-friendly**, TheraMate provides a safe virtual space where users can track their emotions, build positive habits, and seek help when needed.  

---

## ✨ Features

### 🔐 Secure Login
- Users enter a **nickname & password** to start.  
- Session management ensures privacy and safety.  

### 💬 AI Chatbot (TheraMate)
- Chat with a **friendly AI therapist** powered by Gemini.  
- Conversations are stored locally in your session state.  
- Minimalist, soft chat UI for a calm experience.  

### 🌈 Mood Tracker
- Daily mood ratings are visualized in a **Plotly line graph**.  
- Emoji indicators (`😢`, `😐`, `😄`) show mood trends.  
- Selectable time range: last **7, 14, or 30 days**.  

### 🎮 Wellness Games
TheraMate includes several **interactive games & exercises**:
- **Would You Rather?** 🤔 → Fun choices that spark reflection.  
- **Gratitude Spinner** 🌸 → Encourages sharing gratitude.    
- **Emoji Mood Match** 🎨 → Express mood using colors/emojis.  
- **Positive Affirmation Cards** ✨ → Random uplifting messages.  

### 📝 Daily Reflection
- Journaling prompts help record your thoughts.  
- Gratitude & mood entries saved per day.  
- Closing affirmations encourage positivity.  

### ☎️ Verified Helplines
- **India-wide & state-specific helplines**.  
- Includes name, number, supported languages, and availability.  
- Encourages reaching out in times of need.  

---

## 🛠️ Project Structure

mental_health_app/
│
├── src/ # Source code
│ ├── app.py # Main Streamlit application
│ ├── embeddings_store.py # LLM adapter / embeddings (if used)
│ ├── exercises.json # Breathing & relaxation activities
│ ├── games.json # Wellness games data
│ └── .env # API keys & secrets
│
├── data/ # (Optional) Saved user/session data
│
├── requirements.txt # Python dependencies
└── README.md # Project documentation