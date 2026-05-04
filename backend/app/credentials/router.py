from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import require_admin
from app.auth.models import User
from app.shared.database import get_db
from app.credentials import service as credential_service
from app.sync.providers.guesty import test_guesty_connection

router = APIRouter(prefix="/api/v1/credentials", tags=["credentials"])


class CredentialUpsert(BaseModel):
    value: str


class CredentialResponse(BaseModel):
    service_name: str
    updated_at: str | None = None


@router.get("")
async def list_credentials(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    return await credential_service.list_credentials(db)


@router.put("/{service_name}")
async def upsert_credential(
    service_name: str,
    body: CredentialUpsert,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    credential = await credential_service.store_credential(
        db, service_name, body.value, updated_by=current_user.id
    )
    return {"service_name": credential.service_name, "updated_at": credential.updated_at.isoformat()}


@router.delete("/{service_name}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_credential(
    service_name: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    deleted = await credential_service.delete_credential(db, service_name)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Credential not found")


@router.post("/{service_name}/test")
async def test_credential(
    service_name: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    value = await credential_service.get_credential(db, service_name)
    if not value:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Credential not configured")

    if service_name == "GUESTY_API_KEY":
        result = await test_guesty_connection(value)
        return result

    return {"status": "ok", "message": f"Credential '{service_name}' is stored"}
