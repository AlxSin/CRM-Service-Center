from fastapi import FastAPI
from app.auth.router import router as auth_router
from app.admin.router import router as admin_router

app = FastAPI(title="CRM Service Center", version="0.1.0")

app.include_router(auth_router)
app.include_router(admin_router)

@app.get("/health")
async def health():
    return {"status": "ok"}
