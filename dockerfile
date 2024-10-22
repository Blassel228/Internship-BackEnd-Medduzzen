FROM python:3.11.5
WORKDIR /code
COPY ./requirements.txt /code/requirements.txt
RUN pip install --upgrade -r /code/requirements.txt
COPY . /code
COPY start_celery.sh /code/start_celery.sh
RUN chmod +x /code/start_celery.sh

ARG POSTGRES_HOST
ARG POSTGRES_PORT
ARG POSTGRES_DB
ARG POSTGRES_USER
ARG POSTGRES_PASSWORD
ARG REDIS_HOST
ARG REDIS_PORT
ARG REDIS_PASSWORD
ARG SECRET
ARG ALGORITHM
ARG DOMAIN
ARG API_AUDIENCE
ARG ISSUER

RUN echo "POSTGRES_HOST=${POSTGRES_HOST}" > /code/.env && \
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

#RUN generate_env.sh

EXPOSE 8000 5555

CMD ["bash", "/code/start_celery.sh"]
