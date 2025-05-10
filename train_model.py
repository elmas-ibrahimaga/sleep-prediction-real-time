from pyspark.sql import SparkSession
from pyspark.sql.functions import when, col
from pyspark.ml.feature import VectorAssembler, StandardScaler, StringIndexer
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
df = spark.read.csv("datasets/Modified_Sleep_health_and_lifestyle_dataset.csv", header=True, inferSchema=True)


df = df.na.drop(subset=["Sleep Disorder"])

# Map Sleep Disorder to numeric
df = df.withColumn("Sleep_Disorder_Index",
                   when(col("Sleep Disorder") == "Sleep Apnea", 1)
                   .when(col("Sleep Disorder") == "Insomnia", 2)
                   .when(col("Sleep Disorder") == "None", 0)
                   .otherwise(-1))
df = df.filter(col("Sleep_Disorder_Index") != -1)

# Index categorical fields with handleInvalid="keep"
gender_indexer = StringIndexer(inputCol="Gender", outputCol="Gender_Index", handleInvalid="keep")
occupation_indexer = StringIndexer(inputCol="Occupation", outputCol="Occupation_Index", handleInvalid="keep")
bmi_indexer = StringIndexer(inputCol="BMI Category", outputCol="BMI_Category_Index", handleInvalid="keep")

df = gender_indexer.fit(df).transform(df)
df = occupation_indexer.fit(df).transform(df)
df = bmi_indexer.fit(df).transform(df)

# Assemble features
assembler = VectorAssembler(
    inputCols=[
        "Age", "Sleep Duration", "Quality of Sleep", "Physical Activity Level",
        "Stress Level", "Heart Rate", "Daily Steps",
        "Occupation_Index", "Gender_Index", "BMI_Category_Index"
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
train_df = train_df.withColumnRenamed("Sleep_Disorder_Index", "label")
test_df = test_df.withColumnRenamed("Sleep_Disorder_Index", "label")

# Convert to pandas for SVM and Naive Bayes
X_train = pd.DataFrame(train_df.select("scaledFeatures").rdd.map(lambda row: row[0].toArray()).collect())
X_test = pd.DataFrame(test_df.select("scaledFeatures").rdd.map(lambda row: row[0].toArray()).collect())
y_train = train_df.select("label").rdd.flatMap(lambda x: x).collect()
y_test = test_df.select("label").rdd.flatMap(lambda x: x).collect()

# Scale for sklearn
minmax_scaler = MinMaxScaler()
X_train_scaled = minmax_scaler.fit_transform(X_train)
X_test_scaled = minmax_scaler.transform(X_test)

# Models
models = {
    "Multinomial Logistic Regression": LogisticRegression(featuresCol="scaledFeatures", labelCol="label", maxIter=50, family="multinomial"),
    "Random Forest": RandomForestClassifier(featuresCol="scaledFeatures", labelCol="label", numTrees=100),
    "GBT": OneVsRest(classifier=GBTClassifier(featuresCol="scaledFeatures", labelCol="label", maxIter=100)),
    "SVM": SVC(kernel="linear", probability=True, random_state=42),
    "Multinomial Naive Bayes": MultinomialNB()
}

metrics = []
for name, model in models.items():
    if name in ["Multinomial Logistic Regression", "Random Forest", "GBT"]:
        trained = model.fit(train_df)
        predictions = trained.transform(test_df)
        if name == "Multinomial Logistic Regression":
            trained.save("models/logistic_regression_model")
        evaluator = MulticlassClassificationEvaluator(labelCol="label", predictionCol="prediction")

        accuracy = evaluator.evaluate(predictions, {evaluator.metricName: "accuracy"})
        precision = evaluator.evaluate(predictions, {evaluator.metricName: "weightedPrecision"})
        recall = evaluator.evaluate(predictions, {evaluator.metricName: "weightedRecall"})
        f1 = evaluator.evaluate(predictions, {evaluator.metricName: "f1"})

        cm = confusion_matrix(predictions.select("label").toPandas(), predictions.select("prediction").toPandas())
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
        plt.title(f'Confusion Matrix for {name}')
        plt.xlabel('Predicted')
        plt.ylabel('Actual')
        plt.savefig(f'confusion_matrix_{name}.png')
        plt.clf()
    else:
        model.fit(X_train_scaled, y_train)
        y_pred = model.predict(X_test_scaled)
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, average="weighted")
        recall = recall_score(y_test, y_pred, average="weighted")
        f1 = f1_score(y_test, y_pred, average="weighted")
        cm = confusion_matrix(y_test, y_pred)
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
        plt.title(f'Confusion Matrix for {name}')
        plt.xlabel('Predicted')
        plt.ylabel('Actual')
        plt.savefig(f'confusion_matrix_{name}.png')
        plt.clf()

    metrics.append({
        "Model": name,
        "Accuracy": accuracy,
        "Precision": precision,
        "Recall": recall,
        "F1-Score": f1
    })

# Save and print metrics
pd.DataFrame(metrics).to_csv("model_metrics_with_all_models.csv", index=False)
print(pd.DataFrame(metrics))

