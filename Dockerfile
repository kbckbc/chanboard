FROM tiangolo/uwsgi-nginx-flask:python3.8

RUN pip install flask flask-pymongo flask-wtf

COPY . /app
WORKDIR /app