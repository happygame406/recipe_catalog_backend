from pydantic import BaseModel
from typing import List, Optional

# === Схемы для ингредиентов ===
class IngredientBase(BaseModel):
    name: str

class IngredientCreate(IngredientBase):
    pass

class Ingredient(IngredientBase):
    id: int
    
    class Config:
        from_attributes = True

# === Схемы для связи рецепт-ингредиент (с весом и обязательностью) ===
class RecipeIngredientBase(BaseModel):
    ingredient_id: int
    weight: float = 1.0
    is_mandatory: bool = False

# === Схемы для рецептов ===
class RecipeBase(BaseModel):
    title: str
    description: Optional[str] = None
    instructions: Optional[str] = None
    cooking_time_minutes: int = 30
    category: str = "Основное блюдо"

class RecipeCreate(RecipeBase):
    ingredients: List[RecipeIngredientBase]

class Recipe(RecipeBase):
    id: int
    ingredients: List[Ingredient] = []
    
    class Config:
        from_attributes = True

# === Схемы для поиска по ингредиентам ===
class SearchRequest(BaseModel):
    user_ingredients: List[str]
    min_match_percent: float = 0.0
    limit: int = 20

class SearchResultItem(BaseModel):
    recipe_id: int
    title: str
    match_percent: float
    missing_ingredients: List[str]
    cooking_time_minutes: int

class SearchResponse(BaseModel):
    results: List[SearchResultItem]
    total_found: int