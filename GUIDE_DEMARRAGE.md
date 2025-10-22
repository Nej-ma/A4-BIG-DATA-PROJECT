# 🚀 GUIDE DE DÉMARRAGE - Projet CHU Data Lakehouse

## 📋 CE QUI A ÉTÉ FAIT

J'ai créé une infrastructure Data Lakehouse complète pour votre projet. Voici ce qui existe maintenant :

### ✅ Infrastructure Docker
- **PostgreSQL** : Base de données source (100K patients, 1M consultations) ✅
- **MinIO** : Stockage objet S3 pour Delta Lake ✅
- **Spark** : Moteur de traitement Big Data ✅
- **Jupyter** : Interface pour développer et tester ✅
- **Airflow** : Orchestration des pipelines ⚠️ (à corriger)
- **Superset** : Visualisation ✅
- **PgAdmin** : Admin PostgreSQL ✅

### ✅ Scripts créés
1. **spark/jobs/utils/spark_utils.py** - Fonctions utilitaires
2. **spark/jobs/bronze/ingest_postgres_to_bronze.py** - Ingestion PostgreSQL → MinIO
3. **spark/jobs/bronze/ingest_csv_to_bronze.py** - Ingestion CSV → MinIO
4. **docs/livrable2/modele_dimensionnel.md** - Modèle Star Schema
5. **docs/livrable2/README.md** - Documentation détaillée

---

## 🎯 OBJECTIF DU LIVRABLE 2

**Le Livrable 2 consiste à :**

