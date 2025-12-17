# CAMBIO 1: Usamos 'bookworm' (Debian 12). Es mucho más estable que 'slim' a secas.
FROM python:3.11-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/code \
    # --- CORRECCIÓN PARA SIGILL EN GCP ---
    # Desactiva optimizaciones OneDNN que a veces causan SIGILL en CPUs antiguas/virtuales
    TF_ENABLE_ONEDNN_OPTS=0 \
    # Filtra logs de advertencia de TensorFlow para limpiar la salida
    TF_CPP_MIN_LOG_LEVEL=2

WORKDIR /code

# CAMBIO 2: Limpiamos listas antes de instalar para evitar caché corrupta de apt
# Y añadimos intentos de reparación automática
RUN apt-get clean && \
    apt-get update -o Acquire::CompressionTypes::Order::=gz && \
    apt-get install -y --no-install-recommends --fix-missing \
    gcc curl \
    && rm -rf /var/lib/apt/lists/*

COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN useradd -m -u 1000 engineer
USER engineer

COPY --chown=engineer:engineer app /code/app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Comando de arranque (Gunicorn gestiona 4 procesos Uvicorn)
CMD ["gunicorn", "app.main:app", "--bind", "0.0.0.0:8000", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker"]