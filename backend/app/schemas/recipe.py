from typing import List, Optional
from pydantic import BaseModel, Field, field_validator

from .common import DIFFICULTY_LIST, CUISINE_LIST


class RecipeIngredient(BaseModel):
    ingredientId: Optional[str] = None
    name: str
    amount: float
    unit: str
    optional: bool = False


class RecipeStep(BaseModel):
    order: int
    description: str
    duration: int = 0
    tip: str = ""
    images: List[str] = []


class ArchivedInfo(BaseModel):
    reason: str
    archivedAt: str


class DifficultyAssessment(BaseModel):
    id: str
    userId: str
    actualDifficulty: str
    createdAt: str


class RecipeBase(BaseModel):
    name: str
    cuisine: str
    difficulty: str
    cookTime: int = Field(..., gt=0, description="烹饪时长（分钟）")
    servings: int = Field(..., gt=0, description="适合人数")
    mainIngredients: List[RecipeIngredient] = []
    auxIngredients: List[RecipeIngredient] = []
    seasonings: List[RecipeIngredient] = []
    steps: List[RecipeStep] = []
    imageUrl: str = ""

    @field_validator("difficulty")
    @classmethod
    def check_difficulty(cls, v: str) -> str:
        if v not in DIFFICULTY_LIST:
            raise ValueError(f"难度必须是: {DIFFICULTY_LIST}")
        return v


class RecipeCreate(RecipeBase):
    pass


class RecipeUpdate(RecipeBase):
    pass


class Recipe(RecipeBase):
    id: str
    status: str
    archived: Optional[ArchivedInfo] = None
    difficultyAssessments: List[DifficultyAssessment] = []
    createdAt: str
    updatedAt: str
    publishedAt: Optional[str] = None

    class Config:
        from_attributes = True


class RecipeSearchParams(BaseModel):
    q: Optional[str] = None
    ingredients: Optional[List[str]] = None
    cuisine: Optional[str] = None
    difficulty: Optional[str] = None
    minTime: Optional[int] = None
    maxTime: Optional[int] = None
    excludeAllergens: Optional[List[str]] = None
    nutriTags: Optional[List[str]] = None
    status: Optional[str] = None


class RecipeArchive(BaseModel):
    reason: str


class DifficultyAssessCreate(BaseModel):
    userId: str
    actualDifficulty: str

    @field_validator("actualDifficulty")
    @classmethod
    def check_difficulty(cls, v: str) -> str:
        if v not in DIFFICULTY_LIST:
            raise ValueError(f"难度必须是: {DIFFICULTY_LIST}")
        return v


class NutritionSummary(BaseModel):
    calories: float
    protein: float
    fat: float
    carbs: float
