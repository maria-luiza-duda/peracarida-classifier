# Imagem base
FROM python:3.9

# Diretório de trabalho
WORKDIR /app

# Instalar as dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    rabbitmq-server \
    && rm -rf /var/lib/apt/lists/*

# Copiar arquivos de requisitos
COPY backend/requirements.txt .

# Instalar dependências do backend
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --upgrade minio

# Copiar arquivos do backend
COPY . .

# Porta em que o servidor estará escutando
EXPOSE 8000

# ...

# Instalar o MinIO
RUN wget https://dl.minio.io/server/minio/release/linux-amd64/minio && \
    chmod +x minio

# Comando para executar o servidor Django
CMD ["./minio server /data --console-address ":9001"","python", "manage.py", "runserver", "0.0.0.0:8000"]
