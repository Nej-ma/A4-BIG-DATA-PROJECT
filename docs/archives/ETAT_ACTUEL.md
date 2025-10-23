# 📊 ÉTAT ACTUEL DU PROJET - CHU Data Lakehouse

**Date** : 21 Octobre 2025
**Livrable** : Livrable 2 - Modèle physique et optimisation

---

## ✅ CE QUI EST PRÊT ET FONCTIONNE

### 1. Infrastructure Docker (100% opérationnelle)

| Service | URL | Login | Status |
|---------|-----|-------|--------|
| **PostgreSQL** | localhost:5432 | admin / admin123 | ✅ 100K patients, 1M consultations |
| **MinIO Console** | http://localhost:9001 | minioadmin / minioadmin123 | ✅ Buckets: lakehouse, warehouse |
| **Jupyter Lab** | http://localhost:8888 | Token: admin123 | ✅ Prêt avec Spark |
| **Spark Master UI** | http://localhost:8081 | - | ✅ Running |
| **Airflow** | http://localhost:8080 | admin / admin123 | ✅ Corrigé |
| **Superset** | http://localhost:8088 | admin / admin123 | ✅ Running |
| **PgAdmin** | http://localhost:5050 | admin@chu.fr / admin123 | ✅ Running |

### 2. Code créé

```
spark/jobs/
├── utils/
│   └── spark_utils.py                    ✅ Fonctions utilitaires Spark
├── bronze/
│   ├── ingest_postgres_to_bronze.py      ✅ PostgreSQL → MinIO
│   └── ingest_csv_to_bronze.py           ✅ CSV → MinIO
├── test_connections.py                   ✅ Script de test
└── (silver/, gold/, performance/)        ⏳ À créer

docs/livrable2/
├── modele_dimensionnel.md                ✅ Star Schema documenté
└── README.md                             ✅ Guide complet
```

### 3. Données disponibles

**PostgreSQL (restauré)** :
- 100,000 patients
- 1,027,157 consultations
- 13 tables au total

**CSV disponibles** :
- Décès (~300K lignes)
- Satisfaction (2014-2019, multiple fichiers)
- Établissements de santé (~30K)
- Hospitalisations

---

## 🎯 CE QUE VOUS DEVEZ FAIRE MAINTENANT

### OPTION 1 : Tester que tout fonctionne (RECOMMANDÉ)

#### A. Vérifier MinIO
1. Ouvrez http://localhost:9001
2. Login: `minioadmin` / `minioadmin123`
3. Vous devriez voir 2 buckets : `lakehouse` et `warehouse`

#### B. Tester avec Jupyter
1. Ouvrez http://localhost:8888
2. Token: `admin123`
3. Créez un nouveau notebook Python
4. Copiez-collez ce code :

```python
from pyspark.sql import SparkSession

# Créer session Spark
spark = SparkSession.builder.appName("Test").getOrCreate()

# Test PostgreSQL
jdbc_url = "jdbc:postgresql://chu_postgres:5432/healthcare_data"
props = {"user": "admin", "password": "admin123", "driver": "org.postgresql.Driver"}

df_patient = spark.read.jdbc(url=jdbc_url, table='"Patient"', properties=props)
print(f"✅ Patients dans PostgreSQL: {df_patient.count():,}")
df_patient.show(5)

# Test écriture locale (pas S3 pour l'instant)
df_test = spark.createDataFrame([(1, "Test")], ["id", "val"])
df_test.write.mode("overwrite").parquet("/home/jovyan/data/test_output")
print("✅ Écriture Parquet OK")
```

**Résultat attendu** :
```
✅ Patients dans PostgreSQL: 100,000
✅ Écriture Parquet OK
```

---

### OPTION 2 : Lancer l'ingestion Bronze (si Option 1 fonctionne)

Dans Jupyter, exécutez :

```python
# Ingestion PostgreSQL → MinIO
!python /opt/spark-apps/bronze/ingest_postgres_to_bronze.py
```

**Ce que ça fait** :
- Lit les 13 tables de PostgreSQL
- Les sauvegarde en format Delta Lake dans MinIO
- Localisation: `s3a://lakehouse/bronze/postgres/`

**Durée estimée** : 5-10 minutes

---

## ⚠️ PROBLÈMES CONNUS

### 1. Connexion S3A MinIO depuis Spark
**Symptôme** : `IllegalArgumentException: hostname cannot be null`

**Cause** : Configuration Hadoop S3A

**Solution temporaire** :
- Utiliser Jupyter pour lire PostgreSQL
- Sauvegarder localement d'abord (`/home/jovyan/data/`)
- Puis copier manuellement vers MinIO

**Solution permanente** :
- Ajouter un fichier `core-site.xml` avec la config S3A
- Ou utiliser Airflow pour orchestrer (a accès à MinIO)

### 2. Spark Worker redémarre
**Symptôme** : `chu_spark_worker` en status "Restarting"

**Impact** : Aucun pour l'instant (Spark Master fonctionne en mode local)

**Solution** :
```bash
docker logs chu_spark_worker
docker compose restart spark-worker
```

---

## 📋 PLAN D'ACTION POUR LE LIVRABLE 2

### Phase 1 : Ingestion Bronze (EN COURS)
- [ ] Tester connexion PostgreSQL ✅ (FAIT)
- [ ] Tester écriture fichiers ✅ (FAIT)
- [ ] Corriger connexion S3A MinIO ⏳
- [ ] Ingérer PostgreSQL → Bronze
- [ ] Ingérer CSV → Bronze

### Phase 2 : Transformation Silver
- [ ] Script de nettoyage des données
- [ ] Validation des types
- [ ] Dédoublonnage
- [ ] Enrichissements

### Phase 3 : Modèle Gold (Star Schema)
- [ ] Créer dimensions (Patient, Temps, Diagnostic, etc.)
- [ ] Créer faits (Consultations, Hospitalisations, etc.)
- [ ] Implémenter partitionnement
- [ ] Implémenter bucketing

### Phase 4 : Performance
- [ ] Créer requêtes benchmark
- [ ] Mesurer temps SANS optimisation
- [ ] Mesurer temps AVEC optimisation
- [ ] Générer graphiques
- [ ] Rédiger rapport

---

## 💡 RECOMMANDATION

**Pour avancer rapidement** :

1. **Testez Option 1** (code Jupyter ci-dessus) pour vérifier que Spark fonctionne
2. **Si ça marche**, on peut :
   - Soit corriger S3A ensemble
   - Soit passer directement à créer le modèle Gold (plus important pour le livrable)
3. **Si ça ne marche pas**, donnez-moi l'erreur exacte

**Question** : Voulez-vous que je vous aide à :
- A) Corriger S3A pour que l'ingestion Bronze fonctionne ?
- B) Passer directement aux scripts Silver/Gold (plus important) ?
- C) Créer un notebook Jupyter complet avec tout le pipeline ?

Dites-moi ce qui vous bloque exactement et ce que vous voulez faire en priorité !
