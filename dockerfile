FROM python:3
WORKDIR /code
COPY ./requirements.txt /code/requirements.txt
RUN pip install --upgrade -r /code/requirements.txt
COPY . /code
COPY start_celery.sh /code/start_celery.sh
RUN chmod +x /code/start_celery.sh
EXPOSE 8000 5555
CMD ["/code/start_celery.sh"]