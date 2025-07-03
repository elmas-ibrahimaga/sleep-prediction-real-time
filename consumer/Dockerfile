# FROM bitnami/spark:latest
#
# # Set proper working directory and user home
# WORKDIR /app
# ENV HOME=/tmp
#
# # Copy app code and dependencies
# COPY spark_consumer.py .
# COPY jars/ /opt/bitnami/spark/jars/
# COPY models/ /app/models/
#
# # Pre-create Ivy directory to avoid Ivy errors
# RUN mkdir -p /tmp/.ivy2/local
#
# # Install JDK and Python dependencies
# USER root
# RUN apt-get update && apt-get install -y default-jdk
# RUN pip install pandas py4j kafka-python
#
# # Run the Spark consumer
# CMD ["spark-submit", "--master", "local[*]", "--conf", "spark.jars.ivy=/tmp/.ivy2", "/app/spark_consumer.py"]


FROM bitnami/spark:3.3.0-debian-11-r6

# Set proper working directory and user home
WORKDIR /app
ENV HOME=/tmp

# Copy app code and dependencies
COPY spark_consumer.py .
COPY models/ /app/models/

# Pre-create Ivy directory to avoid Ivy errors
RUN mkdir -p /tmp/.ivy2/local

# Copy Kafka connector and client dependency JARs (ensure these are in the consumer folder before build)
COPY spark-sql-kafka-0-10_2.12-3.3.0.jar /opt/bitnami/spark/jars/
COPY kafka-clients-2.8.0.jar /opt/bitnami/spark/jars/
COPY commons-pool2-2.8.1.jar /opt/bitnami/spark/jars/

# Install JDK and Python dependencies
USER root
#RUN apt-get update && apt-get install -y default-jdk
RUN pip install pandas py4j kafka-python

# Run the Spark consumer
CMD ["spark-submit", "--master", "local[*]", "--conf", "spark.jars.ivy=/tmp/.ivy2", "/app/spark_consumer.py"]
