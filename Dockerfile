# 1. Imagem Base
FROM python:3.13-slim-bookworm

# 2. Instalar UV
COPY --from=ghcr.io/astral-sh/uv:0.9.13 /uv /bin/uv

WORKDIR /app

# Variáveis de Ambiente
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV UV_COMPILE_BYTECODE=1
# Garante que o UV use o ambiente virtual criado dentro do container
ENV UV_PROJECT_ENVIRONMENT="/app/.venv"

# ========================================================
# CAMADA 1: DEPENDÊNCIAS (Cacheada)
# ========================================================
COPY pyproject.toml uv.lock .python-version* ./

RUN uv sync --locked --no-install-project

# Setup do Crawl4AI (Browsers) - Isso é pesado, então fazemos antes de copiar o código
RUN uv run crawl4ai-setup

# ========================================================
# CAMADA 2: CÓDIGO FONTE (Muda Frequentemente)
# ========================================================

# Copia explicitamente apenas as pastas e arquivos que você quer
COPY src ./src
COPY docs ./docs
COPY output ./output
COPY streamlit_app.py .
COPY app.py .


# Agora sincroniza o projeto em si (instala o pacote 'src' se estiver configurado como package)
RUN uv sync --locked

# ========================================================
# RUNTIME
# ========================================================

EXPOSE 8501

# O 'uv run' já sabe usar o venv criado anteriormente
CMD ["uv", "run", "streamlit", "run", "streamlit_app.py", "--server.address=0.0.0.0"]