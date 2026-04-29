from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy.sql import select
from typing import List, Dict, Tuple
import models
import schemas
import sys
import os
from database import SessionLocal, engine
import crud
from models import Base

def init_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    recipes_data = [
        {
            "title": "Курица с рисом по-домашнему",
            "ingredients": ["курица", "рис", "морковь", "лук", "соль", "перец"],
            "mandatory": ["курица", "рис"],
            "cooking_time": 45,
            "category": "Основное блюдо",
            "description": "Вкусное и сытное блюдо из курицы с рисом",
            "instructions": "1. Обжарьте курицу. 2. Добавьте овощи. 3. Добавьте рис и воду. 4. Тушите до готовности."
        },
        {
            "title": "Омлет с овощами",
            "ingredients": ["яйцо", "молоко", "помидор", "сыр", "соль"],
            "mandatory": ["яйцо"],
            "cooking_time": 15,
            "category": "Завтрак",
            "description": "Нежный омлет с овощами",
            "instructions": "1. Взбейте яйца с молоком. 2. Добавьте овощи. 3. Жарьте до готовности."
        },
        {
            "title": "Греческий салат",
            "ingredients": ["огурец", "помидор", "сыр фета", "маслины", "лук", "оливковое масло"],
            "mandatory": ["сыр фета", "огурец"],
            "cooking_time": 10,
            "category": "Салаты",
            "description": "Классический греческий салат",
            "instructions": "1. Нарежьте овощи. 2. Добавьте сыр фета. 3. Заправьте маслом."
        },
        {
            "title": "Макароны по-флотски",
            "ingredients": ["макароны", "фарш", "лук", "соль", "перец"],
            "mandatory": ["макароны", "фарш"],
            "cooking_time": 30,
            "category": "Основное блюдо",
            "description": "Сытные макароны с мясным фаршем",
            "instructions": "1. Отварите макароны. 2. Обжарьте фарш с луком. 3. Смешайте."
        },
        {
            "title": "Суп куриный с лапшой",
            "ingredients": ["курица", "лапша", "морковь", "лук", "картофель", "зелень"],
            "mandatory": ["курица", "лапша"],
            "cooking_time": 60,
            "category": "Суп",
            "description": "Ароматный куриный суп с лапшой",
            "instructions": "1. Сварите курицу. 2. Добавьте овощи. 3. Добавьте лапшу. 4. Варите до готовности."
        }
    ]
    
    for recipe in recipes_data:
        crud.create_recipe_simple(
            db,
            title=recipe["title"],
            ingredient_names=recipe["ingredients"],
            mandatory=recipe.get("mandatory", []),
            cooking_time=recipe.get("cooking_time", 30),
            category=recipe.get("category", "Основное блюдо"),
            description=recipe.get("description", ""),
            instructions=recipe.get("instructions", "")
        )
        print(f"✅ Добавлен рецепт: {recipe['title']}")

    ingredients = db.query(models.Ingredient).all()
    print(f"\n📝 Загружено ингредиентов: {len(ingredients)}")
    for ing in ingredients:
        print(f"  - {ing.name}")
    
    db.close()
    print("\n🎉 Тестовые данные загружены!")

if __name__ == "__main__":
    import models
    init_db()
