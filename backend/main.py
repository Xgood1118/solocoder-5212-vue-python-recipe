from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import json

from app.utils.store import DataStore, now_iso
from app.utils.response import success, error
from app.routers import recipes as recipes_router
from app.routers import ingredients as ingredients_router
from app.routers import feedback as feedback_router
from app.routers import stats as stats_router
from app.schemas.common import (
    CUISINE_LIST, CUISINE_ICONS, DIFFICULTY_LIST,
    INGREDIENT_CATEGORIES, ALLERGEN_LIST, NUTRI_TAGS,
    ARCHIVE_REASONS, FEEDBACK_STATUS,
)

app = FastAPI(title="家常菜谱管理系统 API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(recipes_router.router)
app.include_router(ingredients_router.router)
app.include_router(feedback_router.router)
app.include_router(stats_router.router)


@app.get("/api/health", tags=["system"])
async def health_check():
    return success({"status": "ok", "time": now_iso()})


@app.get("/api/constants", tags=["system"])
async def get_constants():
    return success({
        "cuisines": [{"name": c, "icon": CUISINE_ICONS.get(c, "🍽️")} for c in CUISINE_LIST],
        "cuisineIcons": CUISINE_ICONS,
        "difficulties": DIFFICULTY_LIST,
        "ingredientCategories": INGREDIENT_CATEGORIES,
        "allergens": ALLERGEN_LIST,
        "nutriTags": NUTRI_TAGS,
        "archiveReasons": ARCHIVE_REASONS,
        "feedbackStatus": FEEDBACK_STATUS,
    })


@app.post("/api/recipes/export", tags=["recipes"])
async def export_recipes():
    store = await DataStore.get_instance()
    lock = await store.get_lock()
    async with lock:
        recipes = list(store.recipes.values())
        ingredients = list(store.ingredients.values())
        return success({
            "version": "1.0",
            "exportedAt": now_iso(),
            "recipes": recipes,
            "ingredients": ingredients,
        })


@app.post("/api/recipes/import", tags=["recipes"])
async def import_recipes(file: UploadFile = File(...)):
    store = await DataStore.get_instance()
    lock = await store.get_lock()

    content = await file.read()
    try:
        data = json.loads(content)
    except Exception as e:
        return error(f"JSON 解析失败: {str(e)}", code=400)

    recipes = data.get("recipes", [])
    ingredients = data.get("ingredients", [])

    if not isinstance(recipes, list):
        return error("recipes 必须是数组", code=400)

    added_recipes = 0
    added_ingredients = 0

    async with lock:
        # 导入食材（先导入，因为菜谱引用食材）
        name_to_id = {}
        for ing_data in ingredients:
            name = ing_data.get("name", "")
            if not name:
                continue
            # 去重
            exists = None
            for existing in store.ingredients.values():
                if existing["name"] == name:
                    exists = existing
                    break
            if exists:
                name_to_id[name] = exists["id"]
                continue

            import uuid
            iid = str(uuid.uuid4())
            ing_data["id"] = iid
            ing_data["createdAt"] = ing_data.get("createdAt", now_iso())
            ing_data["updatedAt"] = now_iso()
            store.ingredients[iid] = ing_data
            name_to_id[name] = iid
            added_ingredients += 1

        # 导入菜谱
        for recipe_data in recipes:
            import uuid
            rid = str(uuid.uuid4())
            recipe_data["id"] = rid
            recipe_data["createdAt"] = recipe_data.get("createdAt", now_iso())
            recipe_data["updatedAt"] = now_iso()
            recipe_data["difficultyAssessments"] = recipe_data.get("difficultyAssessments", [])
            recipe_data["archived"] = recipe_data.get("archived", None)
            if not recipe_data.get("status"):
                recipe_data["status"] = "draft"
            store.recipes[rid] = recipe_data
            added_recipes += 1

    return success({
        "addedRecipes": added_recipes,
        "addedIngredients": added_ingredients,
    })


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
