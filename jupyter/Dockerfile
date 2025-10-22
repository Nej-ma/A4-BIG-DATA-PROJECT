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

# Téléchargement des JARs nécessaires
USER root
RUN cd /usr/local/spark/jars && \
    curl -O https://jdbc.postgresql.org/download/postgresql-42.7.1.jar && \
    curl -O https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.3.4/hadoop-aws-3.3.4.jar && \
    curl -O https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/1.12.367/aws-java-sdk-bundle-1.12.367.jar && \
    curl -O https://repo1.maven.org/maven2/io/delta/delta-core_2.12/2.4.0/delta-core_2.12-2.4.0.jar && \
    curl -O https://repo1.maven.org/maven2/io/delta/delta-storage/2.4.0/delta-storage-2.4.0.jar
USER jovyan

# Configuration Spark pour Delta Lake avec 8GB mémoire
ENV SPARK_OPTS="--driver-memory 8g \
--executor-memory 8g \
--conf spark.sql.extensions=io.delta.sql.DeltaSparkSessionExtension \
--conf spark.sql.catalog.spark_catalog=org.apache.spark.sql.delta.catalog.DeltaCatalog \
--conf spark.hadoop.fs.s3a.endpoint=http://chu_minio:9000 \
--conf spark.hadoop.fs.s3a.access.key=minioadmin \
--conf spark.hadoop.fs.s3a.secret.key=minioadmin123 \
--conf spark.hadoop.fs.s3a.path.style.access=true \
--conf spark.hadoop.fs.s3a.impl=org.apache.hadoop.fs.s3a.S3AFileSystem \
--conf spark.hadoop.fs.s3a.connection.ssl.enabled=false"
