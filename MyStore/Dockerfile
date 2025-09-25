FROM python:3.10-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt /app/

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

COPY . /app

EXPOSE 8000

CMD gunicorn MyStore.wsgi:application --bind 0.0.0.0:$PORT --workers 4


RUN 

