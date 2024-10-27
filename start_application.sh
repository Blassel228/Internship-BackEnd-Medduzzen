#!/bin/bash
set -e

function start_celery_worker() {
    echo "Starting Celery worker..."
    celery -A app.celery_app:app --broker redis://redis.bdajto.ng.0001.use1.cache.amazonaws.com:6379/0 --result-backend redis://redis.bdajto.ng.0001.use1.cache.amazonaws.com:6379/0 worker --pool=solo --loglevel=info -E &
    WORKER_PID=$!
}

function start_celery_beat() {
    echo "Starting Celery beat..."
    celery -A app.celery_app:app --broker redis://redis.bdajto.ng.0001.use1.cache.amazonaws.com:6379/0 --result-backend redis://redis.bdajto.ng.0001.use1.cache.amazonaws.com:6379/0 beat --loglevel=info &
    BEAT_PID=$!
}

function start_uvicorn() {
    echo "Starting Uvicorn server..."
    uvicorn app.main:app --host 0.0.0.0 --port 8002 &
    UVICORN_PID=$!
}

function stop_services() {
    echo "Stopping Uvicorn server..."
    kill $UVICORN_PID
    echo "Stopping Celery beat..."
    kill $BEAT_PID
    echo "Stopping Celery worker..."
    kill $WORKER_PID
}

trap stop_services SIGTERM SIGINT

start_celery_worker
start_celery_beat
start_uvicorn

wait $UVICORN_PID
stop_services
