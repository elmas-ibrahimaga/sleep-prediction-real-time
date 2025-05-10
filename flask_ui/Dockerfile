FROM python:3.10-slim

# Avoid prompts and warnings from apt
ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# System dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
        iputils-ping \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies
RUN pip install --no-cache-dir flask kafka-python pandas

# Copy your app
COPY app.py .
COPY templates/ /app/templates/
COPY static/ /app/static/
COPY templates/ /app/templates/

CMD ["python", "app.py"]
