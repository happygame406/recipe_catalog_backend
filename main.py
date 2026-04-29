from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

import models
import schemas
import crud
from database import engine, get_db

# Создаем таблицы в БД
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Recipe Catalog API",
    description="Backend для каталога рецептов с подбором по ингредиентам",
    version="1.0.0"
)

# === Эндпоинты для ингредиентов ===
@app.get("/ingredients", response_model=List[schemas.Ingredient])
def read_ingredients(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    ingredients = db.query(models.Ingredient).offset(skip).limit(limit).all()
    return ingredients

@app.post("/ingredients", response_model=schemas.Ingredient)
def create_ingredient(ingredient: schemas.IngredientCreate, db: Session = Depends(get_db)):
    existing = crud.get_ingredient_by_name(db, ingredient.name)
    if existing:
        raise HTTPException(status_code=400, detail="Ingredient already exists")
    return crud.create_ingredient(db, ingredient)

# === Эндпоинты для рецептов ===
@app.get("/recipes", response_model=List[schemas.Recipe])
def read_recipes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    recipes = db.query(models.Recipe).offset(skip).limit(limit).all()
    return recipes

@app.get("/recipes/{recipe_id}", response_model=schemas.Recipe)
def read_recipe(recipe_id: int, db: Session = Depends(get_db)):
    recipe = crud.get_recipe(db, recipe_id)
    if recipe is None:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe

@app.post("/recipes", response_model=schemas.Recipe)
def create_recipe(recipe: schemas.RecipeCreate, db: Session = Depends(get_db)):
    return crud.create_recipe(db, recipe)

# === ГЛАВНЫЙ ЭНДПОИНТ: поиск по ингредиентам ===
@app.post("/recipes/search/by-ingredients", response_model=schemas.SearchResponse)
def search_by_ingredients(
    request: schemas.SearchRequest,
    db: Session = Depends(get_db)
):
    """
    Ищет рецепты на основе списка ингредиентов пользователя.
    
    Пример тела запроса:
    {
        "user_ingredients": ["курица", "рис", "морковь", "лук"],
        "min_match_percent": 30,
        "limit": 10
    }
    """
    results = crud.search_recipes_by_ingredients(
        db,
        user_ingredients=request.user_ingredients,
        min_match_percent=request.min_match_percent,
        limit=request.limit
    )
    
    return schemas.SearchResponse(
        results=results,
        total_found=len(results)
    )

# === Простой поиск через GET (для удобства тестирования) ===
@app.get("/recipes/search/quick", response_model=schemas.SearchResponse)
def quick_search(
    ingredients: str = Query(..., description="Ингредиенты через запятую, например: курица,рис,лук"),
    min_match: float = Query(0.0, ge=0, le=100),
    limit: int = Query(20, le=100),
    db: Session = Depends(get_db)
):
    ing_list = [i.strip() for i in ingredients.split(",")]
    results = crud.search_recipes_by_ingredients(
        db,
        user_ingredients=ing_list,
        min_match_percent=min_match,
        limit=limit
    )
    return schemas.SearchResponse(results=results, total_found=len(results))

# Корневой эндпоинт
@app.get("/")
def root():
    return {
        "message": "Recipe Catalog API",
        "docs": "/docs",
        "search_example": "POST /recipes/search/by-ingredients или GET /recipes/search/quick?ingredients=курица,рис"
    }