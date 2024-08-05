from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.redis_service import redis_service
from app.utils.deps import get_current_user, get_db

redis_router = APIRouter(prefix="/redis", tags=["Redis"])


@redis_router.get("/user/results")
async def get_user_results_cache(current_user=Depends(get_current_user)):
    """Get cached results for the current user."""
    return await redis_service.user_get_its_result(user_id=current_user.id)


@redis_router.get("/admin/results/company")
async def admin_get_all_cache_by_company_name(
    company_name: str,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Admin get all cached results for a company by company name."""
    return await redis_service.admin_get_all_cache_by_company_id(
        user_id=current_user.id, db=db, company_name=company_name
    )


@redis_router.get("/admin/results/quiz")
async def admin_get_all_results_by_quiz_id(
    quiz_id: int,
    company_name: str,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Admin get all cached results for a specific quiz by quiz ID and company name."""
    return await redis_service.admin_get_all_results_by_quiz_id(
        user_id=current_user.id, quiz_id=quiz_id, company_name=company_name, db=db
    )


@redis_router.get("/export/user/results/csv")
async def export_user_results_to_csv(
    id_: int,
    company_name: str,
    quiz_id: int,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Export cached results for a specific user to CSV."""
    return await redis_service.export_cached_results_for_one_user_to_csv(
        user_id=current_user.id,
        quiz_id=quiz_id,
        id_=id_,
        company_name=company_name,
        db=db,
    )


@redis_router.get("/export/all/results/csv")
async def export_all_results_to_csv(
    quiz_id: int,
    company_name: str,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Export all cached results for a specific quiz to CSV."""
    return await redis_service.export_all_cached_results_to_csv(
        user_id=current_user.id, quiz_id=quiz_id, company_name=company_name, db=db
    )


@redis_router.delete("/cache")
async def delete_cache(key: str):
    """Delete a specific cache entry."""
    return await redis_service.delete(key=key)
