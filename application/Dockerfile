# pull official base image
FROM python:3.10
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y python3-dev supervisor mc

COPY ./requirements.txt ./
RUN pip install --upgrade pip
RUN pip install -r /requirements.txt
