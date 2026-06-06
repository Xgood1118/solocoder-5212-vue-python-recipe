from typing import Optional, List, Generic, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationParams(BaseModel):
    page: int = Field(1, ge=1, description="页码")
    size: int = Field(20, ge=1, le=100, description="每页条数")


class PaginatedResponse(BaseModel, Generic[T]):
    list: List[T]
    total: int
    page: int
    size: int


CUISINE_ICONS = {
    "川菜": "🌶️",
    "粤菜": "🦐",
    "鲁菜": "🍲",
    "淮扬菜": "🥢",
    "浙菜": "🍤",
    "闽菜": "🍲",
    "湘菜": "🌶️",
    "徽菜": "🍄",
    "家常菜": "🏠",
    "甜品": "🍰",
    "汤品": "🍜",
}

CUISINE_LIST = list(CUISINE_ICONS.keys())

DIFFICULTY_LIST = ["简单", "中等", "困难"]

INGREDIENT_CATEGORIES = ["蔬菜", "肉禽", "水产", "调料", "主食", "水果"]

ALLERGEN_LIST = ["麸质", "坚果", "乳制品", "海鲜", "蛋类", "大豆"]

NUTRI_TAGS = ["高蛋白", "低脂", "低糖", "高纤维"]

ARCHIVE_REASONS = ["重复", "违规", "作者申请"]

FEEDBACK_STATUS = ["pending", "approved", "rejected"]
