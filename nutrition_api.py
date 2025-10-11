"""
Nutrition API Integration for TheraMate
Supports CalorieNinjas, Edamam, and fallback database
"""

import os
import requests
from typing import Dict, Optional

# Load API keys from environment
CALORIE_NINJAS_KEY = os.getenv("CALORIE_NINJAS_API_KEY")
EDAMAM_APP_ID = os.getenv("EDAMAM_APP_ID")
EDAMAM_APP_KEY = os.getenv("EDAMAM_APP_KEY")

# Fallback nutrition database (common foods)
NUTRITION_DATABASE = {
    # Fruits
    "banana": {"calories": 105, "protein": 1.3, "carbs": 27, "fat": 0.4},
    "apple": {"calories": 95, "protein": 0.5, "carbs": 25, "fat": 0.3},
    "orange": {"calories": 62, "protein": 1.2, "carbs": 15, "fat": 0.2},
    "mango": {"calories": 99, "protein": 1.4, "carbs": 25, "fat": 0.6},
    "grapes": {"calories": 104, "protein": 1.1, "carbs": 27, "fat": 0.2},
    
    # Vegetables
    "rice": {"calories": 206, "protein": 4.3, "carbs": 45, "fat": 0.4},
    "potato": {"calories": 163, "protein": 4.3, "carbs": 37, "fat": 0.2},
    "carrot": {"calories": 41, "protein": 0.9, "carbs": 10, "fat": 0.2},
    "broccoli": {"calories": 55, "protein": 3.7, "carbs": 11, "fat": 0.6},
    "salad": {"calories": 50, "protein": 2, "carbs": 8, "fat": 1},
    
    # Proteins
    "chicken": {"calories": 165, "protein": 31, "carbs": 0, "fat": 3.6},
    "egg": {"calories": 78, "protein": 6.3, "carbs": 0.6, "fat": 5.3},
    "fish": {"calories": 206, "protein": 22, "carbs": 0, "fat": 12},
    "paneer": {"calories": 265, "protein": 18, "carbs": 3.6, "fat": 20},
    "tofu": {"calories": 144, "protein": 15, "carbs": 3, "fat": 9},
    
    # Grains & Bread
    "bread": {"calories": 79, "protein": 2.7, "carbs": 15, "fat": 1},
    "roti": {"calories": 71, "protein": 3, "carbs": 15, "fat": 0.4},
    "pasta": {"calories": 200, "protein": 7, "carbs": 40, "fat": 1},
    "noodles": {"calories": 221, "protein": 7, "carbs": 43, "fat": 2.6},
    "oats": {"calories": 389, "protein": 17, "carbs": 66, "fat": 7},
    
    # Dairy
    "milk": {"calories": 149, "protein": 7.7, "carbs": 12, "fat": 8},
    "yogurt": {"calories": 100, "protein": 5.7, "carbs": 7.7, "fat": 5},
    "cheese": {"calories": 113, "protein": 7, "carbs": 0.9, "fat": 9},
    "butter": {"calories": 102, "protein": 0.1, "carbs": 0, "fat": 11.5},
    
    # Fast Food
    "pizza": {"calories": 285, "protein": 12, "carbs": 36, "fat": 10},
    "burger": {"calories": 354, "protein": 17, "carbs": 30, "fat": 18},
    "fries": {"calories": 312, "protein": 3.4, "carbs": 41, "fat": 15},
    "sandwich": {"calories": 200, "protein": 10, "carbs": 25, "fat": 7},
    
    # Indian Foods
    "dosa": {"calories": 133, "protein": 2.5, "carbs": 20, "fat": 4.3},
    "idli": {"calories": 58, "protein": 2, "carbs": 11, "fat": 0.5},
    "samosa": {"calories": 252, "protein": 4, "carbs": 34, "fat": 11},
    "dal": {"calories": 115, "protein": 7, "carbs": 20, "fat": 0.8},
    "biryani": {"calories": 290, "protein": 6, "carbs": 43, "fat": 10},
    
    # Snacks
    "chips": {"calories": 152, "protein": 2, "carbs": 15, "fat": 10},
    "biscuit": {"calories": 50, "protein": 0.7, "carbs": 7.5, "fat": 2},
    "chocolate": {"calories": 235, "protein": 2.2, "carbs": 29, "fat": 13},
    "cake": {"calories": 257, "protein": 2.9, "carbs": 36, "fat": 12}
}

