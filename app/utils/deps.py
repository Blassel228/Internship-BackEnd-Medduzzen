from passlib.context import CryptContext
from typing import Annotated
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from app.db.models import UserModel, session
from config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token/login/")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def get_db():
    db = session()
    try:
        yield db
    finally:
        await db.close()


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], db: AsyncSession = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    try:
        payload = jwt.decode(token, settings.secret, algorithms=[settings.algorithm])
        user_id: int = payload.get("id")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    res = await db.execute(select(UserModel).where(UserModel.id == user_id))
    user = res.scalar()
    if user is None:
        raise credentials_exception
    return user
