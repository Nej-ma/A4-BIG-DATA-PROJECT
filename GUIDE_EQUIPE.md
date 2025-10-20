# 📖 Guide d'Onboarding - Équipe CHU Data Lakehouse

**Bienvenue dans le projet Big Data CHU !**

Ce guide vous accompagne **pas à pas** pour démarrer sur le projet, que vous soyez nouveau sur Docker, Spark ou Delta Lake.

---

## 🎯 Objectif du Projet

Construire un **Data Lakehouse** pour le CHU (Cloud Healthcare Unit) avec :

1. **Architecture Bronze/Silver/Gold** (médaillons)
2. **Delta Lake** pour le stockage ACID
3. **Pseudonymisation RGPD** des données patients (T1)
4. **Modèle dimensionnel** pour l'analyse BI (T2)
5. **Orchestration** avec Apache Airflow
6. **Visualisation** avec Apache Superset

---

## 📋 Prérequis

### Logiciels à installer

1. **Docker Desktop** (Windows/Mac) ou **Docker Engine** (Linux)
   - Télécharge : https://www.docker.com/products/docker-desktop
   - Vérifie l'installation : `docker --version`

2. **Git**
   - Télécharge : https://git-scm.com/downloads
   - Vérifie : `git --version`

3. **Un éditeur de code** (optionnel mais recommandé)
   - VS Code : https://code.visualstudio.com/
   - PyCharm Community : https://www.jetbrains.com/pycharm/

### Connaissances recommandées

- **SQL** : Bases de données relationnelles
- **Python** : Syntaxe de base, pandas
- **Docker** : Concepts de base (containers, images)
- **Spark** : Notions de DataFrame (similaire à pandas)

**Pas de panique si vous débutez !** Ce guide est fait pour vous accompagner.

---

## 🚀 Premier Lancement (Étape par Étape)

### Étape 1 : Clone le projet

Ouvre un terminal (PowerShell sur Windows, Terminal sur Mac/Linux) :

```bash
cd C:\Users\TON_NOM\Desktop
git clone <url-du-repo>
cd projet_git
```

### Étape 2 : Vérifie que Docker tourne

```bash
docker --version
docker ps
```

Si erreur "Cannot connect to Docker daemon" :
- Sur Windows : Lance **Docker Desktop**
- Sur Linux : `sudo systemctl start docker`

### Étape 3 : Lance la stack complète

```bash
docker-compose up --build -d
```

**Que se passe-t-il ?**
- `--build` : Reconstruit les images Docker personnalisées (Airflow, Jupyter)
- `-d` : Mode détaché (les services tournent en arrière-plan)

**Durée** : 5-10 minutes la première fois (téléchargement des images).

### Étape 4 : Attends que tout démarre

Vérifie l'état des services :

```bash
docker-compose ps
```

Tous les services doivent afficher **Up** (sauf `chu_spark_worker` - non utilisé).

**Si un service est en "Exit" ou "Restarting"** :

```bash
docker logs <nom_du_service>
```

Exemple : `docker logs chu_postgres`

### Étape 5 : Teste les accès

Ouvre ton navigateur et teste chaque service :

| Service | URL | Login | Mot de passe |
|---------|-----|-------|--------------|
| Jupyter Lab | http://localhost:8888 | - | token: admin123 |
| Airflow | http://localhost:8080 | admin | admin123 |
| MinIO | http://localhost:9001 | minioadmin | minioadmin123 |
| Superset | http://localhost:8088 | admin | admin123 |

**✅ Si tu vois les interfaces : bravo, la stack est opérationnelle !**

---

## 🗄️ Découvrir les Données

### Accéder à PostgreSQL avec pgAdmin

1. Va sur **pgAdmin** : http://localhost:5050
2. Login : `admin@chu.fr` / `admin123`
3. Clique droit sur "Servers" → "Create" → "Server"
4. Onglet "General" :
   - Name : `CHU PostgreSQL`
5. Onglet "Connection" :
   - Host : `chu_postgres`
   - Port : `5432`
   - Database : `healthcare_data`
   - Username : `admin`
   - Password : `admin123`
