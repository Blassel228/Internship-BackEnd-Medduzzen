from fastapi import APIRouter
from app.services.redis_service import redis_service

redis_router = APIRouter(prefix="/redis", tags=["Redis"])


@redis_router.get("/get_results_cache")
async def get_results_cache(quiz_id: int, user_id: int):
    return await redis_service.get_cached_result(quiz_id=quiz_id, user_id=user_id)
