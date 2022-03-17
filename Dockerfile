FROM python:alpine

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install psycopg2 dependencies
RUN apk update \
    && apk add postgresql-dev gcc python3-dev musl-dev

RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN mkdir -p /var/logs/stock-buddy/
COPY . . 
# create db if needed,  migrate than runserver
ENTRYPOINT ["/bin/sh", "docker-entrypoint.sh"]


