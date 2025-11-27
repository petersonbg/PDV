from functools import lru_cache
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    app_name: str = Field("PDV Backend", description="Nome da aplicação")
    debug: bool = Field(False, description="Ativa modo debug")
    secret_key: str = Field("changeme", description="Chave JWT/criptografia")
    algorithm: str = Field("HS256", description="Algoritmo JWT")
    access_token_expire_minutes: int = Field(60 * 8, description="Duração do token JWT")

    database_url: str = Field(
        "postgresql+asyncpg://pdv:pdv@localhost:5432/pdv",
        description="URL de conexão ao PostgreSQL",
    )

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache
def get_settings() -> Settings:
    return Settings()
