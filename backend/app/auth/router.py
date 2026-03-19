from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_session
from app.models.user import User, UserRole
from app.auth.schemas import UserCreate, UserLogin, UserRead, Token
from app.auth.service import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    blacklist_refresh_token,
    is_refresh_token_blacklisted
)
from app.auth.dependencies import get_current_user, get_current_active_user
from app.auth.roles import require_role, require_roles
from app.core.email import send_email
from app.auth.service import create_email_verify_token, verify_email_token
from app.core.email_templates import verify_email_template


router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", response_model=UserRead)
async def register(data: UserCreate, session: AsyncSession = Depends(get_session)):
    query = select(User).where(User.email == data.email)
    result = await session.execute(query)
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(400, "User already exists")

    user = User(
        email=data.email,
        hashed_password=hash_password(data.password),
        role=UserRole.user,
        is_verified=False
    )

    session.add(user)
    await session.commit()
    await session.refresh(user)

    token = await create_email_verify_token(user.id)
    verify_url = f"http://192.168.0.10:8000/auth/verify-email?token={token}"

    html = verify_email_template(verify_url)

    send_email(
        to=user.email,
        subject="Подтверждение email для CRM Service Center",
        body=html
    )


    return user

@router.post("/login", response_model=Token)
async def login(data: UserLogin, session: AsyncSession = Depends(get_session)):
    query = select(User).where(User.email == data.email)
    result = await session.execute(query)
    user = result.scalar_one_or_none()

    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(401, "Invalid credentials")

    return Token(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id)
    )

@router.get("/me", response_model=UserRead)
async def me(current_user: User = Depends(get_current_user)):
    return current_user

@router.get("/profile", response_model=UserRead)
async def profile(user = Depends(get_current_active_user)):
    return user


@router.post("/refresh", response_model=Token)
async def refresh(refresh_token: str):
    if await is_refresh_token_blacklisted(refresh_token):
        raise HTTPException(401, "Refresh token has been revoked")

    payload = decode_token(refresh_token)
    if not payload:
        raise HTTPException(401, "Invalid refresh token")

    user_id = payload["sub"]
    exp = payload["exp"]

    await blacklist_refresh_token(refresh_token, exp)

    return Token(
        access_token=create_access_token(user_id),
        refresh_token=create_refresh_token(user_id)
    )

@router.get("/admin-only")
async def admin_only(user = Depends(require_role(UserRole.admin))):
    return {"msg": "Hello, admin"}

@router.get("/managers")
async def managers(user = Depends(require_roles([UserRole.admin, UserRole.manager]))):
    return {"msg": "Hello, manager or admin"}

@router.post("/logout")
async def logout(refresh_token: str):
    payload = decode_token(refresh_token)
    if not payload:
        raise HTTPException(401, "Invalid refresh token")

    exp = payload["exp"]
    await blacklist_refresh_token(refresh_token, exp)

    return {"detail": "Logged out"}

@router.get("/verify-email")
async def verify_email(token: str, session: AsyncSession = Depends(get_session)):
    user_id = await verify_email_token(token)
    if not user_id:
        raise HTTPException(400, "Invalid or expired token")

    query = select(User).where(User.id == user_id)
    result = await session.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(404, "User not found")

    user.is_verified = True
    await session.commit()

    return {"detail": "Email verified successfully"}

@router.post("/resend-verification")
async def resend_verification(email: str, session: AsyncSession = Depends(get_session)):
    # ищем пользователя
    query = select(User).where(User.email == email)
    result = await session.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(404, "User not found")

    if user.is_verified:
        raise HTTPException(400, "Email already verified")

    # создаём новый токен
    token = await create_email_verify_token(user.id)

    # формируем ссылку
    verify_url = f"http://192.168.0.10:8000/auth/verify-email?token={token}"

    # HTML‑шаблон
    html = verify_email_template(verify_url)

    # отправляем письмо
    send_email(
        to=user.email,
        subject="Повторное подтверждение email — CRM Service Center",
        body=html
    )

    return {"detail": "Verification email sent"}