def get_nutrition_info(food_item: str) -> Optional[Dict]:
    """
    Get nutrition information for a food item.
    Tries APIs first, then falls back to local database.
    
    Args:
        food_item: Name of the food item
    
    Returns:
        Dictionary with calories, protein, carbs, fat or None
    """
    
    food_item = food_item.strip().lower()
    
    # Try CalorieNinjas API
    if CALORIE_NINJAS_KEY:
        result = _get_from_calorie_ninjas(food_item)
        if result:
            return result
    
    # Try Edamam API
    if EDAMAM_APP_ID and EDAMAM_APP_KEY:
        result = _get_from_edamam(food_item)
        if result:
            return result
    
    # Fallback to local database
    return _get_from_database(food_item)

def _get_from_calorie_ninjas(food_item: str) -> Optional[Dict]:
    """Query CalorieNinjas API"""
    try:
        url = "https://api.calorieninjas.com/v1/nutrition"
        headers = {"X-Api-Key": CALORIE_NINJAS_KEY}
        params = {"query": food_item}
        
        response = requests.get(url, headers=headers, params=params, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("items"):
                item = data["items"][0]
                return {
                    "calories": round(item.get("calories", 0)),
                    "protein": round(item.get("protein_g", 0), 1),
                    "carbs": round(item.get("carbohydrates_total_g", 0), 1),
                    "fat": round(item.get("fat_total_g", 0), 1),
                    "source": "CalorieNinjas API"
                }
    except Exception as e:
        print(f"CalorieNinjas API error: {e}")
    
    return None

def _get_from_edamam(food_item: str) -> Optional[Dict]:
    """Query Edamam API"""
    try:
        url = "https://api.edamam.com/api/nutrition-data"
        params = {
            "app_id": EDAMAM_APP_ID,
            "app_key": EDAMAM_APP_KEY,
            "ingr": f"1 {food_item}"
        }
        
        response = requests.get(url, params=params, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("calories"):
                return {
                    "calories": round(data.get("calories", 0)),
                    "protein": round(data.get("totalNutrients", {}).get("PROCNT", {}).get("quantity", 0), 1),
                    "carbs": round(data.get("totalNutrients", {}).get("CHOCDF", {}).get("quantity", 0), 1),
                    "fat": round(data.get("totalNutrients", {}).get("FAT", {}).get("quantity", 0), 1),
                    "source": "Edamam API"
                }
    except Exception as e:
        print(f"Edamam API error: {e}")
    
    return None

def _get_from_database(food_item: str) -> Optional[Dict]:
    """Get nutrition info from local database"""
    # Direct match
    if food_item in NUTRITION_DATABASE:
        result = NUTRITION_DATABASE[food_item].copy()
        result["source"] = "Local Database"
        return result
    
    # Fuzzy match - check if food_item contains any key
    for key, value in NUTRITION_DATABASE.items():
        if key in food_item or food_item in key:
            result = value.copy()
            result["source"] = "Local Database"
            result["matched_as"] = key
            return result
    
    return None

def get_quick_estimate(food_item: str) -> int:
    """
    Get a quick calorie estimate for a food item.
    Returns just the calorie value.
    """
    info = get_nutrition_info(food_item)
    return info.get("calories", 0) if info else 0

def format_nutrition_info(info: Dict) -> str:
    """Format nutrition info for display"""
    if not info:
        return "Nutrition information not available"
    
    output = f"""
📊 **Nutrition Information**
- 🔥 Calories: {info.get('calories', 0)} kcal
- 💪 Protein: {info.get('protein', 0)}g
- 🍚 Carbs: {info.get('carbs', 0)}g
- 🧈 Fat: {info.get('fat', 0)}g
- 📖 Source: {info.get('source', 'Unknown')}
"""
    
    if info.get("matched_as"):
        output += f"\n*Matched as: {info['matched_as']}*"
    
    return output

def search_food_suggestions(query: str, limit: int = 5) -> list:
    """
    Get food suggestions based on partial query
    """
    if not query:
        return []
    
    query = query.lower()
    suggestions = []
    
    for food in NUTRITION_DATABASE.keys():
        if query in food:
            suggestions.append(food)
            if len(suggestions) >= limit:
                break
    
    return suggestions

# Export main functions
__all__ = [
    'get_nutrition_info',
    'get_quick_estimate',
    'format_nutrition_info',
    'search_food_suggestions'
]