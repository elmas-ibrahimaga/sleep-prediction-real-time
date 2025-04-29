from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, when, lit
from pyspark.ml.feature import VectorAssembler, StringIndexerModel
from pyspark.ml.classification import LogisticRegressionModel
from pyspark.ml import PipelineModel
from pyspark.sql.types import StructType, StructField, IntegerType, StringType, DoubleType

# Initialize Spark session
spark = SparkSession.builder \
    .appName("Sleep Health and Lifestyle Predictor") \
    .getOrCreate()

# Paths to saved models
pipeline_model_path = "multinomial_logistic_regression_model"

# Load pre-trained pipeline model (contains scaler and logistic regression)
pipeline_model = PipelineModel.load(pipeline_model_path)

# Define schema for incoming data
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
    StructField("Sleep Disorder Index", IntegerType(), True)  # Original disorder index
])

# Read streaming data from Kafka
kafka_stream = spark.readStream.format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "sleep-health") \
    .load()

# Parse JSON data and extract fields
parsed_stream = kafka_stream.selectExpr("CAST(value AS STRING) as value") \
    .select(from_json(col("value"), schema).alias("data")) \
    .select("data.*")

# Transform the data using the pre-trained pipeline
predictions = pipeline_model.transform(parsed_stream) \
    .select(
        "Person ID",
        "Sleep Disorder Index",  # Original disorder index
        col("prediction").alias("Predicted Disorder Index")
    )

# Map indices to disorder names for both original and predicted disorders
predictions = predictions \
    .withColumn(
        "Original Disorder Name",
        when(col("Sleep Disorder Index") == 0, "No Disorder")
        .when(col("Sleep Disorder Index") == 1, "Insomnia")
        .when(col("Sleep Disorder Index") == 2, "Sleep Apnea")
        .otherwise("Unknown")
    ) \
    .withColumn(
        "Predicted Disorder Name",
        when(col("Predicted Disorder Index") == 0, "No Disorder")
        .when(col("Predicted Disorder Index") == 1, "Insomnia")
        .when(col("Predicted Disorder Index") == 2, "Sleep Apnea")
        .otherwise("Unknown")
    )

# Define query to output predictions
query = predictions.select(
    "Person ID",
    "Sleep Disorder Index", "Original Disorder Name",
    "Predicted Disorder Index", "Predicted Disorder Name"
).writeStream \
    .outputMode("append") \
    .format("console") \
    .start()

# Await termination
query.awaitTermination()




# from pyspark.sql import SparkSession
# from pyspark.sql.functions import from_json, col, when, lit
# from pyspark.ml.feature import StringIndexerModel
# from pyspark.ml.classification import LogisticRegressionModel
# from pyspark.ml import PipelineModel
# from pyspark.sql.types import StructType, StructField, IntegerType, StringType, DoubleType
#
# # Initialize Spark session
# spark = SparkSession.builder \
#     .appName("Sleep Health and Lifestyle Predictor") \
#     .getOrCreate()
#
# # Paths to saved models
# pipeline_model_path = "multinomial_logistic_regression_model"
#
# # Load pre-trained pipeline model (contains scaler and logistic regression)
# pipeline_model = PipelineModel.load(pipeline_model_path)
#
# # Define schema for incoming data
# schema = StructType([
#     StructField("Person ID", IntegerType(), True),
#     StructField("Age", IntegerType(), True),
#     StructField("Sleep Duration", DoubleType(), True),
#     StructField("Quality of Sleep", IntegerType(), True),
#     StructField("Physical Activity Level", DoubleType(), True),
#     StructField("Stress Level", IntegerType(), True),
#     StructField("BMI Category", StringType(), True),
#     StructField("Gender", StringType(), True),
#     StructField("Occupation", StringType(), True),
#     StructField("Heart Rate", IntegerType(), True),
#     StructField("Daily Steps", IntegerType(), True),
#     StructField("Sleep Disorder Index", IntegerType(), True)  # Original disorder index
# ])
#
# # Read streaming data from Kafka
# kafka_stream = spark.readStream.format("kafka") \
#     .option("kafka.bootstrap.servers", "localhost:9092") \
#     .option("subscribe", "sleep-health") \
#     .load()
#
# # Parse JSON data and extract fields
# parsed_stream = kafka_stream.selectExpr("CAST(value AS STRING) as value") \
#     .select(from_json(col("value"), schema).alias("data")) \
#     .select("data.*")
#
# # Handle unseen labels for categorical features using StringIndexerModel
# indexer_columns = {
#     "Gender": "Gender_Index",
#     "Occupation": "Occupation_Index",
#     "BMI Category": "BMI_Index"
# }
#
# for input_col, output_col in indexer_columns.items():
#     indexer_model = StringIndexerModel.load(f"{output_col}_indexer_model")
#     indexer_model.setHandleInvalid("keep")  # Handle unseen labels by keeping them
#     parsed_stream = indexer_model.transform(parsed_stream)
#
# # Transform the data using the pre-trained pipeline
# predictions = pipeline_model.transform(parsed_stream) \
#     .select(
#         "Person ID",
#         "Sleep Disorder Index",  # Original disorder index
#         col("prediction").alias("Predicted Disorder Index")
#     )
#
# # Map indices to disorder names for both original and predicted disorders
# predictions = predictions \
#     .withColumn(
#         "Original Disorder Name",
#         when(col("Sleep Disorder Index") == 0, "No Disorder")
#         .when(col("Sleep Disorder Index") == 1, "Insomnia")
#         .when(col("Sleep Disorder Index") == 2, "Sleep Apnea")
#         .otherwise("Unknown")
#     ) \
#     .withColumn(
#         "Predicted Disorder Name",
#         when(col("Predicted Disorder Index") == 0, "No Disorder")
#         .when(col("Predicted Disorder Index") == 1, "Insomnia")
#         .when(col("Predicted Disorder Index") == 2, "Sleep Apnea")
#         .otherwise("Unknown")
#     )
#
# # Define query to output predictions
# query = predictions.select(
#     "Person ID",
#     "Sleep Disorder Index", "Original Disorder Name",
#     "Predicted Disorder Index", "Predicted Disorder Name"
# ).writeStream \
#     .outputMode("append") \
#     .format("console") \
#     .start()
#
# # Await termination
# query.awaitTermination()
