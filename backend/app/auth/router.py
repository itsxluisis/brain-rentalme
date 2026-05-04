from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import COOKIE_NAME, get_current_user
from app.auth.jwt import create_access_token
from app.auth.models import User
from app.auth.schemas import LoginRequest, SetupRequest, UserResponse
from app.auth.service import authenticate, create_admin, get_user_count
from app.shared.config import settings
from app.shared.database import get_db

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

_limiter = Limiter(key_func=get_remote_address)

COOKIE_KWARGS = {
    "key": COOKIE_NAME,
    "httponly": True,
    "samesite": "none" if settings.APP_ENV == "production" else "lax",
    "secure": settings.APP_ENV == "production",
    "max_age": settings.JWT_EXPIRY_HOURS * 3600,
}


@router.post("/setup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@_limiter.limit("5/minute")
async def setup(request: Request, data: SetupRequest, response: Response, db: AsyncSession = Depends(get_db)):
    count = await get_user_count(db)
    if count > 0:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Setup ya completado")

    user = await create_admin(db, data)
    token = create_access_token(user.id, user.role)
    response.set_cookie(value=token, **COOKIE_KWARGS)
    return user


@router.post("/login", response_model=UserResponse)
@_limiter.limit("5/minute")
async def login(request: Request, data: LoginRequest, response: Response, db: AsyncSession = Depends(get_db)):
    user = await authenticate(db, data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas"
        )
    token = create_access_token(user.id, user.role)
    response.set_cookie(value=token, **COOKIE_KWARGS)
    return user


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(key=COOKIE_NAME)
    return {"detail": "Sesión cerrada"}


@router.post("/refresh", response_model=UserResponse)
async def refresh(response: Response, user: User = Depends(get_current_user)):
    token = create_access_token(user.id, user.role)
    response.set_cookie(value=token, **COOKIE_KWARGS)
    return user


@router.get("/me", response_model=UserResponse)
async def me(user: User = Depends(get_current_user)):
    return user
