from kafka import KafkaProducer
import json
import pandas as pd
import time

# Kafka Configuration
kafka_bootstrap_servers = 'localhost:9092'
topic_name = 'sleep-health'

# Load Dataset
data = pd.read_csv('Modified_Sleep_health_and_lifestyle_dataset.csv')

# Initialize Kafka Producer
producer = KafkaProducer(
    bootstrap_servers=kafka_bootstrap_servers,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Stream Data
print("Starting Kafka producer...")
try:
    while True:
        for index, row in data.iterrows():
            message = row.to_dict()
            producer.send(topic_name, value=message)
            print(f"Message Sent: {message}")
            time.sleep(0.1)  # Simulate streaming
        print("Completed one cycle of dataset. Restarting...")
        time.sleep(2)  # Optional delay between cycles
except KeyboardInterrupt:
    print("Producer interrupted.")
finally:
    print("Producer stopping.")
    producer.close()





