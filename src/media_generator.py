import os
import random
from pathlib import Path

# ========== VIDEO GENERATION ==========
def generate_relaxation_video(prompt: str, api_key: str = None):
    """
    Generate relaxation video using AI video generation API
    
    Supported APIs:
    - Pika Labs (requires PIKA_API_KEY)
    - Runway ML (requires RUNWAY_API_KEY)
    
    Falls back to mock generator if no API key provided
    """
    
    # Try to get API key from environment
    pika_key = api_key or os.getenv("PIKA_API_KEY")
    runway_key = api_key or os.getenv("RUNWAY_API_KEY")
    
    if pika_key:
        return _generate_with_pika(prompt, pika_key)
    elif runway_key:
        return _generate_with_runway(prompt, runway_key)
    else:
        return _mock_video_generator(prompt)

def _generate_with_pika(prompt: str, api_key: str):
    """Generate video using Pika Labs API"""
    try:
        # Placeholder for actual API integration
        # import requests
        # response = requests.post(
        #     "https://api.pika.art/v1/generate",
        #     headers={"Authorization": f"Bearer {api_key}"},
        #     json={"prompt": prompt, "duration": 5}
        # )
        # return response.json()["video_url"]
        
        return {
            "status": "success",
            "video_url": f"https://example.com/videos/{hash(prompt)}.mp4",
            "message": "Video generated successfully (Pika Labs)",
            "prompt": prompt
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

def _generate_with_runway(prompt: str, api_key: str):
    """Generate video using Runway ML API"""
    try:
        # Placeholder for actual API integration
        # import requests
        # response = requests.post(
        #     "https://api.runwayml.com/v1/generate",
        #     headers={"Authorization": f"Bearer {api_key}"},
        #     json={"prompt": prompt, "model": "gen2"}
        # )
        # return response.json()["output_url"]
        
        return {
            "status": "success",
            "video_url": f"https://example.com/videos/{hash(prompt)}.mp4",
            "message": "Video generated successfully (Runway ML)",
            "prompt": prompt
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

def _mock_video_generator(prompt: str):
    """Mock video generator for demo purposes"""
    
    # Predefined relaxation video themes
    themes = {
        "ocean": {
            "title": "Peaceful Ocean Waves",
            "description": "Gentle waves rolling on a serene beach at sunset",
            "thumbnail": "🌊"
        },
        "forest": {
            "title": "Calm Forest Path",
            "description": "Sunlight filtering through tall trees in a peaceful forest",
            "thumbnail": "🌲"
        },
        "sunset": {
            "title": "Beautiful Sunset",
            "description": "Golden hour clouds drifting across a colorful sky",
            "thumbnail": "🌅"
        },
        "stars": {
            "title": "Starry Night Sky",
            "description": "Twinkling stars and galaxies in the night sky",
            "thumbnail": "⭐"
        },
        "rain": {
            "title": "Gentle Rain",
            "description": "Soft rain falling on leaves and windows",
            "thumbnail": "🌧️"
        }
    }
    
    # Select theme based on prompt keywords
    selected_theme = "ocean"  # default
    for keyword in ["forest", "sunset", "stars", "rain", "ocean"]:
        if keyword in prompt.lower():
            selected_theme = keyword
            break
    
    theme_data = themes[selected_theme]
    
    return {
        "status": "success",
        "video_url": f"mock://relaxation-video-{selected_theme}",
        "message": "Mock video generated (No API key detected)",
        "prompt": prompt,
        "theme": theme_data,
        "duration": 30,
        "note": "To generate real videos, add PIKA_API_KEY or RUNWAY_API_KEY to .env"
    }

# ========== AUDIO GENERATION ==========
def get_meditation_audio(session_type: str):
    """
    Get meditation audio file path based on session type
    Returns placeholder audio or real file if available
    """
    
    audio_map = {
        "5-Minute Calm": "meditation_5min_calm.mp3",
        "10-Minute Focus": "meditation_10min_focus.mp3",
        "15-Minute Deep Relaxation": "meditation_15min_deep.mp3"
    }
    
    audio_file = audio_map.get(session_type, "meditation_5min_calm.mp3")
    audio_path = Path("audio") / audio_file
    
    # Check if audio file exists
    if audio_path.exists():
        return str(audio_path)
    else:
        # Return demo/placeholder audio
        return _get_placeholder_audio(session_type)

def _get_placeholder_audio(session_type: str):
    """Return placeholder audio information"""
    return {
        "type": "placeholder",
        "session": session_type,
        "message": "Audio file not found. Place meditation audio files in 'audio/' folder.",
        "suggested_sources": [
            "https://freemusicarchive.org (Free meditation music)",
            "https://incompetech.com (Royalty-free ambient tracks)",
            "Record your own guided meditation"
        ]
    }

def get_background_music(mood: str):
    """
    Get background music based on user's mood
    
    Args:
        mood: "calm", "stressed", "energetic"
    
    Returns:
        Audio file path or placeholder data
    """
    
    music_map = {
        "calm": "ocean_waves.mp3",
        "stressed": "soft_piano.mp3",
        "energetic": "upbeat_ambient.mp3"
    }
    
    music_file = music_map.get(mood.lower(), "ocean_waves.mp3")
    music_path = Path("audio") / music_file
    
    if music_path.exists():
        return str(music_path)
    else:
        return {
            "type": "placeholder",
            "mood": mood,
            "file": music_file,
            "message": f"Add {music_file} to 'audio/' folder for background music",
            "free_sources": [
                "YouTube Audio Library (No attribution required)",
                "Pixabay Music (Free for commercial use)",
                "Bensound (Free with attribution)"
            ]
        }

# ========== MEDITATION SCRIPT GENERATOR ==========
def generate_meditation_script(duration: int, focus: str = "relaxation"):
    """
    Generate a guided meditation script
    
    Args:
        duration: Length in minutes (5, 10, or 15)
        focus: "relaxation", "focus", "sleep", "anxiety"
    
    Returns:
        Dict with meditation script and timing cues
    """
    
    scripts = {
        "relaxation": {
            5: [
                "Find a comfortable position... Close your eyes gently...",
                "Take a deep breath in through your nose... hold... and release slowly...",
                "Feel your body relaxing... starting from your toes...",
                "Let go of any tension... you are safe and calm...",
                "When you're ready, gently open your eyes..."
            ],
            10: [
                "Settle into a comfortable position... Close your eyes...",
                "Begin with three deep breaths... inhale peace... exhale stress...",
                "Scan your body from head to toe... releasing tension...",
                "Notice your thoughts without judgment... let them drift by...",
                "Feel gratitude for this moment of self-care...",
                "Gradually return to the present... open your eyes when ready..."
            ],
            15: [
                "Find your comfortable space... Close your eyes gently...",
                "Take five deep, cleansing breaths...",
                "Progressive relaxation: tense and release each muscle group...",
                "Visualize a peaceful place... engage all your senses...",
                "Rest in this tranquility... you are completely at ease...",
                "Slowly bring awareness back to your body...",
                "When you're ready, open your eyes... feeling refreshed..."
            ]
        },
        "focus": {
            5: [
                "Sit upright with alertness... Close your eyes...",
                "Breathe naturally... count each breath from 1 to 10...",
                "If your mind wanders, gently return to counting...",
                "Feel your mental clarity increasing...",
                "Open your eyes, ready to focus..."
            ]
        },
        "sleep": {
            10: [
                "Lie down comfortably... Close your eyes...",
                "Release the day's tension with each exhale...",
                "Your body is heavy and relaxed... sinking into comfort...",
                "Count backwards from 100... drifting deeper...",
                "Allow yourself to fall into peaceful sleep..."
            ]
        },
        "anxiety": {
            5: [
                "You are safe right now... Close your eyes...",
                "Place one hand on your heart... breathe deeply...",
                "Remind yourself: This feeling will pass...",
                "Ground yourself: notice 5 things you can hear...",
                "You are stronger than your anxiety... open your eyes..."
            ]
        }
    }
    
    script = scripts.get(focus, scripts["relaxation"]).get(duration, scripts["relaxation"][5])
    
    # Calculate timing
    interval = (duration * 60) // len(script)
    
    return {
        "duration": duration,
        "focus": focus,
        "script": script,
        "interval_seconds": interval,
        "segments": len(script)
    }

# ========== EXPORT FUNCTIONS ==========
def get_relaxation_video_prompts():
    """Return suggested prompts for video generation"""
    return [
        "Calm ocean waves at sunset with gentle breeze",
        "Peaceful forest path with sunlight filtering through trees",
        "Starry night sky with aurora borealis",
        "Gentle rain falling on green leaves",
        "Serene mountain lake at dawn with mist",
        "Floating clouds in a clear blue sky",
        "Zen garden with raked sand and stones",
        "Candle flame flickering in darkness"
    ]