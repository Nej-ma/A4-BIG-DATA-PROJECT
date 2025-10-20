# Dockerfile Jupyter avec Delta Lake
FROM jupyter/pyspark-notebook:latest

USER root

# Installation des packages système
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

USER jovyan

# Installation Delta Lake + dépendances
RUN pip install --no-cache-dir \
    delta-spark==2.4.0 \
    boto3==1.34.0 \
    psycopg2-binary==2.9.9 \
    matplotlib==3.8.2 \
    seaborn==0.13.0 \
    plotly==5.18.0

# Configuration Spark pour Delta Lake
ENV SPARK_OPTS="--packages io.delta:delta-core_2.12:2.4.0,org.apache.hadoop:hadoop-aws:3.3.4 \
--conf spark.sql.extensions=io.delta.sql.DeltaSparkSessionExtension \
--conf spark.sql.catalog.spark_catalog=org.apache.spark.sql.delta.catalog.DeltaCatalog \
--conf spark.hadoop.fs.s3a.endpoint=http://chu_minio:9000 \
--conf spark.hadoop.fs.s3a.access.key=minioadmin \
--conf spark.hadoop.fs.s3a.secret.key=minioadmin123 \
--conf spark.hadoop.fs.s3a.path.style.access=true \
--conf spark.hadoop.fs.s3a.impl=org.apache.hadoop.fs.s3a.S3AFileSystem"
