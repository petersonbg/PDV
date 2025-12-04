FROM python:3.11-slim

# Dentro do container
WORKDIR /app

# Copia os arquivos de dependência
COPY requirements.txt .

# Instala dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código da aplicação
COPY . .

# Expõe a porta usada pelo FastAPI
EXPOSE 8000

# Comando para aplicar migrações e rodar o servidor
CMD ["./start.sh"]
