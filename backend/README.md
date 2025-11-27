# Backend (FastAPI)

## Execução local
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Migrações
```bash
alembic upgrade head
alembic revision --autogenerate -m "mensagem"
```

## Estrutura
- `app/core`: configurações e utilidades de segurança (JWT, hashing).
- `app/models`: modelos SQLAlchemy (usuários, produtos, vendas, fiscal, auditoria).
- `app/schemas`: modelos Pydantic para requests/responses.
- `app/api/routes`: roteadores FastAPI.
- `app/services`: serviços de negócio (ex: `fiscal.py`).
- `migrations`: scripts Alembic.
