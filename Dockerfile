FROM python:3.9-slim-buster

WORKDIR /usr/src/app

RUN apt-get update \
    && apt-get -y install libpq-dev gcc python3-flask

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .
COPY /lib /lib

# configure the container to run in an executed manner
ENTRYPOINT [ "python", "-m", "flask", "run" ]