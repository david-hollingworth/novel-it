FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /code

# Only copy and install requirements
COPY requirements.txt /code/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Don't COPY the project - it comes from the volume mount

EXPOSE 8000

