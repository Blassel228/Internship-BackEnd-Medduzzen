from passlib.context import CryptContext
from typing import Annotated
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from app.db.models.models import UserModel, session
from app.core.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token/token/")
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
        email = payload.get("email")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    res = await db.execute(select(UserModel).where(UserModel.email == email))
    user = res.scalar()
    if user is None:
        raise credentials_exception
    return user