6. Sauvegarde

Tu peux maintenant explorer les 8 tables :
- `Patient` (100 patients)
- `Medecin` (20 médecins)
- `Service` (8 services)
- `Medicament` (30 médicaments)
- `Consultation` (108 consultations)
- `Hospitalisation` (50 hospitalisations)
- `Prescription` (65 prescriptions)
- `Acte` (94 actes médicaux)

### Requête SQL de test

```sql
-- Nombre de patients par ville
SELECT ville, COUNT(*) as nb_patients
FROM "Patient"
GROUP BY ville
ORDER BY nb_patients DESC
LIMIT 10;
```

---

## 📓 Premier Notebook Jupyter

### Étape 1 : Ouvre Jupyter Lab

1. Va sur http://localhost:8888
2. Token : `admin123`
3. Navigue vers `notebooks/`
4. Crée un nouveau notebook : **New → Python 3 (ipykernel)**

### Étape 2 : Teste la connexion PostgreSQL

Copie ce code dans une cellule :

```python
from pyspark.sql import SparkSession

# Créer session Spark
spark = SparkSession.builder \
    .appName("Test PostgreSQL") \
    .getOrCreate()

# Lire la table Patient
df = spark.read.jdbc(
    url="jdbc:postgresql://chu_postgres:5432/healthcare_data",
    table='"Patient"',
    properties={"user": "admin", "password": "admin123"}
)

# Afficher les 10 premiers patients
df.show(10, truncate=False)

# Statistiques
print(f"Nombre total de patients : {df.count()}")
```

**Exécute la cellule** : `Shift + Enter`

**Résultat attendu** : Tu dois voir 10 lignes de patients.

### Étape 3 : Teste Delta Lake

```python
from delta import *

# Session Spark avec Delta Lake
builder = SparkSession.builder.appName("Test Delta Lake") \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
    .config("spark.hadoop.fs.s3a.endpoint", "http://chu_minio:9000") \
    .config("spark.hadoop.fs.s3a.access.key", "minioadmin") \
    .config("spark.hadoop.fs.s3a.secret.key", "minioadmin123") \
    .config("spark.hadoop.fs.s3a.path.style.access", "true") \
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")

spark = configure_spark_with_delta_pip(builder).getOrCreate()

# Lire depuis PostgreSQL
df_patients = spark.read.jdbc(
    url="jdbc:postgresql://chu_postgres:5432/healthcare_data",
    table='"Patient"',
    properties={"user": "admin", "password": "admin123"}
)

# Écrire en Delta Lake (zone Bronze)
df_patients.write.format("delta").mode("overwrite").save("s3a://lakehouse/bronze/patient")

print("✅ Données écrites en Delta Lake !")

# Relire depuis Delta Lake
df_delta = spark.read.format("delta").load("s3a://lakehouse/bronze/patient")
df_delta.show(5)
```

**Exécute** et vérifie que tu vois les données.

### Étape 4 : Vérifie dans MinIO

1. Va sur **MinIO Console** : http://localhost:9001
2. Login : `minioadmin` / `minioadmin123`
3. Clique sur le bucket `lakehouse`
4. Browse : `bronze/patient/`

Tu dois voir :
- Des fichiers `.parquet` (les données)
- Un dossier `_delta_log/` (le journal de transactions Delta Lake)

**✅ Si tu vois ces fichiers : Delta Lake fonctionne !**

---

## 🎯 Développer les Transformations

### Transformation T1 : RGPD (Bronze → Silver)

**Objectif** : Pseudonymiser les données PII pour respecter le RGPD.

**Données à pseudonymiser** :
- `nom` → SHA-256
- `prenom` → SHA-256
- `numero_securite_sociale` → SHA-256
- `adresse`, `telephone`, `email` → **Supprimer**

**Données à conserver** :
- `date_naissance` → Calculer l'**âge** à la place
- `sexe`, `groupe_sanguin`, `code_postal`, `ville`

