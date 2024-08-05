from datetime import timedelta, datetime
from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi import status
from fastapi.security import HTTPBearer
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt as jose_jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.models.models import UserModel
from app.utils.deps import get_db

bearer = HTTPBearer()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token/login/")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def login_get_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: AsyncSession = Depends(get_db),
):
    user = await authenticate_user(
        username=form_data.username, password=form_data.password, db=db
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=20)
    access_token = create_access_token(
        data={"username": user.username, "id": user.id, "email": user.email},
        expires_delta=access_token_expires,
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
    encoded_jwt = jose_jwt.encode(
        to_encode, settings.secret, algorithm=settings.algorithm
    )
    return encoded_jwt


async def get_auth0_user(
    token: Annotated[str, Depends(oauth2_scheme)], db: AsyncSession = Depends(get_db)
):
    try:
        payload = jose_jwt.decode(
            token,
            settings.secret,
            algorithms=[settings.algorithm],
            audience=settings.api_audience,
            issuer=settings.issuer,
        )
        email = payload.get("email")
        if email is None:
            raise HTTPException(
                status_code=404, detail="Email not found in token payload"
            )
    except JWTError as e:
        raise HTTPException(status_code=404, detail=f"JWT Error: {str(e)}")

    res = await db.execute(select(UserModel).where(UserModel.email == email))
    user = res.scalar()

    if user is None:
        new_user = UserModel(
            username="empty",
            hashed_password=pwd_context.hash("empty"),
            email=email,
            registration_date=datetime.utcnow(),
        )
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        user = new_user

    return user
