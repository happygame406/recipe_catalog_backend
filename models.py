from sqlalchemy import Column, Integer, String, Float, ForeignKey, Table
from sqlalchemy.orm import relationship
from database import Base

recipe_ingredient = Table(
    "recipe_ingredient",
    Base.metadata,
    Column("recipe_id", Integer, ForeignKey("recipes.id")),
    Column("ingredient_id", Integer, ForeignKey("ingredients.id")),
    Column("weight", Float, default=1.0),
    Column("is_mandatory", Integer, default=0) 
)

class Recipe(Base):
    __tablename__ = "recipes"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    instructions = Column(String, nullable=True)
    cooking_time_minutes = Column(Integer, default=30)
    category = Column(String, default="Основное блюдо")

    ingredients = relationship(
        "Ingredient",
        secondary=recipe_ingredient,
        back_populates="recipes"
    )

class Ingredient(Base):
    __tablename__ = "ingredients"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    
    recipes = relationship(
        "Recipe",
        secondary=recipe_ingredient,
        back_populates="ingredients"
    )
