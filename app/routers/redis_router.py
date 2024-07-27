from fastapi import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.redis_service import redis_service
from fastapi import Depends
from app.utils.deps import get_current_user, get_db


redis_router = APIRouter(prefix="/redis", tags=["Redis"])


@redis_router.get("/get_results_cache/{quiz_id}{user_id}")
async def get_results_cache(quiz_id: int, user_id: int):
    return await redis_service.get_cached_result(quiz_id=quiz_id, user_id=user_id)


@redis_router.get("/user_get_its_result")
async def get_results_cache(current_user=Depends(get_current_user)):
    return await redis_service.user_get_its_result(user_id=current_user.id)


@redis_router.get("/admin_get_all_cache_by_company_id")
async def admin_get_all_cache_by_company_id(
    company_id: int,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await redis_service.admin_get_all_cache_by_company_id(
        user_id=current_user.id, company_id=company_id, db=db
    )


@redis_router.get("/admin_get_all_cache_by_quiz_id")
async def admin_get_all_cache_by_quiz_id(
    quiz_id: int, current_user=Depends(get_current_user)
):
    return await redis_service.admin_get_all_cache_by_quiz_id(
        user_id=current_user.id, quiz_id=quiz_id
    )


@redis_router.get("/admin_get_all_cache_by_quiz_id")
async def admin_get_all_cache_by_quiz_id(
    id_: int,
    company_id: int,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await redis_service.export_cached_results_for_one_user_to_csv(
        user_id=current_user.id, id_=id_, company_id=company_id, db=db
    )


@redis_router.get("/admin_get_all_cache_by_quiz_id")
async def admin_get_all_cache_by_quiz_id(
    id_: int,
    company_id: int,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await redis_service.export_cached_results_for_one_user_to_csv(
        user_id=current_user.id, id_=id_, company_id=company_id, db=db
    )

@redis_router.get("/admin_get_all_cache_by_quiz_id")
async def admin_get_all_cache_by_quiz_id(
    quiz_id: int,
    company_id: int,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await redis_service.export_cached_results_to_csv(
        user_id=current_user.id, quiz_id=quiz_id, company_id=company_id, db=db
    )

