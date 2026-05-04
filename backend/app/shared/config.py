import sys

from pydantic_settings import BaseSettings

_INSECURE_DEFAULTS = {
    "JWT_SECRET": "change-me-in-production",
    "ENCRYPTION_MASTER_KEY": "0" * 64,
}


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://brain:brain@localhost:5432/brain"
    JWT_SECRET: str = "change-me-in-production"
    JWT_EXPIRY_HOURS: int = 24
    ENCRYPTION_MASTER_KEY: str = "0" * 64
    CORS_ORIGIN: str = "http://localhost:3000"
    APP_ENV: str = "development"

    model_config = {"env_file": ".env", "extra": "ignore"}

    def validate_production_secrets(self) -> None:
        if self.APP_ENV != "production":
            return
        errors = []
        if self.JWT_SECRET == _INSECURE_DEFAULTS["JWT_SECRET"]:
            errors.append("JWT_SECRET is using the insecure default — set a strong random value")
        if self.ENCRYPTION_MASTER_KEY == _INSECURE_DEFAULTS["ENCRYPTION_MASTER_KEY"]:
            errors.append("ENCRYPTION_MASTER_KEY is using the insecure default — generate with: openssl rand -hex 32")
        if errors:
            print("FATAL: Insecure configuration in production:", file=sys.stderr)
            for e in errors:
                print(f"  - {e}", file=sys.stderr)
            sys.exit(1)


settings = Settings()
settings.validate_production_secrets()
