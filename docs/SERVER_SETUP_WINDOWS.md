# Guia de implantação do servidor (Windows)

Este guia descreve como preparar e publicar o backend FastAPI em um ambiente Windows, partindo do repositório.

## 1. Pré-requisitos
- Windows com **Docker Desktop** (WSL 2 habilitado) para orquestrar PostgreSQL (e opcionalmente o backend).
- **Python 3.11+** e **pip** caso execute o backend fora de contêiner.
- **Git** para obter o código.
- Acesso para abrir portas (ex.: 8000 para a API) e configurar um proxy reverso (NGINX/IIS) com HTTPS.

## 2. Clonar o repositório
```powershell
git clone <url-do-repo> PDV
cd PDV
```
A estrutura de pastas é descrita no README principal.

## 3. Configurar variáveis de ambiente do backend
Crie um arquivo `.env` em `backend/` com, no mínimo:
```
DATABASE_URL=postgresql+asyncpg://usuario:senha@localhost:5432/pdv
SECRET_KEY=uma_chave_segura
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```
A API usa FastAPI/SQLAlchemy e lê esses valores na inicialização.

## 4. Subir infraestrutura com Docker
1. Ajuste `docker-compose.yml` se precisar trocar portas ou credenciais do PostgreSQL.
2. No PowerShell, a partir da raiz do projeto:
   ```powershell
   docker compose up -d
   ```
   Isso cria o banco e pode ser estendido para incluir a imagem do backend.

## 5. Preparar ambiente Python (opção sem contêiner para a API)
```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

## 6. Aplicar migrações do banco
Ainda em `backend/` com o ambiente ativo:
```powershell
alembic upgrade head
```
As tabelas descritas em `docs/ARCHITECTURE.md` serão criadas no PostgreSQL.

## 7. Executar a API
- Desenvolvimento / validação:
  ```powershell
  uvicorn app.main:app --host 0.0.0.0 --port 8000
  ```
- Produção (recomendado detrás de proxy HTTPS):
  ```powershell
  pip install "uvicorn[standard]" gunicorn
  gunicorn app.main:app -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 --workers 4
  ```
Mantenha o serviço rodando como **Windows Service** ou via **NSSM**, e coloque NGINX/IIS como proxy reverso com TLS.

## 8. Verificar conectividade
- Cheque `/docs` (Swagger) em `https://seu-dominio` via browser.
- Verifique logs do serviço e do proxy para status 200/401.

## 9. Próximos passos (opcional)
- Configurar backups automáticos do PostgreSQL.
- Habilitar métricas/healthcheck (ex.: endpoint customizado no FastAPI).
- Integrar a pipeline de CI/CD para build e publicação da imagem do backend.
