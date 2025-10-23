# 🏥 CHU Data Lakehouse - Projet Big Data

**Cloud Healthcare Unit - Delta Lake Architecture**

CESI FISA A4 - Livrable 2

## 👥 Équipe

- **Nejma MOUALHI**
- **Brieuc OLIVIERI**
- **Nicolas TAING**

---

## ⚡ STATUT : LIVRABLE 2 COMPLET ET OPÉRATIONNEL ✅

**🎉 Pipeline 100% fonctionnel - Bronze → Silver → Gold + Superset**

### 📚 Documentation Essentielle

**Tous les guides sont dans le dossier [`docs/`](docs/)**:

- 🚀 **[GUIDE_UTILISATION.md](docs/GUIDE_UTILISATION.md)** - Guide complet d'utilisation (démarrage, notebooks, Superset, SQL, Docker)
- 📊 **[SYNTHESE_PROJET.md](docs/SYNTHESE_PROJET.md)** - Synthèse technique complète (architecture, découvertes, conformité)
- 🔧 **[TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)** - Solutions aux problèmes courants
- 📋 **[docs/README.md](docs/README.md)** - Index de la documentation

**Ancienne documentation** : Archivée dans [`docs/archives/`](docs/archives/) pour référence

### 📊 Résultats Finaux

**Architecture Médaillon Complète**:

| Layer | Tables | Lignes | Temps | Statut |
|-------|--------|--------|-------|--------|
| **Bronze** | 17 | ~4M | ~2 min | ✅ |
| **Silver** | 13 | ~3.5M | ~3 min | ✅ |
| **Gold** | 9 (5 dims + 4 faits) | ~2.9M | ~3 min | ✅ |
| **PostgreSQL** | 9 tables gold | ~2.9M | ~3 min | ✅ |

**Tables de Faits (Conforme Livrable 1)** ✅:
1. **fait_consultation** - 1,027,157 consultations (2015-2023)
2. **fait_hospitalisation** - 82,216 hospitalisations (2013-2025) ← Découvert!
3. **fait_deces** - 620,625 décès (2019 filtré)
4. **fait_satisfaction** - 8 scores E-Satis (2019)

**Dimensions** (5):
- dim_temps, dim_patient, dim_diagnostic, dim_professionnel, dim_etablissement

### 🚀 Quick Start (3 étapes)

```bash
# 1. Démarrer la stack
docker-compose up -d

# 2. Accéder Jupyter: http://localhost:8888

# 3. Exécuter notebooks dans l'ordre:
#    01_Extract_Bronze_SOURCES_DIRECTES.ipynb      (~2 min)
#    02_Transform_Silver_NETTOYAGE.ipynb           (~3 min)
#    03_Transform_Gold_STAR_SCHEMA.ipynb           (~3 min)
#    06_Export_Gold_to_PostgreSQL.ipynb            (~3 min)

# 4. Accéder Superset: http://localhost:8088 (admin/admin123)
```

**Temps total pipeline**: ~11 minutes ⏱️

### ✅ Architecture ETLT (Conforme Livrable 1)

```
PostgreSQL + CSV → Bronze → Silver (Pseudonymisation) → Gold (Star Schema) → PostgreSQL → Superset
```

- ✅ **Extract**: PostgreSQL (13 tables) + CSV (4 fichiers)
- ✅ **Transform 1**: Pseudonymisation RGPD (SHA-256 + sel)
- ✅ **Load**: Parquet compressé (snappy) + partitionnement
- ✅ **Transform 2**: Star Schema (5 dimensions + 4 faits)
- ✅ **Visualisation**: Apache Superset + PostgreSQL Gold

---

## 🚀 Quick Start (3 étapes)

### 1. Clone le projet

```bash
git clone <votre-repo-url>
cd projet_git
```

### 2. Lance la stack complète

```bash
docker-compose up --build -d
```

**Attends 2-3 minutes** que tous les services démarrent.

### 3. Vérifie que tout fonctionne

```bash
docker-compose ps
```

Tous les services doivent être **Up** (sauf worker Spark - non utilisé).

---

## 🌐 Services et Accès

| Service | URL | Login | Mot de passe | Rôle |
|---------|-----|-------|--------------|------|
| **Airflow** | http://localhost:8080 | admin | admin123 | Orchestration ETL |
| **Jupyter Lab** | http://localhost:8888 | - | token: admin123 | Développement PySpark |
| **MinIO Console** | http://localhost:9001 | minioadmin | minioadmin123 | Stockage S3 (Delta Lake) |
| **Spark Master UI** | http://localhost:8081 | - | - | Monitoring Spark |
| **Superset** | http://localhost:8088 | admin | admin123 | Visualisation BI |
| **pgAdmin** | http://localhost:5050 | admin@chu.fr | admin123 | Admin PostgreSQL |
| **PostgreSQL** | localhost:5432 | admin | admin123 | Base de données source |

---

## 📁 Architecture Delta Lake

