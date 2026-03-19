from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from jose import jwt, JWTError
from app.core.config import settings
from app.core.redis import redis
import uuid

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
BLACKLIST_PREFIX = "blacklist:refresh:"
EMAIL_VERIFY_PREFIX = "email_verify:"

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)

def create_access_token(user_id: int) -> str:
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": user_id, "exp": int(expire.timestamp())}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

def create_refresh_token(user_id: int) -> str:
    expire = datetime.utcnow() + timedelta(days=7)
    payload = {"sub": user_id, "exp": int(expire.timestamp())}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

def decode_token(token: str):
    try:
        return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    except JWTError:
        return None

async def blacklist_refresh_token(token: str, expires_at: int):
    ttl = int(expires_at) - int(datetime.now(tz=timezone.utc).timestamp())
    if ttl > 0:
        await redis.setex(f"{BLACKLIST_PREFIX}{token}", ttl, "1")

async def is_refresh_token_blacklisted(token: str) -> bool:
    return await redis.exists(f"{BLACKLIST_PREFIX}{token}") == 1

async def create_email_verify_token(user_id: int) -> str:
    token = str(uuid.uuid4())
    await redis.setex(f"{EMAIL_VERIFY_PREFIX}{token}", 3600, str(user_id))
    return token

async def verify_email_token(token: str) -> int | None:
    key = f"{EMAIL_VERIFY_PREFIX}{token}"
    user_id = await redis.get(key)
    if user_id:
        await redis.delete(key)
        return int(user_id)
    return None