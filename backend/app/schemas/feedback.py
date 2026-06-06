from typing import Optional
from pydantic import BaseModel, Field, field_validator


class FeedbackBase(BaseModel):
    recipeId: str
    rating: int = Field(..., ge=1, le=5)
    content: str = ""
    anonymous: bool = False
    userId: Optional[str] = None
    userName: Optional[str] = None

    @field_validator("content")
    @classmethod
    def check_content_for_low_rating(cls, v: str, info) -> str:
        rating = info.data.get("rating")
        if rating and rating <= 2 and len(v.strip()) < 20:
            raise ValueError("差评（1-2星）必须填写不少于20字的说明")
        return v


class FeedbackCreate(FeedbackBase):
    pass


class FeedbackUpdate(BaseModel):
    rating: Optional[int] = Field(None, ge=1, le=5)
    content: Optional[str] = None
    anonymous: Optional[bool] = None


class Feedback(BaseModel):
    id: str
    recipeId: str
    rating: int
    content: str
    anonymous: bool
    userId: Optional[str] = None
    userName: Optional[str] = None
    status: str
    createdAt: str
    updatedAt: str

    class Config:
        from_attributes = True


class FeedbackReview(BaseModel):
    status: str