**Exemple de code** :

```python
from pyspark.sql.functions import sha2, concat_ws, year, current_date, col, lit

# Lire depuis Bronze
df_bronze = spark.read.format("delta").load("s3a://lakehouse/bronze/patient")

# Transformation T1
df_silver = df_bronze \
    .withColumn("nom_hash", sha2(concat_ws("_", col("nom"), lit("secret_salt_chu")), 256)) \
    .withColumn("prenom_hash", sha2(concat_ws("_", col("prenom"), lit("secret_salt_chu")), 256)) \
    .withColumn("nss_hash", sha2(col("numero_securite_sociale"), 256)) \
    .withColumn("age", year(current_date()) - year(col("date_naissance"))) \
    .select(
        "id_patient",
        "nom_hash",
        "prenom_hash",
        "nss_hash",
        "age",
        "sexe",
        "groupe_sanguin",
        "code_postal",
        "ville",
        "date_inscription",
        "created_at"
    )

# Écrire en Silver
df_silver.write.format("delta").mode("overwrite").save("s3a://lakehouse/silver/patient")

print("✅ Transformation T1 terminée (RGPD)")
df_silver.show(5)
```

### Transformation T2 : Modèle Dimensionnel (Silver → Gold)

**Objectif** : Créer un modèle en étoile pour l'analyse BI.

**Exemple : Fait Consultation enrichi**

```python
# Lire depuis Silver
df_patient_silver = spark.read.format("delta").load("s3a://lakehouse/silver/patient")

# Lire Consultation depuis Bronze
df_consultation = spark.read.jdbc(
    url="jdbc:postgresql://chu_postgres:5432/healthcare_data",
    table='"Consultation"',
    properties={"user": "admin", "password": "admin123"}
)

# Jointure pour enrichir
df_gold_consultation = df_consultation \
    .join(df_patient_silver, "id_patient", "left") \
    .select(
        "id_consultation",
        "id_patient",
        "id_medecin",
        "date_consultation",
        "motif",
        "diagnostic",
        "duree_minutes",
        "tarif",
        "age",
        "sexe",
        "code_postal",
        "ville"
    )

# Écrire en Gold
df_gold_consultation.write.format("delta").mode("overwrite").save("s3a://lakehouse/gold/consultation")

print("✅ Transformation T2 terminée (DWH)")
df_gold_consultation.show(5)
```

---

## 🔄 Orchestration avec Airflow

### Créer un DAG

1. **Crée un fichier** : `airflow/dags/etl_chu_delta_lake.py`

2. **Template de base** :

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'equipe_chu',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'etl_chu_delta_lake',
    default_args=default_args,
    description='Pipeline ETL CHU avec Delta Lake',
    schedule_interval='@daily',
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['chu', 'delta-lake', 'etl'],
)

def extract_bronze():
    """Extraction PostgreSQL vers Bronze"""
    from pyspark.sql import SparkSession
    from delta import configure_spark_with_delta_pip

    builder = SparkSession.builder.appName("CHU Extract") \
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
        .config("spark.hadoop.fs.s3a.endpoint", "http://chu_minio:9000") \
        .config("spark.hadoop.fs.s3a.access.key", "minioadmin") \
        .config("spark.hadoop.fs.s3a.secret.key", "minioadmin123") \
        .config("spark.hadoop.fs.s3a.path.style.access", "true") \
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")

    spark = configure_spark_with_delta_pip(builder).getOrCreate()

    # Extraction Patient
    df = spark.read.jdbc(
        url="jdbc:postgresql://chu_postgres:5432/healthcare_data",
        table='"Patient"',
        properties={"user": "admin", "password": "admin123"}
    )

    df.write.format("delta").mode("overwrite").save("s3a://lakehouse/bronze/patient")
    print("✅ Extraction Bronze terminée")

