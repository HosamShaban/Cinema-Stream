FROM python:3.11-slim AS build

WORKDIR /usr/src/app

# ---------- Install build dependencies ----------
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# ---------- Create virtual environment ----------
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# ---------- Install Python dependencies ----------
COPY requirements.txt ./requirements.txt

RUN pip install --upgrade pip && \
    if [ -f requirements.txt ]; then \
        pip install -r requirements.txt && \
        pip install gunicorn psycopg2-binary; \
    fi

# ---------- Copy project ----------
COPY . .

# ---------- Collect Static ----------
RUN python manage.py collectstatic --noinput


# ---------- Runtime Image ----------
FROM python:3.11-slim

WORKDIR /usr/src/app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=build /opt/venv /opt/venv
COPY --from=build /usr/src/app .

ENV PATH="/opt/venv/bin:$PATH"

RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /usr/src/app
USER appuser

ENV PORT=8080
EXPOSE $PORT

# ------------ START SERVER ------------
CMD python manage.py migrate && \
    gunicorn --bind 0.0.0.0:$PORT --workers 4 --threads 2 --timeout 120 cinema_stream_project.wsgi:application