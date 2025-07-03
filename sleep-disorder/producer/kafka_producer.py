

import os
import json
import time
import pandas as pd
from kafka import KafkaProducer

# Kafka Configuration (via env var, default to kafka:9092)
kafka_bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP", "kafka:9092")
topic_name = 'sleep-health'

# Load Dataset
data = pd.read_csv("Modified_Sleep_health_and_lifestyle_dataset.csv")

# Wait for Kafka to be available
for attempt in range(30):
    try:
        producer = KafkaProducer(
            bootstrap_servers=kafka_bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        print(f"✅ Kafka producer connected at {kafka_bootstrap_servers}.")
        break
    except Exception as e:
        print(f"⚠️ Kafka not ready yet ({e}). Retrying in 3s...")
        time.sleep(3)
else:
    raise Exception("❌ Failed to connect to Kafka after multiple attempts.")

# Stream Data
print("🚀 Starting Kafka producer...")
try:
    while True:
        for _, row in data.iterrows():
            message = row.to_dict()
            producer.send(topic_name, value=message)
            print(f"📤 Message sent: {message}")
            time.sleep(0.1)
        print("🔁 One full cycle completed. Restarting...")
        time.sleep(2)
except KeyboardInterrupt:
    print("🛑 Producer interrupted.")
finally:
    print("👋 Stopping producer...")
    producer.close()
