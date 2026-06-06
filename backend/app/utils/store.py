import asyncio
from typing import Dict, List, Any
import uuid
from datetime import datetime


def generate_id() -> str:
    return str(uuid.uuid4())


def now_iso() -> str:
    return datetime.utcnow().isoformat() + "Z"


class DataStore:
    _instance = None
    _lock = asyncio.Lock()

    def __init__(self):
        self.recipes: Dict[str, dict] = {}
        self.ingredients: Dict[str, dict] = {}
        self.feedback: Dict[str, dict] = {}
        self._seed_data()

    @classmethod
    async def get_instance(cls) -> "DataStore":
        async with cls._lock:
            if cls._instance is None:
                cls._instance = cls()
            return cls._instance

    async def get_lock(self) -> asyncio.Lock:
        return self._lock

    def _seed_data(self):
        cuisines = ["川菜", "粤菜", "鲁菜", "淮扬菜", "浙菜", "闽菜", "湘菜", "徽菜"]
        difficulties = ["简单", "中等", "困难"]
        statuses = ["draft", "published", "archived"]

        ing_data = [
            {"name": "西红柿", "category": "蔬菜", "units": ["克", "个"], "allergens": [],
             "nutrition": {"calories": 19, "protein": 0.9, "fat": 0.2, "carbs": 4.0},
             "nutri_tags": ["低脂", "低糖", "高纤维"]},
            {"name": "鸡蛋", "category": "肉禽", "units": ["克", "个"], "allergens": ["蛋类"],
             "nutrition": {"calories": 155, "protein": 13.0, "fat": 11.0, "carbs": 1.1},
             "nutri_tags": ["高蛋白"]},
            {"name": "盐", "category": "调料", "units": ["克", "勺"], "allergens": [],
             "nutrition": {"calories": 0, "protein": 0, "fat": 0, "carbs": 0}, "nutri_tags": []},
            {"name": "生抽", "category": "调料", "units": ["毫升", "勺"], "allergens": ["大豆"],
             "nutrition": {"calories": 53, "protein": 8.0, "fat": 0.3, "carbs": 5.0}, "nutri_tags": []},
            {"name": "白糖", "category": "调料", "units": ["克", "勺"], "allergens": [],
             "nutrition": {"calories": 387, "protein": 0, "fat": 0, "carbs": 99.8}, "nutri_tags": []},
            {"name": "猪肉", "category": "肉禽", "units": ["克", "两"], "allergens": [],
             "nutrition": {"calories": 242, "protein": 27.0, "fat": 14.0, "carbs": 0}, "nutri_tags": ["高蛋白"]},
            {"name": "土豆", "category": "蔬菜", "units": ["克", "个"], "allergens": [],
             "nutrition": {"calories": 77, "protein": 2.0, "fat": 0.1, "carbs": 17.0},
             "nutri_tags": ["低脂", "高纤维"]},
            {"name": "青椒", "category": "蔬菜", "units": ["克", "个"], "allergens": [],
             "nutrition": {"calories": 20, "protein": 0.9, "fat": 0.2, "carbs": 4.6},
             "nutri_tags": ["低脂", "低糖", "高纤维"]},
        ]
        for item in ing_data:
            iid = generate_id()
            self.ingredients[iid] = {
                "id": iid, "name": item["name"], "category": item["category"],
                "units": item["units"], "allergens": item["allergens"],
                "nutrition": item["nutrition"], "nutri_tags": item.get("nutri_tags", []),
                "createdAt": now_iso(), "updatedAt": now_iso(),
            }

        recipe_data = [
            {
                "name": "西红柿炒鸡蛋", "cuisine": "家常菜", "difficulty": "简单",
                "cookTime": 15, "servings": 2,
                "mainIngredients": [
                    {"ingredientId": None, "name": "西红柿", "amount": 200, "unit": "克", "optional": False},
                    {"ingredientId": None, "name": "鸡蛋", "amount": 3, "unit": "个", "optional": False},
                ],
                "auxIngredients": [],
                "seasonings": [
                    {"ingredientId": None, "name": "盐", "amount": 2, "unit": "克", "optional": False},
                    {"ingredientId": None, "name": "白糖", "amount": 5, "unit": "克", "optional": True},
                ],
                "steps": [
                    {"order": 1, "description": "西红柿切块，鸡蛋打散", "duration": 5, "tip": "西红柿要选熟透的", "images": []},
                    {"order": 2, "description": "热油炒蛋盛出", "duration": 3, "tip": "油温不要太高", "images": []},
                    {"order": 3, "description": "炒西红柿出汁后加蛋翻炒", "duration": 5, "tip": "加糖提鲜", "images": []},
                ],
                "imageUrl": "https://placehold.co/400x300/orange/white?text=番茄炒蛋",
                "status": "published",
            },
            {
                "name": "青椒土豆丝", "cuisine": "川菜", "difficulty": "简单",
                "cookTime": 20, "servings": 2,
                "mainIngredients": [
                    {"ingredientId": None, "name": "土豆", "amount": 250, "unit": "克", "optional": False},
                    {"ingredientId": None, "name": "青椒", "amount": 50, "unit": "克", "optional": False},
                ],
                "auxIngredients": [],
                "seasonings": [
                    {"ingredientId": None, "name": "盐", "amount": 3, "unit": "克", "optional": False},
                    {"ingredientId": None, "name": "生抽", "amount": 5, "unit": "毫升", "optional": True},
                ],
                "steps": [
                    {"order": 1, "description": "土豆去皮切丝泡水", "duration": 5, "tip": "多洗几遍去淀粉", "images": []},
                    {"order": 2, "description": "青椒切丝", "duration": 3, "tip": "切细一点", "images": []},
                    {"order": 3, "description": "热油快炒，调味出锅", "duration": 5, "tip": "大火快炒保持脆感", "images": []},
                ],
                "imageUrl": "https://placehold.co/400x300/green/white?text=青椒土豆丝",
                "status": "published",
            },
        ]

        for item in recipe_data:
            rid = generate_id()
            self.recipes[rid] = {
                "id": rid,
                "name": item["name"],
                "cuisine": item["cuisine"],
                "difficulty": item["difficulty"],
                "cookTime": item["cookTime"],
                "servings": item["servings"],
                "mainIngredients": item["mainIngredients"],
                "auxIngredients": item["auxIngredients"],
                "seasonings": item["seasonings"],
                "steps": item["steps"],
                "imageUrl": item["imageUrl"],
                "status": item["status"],
                "archived": None,
                "difficultyAssessments": [],
                "createdAt": now_iso(),
                "updatedAt": now_iso(),
                "publishedAt": now_iso() if item["status"] == "published" else None,
            }
