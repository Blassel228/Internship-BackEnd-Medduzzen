from typing import Annotated
from fastapi import APIRouter, Depends
from fastapi.security import (
    OAuth2PasswordRequestForm,
    HTTPBearer,
    HTTPAuthorizationCredentials,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.autho.autho import get_auth0_user
from app.autho.autho import login_get_token, oauth2_scheme
from app.schemas.schemas import TokenSchema
from app.utils.deps import get_current_user, get_db

security = HTTPBearer()

token_router = APIRouter(tags=["Token"], prefix="/token")


@token_router.post("/login", response_model=TokenSchema)
async def get_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: AsyncSession = Depends(get_db),
):
    return await login_get_token(form_data=form_data, db=db)


@token_router.post("/me")
async def get_by_token(
    token: Annotated[str, Depends(oauth2_scheme)], db: AsyncSession = Depends(get_db)
):
    return await get_current_user(token=token, db=db)


@token_router.get("/users/me")
async def read_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: AsyncSession = Depends(get_db),
):
    return await get_current_user(token=credentials.credentials, db=db)


@token_router.post("/auth0")
async def get_by_token(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: AsyncSession = Depends(get_db),
):
    return await get_auth0_user(token=credentials.credentials, db=db)
