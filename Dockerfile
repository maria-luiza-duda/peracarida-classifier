# Imagem base para o backend
FROM python:3.9 as backend

# Diretório de trabalho para o backend
WORKDIR /app/backend

# Copiar arquivos de requisitos
COPY requirements.txt .

# Instalar dependências do backend
RUN pip install --no-cache-dir -r requirements.txt

# Instalar o RabbitMQ
RUN apt-get update && apt-get install -y rabbitmq-server

# Copiar os arquivos do backend
COPY backend .

# Comando para executar o treinamento
CMD ["python", "training.py"]


# Imagem final
FROM python:3.9

# Diretório de trabalho
WORKDIR /classifier

# Instalar as dependências do sistema
RUN apt-get update && apt-get install -y sqlite3

# Copiar arquivos de requisitos
COPY backend/requirements.txt .

# Instalar dependências do backend
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --upgrade minio

# Instalar o RabbitMQ
RUN apt-get update && apt-get install -y rabbitmq-server

# Copiar arquivos do backend
COPY . .

# Copiar o arquivo do banco de dados
COPY db.sqlite3 .

# Porta em que o servidor estará escutando
EXPOSE 8000

# Comando para executar o servidor Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
