import pandas as pd
import os

# List the files in the predictions_output directory
pred_dir = "/mnt/data/predictions_output"
os.makedirs(pred_dir, exist_ok=True)

# Create a placeholder summary file for demonstration
summary_file = os.path.join(pred_dir, "README.md")

summary_content = """
# Sleep Health & Lifestyle Prediction Pipeline ✅

This project demonstrates a real-time data analytics architecture using **Apache Kafka**, **Apache Spark**, and **Flask** for predicting sleep disorders based on lifestyle and biometric input data.

## 🔄 Data Flow

User Form (Flask) → Kafka Topic (sleep-health) → Spark Structured Streaming Consumer → ML Model Prediction → CSV Output


## 💡 Components

- **Flask Web App**: Simple HTML form takes user input and sends it to Kafka.
- **Kafka**: Streams input data to the `sleep-health` topic.
- **Spark**: Reads from Kafka, applies pre-trained ML model, writes predictions to `/app/predictions_output`.
- **ML Model**: Logistic regression trained on sleep/lifestyle dataset.

## ✅ Test Checklist

- [x] Flask form loads on `localhost:5000`
- [x] Kafka topic `sleep-health` is created and messages sent from form
- [x] Spark consumer receives and processes data
- [x] Predictions saved as CSV in `consumer:/app/predictions_output`
- [x] Data schema matches trained model's expected input

## 📁 Output

CSV files with predictions are located in:

/app/predictions_output/


Each file includes:
- `Person ID`
- `Sleep Disorder Index` (actual)
- `Predicted Disorder Index`
- Human-readable disorder names

## 🛠️ Next Steps

- Add `volume` mapping to persist CSVs on host
- Optionally log predictions to a database or UI
- Add unit tests and real-time dashboard

---

Made with ❤️ for data streaming excellence!
"""

with open(summary_file, "w") as f:
    f.write(summary_content)

summary_file

---
import os

# Recreate the summary markdown after environment reset
pred_dir = "/mnt/data/predictions_output"
os.makedirs(pred_dir, exist_ok=True)

summary_file = os.path.join(pred_dir, "README.md")
summary_content = """
# Sleep Health & Lifestyle Prediction Pipeline ✅

This project demonstrates a real-time data analytics architecture using **Apache Kafka**, **Apache Spark**, and **Flask** for predicting sleep disorders based on lifestyle and biometric input data.

## 🔄 Data Flow

User Form (Flask) → Kafka Topic (sleep-health) → Spark Structured Streaming Consumer → ML Model Prediction → CSV Output


## 💡 Components

- **Flask Web App**: Simple HTML form takes user input and sends it to Kafka.
- **Kafka**: Streams input data to the `sleep-health` topic.
- **Spark**: Reads from Kafka, applies pre-trained ML model, writes predictions to `/app/predictions_output`.
- **ML Model**: Logistic regression trained on sleep/lifestyle dataset.

## ✅ Test Checklist

- [x] Flask form loads on `localhost:5000`
- [x] Kafka topic `sleep-health` is created and messages sent from form
- [x] Spark consumer receives and processes data
- [x] Predictions saved as CSV in `consumer:/app/predictions_output`
- [x] Data schema matches trained model's expected input

## 📁 Output

CSV files with predictions are located in:

/app/predictions_output/


Each file includes:
- `Person ID`
- `Sleep Disorder Index` (actual)
- `Predicted Disorder Index`
- Human-readable disorder names

## 🛠️ Next Steps

- Add `volume` mapping to persist CSVs on host
- Optionally log predictions to a database or UI
- Add unit tests and real-time dashboard

---

Made with ❤️ for data streaming excellence!
"""

with open(summary_file, "w") as f:
    f.write(summary_content)

summary_file

'/mnt/data/predictions_output/README.md'