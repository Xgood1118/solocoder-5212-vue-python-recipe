from typing import List, Optional
from fastapi import APIRouter, Query

from app.utils.store import DataStore, generate_id, now_iso
from app.utils.response import success, error
from app.schemas.feedback import FeedbackCreate, FeedbackUpdate, Feedback, FeedbackReview
from app.schemas.common import PaginatedResponse, FEEDBACK_STATUS

router = APIRouter(prefix="/api/feedback", tags=["feedback"])


@router.get("", response_model=dict)
async def list_feedback(
    page: int = 1,
    size: int = 20,
    status: Optional[str] = None,
    rating: Optional[int] = None,
    recipeId: Optional[str] = None,
    sortBy: str = "time",
):
    store = await DataStore.get_instance()
    lock = await store.get_lock()
    async with lock:
        items = list(store.feedback.values())

        if status:
            items = [f for f in items if f["status"] == status]
        if rating:
            items = [f for f in items if f["rating"] == rating]
        if recipeId:
            items = [f for f in items if f["recipeId"] == recipeId]

        if sortBy == "time":
            items.sort(key=lambda f: f["createdAt"], reverse=True)
        elif sortBy == "rating":
            items.sort(key=lambda f: f["rating"], reverse=True)

        total = len(items)
        start = (page - 1) * size
        end = start + size
        page_data = items[start:end]

        return success({
            "list": page_data,
            "total": total,
            "page": page,
            "size": size,
        })


@router.get("/{feedback_id}", response_model=dict)
async def get_feedback(feedback_id: str):
    store = await DataStore.get_instance()
    lock = await store.get_lock()
    async with lock:
        fb = store.feedback.get(feedback_id)
        if not fb:
            return error("评价不存在", code=404)
        return success(fb)


@router.post("", response_model=dict)
async def create_feedback(data: FeedbackCreate):
    store = await DataStore.get_instance()
    lock = await store.get_lock()
    async with lock:
        # 检查菜谱是否存在
        if data.recipeId not in store.recipes:
            return error("菜谱不存在", code=404)

        # 同一用户对同一菜谱只能评价一次
        if data.userId:
            for existing in store.feedback.values():
                if (existing["recipeId"] == data.recipeId
                        and existing["userId"] == data.userId):
                    return error("您已经评价过这道菜谱，可以修改评价", code=400)

        fid = generate_id()
        now = now_iso()
        fb_dict = data.model_dump()
        fb_dict["id"] = fid
        fb_dict["status"] = "pending"
        fb_dict["createdAt"] = now
        fb_dict["updatedAt"] = now
        store.feedback[fid] = fb_dict
        return success(fb_dict)


@router.patch("/{feedback_id}", response_model=dict)
async def update_feedback(feedback_id: str, data: FeedbackUpdate):
    store = await DataStore.get_instance()
    lock = await store.get_lock()
    async with lock:
        fb = store.feedback.get(feedback_id)
        if not fb:
            return error("评价不存在", code=404)

        update_data = data.model_dump(exclude_unset=True)

        # 如果修改了评分或内容，差评校验
        new_rating = update_data.get("rating", fb["rating"])
        new_content = update_data.get("content", fb["content"])
        if new_rating <= 2 and len(new_content.strip()) < 20:
            return error("差评（1-2星）必须填写不少于20字的说明", code=400)

        fb.update(update_data)
        fb["status"] = "pending"  # 修改后回到待审状态
        fb["updatedAt"] = now_iso()
        return success(fb)


@router.post("/{feedback_id}/review", response_model=dict)
async def review_feedback(feedback_id: str, data: FeedbackReview):
    store = await DataStore.get_instance()
    lock = await store.get_lock()
    async with lock:
        fb = store.feedback.get(feedback_id)
        if not fb:
            return error("评价不存在", code=404)
        if data.status not in ["approved", "rejected"]:
            return error("审核状态只能是 approved 或 rejected", code=400)

        fb["status"] = data.status
        fb["updatedAt"] = now_iso()
        return success(fb)


@router.delete("/{feedback_id}", response_model=dict)
async def delete_feedback(feedback_id: str):
    store = await DataStore.get_instance()
    lock = await store.get_lock()
    async with lock:
        if feedback_id not in store.feedback:
            return error("评价不存在", code=404)
        del store.feedback[feedback_id]
        return success(None)
