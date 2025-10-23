# 🔧 TROUBLESHOOTING - CHU Data Lakehouse

**Guide de résolution des problèmes courants**

---

## 📋 Table des Matières

1. [Docker et Containers](#-docker-et-containers)
2. [Jupyter et Notebooks](#-jupyter-et-notebooks)
3. [Apache Spark](#-apache-spark)
4. [PostgreSQL](#-postgresql)
5. [Apache Superset](#-apache-superset)
6. [Erreurs de Pipeline](#-erreurs-de-pipeline)
7. [Performances](#-performances)

---

## 🐳 Docker et Containers

### Container ne démarre pas

**Symptôme**: `docker ps` ne montre pas le container

**Solutions**:

```bash
# 1. Vérifier les logs
docker logs chu_jupyter --tail 50
docker logs chu_superset --tail 50
docker logs chu_postgres --tail 50

# 2. Redémarrer le container
docker restart chu_jupyter

# 3. Démarrer manuellement si arrêté
docker start chu_jupyter

# 4. Recréer complètement
docker-compose down
docker-compose up -d
```

### Port déjà utilisé

**Symptôme**: `Error: bind: address already in use`

**Solutions**:

```bash
# Windows: Trouver le processus utilisant le port
netstat -ano | findstr :8888
netstat -ano | findstr :8088
netstat -ano | findstr :5432

# Tuer le processus (remplacer PID par le numéro trouvé)
taskkill /PID <PID> /F

# OU modifier docker-compose.yml pour changer les ports
# Exemple: "8889:8888" au lieu de "8888:8888"
```

### Mémoire insuffisante

**Symptôme**: Container redémarre en boucle, logs montrent OOM

**Solutions**:

```bash
# 1. Augmenter RAM allouée à Docker Desktop
# Docker Desktop → Settings → Resources → Memory: 8GB minimum

# 2. Réduire nombre de workers Spark dans docker-compose.yml
# Supprimer ou commenter chu_spark_worker

# 3. Limiter mémoire Java dans notebooks
spark = SparkSession.builder \
    .config("spark.driver.memory", "2g") \
    .config("spark.executor.memory", "2g") \
    .getOrCreate()
```

### Volumes non montés

**Symptôme**: Données disparaissent après restart

**Solutions**:

```bash
# Vérifier volumes Docker
docker volume ls

# Inspecter un container
docker inspect chu_jupyter | grep -A 10 Mounts

# Recréer volumes si corrompus
docker-compose down -v  # ⚠️ ATTENTION: Supprime les données!
docker-compose up -d
```

---

## 📓 Jupyter et Notebooks

### Token Jupyter invalide

**Symptôme**: "Invalid credentials" lors de la connexion

**Solutions**:

```bash
# 1. Récupérer le token
docker logs chu_jupyter 2>&1 | grep token

# Résultat: http://127.0.0.1:8888/?token=abc123def456...

# 2. OU se connecter sans token (si configuré)
# URL: http://localhost:8888
# Password: (laisser vide)

# 3. Redémarrer Jupyter si problème persiste
docker restart chu_jupyter
```

### Kernel Python crash

**Symptôme**: "Kernel died, restarting" dans notebook

**Solutions**:

```python
# 1. Réduire mémoire Spark
spark = SparkSession.builder \
    .config("spark.driver.memory", "1g") \
    .config("spark.executor.memory", "1g") \
    .getOrCreate()

# 2. Limiter parallélisme
df = df.repartition(2)  # Au lieu de 10

# 3. Libérer cache
spark.catalog.clearCache()

# 4. Arrêter session Spark proprement
spark.stop()
```

### Impossible de sauvegarder notebook

**Symptôme**: "Permission denied" ou "Failed to save"

**Solutions**:

```bash
# 1. Vérifier permissions du volume
docker exec chu_jupyter ls -la /home/jovyan/notebooks/

# 2. Corriger permissions si nécessaire
docker exec --user root chu_jupyter chown -R jovyan:users /home/jovyan/notebooks/

# 3. Redémarrer Jupyter
docker restart chu_jupyter
```

### Package Python manquant

**Symptôme**: `ModuleNotFoundError: No module named 'xxx'`

**Solutions**:

```bash
# 1. Installer dans le container
docker exec chu_jupyter pip install package_name

# 2. OU dans une cellule notebook
!pip install package_name

# 3. Pour installation permanente, ajouter au Dockerfile
RUN pip install package_name

# 4. Reconstruire image
docker-compose build jupyter
docker-compose up -d
```

---

## ⚡ Apache Spark

### Spark session ne démarre pas

**Symptôme**: `Exception: Java gateway process exited before sending its port number`

**Solutions**:

```bash
# 1. Vérifier Java installé dans container
docker exec chu_jupyter java -version

# 2. Vérifier JAVA_HOME
docker exec chu_jupyter echo $JAVA_HOME

# 3. Redémarrer Spark master
docker restart chu_spark_master

# 4. Réduire configuration mémoire
spark = SparkSession.builder \
    .master("local[2]") \
    .config("spark.driver.memory", "1g") \
    .getOrCreate()
```

### Erreur "Cannot connect to Spark master"

**Symptôme**: `Exception: Could not connect to Spark master at spark://chu_spark_master:7077`

**Solutions**:

```bash
# 1. Vérifier Spark master running
docker ps | grep spark_master

# 2. Tester connectivité réseau
docker exec chu_jupyter ping chu_spark_master

# 3. Utiliser mode local si master indisponible
spark = SparkSession.builder \
    .master("local[*]") \  # Au lieu de spark://...
    .getOrCreate()

# 4. Redémarrer tous services Spark
docker restart chu_spark_master chu_spark_worker
```

### OutOfMemoryError Java

**Symptôme**: `java.lang.OutOfMemoryError: Java heap space`

**Solutions**:

```python
# 1. Augmenter mémoire driver
spark = SparkSession.builder \
    .config("spark.driver.memory", "4g") \
    .config("spark.driver.maxResultSize", "2g") \
    .getOrCreate()

# 2. Limiter taille cache
spark.conf.set("spark.sql.inMemoryColumnarStorage.batchSize", 10000)

# 3. Désactiver cache si non nécessaire
df.unpersist()

# 4. Repartitionner pour réduire taille par partition
df = df.repartition(20)
```

### Lecture Parquet échoue

**Symptôme**: `AnalysisException: Unable to infer schema for Parquet`

**Solutions**:

```python
# 1. Vérifier chemin existe
import os
path = "/home/jovyan/data/bronze/postgres/Patient"
if os.path.exists(path):
    print(f"✅ {path} existe")
else:
    print(f"❌ {path} n'existe pas")

# 2. Lire avec option mergeSchema
df = spark.read \
    .option("mergeSchema", "true") \
    .parquet(path)

# 3. Vérifier fichiers parquet non vides
!ls -lh /home/jovyan/data/bronze/postgres/Patient/

# 4. Recréer Bronze si corrompu
# Relancer Notebook 01
```

---

## 🐘 PostgreSQL

### Connection refused

**Symptôme**: `psycopg2.OperationalError: could not connect to server`

**Solutions**:

```bash
# 1. Vérifier PostgreSQL running
docker ps | grep postgres

# 2. Tester connexion depuis Jupyter
docker exec chu_jupyter psql -h chu_postgres -U admin -d healthcare_data -c "SELECT 1;"

# 3. Vérifier port exposé
docker port chu_postgres

# 4. Redémarrer PostgreSQL
docker restart chu_postgres

# 5. Vérifier credentials dans docker-compose.yml
POSTGRES_USER: admin
POSTGRES_PASSWORD: admin123
POSTGRES_DB: healthcare_data
```

### Table n'existe pas

**Symptôme**: `ERROR: relation "gold.fait_consultation" does not exist`

**Solutions**:

```bash
# 1. Lister les schemas
docker exec chu_postgres psql -U admin -d healthcare_data -c "\dn"

# 2. Lister tables dans schema gold
docker exec chu_postgres psql -U admin -d healthcare_data -c "\dt gold.*"

# 3. Créer schema si manquant
docker exec chu_postgres psql -U admin -d healthcare_data -c "CREATE SCHEMA IF NOT EXISTS gold;"

# 4. Re-exécuter Notebook 06 pour exporter Gold
# Jupyter → 06_Export_Gold_to_PostgreSQL.ipynb → Run All
```

### Données sources manquantes

**Symptôme**: `SELECT` retourne 0 lignes sur tables sources

**Solutions**:

```bash
# 1. Vérifier tables sources
docker exec chu_postgres psql -U admin -d healthcare_data -c "
SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename))
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY tablename;
"

# 2. Réinitialiser base si vide
docker exec chu_postgres psql -U admin -d healthcare_data -c "
DROP SCHEMA IF EXISTS public CASCADE;
CREATE SCHEMA public;
"

# 3. Reload données depuis dump SQL
docker cp /path/to/backup.sql chu_postgres:/tmp/
docker exec chu_postgres psql -U admin -d healthcare_data -f /tmp/backup.sql
```

### Erreur JDBC dans Spark

**Symptôme**: `java.sql.SQLException: No suitable driver found for jdbc:postgresql`

**Solutions**:

```python
# 1. Vérifier driver JDBC présent
import os
jdbc_path = "/usr/local/spark/jars/postgresql-42.6.0.jar"
print(f"JDBC driver exists: {os.path.exists(jdbc_path)}")

# 2. Spécifier driver explicitement
jdbc_url = "jdbc:postgresql://chu_postgres:5432/healthcare_data"
properties = {
    "user": "admin",
    "password": "admin123",
    "driver": "org.postgresql.Driver"
}
df = spark.read.jdbc(jdbc_url, "public.Patient", properties=properties)

# 3. Télécharger driver si manquant
!wget https://jdbc.postgresql.org/download/postgresql-42.6.0.jar -P /usr/local/spark/jars/
```

---

## 🎨 Apache Superset

### "Could not load database driver"

**Symptôme**: `ERROR: Could not load database driver: PostgresEngineSpec`

**Solution**:

```bash
# 1. Installer driver PostgreSQL
docker exec --user root chu_superset pip install psycopg2-binary

# 2. Redémarrer Superset
docker restart chu_superset

# 3. Attendre 30 secondes pour redémarrage complet

# 4. Tester connexion
# Superset UI → Settings → Database Connections → Test Connection
```

### Connexion PostgreSQL échoue

**Symptôme**: "Connection failed" lors du test

**Solutions**:

```bash
# 1. Vérifier URI SQLAlchemy
# Format: postgresql://user:password@host:port/database
postgresql://admin:admin123@chu_postgres:5432/healthcare_data

# 2. Tester connexion depuis container Superset
docker exec chu_superset psql -h chu_postgres -U admin -d healthcare_data -c "SELECT 1;"

# 3. Vérifier réseau Docker
docker network inspect projet_git_default

# 4. Utiliser IP au lieu de nom si problème DNS
docker inspect chu_postgres | grep IPAddress
# Remplacer chu_postgres par l'IP dans URI
```

### Schema "gold" invisible

**Symptôme**: Pas de tables visibles dans SQL Lab

**Solutions**:

1. **Vérifier schema existe**:
```bash
docker exec chu_postgres psql -U admin -d healthcare_data -c "\dt gold.*"
```

2. **Dans Superset UI**:
   - Data → Databases → CHU_Gold → Edit
   - Advanced → SQL Lab
   - Cocher: "Expose database in SQL Lab"
   - Cocher: "Allow data upload"
   - **Schema**: Taper manuellement `gold`
   - Save

3. **Refresh metadata**:
   - SQL Lab → SQL Editor
   - Database: CHU_Gold
   - Schema: gold (sélectionner dans dropdown)
   - Cliquer sur refresh icon

### Dataset creation fails

**Symptôme**: Erreur lors de création dataset

**Solutions**:

```bash
# 1. Vérifier permissions PostgreSQL
docker exec chu_postgres psql -U admin -d healthcare_data -c "
GRANT USAGE ON SCHEMA gold TO admin;
GRANT SELECT ON ALL TABLES IN SCHEMA gold TO admin;
"

# 2. Tester query manuellement
# SQL Lab → Exécuter:
SELECT COUNT(*) FROM gold.fait_consultation;

# 3. Créer dataset via SQL Lab
# Après query réussie: Save → Save dataset

# 4. Vérifier table existe et non vide
docker exec chu_postgres psql -U admin -d healthcare_data -c "
SELECT COUNT(*) FROM gold.fait_consultation;
"
```

### Login échoue (admin/admin)

**Symptôme**: "Invalid login" avec admin/admin123

**Solutions**:

```bash
# 1. Réinitialiser admin password
docker exec chu_superset superset fab create-admin \
    --username admin \
    --firstname Admin \
    --lastname User \
    --email admin@admin.com \
    --password admin123

# 2. Redémarrer Superset
docker restart chu_superset

# 3. Attendre 30 secondes et réessayer

# 4. Si toujours bloqué, reset database Superset
docker exec chu_superset superset db upgrade
docker exec chu_superset superset init
```

---

## 🔧 Erreurs de Pipeline

### Erreur "Column not found"

**Symptôme**: `[UNRESOLVED_COLUMN] A column or function parameter with name 'xxx' cannot be resolved`

**Solutions**:

```python
# 1. Afficher schema du DataFrame
df.printSchema()
df.columns  # Liste tous les noms de colonnes

# 2. Vérifier casse (sensible!)
# "date_deces" ≠ "Date_Deces" ≠ "DATE_DECES"

# 3. Vérifier espaces dans nom
# "date_deces" ≠ "date_deces " (espace à la fin)

# 4. Utiliser backticks pour noms avec espaces
df.select(col("`Date Deces`"))

# 5. Renommer colonne si nécessaire
df = df.withColumnRenamed("Date_Deces", "date_deces")
```

**Exemple réel** (erreur colonne décès):
```python
# ❌ AVANT (incorrect):
df = df.filter(col("datdec").startswith("2019"))

# ✅ APRÈS (correct):
df.printSchema()  # Montre: date_deces (pas datdec!)
df = df.filter(col("date_deces").startswith("2019"))
```

### Erreur "File not found"

**Symptôme**: `FileNotFoundError: Path does not exist: /path/to/file`

**Solutions**:

```python
# 1. Vérifier chemin existe
import os
path = "/home/jovyan/data/bronze/postgres/Patient"
print(f"Exists: {os.path.exists(path)}")

# 2. Lister contenu dossier parent
!ls -la /home/jovyan/data/bronze/postgres/

# 3. Vérifier variable path
print(f"SILVER_BASE = {SILVER_BASE}")
print(f"GOLD_OUTPUT = {GOLD_OUTPUT}")

# 4. Utiliser chemin absolu
df = spark.read.parquet("/home/jovyan/data/bronze/postgres/Patient")
```

### Jointure retourne 0 lignes

**Symptôme**: Join DataFrame result est vide

**Solutions**:

```python
# 1. Vérifier données dans chaque DF avant join
print(f"DF1 count: {df1.count()}")
print(f"DF2 count: {df2.count()}")
df1.show(5)
df2.show(5)

# 2. Vérifier types colonnes join
df1.select("id_column").dtypes
df2.select("id_column").dtypes

# 3. Tester join avec left pour voir non-matches
df_left = df1.join(df2, "id_column", "left")
df_left.filter(col("df2_column").isNull()).show()

# 4. Convertir types si nécessaire
df1 = df1.withColumn("id_column", col("id_column").cast("integer"))
df2 = df2.withColumn("id_column", col("id_column").cast("integer"))
```

### Dates invalides

**Symptôme**: `DateTimeException: Text '...' could not be parsed`

**Solutions**:

```python
# 1. Vérifier format date dans données
df.select("date_column").show(10, truncate=False)

# 2. Utiliser to_date avec format explicite
from pyspark.sql.functions import to_date

# Format dd/MM/yyyy
df = df.withColumn("date_clean", to_date(col("date_string"), "dd/MM/yyyy"))

# Format yyyy-MM-dd
df = df.withColumn("date_clean", to_date(col("date_string"), "yyyy-MM-dd"))

# 3. Filtrer dates nulles après conversion
df = df.filter(col("date_clean").isNotNull())

# 4. Gestion erreurs avec coalesce
from pyspark.sql.functions import coalesce, lit
df = df.withColumn("date_safe",
    coalesce(
        to_date(col("date_string"), "dd/MM/yyyy"),
        to_date(col("date_string"), "yyyy-MM-dd"),
        lit(None)
    )
)
```

### Hash SHA-256 échoue

**Symptôme**: `TypeError: 'NoneType' object is not iterable` dans hash

**Solutions**:

```python
# 1. Gérer valeurs NULL
from pyspark.sql.functions import when, col
import hashlib

def hash_with_null_check(value, salt):
    if value is None:
        return None
    return hashlib.sha256((str(value) + salt).encode()).hexdigest()

hash_udf = udf(hash_with_null_check, StringType())

# 2. OU filtrer NULL avant hash
df = df.filter(col("nom").isNotNull())
df = df.withColumn("nom_hash", hash_udf(col("nom"), lit(SALT)))

# 3. OU utiliser fonction Spark native (plus rapide)
from pyspark.sql.functions import sha2, concat
df = df.withColumn("nom_hash",
    sha2(concat(col("nom"), lit(SALT)), 256)
)
```

---

## 🚀 Performances

### Pipeline trop lent

**Symptôme**: Notebook prend 10+ minutes

**Solutions**:

```python
# 1. Filtrer tôt dans pipeline
df = spark.read.parquet(path) \
    .filter(col("annee") >= 2019)  # Avant transformations

# 2. Limiter partitions
df = df.coalesce(4)  # Réduire de 200 à 4 partitions

# 3. Utiliser broadcast pour petites tables (<10MB)
from pyspark.sql.functions import broadcast
df_result = df_large.join(broadcast(df_small), "id")

# 4. Persister DataFrames réutilisés
df.cache()
df.count()  # Trigger cache
# ... utiliser df plusieurs fois ...
df.unpersist()  # Libérer cache après

# 5. Désactiver statistics si non nécessaires
spark.conf.set("spark.sql.statistics.histogram.enabled", "false")
```

### Écriture Parquet lente

**Symptôme**: `.write.parquet()` prend plusieurs minutes

**Solutions**:

```python
# 1. Réduire nombre de partitions avant écriture
df = df.coalesce(5)  # 5 fichiers parquet au lieu de 200

# 2. Utiliser compression efficace
df.write \
    .mode("overwrite") \
    .option("compression", "snappy") \  # Plus rapide que gzip
    .parquet(path)

# 3. Partitionner seulement si nécessaire
# ❌ Trop de partitions:
df.write.partitionBy("annee", "mois", "jour").parquet(path)  # 365+ dossiers

# ✅ Partitions raisonnables:
df.write.partitionBy("annee").parquet(path)  # ~10 dossiers

# 4. Repartitionner avant write
df = df.repartition("annee")  # Groupe par partition key
df.write.partitionBy("annee").parquet(path)
```

### PostgreSQL export timeout

**Symptôme**: `JDBC write` timeout après 10+ minutes

**Solutions**:

```python
# 1. Réduire batchsize
jdbc_url = "jdbc:postgresql://chu_postgres:5432/healthcare_data"
properties = {
    "user": "admin",
    "password": "admin123",
    "batchsize": "1000"  # Default: 10000
}
df.write.jdbc(jdbc_url, "gold.table_name", mode="overwrite", properties=properties)

# 2. Augmenter timeout
properties = {
    "user": "admin",
    "password": "admin123",
    "socketTimeout": "600"  # 10 minutes
}

# 3. Écrire en chunks
def write_chunks(df, table_name, chunk_size=100000):
    total = df.count()
    for offset in range(0, total, chunk_size):
        chunk = df.limit(chunk_size).offset(offset)
        mode = "overwrite" if offset == 0 else "append"
        chunk.write.jdbc(jdbc_url, table_name, mode=mode, properties=properties)

# 4. Utiliser mode append avec truncate
df.write \
    .mode("overwrite") \
    .option("truncate", "true") \
    .jdbc(jdbc_url, table_name, properties=properties)
```

### Mémoire RAM saturée

**Symptôme**: Docker Desktop consomme 100% RAM, système lent

**Solutions**:

```bash
# 1. Réduire mémoire allouée à Docker
# Docker Desktop → Settings → Resources
# RAM: 6GB au lieu de 12GB

# 2. Limiter workers Spark
# docker-compose.yml: Supprimer chu_spark_worker

# 3. Réduire cache Spark dans notebooks
spark = SparkSession.builder \
    .config("spark.driver.memory", "2g") \
    .config("spark.executor.memory", "2g") \
    .config("spark.sql.shuffle.partitions", "20") \
    .getOrCreate()

# 4. Clear cache régulièrement
spark.catalog.clearCache()

# 5. Utiliser mode local[2] au lieu cluster
spark = SparkSession.builder.master("local[2]").getOrCreate()
```

---

## 🆘 Dernier Recours

### Réinitialisation complète

**⚠️ ATTENTION: Supprime toutes les données!**

```bash
# 1. Arrêter tous containers
docker-compose down

# 2. Supprimer volumes
docker-compose down -v

# 3. Supprimer images (optionnel)
docker rmi $(docker images -q)

# 4. Nettoyer système Docker
docker system prune -a --volumes

# 5. Redémarrer from scratch
docker-compose up -d

# 6. Re-exécuter notebooks 01 → 02 → 03 → 06
```

### Logs détaillés

```bash
# Tous logs d'un container
docker logs chu_jupyter > jupyter.log 2>&1

# Suivre logs en temps réel
docker logs -f chu_superset

# Logs avec timestamps
docker logs --timestamps chu_postgres

# Dernières 100 lignes
docker logs --tail 100 chu_spark_master
```

### Support et Ressources

- **Docker**: https://docs.docker.com/
- **Spark**: https://spark.apache.org/docs/latest/
- **PostgreSQL**: https://www.postgresql.org/docs/
- **Superset**: https://superset.apache.org/docs/
- **Stack Overflow**: Rechercher erreurs spécifiques

---

**🔧 Guide Troubleshooting Complet - Bonne chance !**
