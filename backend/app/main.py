from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.shared.config import settings
from app.shared.database import async_session
from app.auth.router import router as auth_router
from app.properties.router import router as properties_router
from app.systems.router import router as systems_router
from app.knowledge.router import router as knowledge_router
from app.credentials.router import router as credentials_router
from app.sync.router import router as sync_router
from app.automations.router import router as automations_router
from app.automations.scheduler import create_scheduler, sync_tasks_to_scheduler
from app.rag.router import router as rag_router
from app.chat.router import router as chat_router
from app.tools.router import key_mgmt_router, tool_router
from app.users.router import router as users_router
from app.admin.router import router as admin_router
from app.sync.reservations_router import router as reservations_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = await create_scheduler()
    async with async_session() as db:
        await sync_tasks_to_scheduler(db, scheduler)
    async with scheduler:
        yield


limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="BrAIn API",
    version="1.0.0",
    description="Business Knowledge Operating System for RentalMe.es",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.CORS_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth_router)
app.include_router(properties_router)
app.include_router(systems_router)
app.include_router(knowledge_router)
app.include_router(credentials_router)
app.include_router(sync_router)
app.include_router(automations_router)
app.include_router(rag_router)
app.include_router(chat_router)
app.include_router(key_mgmt_router)
app.include_router(tool_router)
app.include_router(users_router)
app.include_router(admin_router)
app.include_router(reservations_router)


@app.get("/health")
async def health():
    return {"status": "ok", "version": "1.0.0"}
