# Dockerfile Airflow avec Delta Lake
FROM apache/airflow:2.8.1-python3.11

USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
    openjdk-17-jre-headless \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

USER airflow

# Installation des packages Python pour Delta Lake + Spark
RUN pip install --no-cache-dir \
    delta-spark==2.4.0 \
    pyspark==3.4.0 \
    apache-airflow-providers-apache-spark==4.5.0 \
    boto3==1.34.0 \
    psycopg2-binary==2.9.9

# Configuration environnement Java pour Spark
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
