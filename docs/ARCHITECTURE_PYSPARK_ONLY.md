# ✅ ARCHITECTURE 100% PYSPARK (Sans Scala/JARs compliqués)

**Date**: 23 Octobre 2025
**Confirmation**: OUI, on peut faire TOUT en PySpark sans toucher à Scala

---

## 🎯 VOTRE ARCHITECTURE (Validée ✅)

```
┌─────────────────────────────────────────────────────────────┐
│  CODE PYSPARK (.py files)                                   │
│  ├─ 01_extract_bronze.py                                    │
│  ├─ 02_transform_silver.py                                  │
│  ├─ 03_transform_gold.py                                    │
│  └─ 04_benchmarks.py                                        │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│  AIRFLOW DAG (orchestration Python)                         │
│  └─ chu_etlt_dag.py                                         │
│     - PythonOperator (exécute .py directement)              │
│     OU                                                       │
│     - SparkSubmitOperator (soumet à Spark Master)           │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│  SPARK ENGINE (moteur de calcul)                            │
│  - Spark Master + Worker                                    │
│  - Exécute le bytecode Python                               │
│  - PAS besoin de Scala/JAR custom                           │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│  STOCKAGE (MinIO/Local)                                     │
│  ├─ Bronze/ (Parquet)                                       │
│  ├─ Silver/ (Parquet)                                       │
│  └─ Gold/ (Parquet)                                         │
│  Note: Delta Lake = optionnel (Parquet suffit!)             │
└─────────────────────────────────────────────────────────────┘
```

---

## ✅ CE QU'ON VA FAIRE (100% Python)

### 1. Code PySpark Pur

```python
# spark/jobs/01_extract_bronze.py
from pyspark.sql import SparkSession
from pyspark.sql.functions import *

# ✅ Tout en Python
# ❌ Pas de Scala
# ❌ Pas de JARs custom

def main():
    spark = SparkSession.builder \
        .appName("CHU Extract Bronze") \
        .getOrCreate()  # ✅ Simple et propre

    # Extraction PostgreSQL (driver JDBC déjà dans Spark)
    df = spark.read.jdbc(
        url="jdbc:postgresql://chu_postgres:5432/healthcare_data",
        table="Patient",
        properties={"user": "admin", "password": "admin123"}
    )

    # Écrire en Parquet (pas besoin de JAR)
    df.write.mode("overwrite") \
        .option("compression", "snappy") \
        .parquet("/home/jovyan/data/bronze/patient")

    spark.stop()

if __name__ == "__main__":
    main()
```

### 2. Airflow DAG Python

```python
# airflow/dags/chu_etlt_dag.py
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import subprocess

# ✅ Option 1: PythonOperator (exécute Python directement)
def run_extract_bronze():
    """Exécute le job PySpark via subprocess"""
    result = subprocess.run([
        'spark-submit',
        '--master', 'local[*]',  # ou 'spark://chu_spark_master:7077'
        '/opt/spark-apps/01_extract_bronze.py'
    ], capture_output=True, text=True)

    if result.returncode != 0:
        raise Exception(f"Job failed: {result.stderr}")

    print(result.stdout)

dag = DAG('chu_etlt', start_date=datetime(2025, 10, 23))

extract_task = PythonOperator(
    task_id='extract_bronze',
    python_callable=run_extract_bronze,
    dag=dag
)
```

**OU encore plus simple**:

```python
# ✅ Option 2: SparkSubmitOperator (Airflow gère spark-submit)
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator

extract_task = SparkSubmitOperator(
    task_id='extract_bronze',
    application='/opt/spark-apps/01_extract_bronze.py',
    conn_id='spark_default',  # Connection Spark dans Airflow UI
    dag=dag
)
```

---

## ❓ DELTA LAKE: Obligatoire ou pas?

### Réponse: **PAS OBLIGATOIRE** pour votre Livrable 2 ! ✅

**Ce qui suffit**:
```python
# ✅ PARQUET SIMPLE (ce que vous faites déjà)
df.write.mode("overwrite").parquet(path)

# Avantages:
# ✅ Pas de dépendance Delta Lake
# ✅ Pas de JAR supplémentaire
# ✅ Compatible avec tout (Spark, Pandas, DuckDB, etc.)
# ✅ Format standard industrie
```

**Delta Lake apporte quoi?**
```python
# 🔸 DELTA LAKE (optionnel, ajout de features)
df.write.format("delta").mode("overwrite").save(path)

# Avantages supplémentaires:
# + Transactions ACID (important pour production)
# + Time travel (revenir version précédente)
# + Schema evolution automatique
# + Meilleure gestion concurrence

# Inconvénient:
# - Besoin de la lib Delta Lake (mais c'est juste pip install)
```

**Recommandation pour VOUS**:
- **Livrable 2**: Rester avec **Parquet simple** ✅
- **Bonus (si temps)**: Ajouter Delta Lake dans 1-2 jobs pour montrer que vous connaissez
- **Production future**: Migrer vers Delta Lake

---

## 🔧 CONFIGURATION MINIMALE (Aucun JAR custom nécessaire)

