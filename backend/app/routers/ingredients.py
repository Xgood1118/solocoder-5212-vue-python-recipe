from typing import List, Optional
import csv
import io
from fastapi import APIRouter, Query, UploadFile, File, HTTPException

from app.utils.store import DataStore, generate_id, now_iso
from app.utils.response import success, error
from app.schemas.ingredient import IngredientCreate, IngredientUpdate, Ingredient, NutritionInfo
from app.schemas.common import PaginatedResponse, INGREDIENT_CATEGORIES, ALLERGEN_LIST, NUTRI_TAGS

router = APIRouter(prefix="/api/ingredients", tags=["ingredients"])


@router.get("", response_model=dict)
async def list_ingredients(
    page: int = 1,
    size: int = 20,
    q: Optional[str] = None,
    category: Optional[str] = None,
):
    store = await DataStore.get_instance()
    lock = await store.get_lock()
    async with lock:
        items = list(store.ingredients.values())
        filtered = []

        for ing in items:
            if q and q.lower() not in ing["name"].lower():
                continue
            if category and ing.get("category") != category:
                continue
            filtered.append(ing)

        filtered.sort(key=lambda x: x["name"])

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


@router.get("/search", response_model=dict)
async def search_ingredients(
    q: str = "",
    limit: int = 20,
):
    store = await DataStore.get_instance()
    lock = await store.get_lock()
    async with lock:
        items = list(store.ingredients.values())
        if q:
            items = [ing for ing in items if q.lower() in ing["name"].lower()]
        items.sort(key=lambda x: x["name"])
        return success(items[:limit])


@router.get("/{ingredient_id}", response_model=dict)
async def get_ingredient(ingredient_id: str):
    store = await DataStore.get_instance()
    lock = await store.get_lock()
    async with lock:
        ing = store.ingredients.get(ingredient_id)
        if not ing:
            return error("食材不存在", code=404)
        return success(ing)


@router.post("", response_model=dict)
async def create_ingredient(data: IngredientCreate):
    store = await DataStore.get_instance()
    lock = await store.get_lock()
    async with lock:
        # 检查名称是否已存在
        for existing in store.ingredients.values():
            if existing["name"] == data.name:
                return error("食材名称已存在", code=400)

        iid = generate_id()
        now = now_iso()
        ing_dict = data.model_dump()
        ing_dict["id"] = iid
        ing_dict["createdAt"] = now
        ing_dict["updatedAt"] = now
        store.ingredients[iid] = ing_dict
        return success(ing_dict)


@router.put("/{ingredient_id}", response_model=dict)
async def update_ingredient(ingredient_id: str, data: IngredientUpdate):
    store = await DataStore.get_instance()
    lock = await store.get_lock()
    async with lock:
        ing = store.ingredients.get(ingredient_id)
        if not ing:
            return error("食材不存在", code=404)

        # 检查重名
        for eid, existing in store.ingredients.items():
            if eid != ingredient_id and existing["name"] == data.name:
                return error("食材名称已存在", code=400)

        update_data = data.model_dump()
        ing.update(update_data)
        ing["updatedAt"] = now_iso()
        return success(ing)


@router.delete("/{ingredient_id}", response_model=dict)
async def delete_ingredient(ingredient_id: str):
    store = await DataStore.get_instance()
    lock = await store.get_lock()
    async with lock:
        if ingredient_id not in store.ingredients:
            return error("食材不存在", code=404)
        del store.ingredients[ingredient_id]
        return success(None)


@router.post("/import/csv", response_model=dict)
async def import_csv(file: UploadFile = File(...)):
    store = await DataStore.get_instance()
    lock = await store.get_lock()

    content = await file.read()
    text = content.decode("utf-8-sig")

    reader = csv.DictReader(io.StringIO(text))
    added = 0
    skipped = 0
    errors = []

    async with lock:
        existing_names = {ing["name"] for ing in store.ingredients.values()}

        for idx, row in enumerate(reader, start=2):
            try:
                name = (row.get("name") or row.get("名称") or "").strip()
                if not name:
                    errors.append(f"第{idx}行：名称为空")
                    continue
                if name in existing_names:
                    skipped += 1
                    continue

                category = (row.get("category") or row.get("分类") or "蔬菜").strip()
                units_str = (row.get("units") or row.get("单位") or "克").strip()
                units = [u.strip() for u in units_str.split("/") if u.strip()]

                allergens_str = (row.get("allergens") or row.get("过敏原") or "").strip()
                allergens = [a.strip() for a in allergens_str.split("/") if a.strip()]

                nutri_tags_str = (row.get("nutri_tags") or row.get("营养标签") or "").strip()
                nutri_tags = [t.strip() for t in nutri_tags_str.split("/") if t.strip()]

                calories = float(row.get("calories") or row.get("卡路里") or 0)
                protein = float(row.get("protein") or row.get("蛋白质") or 0)
                fat = float(row.get("fat") or row.get("脂肪") or 0)
                carbs = float(row.get("carbs") or row.get("碳水") or 0)

                iid = generate_id()
                now = now_iso()
                store.ingredients[iid] = {
                    "id": iid,
                    "name": name,
                    "category": category,
                    "units": units,
                    "allergens": allergens,
                    "nutriTags": nutri_tags,
                    "nutrition": {
                        "calories": calories,
                        "protein": protein,
                        "fat": fat,
                        "carbs": carbs,
                    },
                    "createdAt": now,
                    "updatedAt": now,
                }
                existing_names.add(name)
                added += 1
            except Exception as e:
                errors.append(f"第{idx}行：{str(e)}")

    return success({
        "added": added,
        "skipped": skipped,
        "errors": errors,
    })
