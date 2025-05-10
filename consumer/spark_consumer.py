from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, when
from pyspark.sql.types import StructType, StructField, IntegerType, StringType, DoubleType
from pyspark.ml.feature import StringIndexerModel, VectorAssembler, StandardScalerModel
from pyspark.ml.classification import LogisticRegressionModel
from kafka.admin import KafkaAdminClient, NewTopic
import os
from datetime import datetime
from pyspark.sql.functions import lit

# ---------------------------
# 0. Configuration
# ---------------------------
KAFKA_SERVER = os.getenv("KAFKA_BOOTSTRAP", "kafka:9092")
TOPIC_NAME = "sleep-health"
BASE_PATH = "/app/models"

print(f">>> Connecting to Kafka at {KAFKA_SERVER}")

# ---------------------------
# 1. Create Topic if Missing
# ---------------------------
try:
    admin_client = KafkaAdminClient(bootstrap_servers=KAFKA_SERVER)
    topic_list = [NewTopic(name=TOPIC_NAME, num_partitions=1, replication_factor=1)]
    admin_client.create_topics(new_topics=topic_list, validate_only=False)
    print("✅ Created topic sleep-health.")
except Exception as e:
    print(f"⚠️ Topic already exists or could not be created: {e}")

# ---------------------------
# 2. Start Spark Session
# ---------------------------
spark = SparkSession.builder.appName("Sleep Health and Lifestyle Predictor").getOrCreate()
spark.sparkContext.setLogLevel("WARN")

# ---------------------------
# 3. Load Pretrained Models
# ---------------------------
gender_indexer = StringIndexerModel.load(f"{BASE_PATH}/Gender_Index_indexer_model")
occupation_indexer = StringIndexerModel.load(f"{BASE_PATH}/Occupation_Index_indexer_model")
bmi_indexer = StringIndexerModel.load(f"{BASE_PATH}/BMI_Index_indexer_model")
scaler = StandardScalerModel.load(f"{BASE_PATH}/scaler_model")
classifier = LogisticRegressionModel.load(f"{BASE_PATH}/logistic_regression_model")

# ---------------------------
# 4. Define Schema
# ---------------------------
schema = StructType([
    StructField("Person ID", IntegerType(), True),
    StructField("Age", IntegerType(), True),
    StructField("Sleep Duration", DoubleType(), True),
    StructField("Quality of Sleep", IntegerType(), True),
    StructField("Physical Activity Level", DoubleType(), True),
    StructField("Stress Level", IntegerType(), True),
    StructField("BMI Category", StringType(), True),
    StructField("Gender", StringType(), True),
    StructField("Occupation", StringType(), True),
    StructField("Heart Rate", IntegerType(), True),
    StructField("Daily Steps", IntegerType(), True),
    StructField("Sleep Disorder Index", IntegerType(), True),
])

# ---------------------------
# 5. Read Stream from Kafka
# ---------------------------
kafka_stream = spark.readStream.format("kafka") \
    .option("kafka.bootstrap.servers", KAFKA_SERVER) \
    .option("subscribe", TOPIC_NAME) \
    .option("startingOffsets", "earliest") \
    .option("failOnDataLoss", "false") \
    .load()

# ---------------------------
# 6. Parse and Transform Data
# ---------------------------
parsed_df = kafka_stream.selectExpr("CAST(value AS STRING)") \
    .select(from_json(col("value"), schema).alias("data")) \
    .select("data.*")

indexed_df = gender_indexer.transform(parsed_df)
indexed_df = occupation_indexer.transform(indexed_df)
indexed_df = bmi_indexer.transform(indexed_df)

assembler = VectorAssembler(
    inputCols=[
        "Age", "Sleep Duration", "Quality of Sleep", "Physical Activity Level",
        "Stress Level", "Heart Rate", "Daily Steps",
        "Gender_Index", "Occupation_Index", "BMI_Index"
    ],
    outputCol="features",
    handleInvalid="skip"
)
assembled_df = assembler.transform(indexed_df)
scaled_df = scaler.transform(assembled_df)

# ---------------------------
# 7. Predict
# ---------------------------
predictions = classifier.transform(scaled_df)

result_df = predictions.select(
    "Person ID",
    "Sleep Disorder Index",
    when(col("Sleep Disorder Index") == 0, "No Disorder")
        .when(col("Sleep Disorder Index") == 1, "Insomnia")
        .when(col("Sleep Disorder Index") == 2, "Sleep Apnea")
        .otherwise("Unknown").alias("Original Disorder Name"),
    col("prediction").cast(IntegerType()).alias("Predicted Disorder Index"),
    when(col("prediction") == 0, "No Disorder")
        .when(col("prediction") == 1, "Insomnia")
        .when(col("prediction") == 2, "Sleep Apnea")
        .otherwise("Unknown").alias("Predicted Disorder Name")
)

# ---------------------------
# 8. Output to Console + CSV
# ---------------------------
result_df_with_time = result_df.withColumn("timestamp", lit(datetime.now().isoformat()))

query = result_df_with_time.writeStream \
    .outputMode("append") \
    .format("csv") \
    .option("checkpointLocation", "/tmp/spark_checkpoint") \
    .option("path", "/app/predictions_output/predictions") \
    .option("header", True) \
    .trigger(processingTime="5 seconds") \
    .start()

query.awaitTermination()
