FROM python:3.10-slim

WORKDIR /app

# Variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instala dependências do sistema (git é útil)
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# 1. Copia APENAS o requirements primeiro (para aproveitar o cache do Docker)
COPY requirements.txt .

# 2. Instala as bibliotecas
RUN pip install --no-cache-dir -r requirements.txt

# 3. Só depois copia o código
COPY . .

CMD ["python", "main.py"]