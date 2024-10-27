#!/bin/bash

echo "POSTGRES_HOST=${POSTGRES_HOST}" > /code/.env && \
echo "POSTGRES_PORT=${POSTGRES_PORT}" >> /code/.env && \
echo "POSTGRES_DB=${POSTGRES_DB}" >> /code/.env && \
echo "POSTGRES_USER=${POSTGRES_USER}" >> /code/.env && \
echo "POSTGRES_PASSWORD=${POSTGRES_PASSWORD}" >> /code/.env && \
echo "REDIS_HOST=${REDIS_HOST}" >> /code/.env && \
echo "REDIS_PORT=${REDIS_PORT}" >> /code/.env && \
echo "REDIS_PASSWORD=${REDIS_PASSWORD}" >> /code/.env && \
echo "SECRET=${SECRET}" >> /code/.env && \
echo "ALGORITHM=${ALGORITHM}" >> /code/.env && \
echo "DOMAIN=${DOMAIN}" >> /code/.env && \
echo "API_AUDIENCE=${API_AUDIENCE}" >> /code/.env && \
echo "ISSUER=${ISSUER}" >> /code/.env
