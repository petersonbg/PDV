from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    app_name: str = Field("PDV Backend", description="Nome da aplicação")
    debug: bool = Field(False, description="Ativa modo debug")
    secret_key: str = Field("changeme", description="Chave JWT/criptografia")
    algorithm: str = Field("HS256", description="Algoritmo JWT")
    access_token_expire_minutes: int = Field(60 * 8, description="Duração do token JWT")
    refresh_token_expire_days: int = Field(7, description="Duração do refresh token em dias")
    log_file: str = Field("logs/app.log", description="Arquivo para logs de erro")

    # IMPORTANTE: no Docker, o host é "postgres", não "localhost"
    database_url: str = Field(
        default="postgresql+asyncpg://pdv:pdv@postgres:5432/pdv",
        description="URL de conexão ao PostgreSQL"
    )

    class Config:
        env_file = ".env"
        extra = "ignore"
        case_sensitive = False


@lru_cache
def get_settings() -> Settings:
    return Settings()
