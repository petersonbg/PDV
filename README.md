# PDV System Blueprint

Este repositório fornece uma estrutura inicial para um sistema de PDV (Ponto de Venda) completo, cobrindo frente de caixa, retaguarda, integrações fiscais e controles financeiros/estoque. A base utiliza **FastAPI + PostgreSQL** no backend, **SQLAlchemy/Alembic** para ORM e migrações, e frontends em **React** (Electron para o PDV desktop e Web para a retaguarda).

## Componentes
- **Backend (FastAPI):** serviços REST, autenticação, permissões, logs e integrações fiscais.
- **Banco de dados (PostgreSQL):** persistência relacional com SQLAlchemy e migrações Alembic.
- **PDV Desktop (Electron + React):** interface de frente de caixa, suporte offline e sincronização com o backend.
- **Admin Web (React):** retaguarda para cadastros, estoque, financeiro e relatórios.
- **Infra/Docker:** `docker-compose` para desenvolvimento local com PostgreSQL e backend.

## Estrutura resumida
- `backend/`: aplicação FastAPI, modelos, schemas, serviços e migrações.
- `frontend/pdv-app/`: shell Electron + React para frente de caixa.
- `frontend/admin-app/`: SPA React para retaguarda/admin.
- `docs/`: notas de arquitetura e decisões.

Consulte `docs/ARCHITECTURE.md` para detalhes das camadas, fluxos e boas práticas.
