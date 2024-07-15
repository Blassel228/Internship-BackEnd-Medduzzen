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
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from urllib.request import urlopen
from config import settings
from app.schemas.schemas import TokenBearerSchema
import json

bearer = HTTPBearer()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token/token/")
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
    encoded_jwt = jwt.encode(to_encode, settings.secret, algorithm=settings.algorithm)
    return encoded_jwt


class VerifyToken():
    def __init__(self, token, permissions=None, scopes=None):
        self.token = token
        self.permissions = permissions
        self.scopes = scopes

        # This gets the JWKS from a given URL and does processing so you can use any of
        # the keys available
        jwks_url = f'https://{settings.domain}/.well-known/jwks.json'
        self.jwks_client = jwt.PyJWKClient(jwks_url)

    def verify(self):
        # This gets the 'kid' from the passed token
        try:
            self.signing_key = self.jwks_client.get_signing_key_from_jwt(
                self.token
            ).key
        except jwt.exceptions.PyJWKClientError as error:
            return {"status": "error", "msg": error.__str__()}
        except jwt.exceptions.DecodeError as error:
            return {"status": "error", "msg": error.__str__()}
        try:
            payload = jwt.decode(
                self.token,
                self.signing_key,
                algorithms=settings.algorithm,
                audience=settings.api_audience,
                issuer=settings.issuer,
            )
        except Exception as e:
            return {"status": "error", "message": str(e)}
        if self.scopes:
            result = self._check_claims(payload, 'scope', str, self.scopes.split(' '))
            if result.get("error"):
                return result
        if self.permissions:
            result = self._check_claims(payload, 'permissions', list, self.permissions)
            if result.get("error"):
                return result
        return payload

    def _check_claims(self, payload, claim_name, claim_type, expected_value):
        instance_check = isinstance(payload[claim_name], claim_type)
        result = {"status": "success", "status_code": 200}
        payload_claim = payload[claim_name]
        if claim_name not in payload or not instance_check:
            result["status"] = "error"
            result["status_code"] = 400

            result["code"] = f"missing_{claim_name}"
            result["msg"] = f"No claim '{claim_name}' found in token."
            return result
        if claim_name == 'scope':
            payload_claim = payload[claim_name].split(' ')
        for value in expected_value:
            if value not in payload_claim:
                result["status"] = "error"
                result["status_code"] = 403
                result["code"] = f"insufficient_{claim_name}"
                result["msg"] = (f"Insufficient {claim_name} ({value}). You don't have "
                                  "access to this resource")
                return result
        return result