```
┌─────────────────────────────────────────────────────────────┐
│                 DATA LAKEHOUSE CHU - DELTA LAKE             │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  PostgreSQL (sources) ──┐                                   │
│                         │                                   │
│                         ▼                                   │
│                    ┌─────────┐                              │
│                    │ Airflow │  (Orchestration ETL)         │
│                    └────┬────┘                              │
│                         │                                   │
│                         ▼                                   │
│            ┌────────────────────────────┐                   │
│            │   MinIO S3 (Delta Lake)    │                   │
│            ├────────────────────────────┤                   │
│            │  📦 lakehouse/             │                   │
│            │    ├─ bronze/  (raw)       │                   │
│            │    ├─ silver/  (T1 RGPD)   │                   │
│            │    └─ gold/    (T2 DWH)    │                   │
│            └────────────────────────────┘                   │
│                         │                                   │
│        ┌────────────────┴────────────────┐                 │
│        ▼                                  ▼                 │
│  ┌──────────────┐                  ┌─────────┐             │
│  │ Jupyter Lab  │                  │ Superset│             │
│  │  + PySpark   │                  │   BI    │             │
│  │ (Analytics)  │                  │(Dashbds)│             │
│  └──────────────┘                  └─────────┘             │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 🗄️ Données de Départ

### ⚠️ IMPORTANT : Restauration du dump PostgreSQL

**Après le premier lancement**, vous devez restaurer le dump de la base de données :

```bash
# 1. Lancer la stack
docker-compose up -d

# 2. Attendre que PostgreSQL soit prêt (2-3 minutes)

# 3. Restaurer le dump
docker exec -it chu_postgres pg_restore -U admin -d healthcare_data -v /docker-entrypoint-initdb.d/DATA2023.dump
```

Le dump contient toutes les **données réelles du CHU** (patients, consultations, diagnostics, etc.)

📖 **Voir [data/README.md](data/README.md) pour les instructions détaillées.**

---

## 🎯 Workflow Livrable 2

### Étape 1 : Développer dans Jupyter Lab

1. Ouvre **Jupyter Lab** : http://localhost:8888 (token: `admin123`)
2. Crée un nouveau notebook dans `notebooks/`
3. Utilise PySpark avec Delta Lake :

```python
from pyspark.sql import SparkSession
from delta import *

# Session Spark avec Delta Lake
builder = SparkSession.builder.appName("CHU ETL") \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
    .config("spark.hadoop.fs.s3a.endpoint", "http://chu_minio:9000") \
    .config("spark.hadoop.fs.s3a.access.key", "minioadmin") \
    .config("spark.hadoop.fs.s3a.secret.key", "minioadmin123") \
    .config("spark.hadoop.fs.s3a.path.style.access", "true") \
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")

spark = configure_spark_with_delta_pip(builder).getOrCreate()

# Lire depuis PostgreSQL
df = spark.read.jdbc(
    url="jdbc:postgresql://chu_postgres:5432/healthcare_data",
    table='"Patient"',
    properties={"user": "admin", "password": "admin123"}
)

# Écrire en Delta Lake (Bronze)
df.write.format("delta").mode("overwrite").save("s3a://lakehouse/bronze/patient")

# Lire depuis Delta Lake
df_delta = spark.read.format("delta").load("s3a://lakehouse/bronze/patient")
df_delta.show(5)
```

### Étape 2 : Créer les transformations T1 et T2

**T1 (Bronze → Silver) : RGPD - Pseudonymisation**
- Anonymiser les données PII (SHA-256)
- Calculer l'âge à partir de la date de naissance
- Supprimer les colonnes sensibles

**T2 (Silver → Gold) : Modèle dimensionnel**
- Créer les dimensions dénormalisées
- Enrichir les faits avec les dimensions
- Calculer les métriques agrégées

### Étape 3 : Orchestrer avec Airflow

1. Crée ton DAG dans `airflow/dags/`
2. Ouvre **Airflow UI** : http://localhost:8080 (admin / admin123)
3. Active ton DAG
4. Trigger manuellement
5. Vérifie les logs d'exécution

Exemple DAG fourni : `airflow/dags/exemple_delta_lake.py`

### Étape 4 : Vérifier dans MinIO

1. Ouvre **MinIO Console** : http://localhost:9001 (minioadmin / minioadmin123)
2. Browse `lakehouse/bronze/`, `silver/`, `gold/`
3. Vérifie la présence des fichiers Parquet et `_delta_log/`

### Étape 5 : Visualiser avec Superset

1. Ouvre **Superset** : http://localhost:8088 (admin / admin123)
2. Connecte-toi à PostgreSQL ou aux données Gold
3. Crée tes dashboards

---

## 🛠️ Stack Technique

| Composant | Version | Rôle |
|-----------|---------|------|
| **Apache Airflow** | 2.8.1 | Orchestration ETL |
| **Delta Lake** | 2.4.0 | Lakehouse ACID + versioning |
| **Apache Spark** | 3.4.0 | Moteur distribué |
| **PySpark** | 3.4.0 | API Python Spark |
| **MinIO** | latest | Stockage S3-compatible |
| **PostgreSQL** | 15-alpine | Base source |
| **Jupyter Lab** | latest | Développement |
| **Apache Superset** | latest | Visualisation BI |

---

## 🔧 Commandes Utiles

### Voir les logs d'un service

```bash
docker logs chu_airflow_webserver -f
docker logs chu_jupyter -f
docker logs chu_postgres -f
```

### Redémarrer un service

```bash
docker-compose restart airflow-webserver
docker-compose restart jupyter
```

### Arrêter tout

```bash
docker-compose down
```

### Tout supprimer et recommencer (⚠️ PERTE DE DONNÉES)

```bash
docker-compose down -v
docker-compose up --build -d
```

### Vérifier l'état des services

```bash
docker-compose ps
```

### Exécuter une commande SQL dans PostgreSQL

```bash
docker exec -it chu_postgres psql -U admin -d healthcare_data
```

### Tester Delta Lake dans Jupyter

```bash
docker exec -it chu_jupyter python3 -c "from delta import *; print('✅ Delta Lake OK')"
```

---

## ❓ Problèmes Fréquents

### Airflow ne démarre pas

```bash
# Vérifie les logs
docker logs chu_airflow_init