### Dockerfile Spark (déjà fourni par Apache)

```dockerfile
# Votre image Spark actuelle suffit!
FROM apache/spark:3.4.0

# ✅ Driver PostgreSQL JDBC (déjà inclus dans l'image)
# ✅ PySpark (déjà inclus)
# ✅ Pandas (pour conversions optionnelles)

# Optionnel: Delta Lake si vous voulez
RUN pip install delta-spark

# C'EST TOUT! Pas de Scala, pas de compilation, pas de JARs custom
```

### spark-submit Command

```bash
# ✅ SIMPLE: Python pur
spark-submit \
  --master spark://chu_spark_master:7077 \
  --executor-memory 2g \
  --driver-memory 1g \
  /opt/spark-apps/01_extract_bronze.py

# ❌ PAS BESOIN DE:
# --jars custom.jar                    # Non!
# --packages avec.maven.coordinates    # Non!
# --class com.scala.MainClass          # Non! (Scala only)
```

---

## 📦 LIBRAIRIES NÉCESSAIRES (Toutes disponibles via pip)

```txt
# requirements.txt pour vos jobs Spark
pyspark==3.4.0          # ✅ Moteur Spark Python
pandas==2.0.0           # ✅ Manipulation données
numpy==1.24.0           # ✅ Calculs numériques

# Optionnel:
delta-spark==2.4.0      # 🔸 Si vous voulez Delta Lake
psycopg2-binary==2.9.0  # 🔸 Si accès direct PostgreSQL depuis Python
matplotlib==3.7.0       # 🔸 Pour graphiques dans notebooks
seaborn==0.12.0         # 🔸 Pour graphiques plus jolis
```

**Installation**:
```bash
# Dans le container Jupyter
pip install -r requirements.txt

# ✅ Pas de compilation Java/Scala
# ✅ Pas de mvn package
# ✅ Pas de sbt assembly
```

---

## 🎯 FLUX COMPLET (100% Python)

### 1. Développement (Jupyter)

```python
# Dans notebook 01_Extract_Bronze.ipynb
spark = SparkSession.builder \
    .appName("Test") \
    .master("local[*]") \
    .getOrCreate()

# Développer et tester le code interactivement
df = spark.read.jdbc(...)
df.write.parquet(...)
```

### 2. Conversion en Job (Script Python)

```bash
# Copier cellules notebook → fichier .py
# spark/jobs/01_extract_bronze.py
# (voir template plus haut)
```

### 3. Test Local

```bash
# Tester job directement
docker exec chu_jupyter python /opt/spark-apps/01_extract_bronze.py

# OU avec spark-submit
docker exec chu_jupyter spark-submit /opt/spark-apps/01_extract_bronze.py
```

### 4. Orchestration Airflow

```python
# airflow/dags/chu_etlt_dag.py
# (voir template plus haut)

# Airflow appelle:
# → spark-submit 01_extract_bronze.py
# → spark-submit 02_transform_silver.py
# → etc.
```

### 5. Monitoring

```bash
# Spark UI: http://localhost:4040 (pendant exécution)
# Airflow UI: http://localhost:8080 (orchestration)
# Logs: docker logs chu_spark_master
```

---

## ✅ AVANTAGES DE CETTE APPROCHE

| Aspect | Avec Scala/JARs | Avec PySpark Pur |
|--------|----------------|------------------|
| **Complexité** | 🔴 Élevée (build, JARs, Maven) | 🟢 Simple (Python pur) |
| **Compilation** | 🔴 Obligatoire (sbt/mvn) | 🟢 Aucune (interprété) |
| **Dépendances** | 🔴 Gestion JARs complexe | 🟢 pip install |
| **Débogage** | 🔴 Difficile (stacktraces Java) | 🟢 Facile (Python) |
| **Courbe apprentissage** | 🔴 Scala + Spark | 🟢 Python seulement |
| **Performance** | 🟡 Légèrement meilleur | 🟡 Quasi identique |
| **Livrable académique** | 🔴 Surcomplication | 🟢 Approprié |

**Conclusion**: PySpark pur = **parfait pour votre contexte** ✅

---

## 🚫 CE QU'ON NE FAIT PAS

### ❌ Pas de Scala

```scala
// ❌ On NE fait PAS ça:
object ExtractBronze {
  def main(args: Array[String]): Unit = {
    val spark = SparkSession.builder()...
    // Compilation requise, JARs, complexe
  }
}
```

### ❌ Pas de JARs custom

```bash
# ❌ On NE fait PAS ça:
sbt assembly  # Créer JAR custom
spark-submit --jars custom-assembly.jar ...
```

### ❌ Pas de Maven/SBT

```xml
<!-- ❌ Pas de pom.xml -->
<dependencies>
  <dependency>...</dependency>
</dependencies>
```

---

## 🎯 EXEMPLE COMPLET: Job PySpark → Airflow → Spark Engine

### Fichier 1: Job PySpark

