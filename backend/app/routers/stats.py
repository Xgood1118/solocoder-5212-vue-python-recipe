from typing import List
from fastapi import APIRouter
from datetime import datetime, timedelta

from app.utils.store import DataStore
from app.utils.response import success

router = APIRouter(prefix="/api/stats", tags=["stats"])


@router.get("/overview", response_model=dict)
async def get_overview():
    store = await DataStore.get_instance()
    lock = await store.get_lock()
    async with lock:
        total_recipes = len(store.recipes)
        published_recipes = sum(1 for r in store.recipes.values() if r["status"] == "published")
        pending_feedback = sum(1 for f in store.feedback.values() if f["status"] == "pending")

        # 近7天发布数
        now = datetime.utcnow()
        seven_days_ago = (now - timedelta(days=7)).isoformat() + "Z"
        last_7_days_published = sum(
            1 for r in store.recipes.values()
            if r["status"] == "published"
            and r.get("publishedAt")
            and r["publishedAt"] >= seven_days_ago
        )

        # 近7天评分均值
        recent_feedback = [
            f for f in store.feedback.values()
            if f["status"] == "approved"
            and f["createdAt"] >= seven_days_ago
        ]
        if recent_feedback:
            avg_rating = sum(f["rating"] for f in recent_feedback) / len(recent_feedback)
        else:
            avg_rating = 0.0

        return success({
            "totalRecipes": total_recipes,
            "publishedRecipes": published_recipes,
            "pendingFeedback": pending_feedback,
            "last7DaysPublished": last_7_days_published,
            "last7DaysAvgRating": round(avg_rating, 2),
        })


@router.get("/ingredient-rank", response_model=dict)
async def get_ingredient_rank(limit: int = 20):
    store = await DataStore.get_instance()
    lock = await store.get_lock()
    async with lock:
        usage_count = {}
        category_map = {}

        for recipe in store.recipes.values():
            ingredient_names = set()
            for ing_list in ["mainIngredients", "auxIngredients", "seasonings"]:
                for ing in recipe.get(ing_list, []):
                    name = ing.get("name", "")
                    if name:
                        ingredient_names.add(name)

            for name in ingredient_names:
                usage_count[name] = usage_count.get(name, 0) + 1

        # 从食材库补充分类信息
        for ing in store.ingredients.values():
            category_map[ing["name"]] = ing["category"]

        ranked = sorted(usage_count.items(), key=lambda x: x[1], reverse=True)[:limit]
        result = [
            {
                "name": name,
                "count": count,
                "category": category_map.get(name, "其他"),
            }
            for name, count in ranked
        ]

        return success(result)