# Redémarre
docker-compose restart airflow-webserver airflow-scheduler
```

### MinIO buckets n'existent pas

Les buckets sont créés automatiquement par `chu_minio_setup`.

Si problème :
1. Va sur http://localhost:9001
2. Créé manuellement `lakehouse` et `warehouse`

### Jupyter ne se connecte pas à MinIO

Vérifie le hostname dans ton code :
- ✅ `http://chu_minio:9000` (dans Docker)
- ❌ `http://localhost:9000` (ne marche pas)

### Port déjà utilisé

Si tu as déjà des services sur les mêmes ports :
1. Arrête les anciens services
2. Ou modifie les ports dans `docker-compose.yml`

### PostgreSQL n'a pas de données

Vérifiez que les scripts SQL sont bien dans `data/` :

```bash
ls data/
# Doit afficher : 01_init_schema.sql  02_seed_data.sql  03_seed_transactions.sql
```

Si vous devez recharger les données :

```bash
# Stopper et supprimer les volumes
docker-compose down -v

# Relancer (rechargera depuis data/)
docker-compose up --build -d
```

---

## 📚 Documentation Complémentaire

- **Guide Équipe** : [GUIDE_EQUIPE.md](GUIDE_EQUIPE.md) - Onboarding complet pas à pas
- **Données** : [data/README.md](data/README.md) - Instructions pour ajouter vos données

---

## ⚠️ Sécurité et RGPD

### Données sensibles

Ce projet contient des **données PII de patients** (nom, prénom, NSS, adresse, etc.).

**Important** :
- ✅ Les données sont **fictives** (générées pour le projet)
- ⚠️ Ne jamais utiliser de vraies données patients
- 🔒 Le `.gitignore` empêche le commit de fichiers sensibles (CSV, Parquet, volumes Docker)

### Pseudonymisation (T1)

La transformation T1 doit pseudonymiser :
- `nom` → SHA-256
- `prenom` → SHA-256
- `numero_securite_sociale` → SHA-256
- `adresse`, `telephone`, `email` → Supprimés

**Exemple** :

```python
from pyspark.sql.functions import sha2, concat_ws

df_silver = df_bronze.withColumn(
    "nom_hash", sha2(concat_ws("_", col("nom"), lit("salt_secret")), 256)
).drop("nom", "prenom", "numero_securite_sociale", "adresse", "telephone", "email")
```

---

## ✅ Checklist Livrable 2

- [ ] Stack complète opérationnelle (tous les services UP)
- [ ] Connexion PostgreSQL → Jupyter Lab validée
- [ ] Écriture en Delta Lake Bronze validée
- [ ] Transformation T1 (RGPD) implémentée
- [ ] Transformation T2 (DWH) implémentée
- [ ] DAG Airflow fonctionnel (Bronze → Silver → Gold)
- [ ] Données visibles dans MinIO (3 zones)
- [ ] Dashboard Superset créé
- [ ] Documentation complétée
- [ ] Code versionné sur Git

---

## 🎓 Objectifs Pédagogiques

1. **Data Lakehouse** : Comprendre l'architecture Bronze/Silver/Gold
2. **Delta Lake** : ACID, versioning, time travel
3. **RGPD** : Pseudonymisation et protection des PII
4. **ETL/ELT** : Orchestration avec Airflow
5. **Big Data** : PySpark pour traiter des volumétries importantes
6. **BI** : Visualisation des données de santé

---

## 📞 Support

En cas de problème :
1. Vérifie les logs : `docker logs <container_name>`
2. Consulte la section **Problèmes Fréquents**
3. Redémarre le service concerné
4. En dernier recours : `docker-compose down -v && docker-compose up --build -d`

---

**Bon courage pour le Livrable 2 ! 💪**
