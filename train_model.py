from pyspark.sql import SparkSession
from pyspark.sql.functions import when, col
from pyspark.ml.feature import VectorAssembler, StandardScaler
from pyspark.ml.classification import LogisticRegression, RandomForestClassifier, GBTClassifier, OneVsRest
from pyspark.ml.evaluation import MulticlassClassificationEvaluator
from sklearn.svm import SVC
from sklearn.naive_bayes import MultinomialNB
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Initialize Spark session
spark = SparkSession.builder.appName("Train Sleep Disorder Model").getOrCreate()

# Load dataset
df = spark.read.csv("Modified_Sleep_health_and_lifestyle_dataset.csv", header=True, inferSchema=True)

# Preprocess data
df = df.na.drop(subset=["Sleep Disorder"])

# Map Sleep Disorder to numeric values (None=0, Sleep Apnea=1, Insomnia=2)
df = df.withColumn("Sleep_Disorder_Index",
                   when(col("Sleep Disorder") == "Sleep Apnea", 1)
                   .when(col("Sleep Disorder") == "Insomnia", 2)
                   .when(col("Sleep Disorder") == "None", 0)
                   .otherwise(-1))

# Ensure we exclude invalid rows (if any)
df = df.filter(col("Sleep_Disorder_Index") != -1)

# Feature engineering
assembler = VectorAssembler(
    inputCols=[
        "Age", "Sleep Duration", "Quality of Sleep", "Physical Activity Level",
        "Stress Level", "Heart Rate", "Daily Steps"
    ],
    outputCol="features"
)
df = assembler.transform(df)

# Scale features
scaler = StandardScaler(inputCol="features", outputCol="scaledFeatures", withStd=True, withMean=False)
scaler_model = scaler.fit(df)
df = scaler_model.transform(df)

# Train-test split
train_df, test_df = df.randomSplit([0.8, 0.2], seed=42)

# Rename the label column for OneVsRest model
train_df = train_df.withColumnRenamed("Sleep_Disorder_Index", "label")
test_df = test_df.withColumnRenamed("Sleep_Disorder_Index", "label")

# Convert Spark DataFrames to Pandas for SVM and Naive Bayes
X_train = pd.DataFrame(train_df.select("scaledFeatures").rdd.map(lambda row: row[0].toArray()).collect())
X_test = pd.DataFrame(test_df.select("scaledFeatures").rdd.map(lambda row: row[0].toArray()).collect())
y_train = train_df.select("label").rdd.flatMap(lambda x: x).collect()
y_test = test_df.select("label").rdd.flatMap(lambda x: x).collect()

# Scale for SVM and MultinomialNB
scaler = MinMaxScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Models
models = {
    "Multinomial Logistic Regression": LogisticRegression(featuresCol="scaledFeatures", labelCol="label", maxIter=50,
                                                          family="multinomial"),
    "Random Forest": RandomForestClassifier(featuresCol="scaledFeatures", labelCol="label", numTrees=100),
    "GBT": OneVsRest(classifier=GBTClassifier(featuresCol="scaledFeatures", labelCol="label", maxIter=100)),
    "SVM": SVC(kernel="linear", probability=True, random_state=42),
    "Multinomial Naive Bayes": MultinomialNB()
}

# Evaluate models
metrics = []
for model_name, model in models.items():
    if model_name in ["Multinomial Logistic Regression", "Random Forest", "GBT"]:
        # Train models in PySpark
        trained_model = model.fit(train_df)
        predictions = trained_model.transform(test_df)
        evaluator = MulticlassClassificationEvaluator(labelCol="label", predictionCol="prediction")

        accuracy = evaluator.evaluate(predictions, {evaluator.metricName: "accuracy"})
        precision = evaluator.evaluate(predictions, {evaluator.metricName: "weightedPrecision"})
        recall = evaluator.evaluate(predictions, {evaluator.metricName: "weightedRecall"})
        f1 = evaluator.evaluate(predictions, {evaluator.metricName: "f1"})

        # Confusion Matrix
        predictions_pd = predictions.select("prediction", "label").toPandas()
        cm = confusion_matrix(predictions_pd["label"], predictions_pd["prediction"])
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
        plt.title(f'Confusion Matrix for {model_name}')
        plt.xlabel('Predicted')
        plt.ylabel('Actual')
        plt.savefig(f'confusion_matrix_{model_name}.png')
        plt.clf()

    else:
        # Train SVM and Multinomial Naive Bayes
        model.fit(X_train_scaled, y_train)
        y_pred = model.predict(X_test_scaled)

        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, average="weighted")
        recall = recall_score(y_test, y_pred, average="weighted")
        f1 = f1_score(y_test, y_pred, average="weighted")

        # Confusion Matrix
        cm = confusion_matrix(y_test, y_pred)
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
        plt.title(f'Confusion Matrix for {model_name}')
        plt.xlabel('Predicted')
        plt.ylabel('Actual')
        plt.savefig(f'confusion_matrix_{model_name}.png')
        plt.clf()

    # Append metrics
    metrics.append({
        "Model": model_name,
        "Accuracy": accuracy,
        "Precision": precision,
        "Recall": recall,
        "F1-Score": f1
    })

# Save metrics to CSV
metrics_df = pd.DataFrame(metrics)
metrics_df.to_csv("model_metrics_with_all_models.csv", index=False)

# Print metrics
print(metrics_df)

# Rename label column back to original
train_df = train_df.withColumnRenamed("label", "Sleep_Disorder_Index")
test_df = test_df.withColumnRenamed("label", "Sleep_Disorder_Index")






