FROM python:3.12-slim

WORKDIR /workspace

# git: solo para el fallback de VERSION (main.py lo calcula del repo padre
# montado en /workspace/repo si nadie ha corrido generar_version.sh --
# sesion 2026-09-16, instalacion limpia sin ese paso se quedaba en
# "sin-version" para siempre).
RUN apt-get update && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
