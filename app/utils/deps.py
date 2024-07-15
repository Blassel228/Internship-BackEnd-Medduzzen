from passlib.context import CryptContext
from app.db.models import session

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def get_db():
    db = session()
    try:
        yield db
    finally:
        await db.close()