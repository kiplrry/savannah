FROM python:3.10-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt /app/

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

COPY . /app

EXPOSE 8000

RUN 

