from flask import Flask, request, render_template
from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable
import json, time, os, glob, logging
import pandas as pd

app = Flask(__name__, static_folder='static', template_folder='templates')

# ---------------- Logging Setup ----------------
logging.basicConfig(
    filename='user_submissions.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# ---------------- Kafka Setup ----------------
KAFKA_TOPIC = "sleep-health"
KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP", "kafka:9092")

producer = None
for i in range(10):
    try:
        producer = KafkaProducer(
            bootstrap_servers=KAFKA_BOOTSTRAP,
            value_serializer=lambda v: json.dumps(v).encode("utf-8")
        )
        print(f"✅ Connected to Kafka at {KAFKA_BOOTSTRAP}")
        break
    except NoBrokersAvailable:
        print(f"⚠️ Kafka not available. Retry {i+1}/10...")
        time.sleep(5)
    except Exception as e:
        print(f"❌ Kafka error: {e}")
        break

# ---------------- Prediction Fetch ----------------
def get_latest_prediction(person_id):
    try:
        files = sorted(glob.glob("/app/predictions_output/predictions/*.csv"), key=os.path.getmtime, reverse=True)
        for f in files:
            df = pd.read_csv(f)
            if "Person ID" in df.columns and "Predicted Disorder Name" in df.columns:
                df["Person ID"] = pd.to_numeric(df["Person ID"], errors="coerce").fillna(-1).astype(int)
                match = df[df["Person ID"] == person_id]
                if not match.empty:
                    return match.iloc[-1].to_dict()
    except Exception as e:
        print(f"❌ Error reading prediction: {e}")
    return None

# ---------------- Main Route ----------------
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            person_id = int(request.form["person_id"])
            message = {
                "Person ID": person_id,
                "Age": int(request.form["age"]),
                "Sleep Duration": float(request.form["sleep_duration"]),
                "Quality of Sleep": int(request.form["quality_of_sleep"]),
                "Physical Activity Level": float(request.form["physical_activity_level"]),
                "Stress Level": int(request.form["stress_level"]),
                "BMI Category": request.form["bmi_category"],
                "Gender": request.form["gender"],
                "Occupation": request.form["occupation"],
                "Heart Rate": int(request.form["heart_rate"]),
                "Daily Steps": int(request.form["daily_steps"]),
                "Sleep Disorder Index": 0
            }

            if producer:
                producer.send(KAFKA_TOPIC, value=message)
                print("✅ Kafka sent:", message)

                prediction = None
                for _ in range(10):
                    time.sleep(1)
                    prediction = get_latest_prediction(person_id)
                    if prediction and "Predicted Disorder Name" in prediction:
                        break

                logging.info(f"User ID {person_id} → Predicted: {prediction.get('Predicted Disorder Name', 'N/A')}")
                return render_template("index.html", prediction=prediction)
            else:
                return render_template("index.html", message="⚠️ Kafka not connected.", prediction=None)

        except Exception as e:
            return render_template("index.html", message=f"❌ Error: {e}", prediction=None)

    return render_template("index.html", prediction=None)

# ---------------- Stats Route ----------------
@app.route('/stats')
def stats():
    stats = {}
    try:
        log_path = 'user_submissions.log'
        if os.path.exists(log_path):
            with open(log_path, 'r') as f:
                for line in f:
                    if "Predicted:" in line:
                        disorder = line.strip().split("Predicted:")[-1].strip()
                        stats[disorder] = stats.get(disorder, 0) + 1
    except Exception as e:
        print(f"⚠️ Error loading stats: {e}")
    return render_template("stats.html", stats=stats)

# ---------------- Run App ----------------
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
