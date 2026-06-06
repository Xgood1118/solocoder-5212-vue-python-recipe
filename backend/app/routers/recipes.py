from typing import List, Optional
from fastapi import APIRouter, Query, HTTPException
from datetime import datetime, timedelta

from app.utils.store import DataStore, generate_id, now_iso
from app.utils.response import success, error
from app.schemas.recipe import (
    RecipeCreate, RecipeUpdate, Recipe, RecipeSearchParams,
    RecipeArchive, DifficultyAssessCreate, NutritionSummary
)
from app.schemas.common import PaginatedResponse, ARCHIVE_REASONS
from app.schemas.feedback import Feedback

router = APIRouter(prefix="/api/recipes", tags=["recipes"])


def _get_ingredient_map(store: DataStore) -> dict:
    return {ing["name"]: ing for ing in store.ingredients.values()}


def _recipe_allergens(recipe: dict, ing_map: dict) -> set:
    allergens = set()
    for ing_list in ["mainIngredients", "auxIngredients", "seasonings"]:
        for ing in recipe.get(ing_list, []):
            name = ing.get("name", "")
            if name in ing_map:
                allergens.update(ing_map[name].get("allergens", []))
    return allergens


def _recipe_nutri_tags(recipe: dict, ing_map: dict) -> set:
    tags = set()
    for ing_list in ["mainIngredients", "auxIngredients", "seasonings"]:
        for ing in recipe.get(ing_list, []):
            name = ing.get("name", "")
            if name in ing_map:
                tags.update(ing_map[name].get("nutriTags", []))
    return tags


def _calc_relevance(recipe: dict, q: str, ingredient_names: List[str]) -> float:
    score = 0.0
    name = recipe.get("name", "")
    if q and q.lower() in name.lower():
        score += 10.0
    if ingredient_names:
        all_ingredients = set()
        for ing_list in ["mainIngredients", "auxIngredients", "seasonings"]:
            for ing in recipe.get(ing_list, []):
                all_ingredients.add(ing.get("name", "").lower())
        match_count = sum(1 for ing in ingredient_names if ing.lower() in all_ingredients)
        score += match_count * 5.0
    return score


@router.get("", response_model=dict)
async def list_recipes(
    page: int = 1,
    size: int = 20,
    q: Optional[str] = None,
    cuisine: Optional[str] = None,
    difficulty: Optional[str] = None,
    minTime: Optional[int] = None,
    maxTime: Optional[int] = None,
    status: Optional[str] = None,
    ingredients: Optional[List[str]] = Query(None),
    excludeAllergens: Optional[List[str]] = Query(None),
    nutriTags: Optional[List[str]] = Query(None),
):
    store = await DataStore.get_instance()
    lock = await store.get_lock()
    async with lock:
        ing_map = _get_ingredient_map(store)
        recipes = list(store.recipes.values())
        filtered = []

        for r in recipes:
            if q and q.lower() not in r["name"].lower():
                continue
            if cuisine and r.get("cuisine") != cuisine:
                continue
            if difficulty and r.get("difficulty") != difficulty:
                continue
            if minTime and r.get("cookTime", 0) < minTime:
                continue
            if maxTime and r.get("cookTime", 0) > maxTime:
                continue
            if status and r.get("status") != status:
                continue
            if excludeAllergens:
                r_allergens = _recipe_allergens(r, ing_map)
                if r_allergens & set(excludeAllergens):
                    continue
            if nutriTags:
                r_tags = _recipe_nutri_tags(r, ing_map)
                if not set(nutriTags).issubset(r_tags):
                    continue
            if ingredients:
                r_ings = set()
                for ing_list in ["mainIngredients", "auxIngredients", "seasonings"]:
                    for ing in r.get(ing_list, []):
                        r_ings.add(ing.get("name", "").lower())
                match_all = all(ing.lower() in r_ings for ing in ingredients)
                if not match_all:
                    continue

            filtered.append(r)

        # 按相关度+评分综合排序
        def sort_key(r):
            relevance = _calc_relevance(r, q or "", ingredients or [])
            # 计算平均评分
            feedback_list = [
                f for f in store.feedback.values()
                if f["recipeId"] == r["id"] and f["status"] == "approved"
            ]
            avg_rating = sum(f["rating"] for f in feedback_list) / len(feedback_list) if feedback_list else 0
            return relevance + avg_rating

        filtered.sort(key=sort_key, reverse=True)

        total = len(filtered)
        start = (page - 1) * size
        end = start + size
        page_data = filtered[start:end]

        return success({
            "list": page_data,
            "total": total,
            "page": page,
            "size": size,
        })


