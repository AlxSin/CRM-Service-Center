from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.auth.roles import require_role
from app.models.user import UserRole

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
    dependencies=[Depends(require_role(UserRole.admin))]
)

templates = Jinja2Templates(directory="app/admin/templates")


@router.get("/", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@router.get("/users", response_class=HTMLResponse)
async def admin_users(request: Request, session=Depends(get_session)):
    users = (await session.execute(select(User))).scalars().all()
    return templates.TemplateResponse("users.html", {"request": request, "users": users})

@router.get("/users/{user_id}", response_class=HTMLResponse)
async def admin_user_detail(user_id: int, request: Request, session=Depends(get_session)):
    query = select(User).where(User.id == user_id)
    result = await session.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "message": "User not found"},
            status_code=404
        )

    return templates.TemplateResponse(
        "user_detail.html",
        {"request": request, "user": user}
    )

from fastapi import Form

@router.post("/users/{user_id}/update-role")
async def admin_update_role(
    user_id: int,
    role: str = Form(...),
    session=Depends(get_session)
):
    query = select(User).where(User.id == user_id)
    result = await session.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(404, "User not found")

    user.role = role
    await session.commit()

    return RedirectResponse(f"/admin/users/{user_id}", status_code=303)

@router.post("/users/{user_id}/verify")
async def admin_verify_user(user_id: int, session=Depends(get_session)):
    query = select(User).where(User.id == user_id)
    result = await session.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(404, "User not found")

    user.is_verified = True
    await session.commit()

    return RedirectResponse(f"/admin/users/{user_id}", status_code=303)

@router.post("/users/{user_id}/delete")
async def admin_delete_user(user_id: int, session=Depends(get_session)):
    query = select(User).where(User.id == user_id)
    result = await session.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(404, "User not found")

    await session.delete(user)
    await session.commit()

    return RedirectResponse("/admin/users", status_code=303)