1. **Créer un entrepôt de données (Data Warehouse)** dans MinIO
2. **Charger toutes les données** (PostgreSQL + CSV) dans cet entrepôt
3. **Organiser en 3 couches** :
   - **BRONZE** = Données brutes (copie exacte des sources)
   - **SILVER** = Données nettoyées (typage, validation)
   - **GOLD** = Modèle dimensionnel (Star Schema pour l'analyse)
4. **Optimiser les performances** avec partitionnement et bucketing
5. **Mesurer les performances** avec des requêtes benchmark
6. **Créer des graphiques** montrant les gains de performance

---

## 🔧 PROBLÈMES ACTUELS À CORRIGER

### 1. ❌ Airflow CSRF Error
**Problème** : Erreur "CSRF token missing"
**Solution** : Redémarrer Airflow proprement

### 2. ❌ MinIO buckets
**Problème** : Les buckets ne sont peut-être pas visibles
**Solution** : Vérifier via l'interface web

---

## 📝 ÉTAPES POUR COMMENCER

### ÉTAPE 1 : Vérifier que tout fonctionne

```bash
# Lister tous les conteneurs
docker compose ps

# Tous doivent être "Up" et "healthy"
```

### ÉTAPE 2 : Accéder à MinIO

1. Ouvrir : http://localhost:9001
2. Login : **minioadmin** / **minioadmin123**
3. Vérifier qu'il y a 2 buckets :
   - `lakehouse`
   - `warehouse`

**Si les buckets n'existent pas**, exécutez :
```bash
docker compose up -d minio_setup
docker logs chu_minio_setup
```

### ÉTAPE 3 : Accéder à Jupyter

1. Ouvrir : http://localhost:8888
2. Token : **admin123**
3. Créer un nouveau notebook

### ÉTAPE 4 : Tester la connexion PostgreSQL

Dans Jupyter, créez un notebook et exécutez :

```python
from pyspark.sql import SparkSession

# Créer session Spark
spark = SparkSession.builder \
    .appName("Test PostgreSQL") \
    .getOrCreate()

# Connexion PostgreSQL
jdbc_url = "jdbc:postgresql://chu_postgres:5432/healthcare_data"
jdbc_props = {
    "user": "admin",
    "password": "admin123",
    "driver": "org.postgresql.Driver"
}

# Lire la table Patient
df = spark.read.jdbc(url=jdbc_url, table='"Patient"', properties=jdbc_props)

# Afficher
print(f"Nombre de patients : {df.count()}")
df.show(5)
```

**Résultat attendu** : 100,000 patients affichés ✅

### ÉTAPE 5 : Tester MinIO

Dans le même notebook :

```python
# Créer un DataFrame de test
test_data = [(1, "Test 1"), (2, "Test 2")]
df_test = spark.createDataFrame(test_data, ["id", "nom"])

# Essayer d'écrire dans MinIO
try:
    df_test.write.mode("overwrite").parquet("s3a://lakehouse/test/data")
    print("✅ SUCCÈS : MinIO fonctionne !")
except Exception as e:
    print(f"❌ ERREUR MinIO : {e}")
```

---

## 🎓 COMMENT UTILISER CE PROJET

### Scénario 1 : Vous voulez JUSTE faire l'ingestion (Bronze Layer)

**Ce qui va se passer** :
- Toutes les tables PostgreSQL → Copiées dans MinIO (`s3a://lakehouse/bronze/postgres/`)
- Tous les CSV → Copiés dans MinIO (`s3a://lakehouse/bronze/csv/`)
- Format : **Delta Lake** (format optimisé pour Big Data)

**Comment faire** :
```python
# Dans Jupyter
!python /opt/spark-apps/bronze/ingest_postgres_to_bronze.py
!python /opt/spark-apps/bronze/ingest_csv_to_bronze.py
```

### Scénario 2 : Vous voulez créer le modèle dimensionnel (Gold Layer)

**Ce qui va se passer** :
- Création de tables de **dimensions** (Patient, Temps, Diagnostic, etc.)
- Création de tables de **faits** (Consultations, Hospitalisations, Décès, Satisfaction)
- Partitionnement par année/mois
- Bucketing sur les clés de jointure

**Comment faire** :
```python
# Dans Jupyter (scripts à créer ensemble)
!python /opt/spark-apps/gold/create_dimensions.py
!python /opt/spark-apps/gold/create_facts.py
```

### Scénario 3 : Vous voulez mesurer les performances

**Ce qui va se passer** :
- Exécution de requêtes de test
- Mesure des temps de réponse
- Comparaison avant/après optimisation
- Génération de graphiques

**Comment faire** :
```python
# Dans Jupyter (scripts à créer ensemble)
!python /opt/spark-apps/performance/benchmark_queries.py
```

---

## 🆘 EN CAS DE PROBLÈME

### Problème : "Rien ne marche"
```bash
# Tout arrêter
docker compose down

# Tout redémarrer proprement
docker compose up -d postgres minio jupyter spark-master spark-worker

# Attendre 30 secondes, puis vérifier
docker compose ps
```

### Problème : "Airflow ne fonctionne pas"
```bash
# Arrêter Airflow
docker compose stop airflow-webserver airflow-scheduler

# Redémarrer
docker compose up -d airflow-init
# Attendre que airflow-init se termine
docker compose up -d airflow-webserver airflow-scheduler
```

### Problème : "MinIO n'a pas de buckets"
```bash
# Recréer les buckets
docker compose up -d minio_setup

# Vérifier les logs
docker logs chu_minio_setup

# Vérifier sur http://localhost:9001
```

---

## 📊 PROCHAINES ÉTAPES (Ce qu'il reste à faire)

1. ✅ Infrastructure Docker → **FAIT**
2. ✅ Scripts Bronze → **FAIT**
3. ✅ Modèle dimensionnel → **DOCUMENTÉ**
4. ⏳ Tester l'ingestion Bronze → **À FAIRE MAINTENANT**
5. ⏳ Créer scripts Silver (nettoyage) → **À FAIRE**
6. ⏳ Créer scripts Gold (Star Schema) → **À FAIRE**
7. ⏳ Optimisations (partitionnement/bucketing) → **À FAIRE**
8. ⏳ Benchmarks de performance → **À FAIRE**
9. ⏳ Graphiques de résultats → **À FAIRE**

---

## 🎯 POUR RÉSUMER EN 3 PHRASES

1. **J'ai créé toute l'infrastructure** (Docker + Spark + MinIO) pour stocker et traiter vos données
2. **J'ai écrit les scripts** pour copier PostgreSQL et les CSV dans un Data Lakehouse
3. **Il faut maintenant tester que tout fonctionne** puis créer le modèle dimensionnel

---

## 💡 CE QUE VOUS DEVEZ FAIRE MAINTENANT

**Option 1 (Recommandée)** : On corrige MinIO ensemble et on teste l'ingestion
**Option 2** : On crée d'abord les scripts Gold (modèle dimensionnel)
**Option 3** : Vous testez manuellement avec Jupyter et me dites ce qui bloque

**Quelle option voulez-vous choisir ?**
