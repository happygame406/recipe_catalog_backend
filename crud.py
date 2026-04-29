from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict, Tuple
import models
import schemas

# === CRUD для ингредиентов ===
def get_ingredient_by_name(db: Session, name: str):
    return db.query(models.Ingredient).filter(models.Ingredient.name == name).first()

def create_ingredient(db: Session, ingredient: schemas.IngredientCreate):
    db_ingredient = models.Ingredient(name=ingredient.name)
    db.add(db_ingredient)
    db.commit()
    db.refresh(db_ingredient)
    return db_ingredient

def get_or_create_ingredient(db: Session, name: str):
    ingredient = get_ingredient_by_name(db, name)
    if not ingredient:
        ingredient = create_ingredient(db, schemas.IngredientCreate(name=name))
    return ingredient

# === CRUD для рецептов ===
def get_recipe(db: Session, recipe_id: int):
    return db.query(models.Recipe).filter(models.Recipe.id == recipe_id).first()

def create_recipe(db: Session, recipe: schemas.RecipeCreate):
    # Создаем рецепт
    db_recipe = models.Recipe(
        title=recipe.title,
        description=recipe.description,
        instructions=recipe.instructions,
        cooking_time_minutes=recipe.cooking_time_minutes,
        category=recipe.category
    )
    db.add(db_recipe)
    db.flush()  # чтобы получить id рецепта без коммита
    
    # Добавляем ингредиенты через ассоциативную таблицу
    for ri in recipe.ingredients:
        # Получаем ингредиент по ID
        ingredient = db.query(models.Ingredient).filter(models.Ingredient.id == ri.ingredient_id).first()
        if ingredient:
            # Добавляем связь через ассоциативную таблицу
            db.execute(
                models.recipe_ingredient.insert().values(
                    recipe_id=db_recipe.id,
                    ingredient_id=ingredient.id,
                    weight=ri.weight,
                    is_mandatory=1 if ri.is_mandatory else 0  # конвертируем bool в int
                )
            )
    
    db.commit()
    db.refresh(db_recipe)
    return db_recipe

# === АЛГОРИТМ ПОДБОРА РЕЦЕПТОВ ПО ИНГРЕДИЕНТАМ ===
def search_recipes_by_ingredients(
    db: Session, 
    user_ingredients: List[str],
    min_match_percent: float = 0.0,
    limit: int = 20
) -> List[schemas.SearchResultItem]:
    """
    Основной алгоритм:
    1. Для каждого рецепта вычисляем процент совпадения имеющихся ингредиентов.
    2. Если в рецепте есть обязательный ингредиент (is_mandatory=1) и его НЕТ у пользователя → рецепт отбрасывается.
    3. Возвращаем отсортированный список.
    """
    # Получаем все рецепты с их ингредиентами
    recipes = db.query(models.Recipe).all()
    
    user_ingredients_lower = [i.lower().strip() for i in user_ingredients]
    results = []
    
    for recipe in recipes:
        # Получаем ингредиенты рецепта с их свойствами через ассоциативную таблицу
        recipe_ingredients_data = []
        mandatory_ingredients = []
        
        # Запрос к ассоциативной таблице
        stmt = db.query(
            models.recipe_ingredient.c.ingredient_id,
            models.recipe_ingredient.c.is_mandatory,
            models.Ingredient.name
        ).join(
            models.Ingredient,
            models.recipe_ingredient.c.ingredient_id == models.Ingredient.id
        ).filter(
            models.recipe_ingredient.c.recipe_id == recipe.id
        )
        
        for ing_id, is_mandatory, ing_name in stmt:
            ing_name_lower = ing_name.lower()
            recipe_ingredients_data.append(ing_name_lower)
            if is_mandatory == 1:
                mandatory_ingredients.append(ing_name_lower)
        
        # Проверка обязательных ингредиентов
        all_mandatory_present = True
        for mand in mandatory_ingredients:
            if mand not in user_ingredients_lower:
                all_mandatory_present = False
                break
        
        if not all_mandatory_present:
            continue  # пропускаем рецепт
        
        # Вычисляем совпадение
        matched = 0
        for ing in recipe_ingredients_data:
            if ing in user_ingredients_lower:
                matched += 1
        
        total = len(recipe_ingredients_data)
        if total == 0:
            match_percent = 0.0
        else:
            match_percent = (matched / total) * 100
        
        # Фильтр по минимальному проценту
        if match_percent >= min_match_percent:
            # Определяем недостающие ингредиенты
            missing = [ing for ing in recipe_ingredients_data if ing not in user_ingredients_lower]
            
            results.append(schemas.SearchResultItem(
                recipe_id=recipe.id,
                title=recipe.title,
                match_percent=round(match_percent, 2),
                missing_ingredients=missing,
                cooking_time_minutes=recipe.cooking_time_minutes
            ))
    
    # Сортируем по убыванию процента совпадения
    results.sort(key=lambda x: x.match_percent, reverse=True)
    
    # Ограничиваем количество
    return results[:limit]

# Простая версия создания рецепта (для seed.py)
def create_recipe_simple(db: Session, title: str, ingredient_names: List[str], **kwargs):
    db_recipe = models.Recipe(
        title=title,
        description=kwargs.get("description", ""),
        instructions=kwargs.get("instructions", ""),
        cooking_time_minutes=kwargs.get("cooking_time", 30),
        category=kwargs.get("category", "Основное блюдо")
    )
    db.add(db_recipe)
    db.flush()
    
    mandatory_list = [m.lower() for m in kwargs.get("mandatory", [])]
    
    for ing_name in ingredient_names:
        ingredient = get_or_create_ingredient(db, ing_name)
        # Добавляем в ассоциативную таблицу
        db.execute(
            models.recipe_ingredient.insert().values(
                recipe_id=db_recipe.id,
                ingredient_id=ingredient.id,
                weight=1.0,
                is_mandatory=1 if ing_name.lower() in mandatory_list else 0
            )
        )
    
    db.commit()
    db.refresh(db_recipe)
    return db_recipe