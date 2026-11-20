from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
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

    @property
    def cors_origins_list(self) -> list[str]:
        return [
            origin.strip() for origin in self.cors_origins.split(",") if origin.strip()
        ]


settings = Settings()
