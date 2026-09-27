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

# Recarga automatica del codigo SOLO si TALLER_RELOAD tiene valor (el equipo de
# desarrollo lo pone en Taller_Administracion/.env). Por defecto va sin ella:
# en la prueba de Windows del 2026-09-23 uvicorn veia "cambios" sin parar en el
# repo montado (ros2_ws/build e install) y la web entraba en un bucle infinito
# de reinicios. Acotarlo con --reload-dir NO lo evito (probado: decia vigilar
# solo app/ y seguia recargando). Quien usa el proyecto no necesita recarga.
CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port 8000 ${TALLER_RELOAD:+--reload --reload-dir /workspace/app}"]
