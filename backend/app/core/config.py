from pydantic_settings import BaseSettings, SettingsConfigDict

INSECURE_DEFAULTS = {"", "change_me", "change_me_jwt_secret", "change_me_pepper"}


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    env: str = "development"
    app_name: str = "Cuidar API"
    api_v1_prefix: str = "/api"

    database_url: str = "sqlite+pysqlite:///./test.db"
    cors_origins: str = "http://localhost:5173"

    jwt_secret_key: str = "change_me"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7

    fernet_key: str = ""
    tracking_code_pepper: str = "change_me"

    captcha_provider: str = "mock"
    turnstile_site_key: str = ""
    turnstile_secret_key: str = ""

    @property
    def cors_origins_list(self) -> list[str]:
        return [
            origin.strip() for origin in self.cors_origins.split(",") if origin.strip()
        ]


settings = Settings()


def validate_production_settings(config: Settings | None = None) -> None:
    current = config or settings
    if current.env != "production":
        return
    insecure: list[str] = []
    if current.jwt_secret_key.strip() in INSECURE_DEFAULTS:
        insecure.append("JWT_SECRET_KEY")
    if current.tracking_code_pepper.strip() in INSECURE_DEFAULTS:
        insecure.append("TRACKING_CODE_PEPPER")
    if current.fernet_key.strip() in INSECURE_DEFAULTS:
        insecure.append("FERNET_KEY")
    if current.captcha_provider.strip().lower() == "mock":
        insecure.append("CAPTCHA_PROVIDER=mock")
    if insecure:
        raise RuntimeError(
            "Configuración insegura para producción: " + ", ".join(insecure)
        )
