#!/bin/bash
set -e

echo "Starting Celery worker..."
celery -A app.celery_app:app --broker redis://redis1.bdajto.ng.0001.use1.cache.amazonaws.com:6379/0 --result-backend redis://redis-bdajto.serverless.use1.cache.a>
WORKER_PID=$!

echo "Starting Celery beat..."
celery -A app.celery_app:app --broker redis://redis1.bdajto.ng.0001.use1.cache.amazonaws.com:6379/0 --result-backend redis://redis-bdajto.serverless.use1.cache.a>
BEAT_PID=$!

echo "Starting Uvicorn server..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 &
UVICORN_PID=$!

function stop_services() {
    echo "Stopping Uvicorn server..."
    kill $UVICORN_PID
    echo "Stopping Celery beat..."
    kill $BEAT_PID
    echo "Stopping Celery worker..."
    kill $WORKER_PID
}

trap stop_services SIGTERM SIGINT

wait $UVICORN_PID
wait $BEAT_PID
wait $WORKER_PID