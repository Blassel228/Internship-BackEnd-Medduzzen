#!/bin/bash
set -e

REDIS_URL="redis://redis.bdajto.ng.0001.use1.cache.amazonaws.com:6379/0"

function start_celery_worker() {
    echo "Starting Celery worker..."
    exec celery -A app.celery_app:app --broker "$REDIS_URL" --result-backend "$REDIS_URL" worker --pool=solo --loglevel=info -E &
    WORKER_PID=$!
}

function start_celery_beat() {
    echo "Starting Celery beat..."
    exec celery -A app.celery_app:app --broker "$REDIS_URL" --result-backend "$REDIS_URL" beat --loglevel=info &
    BEAT_PID=$!
}

function start_uvicorn() {
    echo "Starting Uvicorn server..."
    exec uvicorn app.main:app --host 0.0.0.0 --port 8002 &
    UVICORN_PID=$!
}

function stop_services() {
    echo "Stopping services..."
    kill $UVICORN_PID $BEAT_PID $WORKER_PID
}

trap stop_services SIGTERM SIGINT

start_celery_worker
start_celery_beat
start_uvicorn

wait $UVICORN_PID
stop_services
