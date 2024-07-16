from app.autho.autho import login_get_token, oauth2_scheme, bearer, VerifyToken
from app.utils.deps import get_current_user, get_db
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from fastapi import APIRouter, Depends, Response, status
from app.schemas.schemas import TokenSchema
from sqlalchemy.ext.asyncio import AsyncSession

token_router = APIRouter(tags=["token"], prefix="/token")


def private(token: str, response: Response):
    result = VerifyToken(token.credentials).verify()
    if result.get("status"):
        response.status_code = status.HTTP_400_BAD_REQUEST
        return result
    return result

@token_router.post("/login", response_model=TokenSchema)
async def get_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: AsyncSession = Depends(get_db)):
    return await login_get_token(form_data=form_data, db=db)

@token_router.post("/me")
async def get_by_token(token: Annotated[str, Depends(oauth2_scheme)], db: AsyncSession = Depends(get_db)):
    return await get_current_user(token=token, db=db)

@token_router.post("/private")
def private(token: str = Depends(bearer), response: Response = Response()):
    return private(token=token, response=response)