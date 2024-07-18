from datetime import timedelta, datetime
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Annotated
from fastapi import status
from passlib.context import CryptContext
from app.db.models import UserModel
from app.utils.deps import get_db
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import  Depends, HTTPException
from fastapi.security import HTTPBearer
from jose import jwt as jose_jwt
from config import settings

bearer = HTTPBearer()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token/login/")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def login_get_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                          db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(username=form_data.username, password=form_data.password, db=db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=20)
    access_token = create_access_token(
        data={"username": user.username, "id": user.id, "email": user.email},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

async def authenticate_user(password: str, username: str, db: AsyncSession):
    res = await db.execute(select(UserModel).where(UserModel.username == username))
    user = res.scalar()
    if not user:
        return False
    if not pwd_context.verify(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jose_jwt.encode(to_encode, settings.secret, algorithm=settings.algorithm)
    return encoded_jwt