def transform_t1_silver():
    """Transformation T1 : RGPD"""
    from pyspark.sql import SparkSession
    from pyspark.sql.functions import sha2, concat_ws, year, current_date, col, lit
    from delta import configure_spark_with_delta_pip

    builder = SparkSession.builder.appName("CHU T1") \
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
        .config("spark.hadoop.fs.s3a.endpoint", "http://chu_minio:9000") \
        .config("spark.hadoop.fs.s3a.access.key", "minioadmin") \
        .config("spark.hadoop.fs.s3a.secret.key", "minioadmin123") \
        .config("spark.hadoop.fs.s3a.path.style.access", "true") \
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")

    spark = configure_spark_with_delta_pip(builder).getOrCreate()

    df_bronze = spark.read.format("delta").load("s3a://lakehouse/bronze/patient")

    df_silver = df_bronze \
        .withColumn("nom_hash", sha2(concat_ws("_", col("nom"), lit("secret_salt_chu")), 256)) \
        .withColumn("age", year(current_date()) - year(col("date_naissance"))) \
        .select("id_patient", "nom_hash", "age", "sexe", "groupe_sanguin", "code_postal", "ville")

    df_silver.write.format("delta").mode("overwrite").save("s3a://lakehouse/silver/patient")
    print("✅ Transformation T1 terminée")

def transform_t2_gold():
    """Transformation T2 : DWH"""
    from pyspark.sql import SparkSession
    from delta import configure_spark_with_delta_pip

    builder = SparkSession.builder.appName("CHU T2") \
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
        .config("spark.hadoop.fs.s3a.endpoint", "http://chu_minio:9000") \
        .config("spark.hadoop.fs.s3a.access.key", "minioadmin") \
        .config("spark.hadoop.fs.s3a.secret.key", "minioadmin123") \
        .config("spark.hadoop.fs.s3a.path.style.access", "true") \
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")

    spark = configure_spark_with_delta_pip(builder).getOrCreate()

    df_patient = spark.read.format("delta").load("s3a://lakehouse/silver/patient")

    # Ici : ajouter jointures et enrichissements

    df_patient.write.format("delta").mode("overwrite").save("s3a://lakehouse/gold/dim_patient")
    print("✅ Transformation T2 terminée")

# Définition des tâches
task_extract = PythonOperator(
    task_id='extract_bronze',
    python_callable=extract_bronze,
    dag=dag,
)

task_t1 = PythonOperator(
    task_id='transform_t1_silver',
    python_callable=transform_t1_silver,
    dag=dag,
)

task_t2 = PythonOperator(
    task_id='transform_t2_gold',
    python_callable=transform_t2_gold,
    dag=dag,
)

# Pipeline
task_extract >> task_t1 >> task_t2
```

3. **Active le DAG** :
   - Va sur http://localhost:8080
   - Login : `admin` / `admin123`
   - Cherche ton DAG `etl_chu_delta_lake`
   - Active-le (toggle à gauche)
   - Clique sur "Trigger DAG" (bouton play)

4. **Vérifie l'exécution** :
   - Clique sur le DAG → Graph View
   - Chaque tâche doit être verte
   - Clique sur une tâche → Logs pour voir les détails

---

## 📊 Visualisation avec Superset

### Étape 1 : Connecte-toi à PostgreSQL

1. Va sur http://localhost:8088 (admin / admin123)
2. En haut à droite : **Settings** → **Database Connections**
3. **+ Database**
4. Sélectionne **PostgreSQL**
5. Remplis :
   - **Host** : `chu_postgres`
   - **Port** : `5432`
   - **Database** : `healthcare_data`
   - **Username** : `admin`
   - **Password** : `admin123`
6. **Test Connection** → **Connect**

### Étape 2 : Crée un Dataset

1. **Data** → **Datasets** → **+ Dataset**
2. Sélectionne la connexion PostgreSQL
3. Schema : `public`
4. Table : `Consultation`
5. **Add**

### Étape 3 : Crée un Chart

1. Clique sur le dataset `Consultation`
2. **Create Chart**
3. Choisis **Bar Chart**
4. Dimensions :
   - **X-Axis** : `date_consultation` (groupé par mois)
   - **Metric** : `COUNT(*)`
5. **Update Chart**
6. **Save** → Donne un nom

### Étape 4 : Crée un Dashboard

1. **Dashboards** → **+ Dashboard**
2. Glisse-dépose ton chart
3. Ajoute d'autres charts
4. **Save**

---

## ❓ FAQ - Questions Fréquentes

### Pourquoi le Spark Worker ne démarre pas ?

**Réponse** : C'est normal ! On utilise **PySpark en mode local** dans Jupyter au lieu d'un cluster distribué. C'est largement suffisant pour ce projet.

### Comment arrêter la stack ?

```bash
docker-compose down
```

Les **volumes persistent** : tes données PostgreSQL et MinIO sont conservées.

### Comment tout supprimer et recommencer ?

```bash
docker-compose down -v
```

**⚠️ ATTENTION** : Cela supprime les volumes Docker = perte de données !

### J'ai modifié un Dockerfile, comment rebuild ?

```bash
docker-compose up --build -d
```

### Comment voir les logs en temps réel ?

```bash
docker logs chu_airflow_webserver -f
```

Appuie sur `Ctrl+C` pour quitter.

### MinIO dit "Access Denied" quand j'écris

Vérifie que tu utilises les bons credentials :
- Access Key : `minioadmin`
- Secret Key : `minioadmin123`

Et le bon endpoint **dans Docker** : `http://chu_minio:9000`

