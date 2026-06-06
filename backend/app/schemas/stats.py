from typing import List, Optional
from pydantic import BaseModel


class StatsOverview(BaseModel):
    totalRecipes: int
    publishedRecipes: int
    pendingFeedback: int
    last7DaysPublished: int
    last7DaysAvgRating: float


class IngredientUsageRank(BaseModel):
    name: str
    count: int
    category: str
