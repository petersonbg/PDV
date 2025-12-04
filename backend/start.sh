#!/bin/sh
set -e

# Executa migrações para garantir que o banco de dados exista e esteja atualizado
alembic upgrade head

# Inicia o servidor FastAPI
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
