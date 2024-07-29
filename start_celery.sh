#!/bin/bash
set -e

echo "Starting Celery worker..."
celery -A app.celery_app:app --broker redis://redis:6379/0 --result-backend redis://redis:6379/0 worker --pool=solo --loglevel=info -E &
WORKER_PID=$!

echo "Starting Celery beat..."
celery -A app.celery_app:app --broker redis://redis:6379/0 --result-backend redis://redis:6379/0 beat --loglevel=info &
BEAT_PID=$!

echo "Starting Uvicorn server..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 &
UVICORN_PID=$!

# Function to stop all services
function stop_services() {
    echo "Stopping Uvicorn server..."
    kill $UVICORN_PID
    echo "Stopping Celery beat..."
    kill $BEAT_PID
    echo "Stopping Celery worker..."
    kill $WORKER_PID
}

# Trap SIGTERM and SIGINT to stop services
trap stop_services SIGTERM SIGINT

# Wait for all services to stop
wait $UVICORN_PID
#wait $FLOWER_PID
wait $BEAT_PID
wait $WORKER_PID