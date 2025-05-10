FROM python:3.10-slim

WORKDIR /app

COPY kafka_producer.py .
COPY Modified_Sleep_health_and_lifestyle_dataset.csv .

RUN pip install --no-cache-dir kafka-python pandas

CMD ["python", "kafka_producer.py"]
