import streamlit as st
import json
from pathlib import Path
from datetime import datetime, timedelta
import plotly.graph_objects as go

# File paths
NUTRITION_FILE = Path("nutrition.json")
WATER_FILE = Path("water_log.json")
SLEEP_FILE = Path("sleep_log.json")

def load_data(filepath, default=None):
    if filepath.exists():
        return json.loads(filepath.read_text(encoding="utf-8"))
    return default or []

def save_data(filepath, data):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# ========== NUTRITION TRACKER ==========
def render_nutrition_tracker():
    st.title("🍎 Nutrition Tracker")
    
    nutrition_data = load_data(NUTRITION_FILE)
    today = datetime.today().strftime("%Y-%m-%d")
    
    st.subheader("📝 Log Today's Meals")
    
    col1, col2 = st.columns(2)
    
    with col1:
        meal_type = st.selectbox("Meal Type", ["Breakfast", "Lunch", "Dinner", "Snack"])
        meal_desc = st.text_input("What did you eat?")
    
    with col2:
        calories = st.number_input("Estimated Calories", min_value=0, step=50)
        portion = st.selectbox("Portion Size", ["Small", "Medium", "Large"])
    
    if st.button("Add Meal", type="primary"):
        if meal_desc:
            nutrition_data.append({
                "date": today,
                "meal_type": meal_type,
                "description": meal_desc,
                "calories": calories,
                "portion": portion,
                "timestamp": datetime.now().strftime("%I:%M %p")
            })
            save_data(NUTRITION_FILE, nutrition_data)
            st.success(f"✅ {meal_type} logged!")
            st.balloons()
        else:
            st.error("Please enter meal description")
    
    # Display today's meals
    st.subheader("📊 Today's Nutrition")
    today_meals = [m for m in nutrition_data if m.get("date") == today]
    
    if today_meals:
        total_calories = sum(m.get("calories", 0) for m in today_meals)
        
        st.metric("Total Calories Today", f"{total_calories} kcal")
        
        st.markdown("### Meals Logged")
        for meal in today_meals:
            st.markdown(f"""
            <div style="background: white; padding: 10px; border-radius: 10px; margin: 5px 0;">
                <strong>{meal['meal_type']}</strong> - {meal['description']}<br>
                <small>{meal['calories']} kcal | {meal['portion']} | {meal.get('timestamp', '')}</small>
            </div>
            """, unsafe_allow_html=True)
        
        # Weekly calorie chart
        st.subheader("📈 Weekly Calorie Intake")
        week_data = {}
        for i in range(7):
            date = (datetime.today() - timedelta(days=i)).strftime("%Y-%m-%d")
            day_meals = [m for m in nutrition_data if m.get("date") == date]
            week_data[date] = sum(m.get("calories", 0) for m in day_meals)
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=list(week_data.keys()),
            y=list(week_data.values()),
            marker_color='#52B788'
        ))
        fig.update_layout(
            title="Daily Calorie Intake",
            yaxis_title="Calories (kcal)",
            template="plotly_white"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No meals logged today. Start tracking your nutrition!")

# ========== WATER TRACKER ==========
def render_water_tracker():
    st.title("💧 Water Intake Tracker")
    
    water_data = load_data(WATER_FILE)
    today = datetime.today().strftime("%Y-%m-%d")
    
    # Get today's water count
    today_entry = next((w for w in water_data if w.get("date") == today), None)
    if not today_entry:
        today_entry = {"date": today, "glasses": 0, "goal": 8}
        water_data.append(today_entry)
    
    current_glasses = today_entry.get("glasses", 0)
    goal = today_entry.get("goal", 8)
    
    # Display progress
    st.subheader(f"💦 Today's Progress: {current_glasses}/{goal} glasses")
    
    # Progress bar
    progress = min(current_glasses / goal, 1.0)
    st.progress(progress)
    
    # Visual water glasses
    cols = st.columns(8)
    for i in range(8):
        with cols[i]:
            if i < current_glasses:
                st.markdown("💧", unsafe_allow_html=True)
            else:
                st.markdown("🫙", unsafe_allow_html=True)
    
    # Buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("➕ Add Glass", type="primary"):
            today_entry["glasses"] = min(current_glasses + 1, 20)
            save_data(WATER_FILE, water_data)
            st.success("💧 Glass added!")
            st.rerun()
    
    with col2:
        if st.button("➖ Remove Glass"):
            today_entry["glasses"] = max(current_glasses - 1, 0)
            save_data(WATER_FILE, water_data)
            st.rerun()
    
    with col3:
        if st.button("🔄 Reset Today"):
            today_entry["glasses"] = 0
            save_data(WATER_FILE, water_data)
            st.rerun()
    
    # Weekly chart
    st.subheader("📊 Weekly Water Intake")
    week_data = {}
    for i in range(7):
        date = (datetime.today() - timedelta(days=i)).strftime("%Y-%m-%d")
        entry = next((w for w in water_data if w.get("date") == date), None)
        week_data[date] = entry.get("glasses", 0) if entry else 0
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=list(week_data.keys()),
        y=list(week_data.values()),
        mode='lines+markers',
        line=dict(color='#00A8E8', width=3),
        marker=dict(size=10)
    ))
    fig.add_hline(y=8, line_dash="dash", line_color="green", 
                  annotation_text="Daily Goal")
    fig.update_layout(
        yaxis_title="Glasses of Water",
        template="plotly_white"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Tips
    if current_glasses < 4:
        st.warning("💡 **Hydration Tip:** You're behind on water! Try setting hourly reminders.")
    elif current_glasses >= goal:
        st.success("🎉 Amazing! You've hit your water goal today!")

# ========== SLEEP TRACKER ==========
def render_sleep_tracker():
    st.title("😴 Sleep Tracker")
    
    sleep_data = load_data(SLEEP_FILE)
    today = datetime.today().strftime("%Y-%m-%d")
    
    st.subheader("🌙 Log Your Sleep")
    
    col1, col2 = st.columns(2)
    
    with col1:
        sleep_time = st.time_input("Bedtime", value=None)
        wake_time = st.time_input("Wake Time", value=None)
    
    with col2:
        sleep_quality = st.select_slider(
            "Sleep Quality",
            options=["Poor", "Fair", "Good", "Great", "Excellent"],
            value="Good"
        )
        
        dreams = st.checkbox("Had vivid dreams?")
    
    if st.button("Log Sleep", type="primary"):
        if sleep_time and wake_time:
            # Calculate sleep duration
            from datetime import datetime as dt
            sleep_dt = dt.combine(dt.today(), sleep_time)
            wake_dt = dt.combine(dt.today(), wake_time)
            
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
            save_data(SLEEP_FILE, sleep_data)
            st.success(f"✅ Logged {duration:.1f} hours of sleep!")
            st.balloons()
        else:
            st.error("Please enter both sleep and wake times")
    
    # Display sleep history
    st.subheader("📊 Sleep History")
    
    if sleep_data:
        recent_sleep = [s for s in sleep_data if s.get("date")][-7:]
        
        if recent_sleep:
            # Calculate average
            avg_duration = sum(s.get("duration", 0) for s in recent_sleep) / len(recent_sleep)
            
            st.metric("Average Sleep (7 days)", f"{avg_duration:.1f} hours")
            
            # Sleep chart
            dates = [s["date"] for s in recent_sleep]
            durations = [s.get("duration", 0) for s in recent_sleep]
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=dates,
                y=durations,
                marker_color='#9D4EDD'
            ))
            fig.add_hline(y=7, line_dash="dash", line_color="green",
                         annotation_text="Recommended (7-9h)")
            fig.add_hline(y=9, line_dash="dash", line_color="green")
            fig.update_layout(
                title="Weekly Sleep Duration",
                yaxis_title="Hours",
                template="plotly_white"
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Sleep quality breakdown
            st.markdown("### Recent Sleep Logs")
            for s in reversed(recent_sleep[-5:]):
                quality_emoji = {
                    "Poor": "😴",
                    "Fair": "😐",
                    "Good": "😊",
                    "Great": "😄",
                    "Excellent": "⭐"
                }.get(s.get("quality"), "😴")
                
                st.markdown(f"""
                <div style="background: white; padding: 10px; border-radius: 10px; margin: 5px 0;">
                    <strong>{s['date']}</strong> {quality_emoji}<br>
                    🛏️ {s.get('sleep_time')} → ⏰ {s.get('wake_time')}<br>
                    ⏱️ {s.get('duration')} hours | Quality: {s.get('quality')}
                    {' | 💭 Dreams' if s.get('dreams') else ''}
                </div>
                """, unsafe_allow_html=True)
        
        # Sleep insights
        if avg_duration < 6:
            st.warning("⚠️ You're getting less than 6 hours of sleep. Consider improving your sleep schedule.")
        elif avg_duration < 7:
            st.info("💡 You're close to the recommended 7-9 hours. A bit more rest would be ideal!")
        else:
            st.success("✅ Great sleep pattern! You're getting adequate rest.")
    else:
        st.info("No sleep data yet. Start logging your sleep to see insights!")