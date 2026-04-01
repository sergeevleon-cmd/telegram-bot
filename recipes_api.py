import requests
import logging

logger = logging.getLogger(__name__)

BASE_URL = "https://www.themealdb.com/api/json/v1/1"


def translate_to_russian(text):
    """Переводит текст на русский язык через бесплатный API"""
    if not text or not text.strip():
        return text
    
    try:
        url = "https://translate.googleapis.com/translate_a/single"
        params = {
            "client": "gtx",
            "sl": "en",
            "tl": "ru",
            "dt": "t",
            "q": text
        }
        response = requests.get(url, params=params, timeout=5)
        if response.status_code == 200:
            result = response.json()
            translated = result[0][0][0]
            return translated
        return text
    except Exception as e:
        logger.warning(f"Translation failed for '{text[:50]}': {e}")
        return text


def get_random_recipe():
    """Получает случайный рецепт"""
    try:
        response = requests.get(f"{BASE_URL}/random.php", timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if "meals" in data and data["meals"]:
            return data["meals"][0]
        return None
    except Exception as e:
        logger.error(f"Error getting random recipe: {e}")
        return None


def search_recipe_by_name(name):
    """Ищет рецепты по названию"""
    try:
        response = requests.get(f"{BASE_URL}/search.php?s={name}", timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if "meals" in data and data["meals"]:
            return data["meals"]
        return []
    except Exception as e:
        logger.error(f"Error searching recipe by name: {e}")
        return []


def get_categories():
    """Получает список категорий"""
    try:
        response = requests.get(f"{BASE_URL}/categories.php", timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if "categories" in data:
            return data["categories"]
        return []
    except Exception as e:
        logger.error(f"Error getting categories: {e}")
        return []


def get_recipes_by_category(category):
    """Получает рецепты по категории"""
    try:
        response = requests.get(f"{BASE_URL}/filter.php?c={category}", timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if "meals" in data and data["meals"]:
            return data["meals"]
        return []
    except Exception as e:
        logger.error(f"Error getting recipes by category: {e}")
        return []


def get_areas():
    """Получает список кухонь мира"""
    try:
        response = requests.get(f"{BASE_URL}/list.php?a=list", timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if "meals" in data:
            return data["meals"]
        return []
    except Exception as e:
        logger.error(f"Error getting areas: {e}")
        return []


def get_recipes_by_area(area):
    """Получает рецепты по кухне мира"""
    try:
        response = requests.get(f"{BASE_URL}/filter.php?a={area}", timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if "meals" in data and data["meals"]:
            return data["meals"]
        return []
    except Exception as e:
        logger.error(f"Error getting recipes by area: {e}")
        return []


def get_recipe_by_id(meal_id):
    """Получает полную информацию о рецепте по ID"""
    try:
        response = requests.get(f"{BASE_URL}/lookup.php?i={meal_id}", timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if "meals" in data and data["meals"]:
            return data["meals"][0]
        return None
    except Exception as e:
        logger.error(f"Error getting recipe by ID: {e}")
        return None


def format_recipe_text(meal, include_instructions=False):
    """Форматирует текст рецепта для отправки на русском языке"""
    if not meal:
        return "Рецепт не найден"
    
    meal_name_ru = translate_to_russian(meal['strMeal'])
    category_ru = translate_to_russian(meal.get('strCategory', 'N/A'))
    area_ru = translate_to_russian(meal.get('strArea', 'N/A'))
    
    text = f"🍽️ *{meal_name_ru}*\n\n"
    text += f"📂 Категория: {category_ru}\n"
    text += f"🌍 Кухня: {area_ru}\n\n"
    
    ingredients = []
    for i in range(1, 21):
        ingredient = meal.get(f"strIngredient{i}")
        measure = meal.get(f"strMeasure{i}")
        if ingredient and ingredient.strip():
            ingredient_ru = translate_to_russian(ingredient)
            measure_ru = translate_to_russian(measure) if measure and measure.strip() else ""
            ingredients.append(f"• {measure_ru} {ingredient_ru}".strip())
    
    if ingredients:
        text += "*Ингредиенты:*\n"
        text += "\n".join(ingredients[:15])
        if len(ingredients) > 15:
            text += f"\n_...и еще {len(ingredients) - 15} ингредиентов_"
    
    if include_instructions and meal.get("strInstructions"):
        instructions = meal["strInstructions"]
        if len(instructions) > 1000:
            instructions = instructions[:1000] + "..."
        instructions_ru = translate_to_russian(instructions)
        text += f"\n\n📝 *Инструкция:*\n{instructions_ru}"
    
    return text