@router.get("/{recipe_id}", response_model=dict)
async def get_recipe(recipe_id: str):
    store = await DataStore.get_instance()
    lock = await store.get_lock()
    async with lock:
        recipe = store.recipes.get(recipe_id)
        if not recipe:
            return error("菜谱不存在", code=404)
        return success(recipe)


@router.post("", response_model=dict)
async def create_recipe(data: RecipeCreate):
    store = await DataStore.get_instance()
    lock = await store.get_lock()
    async with lock:
        rid = generate_id()
        now = now_iso()
        recipe_dict = data.model_dump()
        recipe_dict["id"] = rid
        recipe_dict["status"] = "draft"
        recipe_dict["archived"] = None
        recipe_dict["difficultyAssessments"] = []
        recipe_dict["createdAt"] = now
        recipe_dict["updatedAt"] = now
        recipe_dict["publishedAt"] = None
        # 按 order 排序步骤
        recipe_dict["steps"].sort(key=lambda s: s["order"])
        store.recipes[rid] = recipe_dict
        return success(recipe_dict)


@router.put("/{recipe_id}", response_model=dict)
async def update_recipe(recipe_id: str, data: RecipeUpdate):
    store = await DataStore.get_instance()
    lock = await store.get_lock()
    async with lock:
        recipe = store.recipes.get(recipe_id)
        if not recipe:
            return error("菜谱不存在", code=404)
        if recipe["status"] == "published":
            return error("已发布的菜谱不能直接修改，请先下架", code=400)

        update_data = data.model_dump()
        update_data["steps"].sort(key=lambda s: s["order"])
        recipe.update(update_data)
        recipe["updatedAt"] = now_iso()
        return success(recipe)


@router.delete("/{recipe_id}", response_model=dict)
async def delete_recipe(recipe_id: str):
    store = await DataStore.get_instance()
    lock = await store.get_lock()
    async with lock:
        if recipe_id not in store.recipes:
            return error("菜谱不存在", code=404)
        del store.recipes[recipe_id]
        # 同时删除相关评价
        fb_ids = [fid for fid, f in store.feedback.items() if f["recipeId"] == recipe_id]
        for fid in fb_ids:
            del store.feedback[fid]
        return success(None)


@router.post("/{recipe_id}/publish", response_model=dict)
async def publish_recipe(recipe_id: str):
    store = await DataStore.get_instance()
    lock = await store.get_lock()
    async with lock:
        recipe = store.recipes.get(recipe_id)
        if not recipe:
            return error("菜谱不存在", code=404)
        if recipe["status"] == "published":
            return error("菜谱已经是发布状态", code=400)
        recipe["status"] = "published"
        recipe["archived"] = None
        recipe["publishedAt"] = now_iso()
        recipe["updatedAt"] = now_iso()
        return success(recipe)


@router.post("/{recipe_id}/archive", response_model=dict)
async def archive_recipe(recipe_id: str, data: RecipeArchive):
    store = await DataStore.get_instance()
    lock = await store.get_lock()
    async with lock:
        recipe = store.recipes.get(recipe_id)
        if not recipe:
            return error("菜谱不存在", code=404)
        if data.reason not in ARCHIVE_REASONS:
            return error(f"下架原因必须是: {ARCHIVE_REASONS}", code=400)
        recipe["status"] = "archived"
        recipe["archived"] = {
            "reason": data.reason,
            "archivedAt": now_iso(),
        }
        recipe["updatedAt"] = now_iso()
        return success(recipe)


