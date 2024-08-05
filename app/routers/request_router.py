from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.CRUD.request_crud import request_crud
from app.schemas.schemas import RequestCreateInSchema
from app.services.request_service import request_service
from app.utils.deps import get_db, get_current_user

request_router = APIRouter(tags=["Request"], prefix="/request")


@request_router.get("/sent")
async def get_all_sent_requests(
    db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)
):
    """Retrieve all requests sent by the current user."""
    return await request_crud.get_all_by_filter(
        db=db, filters={"sender_id": current_user.id}
    )


@request_router.get("/owner/requests")
async def get_all_owner_requests(
    company_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Retrieve all requests sent within a company."""
    return await request_service.owner_get_all_requests(
        user_id=current_user.id, company_id=company_id, db=db
    )


@request_router.post("/send")
async def send_request(
    request: RequestCreateInSchema,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Send a new request."""
    return await request_service.send_request(
        request=request, db=db, user_id=current_user.id
    )


@request_router.delete("/delete")
async def delete_request(
    id_: int, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)
):
    """Delete a request sent by the current user."""
    return await request_service.user_delete_its_request(
        id_=id_, db=db, user_id=current_user.id
    )


@request_router.post("/accept")
async def accept_request(
    id_: int,
    company_name: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Accept a request."""
    return await request_service.accept_request(
        id_=id_, db=db, user_id=current_user.id, company_name=company_name
    )


@request_router.delete("/reject")
async def reject_request(
    id_: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Reject a request."""
    return await request_service.reject_request(
        id_=id_, db=db, user_id=current_user.id
    )