```python
# spark/jobs/01_extract_bronze.py
from pyspark.sql import SparkSession
from pyspark.sql.functions import current_timestamp, current_date
import sys

def create_spark_session():
    """Crée session Spark avec config optimale"""
    return SparkSession.builder \
        .appName("CHU - Extract Bronze") \
        .config("spark.sql.adaptive.enabled", "true") \
        .getOrCreate()

def extract_postgres(spark):
    """Extrait tables PostgreSQL"""
    jdbc_url = "jdbc:postgresql://chu_postgres:5432/healthcare_data"
    props = {"user": "admin", "password": "admin123"}

    tables = ["Patient", "Consultation", "AAAA", "date"]

    for table in tables:
        print(f"📖 Extracting {table}...")

        df = spark.read.jdbc(jdbc_url, table, properties=props)
        df = df.withColumn("ingestion_timestamp", current_timestamp()) \
               .withColumn("ingestion_date", current_date())

        output = f"/home/jovyan/data/bronze/postgres/{table}"
        df.write.mode("overwrite") \
            .option("compression", "snappy") \
            .partitionBy("ingestion_date") \
            .parquet(output)

        count = df.count()
        print(f"✅ {table}: {count:,} rows extracted")

def main():
    print("🚀 Starting Bronze Extraction...")
    spark = create_spark_session()

    try:
        extract_postgres(spark)
        print("✅ Extraction completed successfully!")
        return 0
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return 1
    finally:
        spark.stop()

if __name__ == "__main__":
    sys.exit(main())
```

### Fichier 2: DAG Airflow

```python
# airflow/dags/chu_etlt_dag.py
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import subprocess
import sys

default_args = {
    'owner': 'chu_team',
    'depends_on_past': False,
    'start_date': datetime(2025, 10, 23),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'chu_etlt_pipeline',
    default_args=default_args,
    description='Pipeline ETLT CHU (100% PySpark)',
    schedule_interval='@daily',
    catchup=False,
)

def run_pyspark_job(job_name):
    """Exécute un job PySpark"""
    print(f"🚀 Launching {job_name}...")

    cmd = [
        'spark-submit',
        '--master', 'local[*]',
        '--executor-memory', '2g',
        '--driver-memory', '1g',
        f'/opt/spark-apps/{job_name}.py'
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr, file=sys.stderr)
        raise Exception(f"Job {job_name} failed!")

    print(f"✅ {job_name} completed!")

# Définir les tâches
extract_bronze = PythonOperator(
    task_id='extract_bronze',
    python_callable=lambda: run_pyspark_job('01_extract_bronze'),
    dag=dag,
)

transform_silver = PythonOperator(
    task_id='transform_silver',
    python_callable=lambda: run_pyspark_job('02_transform_silver'),
    dag=dag,
)

transform_gold = PythonOperator(
    task_id='transform_gold',
    python_callable=lambda: run_pyspark_job('03_transform_gold'),
    dag=dag,
)

benchmarks = PythonOperator(
    task_id='run_benchmarks',
    python_callable=lambda: run_pyspark_job('04_benchmarks'),
    dag=dag,
)

# Ordre d'exécution
extract_bronze >> transform_silver >> transform_gold >> benchmarks
```

### Fichier 3: Test

```bash
# Test local du job
docker exec chu_jupyter python /opt/spark-apps/01_extract_bronze.py

# Test avec Airflow
docker exec chu_airflow_webserver airflow dags trigger chu_etlt_pipeline

# Vérifier logs
docker exec chu_airflow_webserver airflow tasks logs chu_etlt_pipeline extract_bronze 2025-10-23
```

---

## 🎓 POUR LE LIVRABLE 2

### Dans le rapport LaTeX

**Section "Technologies"**:
```latex
\subsection{Justification PySpark}

Le projet utilise exclusivement \textbf{PySpark} (API Python pour Apache Spark)
plutôt que Scala pour les raisons suivantes:

\begin{itemize}
\item \textbf{Simplicité}: Pas de compilation, déploiement direct de scripts Python
\item \textbf{Maintenabilité}: Code Python plus accessible pour l'équipe data science
\item \textbf{Écosystème}: Intégration naturelle avec pandas, numpy, matplotlib
\item \textbf{Performance}: Quasi-identique à Scala pour nos volumes (< 5M lignes)
\item \textbf{Déploiement}: Pas de gestion de JARs, dépendances via pip
\end{itemize}

Les jobs Spark sont orchestrés par \textbf{Apache Airflow} qui lance les scripts
Python via \texttt{spark-submit}, exploitant le moteur Spark distribué sans
nécessiter de code Scala.
```

---

## ✅ CONCLUSION

**Votre architecture est PARFAITE**:

```
PySpark Scripts (.py)
    ↓
Airflow DAG (orchestration)
    ↓
Spark Engine (calcul distribué)
    ↓
Parquet Files (stockage)
```

**Pas besoin de**:
- ❌ Scala
- ❌ JARs custom
- ❌ Maven/SBT
- ❌ Delta Lake (optionnel)

**Tout en**:
- ✅ Python pur
- ✅ PySpark natif
- ✅ Spark Engine standard
- ✅ Parquet standard

**🎯 On commence maintenant à créer les jobs?**