---

## 🎓 Ressources Pédagogiques

### Documentation Officielle

- **Delta Lake** : https://docs.delta.io/latest/index.html
- **PySpark** : https://spark.apache.org/docs/latest/api/python/
- **Airflow** : https://airflow.apache.org/docs/
- **MinIO** : https://min.io/docs/minio/linux/index.html

### Tutoriels Recommandés

- **Delta Lake Quickstart** : https://docs.delta.io/latest/quick-start.html
- **PySpark Tutorial** : https://spark.apache.org/docs/latest/api/python/getting_started/index.html
- **Airflow Tutorial** : https://airflow.apache.org/docs/apache-airflow/stable/tutorial/index.html

### Concepts Clés

- **Data Lakehouse** : Fusion Data Lake + Data Warehouse
- **Architecture Médaillons** : Bronze (raw) → Silver (cleaned) → Gold (curated)
- **ACID** : Atomicity, Consistency, Isolation, Durability
- **Delta Lake Transaction Log** : `_delta_log/` pour la gestion des versions
- **Time Travel** : Interroger une version antérieure des données

---

## ✅ Checklist de Démarrage

- [ ] Docker Desktop installé et lancé
- [ ] Git installé
- [ ] Projet cloné : `git clone <url>`
- [ ] Stack lancée : `docker-compose up --build -d`
- [ ] Tous les services UP : `docker-compose ps`
- [ ] Jupyter accessible : http://localhost:8888
- [ ] Airflow accessible : http://localhost:8080
- [ ] MinIO accessible : http://localhost:9001
- [ ] PostgreSQL testé : 100 patients visibles
- [ ] Premier notebook créé et testé
- [ ] Delta Lake testé : données écrites en Bronze
- [ ] Données visibles dans MinIO (`lakehouse/bronze/patient/`)

**✅ Une fois tout coché : tu es prêt à développer !**

---

## 🚀 Next Steps

1. **Développe T1** : Pseudonymisation complète dans un notebook
2. **Développe T2** : Modèle dimensionnel (dimensions + faits)
3. **Crée ton DAG Airflow** : Automatise le pipeline complet
4. **Teste le pipeline** : Bronze → Silver → Gold
5. **Vérifie dans MinIO** : Les 3 zones doivent être remplies
6. **Crée tes dashboards Superset** : Visualisation BI
7. **Documente** : README du projet, explications des choix techniques
8. **Teste en équipe** : Chacun clone et teste

---

**Bon courage ! 💪**

En cas de problème, n'hésite pas à :
1. Checker les logs : `docker logs <service>`
2. Redémarrer le service : `docker-compose restart <service>`
3. Demander de l'aide à l'équipe !
