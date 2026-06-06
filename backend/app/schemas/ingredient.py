from typing import List, Optional
from pydantic import BaseModel, Field

from .common import INGREDIENT_CATEGORIES, ALLERGEN_LIST, NUTRI_TAGS


class NutritionInfo(BaseModel):
    calories: float = 0
    protein: float = 0
    fat: float = 0
    carbs: float = 0


class IngredientBase(BaseModel):
    name: str
    category: str
    units: List[str] = []
    allergens: List[str] = []
    nutrition: NutritionInfo = NutritionInfo()
    nutriTags: List[str] = []


class IngredientCreate(IngredientBase):
    pass


class IngredientUpdate(IngredientBase):
    pass


class Ingredient(IngredientBase):
    id: str
    createdAt: str
    updatedAt: str

    class Config:
        from_attributes = True


class IngredientSearchParams(BaseModel):
    q: Optional[str] = None
    category: Optional[str] = None