@router.post("/{recipe_id}/difficulty-assess", response_model=dict)
async def add_difficulty_assessment(recipe_id: str, data: DifficultyAssessCreate):
    store = await DataStore.get_instance()
    lock = await store.get_lock()
    async with lock:
        recipe = store.recipes.get(recipe_id)
        if not recipe:
            return error("菜谱不存在", code=404)
        # 同一用户对同一菜谱只能评估一次
        assessments = recipe.get("difficultyAssessments", [])
        for a in assessments:
            if a["userId"] == data.userId:
                a["actualDifficulty"] = data.actualDifficulty
                a["createdAt"] = now_iso()
                recipe["updatedAt"] = now_iso()
                return success(recipe)

        aid = generate_id()
        assessments.append({
            "id": aid,
            "userId": data.userId,
            "actualDifficulty": data.actualDifficulty,
            "createdAt": now_iso(),
        })
        recipe["difficultyAssessments"] = assessments
        recipe["updatedAt"] = now_iso()
        return success(recipe)


@router.get("/{recipe_id}/nutrition", response_model=dict)
async def get_nutrition_summary(recipe_id: str):
    store = await DataStore.get_instance()
    lock = await store.get_lock()
    async with lock:
        recipe = store.recipes.get(recipe_id)
        if not recipe:
            return error("菜谱不存在", code=404)

        ing_map = _get_ingredient_map(store)
        total_calories = 0.0
        total_protein = 0.0
        total_fat = 0.0
        total_carbs = 0.0

        for ing_list in ["mainIngredients", "auxIngredients", "seasonings"]:
            for ing in recipe.get(ing_list, []):
                name = ing.get("name", "")
                amount = ing.get("amount", 0)
                unit = ing.get("unit", "")

                if name in ing_map:
                    nutrition = ing_map[name].get("nutrition", {})
                    # 简单按克或毫升估算（1克≈1卡路里基准比）
                    # 假设每100克为基准
                    if unit in ["克", "毫升"]:
                        factor = amount / 100.0
                    elif unit == "千克":
                        factor = amount * 10
                    elif unit == "两":
                        factor = amount * 0.5
                    else:
                        # 个/勺等单位用估算值
                        factor = amount * 0.5

                    total_calories += nutrition.get("calories", 0) * factor
                    total_protein += nutrition.get("protein", 0) * factor
                    total_fat += nutrition.get("fat", 0) * factor
                    total_carbs += nutrition.get("carbs", 0) * factor

        summary = {
            "calories": round(total_calories, 1),
            "protein": round(total_protein, 1),
            "fat": round(total_fat, 1),
            "carbs": round(total_carbs, 1),
        }
        return success(summary)


@router.get("/{recipe_id}/feedback", response_model=dict)
async def list_recipe_feedback(
    recipe_id: str,
    page: int = 1,
    size: int = 20,
    rating: Optional[int] = None,
    sortBy: str = "time",
    status: Optional[str] = "approved",
):
    store = await DataStore.get_instance()
    lock = await store.get_lock()
    async with lock:
        recipe = store.recipes.get(recipe_id)
        if not recipe:
            return error("菜谱不存在", code=404)

        fb_list = [
            f for f in store.feedback.values()
            if f["recipeId"] == recipe_id and (status is None or f["status"] == status)
        ]
        if rating:
            fb_list = [f for f in fb_list if f["rating"] == rating]

        if sortBy == "time":
            fb_list.sort(key=lambda f: f["createdAt"], reverse=True)
        elif sortBy == "rating":
            fb_list.sort(key=lambda f: f["rating"], reverse=True)

        total = len(fb_list)
        start = (page - 1) * size
        end = start + size
        page_data = fb_list[start:end]

        return success({
            "list": page_data,
            "total": total,
            "page": page,
            "size": size,
        })
