# pull official base image
FROM python:3.10

COPY ./requirements.txt ./
RUN apt-get update && apt-get install -y python3-dev supervisor
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
