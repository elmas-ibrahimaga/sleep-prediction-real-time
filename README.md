# 💤 Sleep Disorder Prediction - Real-Time System

This project predicts sleep disorders in real time using a fully containerized big data pipeline.

## 🚀 Architecture

```text
User → Flask Web Form → Kafka Topic → Spark Streaming → Kafka Topic → Kafka Consumer → Output

🔧 Technologies Used
Python

Apache Kafka – Streaming platform

Apache Spark – Real-time processing & ML

Flask – Web interface

Docker & Docker Compose – Deployment & orchestration

Machine Learning – Pretrained classifier on health data

🛠️ Features
Real-time prediction of sleep disorders

Interactive web form with Flask

Spark reads Kafka topic & applies ML model

Containerized with Docker Compose

Lightweight and modular codebase

📂 How to Run
Make sure you have Docker & Docker Compose installed.

bash
Kopyala
Düzenle
docker-compose up --build
Then open your browser to:
👉 http://localhost:5000

📊 Dataset
Based on the Sleep Health and Lifestyle Dataset.

🧠 ML Model
The model predicts sleep disorders using:

Sleep Duration

Stress Levels

BMI

Occupation

Age

and more

Model trained separately, loaded at runtime by Spark job.
