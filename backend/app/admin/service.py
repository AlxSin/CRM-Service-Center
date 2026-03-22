from typing import Any

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


async def get_dashboard_stats(session: AsyncSession) -> dict[str, Any]:
    total_users_result = await session.execute(select(func.count()).select_from(User))
    total_users = int(total_users_result.scalar_one())

    verified_users_result = await session.execute(
        select(func.count()).select_from(User).where(User.is_verified.is_(True))
    )
    verified_users = int(verified_users_result.scalar_one())

    active_users_result = await session.execute(
        select(func.count()).select_from(User).where(User.is_active.is_(True))
    )
    active_users = int(active_users_result.scalar_one())

    return {
        "total_users": total_users,
        "verified_users": verified_users,
        "active_users": active_users,
    }


async def list_users(session: AsyncSession, limit: int = 50) -> list[User]:
    result = await session.execute(
        select(User).order_by(User.created_at.desc()).limit(limit)
    )
    return list(result.scalars().all())


async def get_user_by_id(session: AsyncSession, user_id: int) -> User | None:
    result = await session.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()

