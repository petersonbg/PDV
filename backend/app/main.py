from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth, health, products, sales, audit
from app.core.config import get_settings

settings = get_settings()
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
app.include_router(products.router, prefix="/api")
app.include_router(sales.router, prefix="/api")
app.include_router(audit.router, prefix="/api")


@app.get("/", tags=["root"])
async def root():
    return {"message": "PDV API up"}
