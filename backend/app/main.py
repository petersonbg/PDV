import traceback

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from app.api.routes import (
    auth,
    estoque,
    financeiro,
    fiscal,
    health,
    impressoras,
    pagamentos,
    produtos,
    relatorios,
    vendas,
)
from app.core.config import get_settings
from app.core.logging import setup_logging
from app.db.session import AsyncSessionLocal
from app.models.error_log import ErrorLog
from app.models.user import User

settings = get_settings()
logger = setup_logging(settings)
app = FastAPI(title=settings.app_name, debug=settings.debug, version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(produtos.router, prefix="/api")
app.include_router(vendas.router, prefix="/api")
app.include_router(estoque.router, prefix="/api")
app.include_router(financeiro.router, prefix="/api")
app.include_router(pagamentos.router, prefix="/api")
app.include_router(fiscal.router, prefix="/api")
app.include_router(relatorios.router, prefix="/api")
app.include_router(impressoras.router, prefix="/api")


@app.get("/", tags=["root"])
async def root():
    return {"message": "PDV API up"}


async def _extract_user_id(session: AsyncSession, request: Request) -> int | None:
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.lower().startswith("bearer "):
        return None

    token = auth_header.split(" ", 1)[1]
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    except JWTError:
        return None

    email = payload.get("sub")
    if not email:
        return None

    result = await session.execute(select(User.id).where(User.email == email))
    return result.scalar_one_or_none()


async def _persist_error_log(
    request: Request, status_code: int | None = None, exc: Exception | None = None
) -> None:
    async with AsyncSessionLocal() as session:
        user_id = await _extract_user_id(session, request)
        details = traceback.format_exc() if exc else None
        message = str(exc) if exc else "Erro durante processamento da requisição"
        log = ErrorLog(
            level="ERROR" if (status_code or 0) >= 500 else "WARNING",
            message=message,
            details=details,
            path=str(request.url.path),
            method=request.method,
            status_code=status_code,
            user_id=user_id,
        )
        session.add(log)
        await session.commit()


@app.middleware("http")
async def error_logging_middleware(request: Request, call_next):
    try:
        response = await call_next(request)
        if response.status_code >= 500:
            logger.error("Erro interno na requisição %s", request.url.path)
            await _persist_error_log(request, status_code=response.status_code)
        return response
    except HTTPException as exc:
        if exc.status_code >= 500:
            logger.exception("HTTPException capturada")
            await _persist_error_log(request, status_code=exc.status_code, exc=exc)
        raise
    except Exception as exc:  # pylint: disable=broad-except
        logger.exception("Exceção não tratada")
        await _persist_error_log(request, status_code=500, exc=exc)
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})
