# Usamos uma imagem "slim" para economizar espaço e memória
FROM python:3.10-slim

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Variáveis de ambiente para evitar arquivos .pyc e logs presos no buffer
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instalamos o git (necessário para algumas dependências ou operações futuras)
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Comando padrão que mantém o container rodando para podermos desenvolver
CMD ["tail", "-f", "/dev/null"]