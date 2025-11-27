# Arquitetura do PDV

## Visão geral
- **API**: FastAPI (Python 3.11+) com SQLAlchemy 2.0 e async sessions.
- **Banco**: PostgreSQL.
- **Migrações**: Alembic.
- **Frente de Caixa**: Electron + React (desktop), com cache local e sincronização.
- **Retaguarda**: React Web (SPA) consumindo a API.

## Camadas do backend
- `core/`: configuração, segurança (JWT), middlewares e utilidades.
- `db/`: sessão assíncrona e base declarativa.
- `models/`: entidades de domínio (usuários, produtos, estoque, vendas, financeiro, auditoria, fiscal).
- `schemas/`: contratos Pydantic para entrada/saída.
- `services/`: regras de negócio e integrações (ex: fiscal).
- `api/routes/`: roteadores agrupados por contexto.

## Fluxos principais
- **Autenticação e permissões**: JWT + perfis (roles) e permissões granularizadas.
- **Cadastro de produtos e estoque**: produtos, variantes, estoque por local, movimentações e inventário cíclico.
- **Vendas (PDV)**: abertura de caixa, pré-venda, pagamento, emissão fiscal (NFC-e/SAT/MFE) e cancelamento.
- **Financeiro**: contas a pagar/receber, conciliações, meios de pagamento e taxas.
- **Auditoria**: trilhas de auditoria para operações críticas, armazenadas na tabela `audit_logs`.

## Integração fiscal
- Interface `FiscalAdapter` em `services/fiscal.py` padroniza emissões/consultas.
- Implementações concretas podem chamar SDKs (NFC-e, SAT/MFE) ou serviços de terceiros.
- As tabelas `fiscal_documents` e `fiscal_events` mantêm estado e histórico.

## Frontends
- **PDV (Electron)**: UI otimizada para teclado/leitor de código de barras, fila offline de operações e sincronização via API.
- **Admin Web**: dashboards, cadastros, estoque, financeiro e auditoria.
- Ambos usam React com componentes reutilizáveis e chamadas à API via fetch/axios.

## Dev/ops
- `docker-compose.yml` sobe PostgreSQL e backend.
- Use `alembic upgrade head` para preparar o banco.
- Variáveis em `.env` (backend) controlam secrets e URLs.
