# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.12.5
FROM python:${PYTHON_VERSION}-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    server

COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt


FROM base AS dev
COPY . .
USER server
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]


FROM base AS prod
COPY . .
RUN python manage.py collectstatic --noinput
USER server
CMD ["gunicorn", "--bind", "0.0.0.0:3045", "--access-logfile", "-", "-w", "2", "voximplant_medsenger_bot.wsgi:application"]


FROM base AS worker
COPY . .
USER server
CMD ["python", "manage.py", "start_bot"]

