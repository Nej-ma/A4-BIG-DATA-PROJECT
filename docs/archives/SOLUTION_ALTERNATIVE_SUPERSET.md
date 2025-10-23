# 🎯 SOLUTION ALTERNATIVE - Superset sans Hive

**Problème** : Les tables Hive avec `PARTITIONED BY` + `convertMetastoreParquet=false` causent des erreurs de lecture.

**Solution** : Utiliser **PostgreSQL** ou **Trino** comme passerelle vers les fichiers Parquet.

---

## ✅ OPTION 1 : PostgreSQL + Foreign Data Wrapper (RECOMMANDÉ)

### Pourquoi ?

- ✅ PostgreSQL est déjà dans le stack
- ✅ Superset a un driver natif PostgreSQL
- ✅ Pas besoin d'installer de drivers
- ✅ Performant avec `parquet_fdw`

### Étape 1 : Créer des vues matérialisées dans PostgreSQL

Depuis Jupyter, exécuter ce code dans une nouvelle cellule :

```python
from sqlalchemy import create_engine
import pandas as pd

# Connexion PostgreSQL
engine = create_engine('postgresql://postgres:postgres@postgres:5432/hopital')

# Lire les fichiers Parquet
dim_temps = spark.read.parquet("/home/jovyan/data/gold/dim_temps").toPandas()
dim_patient = spark.read.parquet("/home/jovyan/data/gold/dim_patient").toPandas()
dim_diagnostic = spark.read.parquet("/home/jovyan/data/gold/dim_diagnostic").toPandas()
dim_professionnel = spark.read.parquet("/home/jovyan/data/gold/dim_professionnel").toPandas()
dim_etablissement = spark.read.parquet("/home/jovyan/data/gold/dim_etablissement").toPandas()

# Échantillon de consultations (ou toutes si assez de RAM)
fait_consultation = spark.read.parquet("/home/jovyan/data/gold/fait_consultation") \
    .limit(100000).toPandas()  # Limiter à 100K pour test

# Écrire dans PostgreSQL
dim_temps.to_sql('gold_dim_temps', engine, schema='public', if_exists='replace', index=False)
dim_patient.to_sql('gold_dim_patient', engine, schema='public', if_exists='replace', index=False)
dim_diagnostic.to_sql('gold_dim_diagnostic', engine, schema='public', if_exists='replace', index=False)
dim_professionnel.to_sql('gold_dim_professionnel', engine, schema='public', if_exists='replace', index=False)
dim_etablissement.to_sql('gold_dim_etablissement', engine, schema='public', if_exists='replace', index=False)
fait_consultation.to_sql('gold_fait_consultation', engine, schema='public', if_exists='replace', index=False)

print("✅ Tables Gold exportées vers PostgreSQL")
```

### Étape 2 : Connecter Superset à PostgreSQL

Dans Superset :

1. **Settings** → **Database Connections** → **+ DATABASE**
2. **SUPPORTED DATABASES** → **PostgreSQL**
3. **SQLALCHEMY URI** :
   ```
   postgresql://postgres:postgres@postgres:5432/hopital
   ```
4. **TEST CONNECTION** → **CONNECT**

### Étape 3 : Utiliser SQL Lab

Les tables `gold_*` sont maintenant disponibles dans Superset via PostgreSQL !

```sql
SELECT
    t.annee,
    COUNT(*) as nb_consultations
FROM gold_fait_consultation f
JOIN gold_dim_temps t ON f.id_temps = t.id_temps
GROUP BY t.annee
ORDER BY t.annee
```

---

## ✅ OPTION 2 : Utiliser DuckDB (ULTRA RAPIDE)

### Pourquoi ?

- ✅ DuckDB peut lire Parquet directement
- ✅ Performant (moteur OLAP)
- ✅ Support SQLAlchemy

### Étape 1 : Installer DuckDB

```bash
docker exec chu_superset pip install duckdb duckdb-engine
docker restart chu_superset
```

### Étape 2 : Créer fichier DuckDB avec vues

Dans Jupyter, créer une nouvelle cellule :

```python
import duckdb

# Créer base DuckDB
conn = duckdb.connect('/home/jovyan/data/chu_gold.duckdb')

# Créer vues sur les fichiers Parquet
conn.execute("""
    CREATE OR REPLACE VIEW dim_temps AS
    SELECT * FROM read_parquet('/home/jovyan/data/gold/dim_temps/**/*.parquet', hive_partitioning=true)
""")

conn.execute("""
    CREATE OR REPLACE VIEW dim_patient AS
    SELECT * FROM read_parquet('/home/jovyan/data/gold/dim_patient/*.parquet')
""")

conn.execute("""
    CREATE OR REPLACE VIEW dim_diagnostic AS
    SELECT * FROM read_parquet('/home/jovyan/data/gold/dim_diagnostic/*.parquet')
""")

conn.execute("""
    CREATE OR REPLACE VIEW dim_professionnel AS
    SELECT * FROM read_parquet('/home/jovyan/data/gold/dim_professionnel/*.parquet')
""")

conn.execute("""
    CREATE OR REPLACE VIEW dim_etablissement AS
    SELECT * FROM read_parquet('/home/jovyan/data/gold/dim_etablissement/*.parquet')
""")

conn.execute("""
    CREATE OR REPLACE VIEW fait_consultation AS
    SELECT * FROM read_parquet('/home/jovyan/data/gold/fait_consultation/**/*.parquet', hive_partitioning=true)
""")

conn.close()
print("✅ Vues DuckDB créées")
```

### Étape 3 : Connecter Superset à DuckDB

Dans Superset :

1. **Settings** → **Database Connections** → **+ DATABASE**
2. **Other** (DuckDB pas dans la liste)
3. **SQLALCHEMY URI** :
   ```
   duckdb:////home/jovyan/data/chu_gold.duckdb
   ```
4. **TEST CONNECTION** → **CONNECT**

---

## ✅ OPTION 3 : Simplifier les tables Hive (QUICK FIX)

### Recréer les tables SANS partitionnement

Dans Notebook 05, modifier la cellule 4 :

```python
tables_definitions = {
    "dim_temps": """
        CREATE EXTERNAL TABLE dim_temps (
            id_temps STRING,
            date_complete DATE,
            annee INT,
            mois INT,
            jour INT,
            jour_semaine INT,
            nom_jour STRING,
            trimestre INT,
            semaine_annee INT
        )
        STORED AS PARQUET
        LOCATION '/home/jovyan/data/gold/dim_temps'
        TBLPROPERTIES('parquet.compression'='SNAPPY')
    """,

    "fait_consultation": """
        CREATE EXTERNAL TABLE fait_consultation (
            id_consultation STRING,
            id_temps STRING,
            id_patient STRING,
            code_diag STRING,
            id_prof STRING,
            cout DECIMAL(10,2),
            duree_minutes INT,
            urgence BOOLEAN,
            annee INT,
            mois INT
        )
        STORED AS PARQUET
        LOCATION '/home/jovyan/data/gold/fait_consultation'
        TBLPROPERTIES('parquet.compression'='SNAPPY')
    """,
    # ... autres tables inchangées
}
```

**MAIS** : Cela nécessite de **réécrire les fichiers Parquet** dans Notebook 03 sans partitionnement.

---

## 🎯 RECOMMANDATION

**Pour ta soutenance MAINTENANT** : **OPTION 1 (PostgreSQL)**

### Pourquoi ?

1. ✅ **Rapide** : 5 minutes pour exporter vers PostgreSQL
2. ✅ **Fonctionne à coup sûr** : Driver natif Superset
3. ✅ **Pas de config Docker** : Tout dans Jupyter
4. ✅ **Démo fonctionnelle** : Workflow E2E validé

### Code complet Option 1

```python
# DANS JUPYTER - Nouvelle cellule après le Notebook 05

from sqlalchemy import create_engine

# Connexion PostgreSQL
engine = create_engine('postgresql://postgres:postgres@postgres:5432/hopital')

print("📊 Export Gold Layer vers PostgreSQL pour Superset...\n")

# Lire et exporter chaque table
tables = {
    "gold_dim_temps": "/home/jovyan/data/gold/dim_temps",
    "gold_dim_patient": "/home/jovyan/data/gold/dim_patient",
    "gold_dim_diagnostic": "/home/jovyan/data/gold/dim_diagnostic",
    "gold_dim_professionnel": "/home/jovyan/data/gold/dim_professionnel",
    "gold_dim_etablissement": "/home/jovyan/data/gold/dim_etablissement",
    "gold_fait_consultation": "/home/jovyan/data/gold/fait_consultation"
}

for table_name, parquet_path in tables.items():
    print(f"  Exportation {table_name}...", end="")

    # Lire Parquet
    df = spark.read.parquet(parquet_path)

    # Limiter fait_consultation si trop gros (optionnel)
    if "consultation" in table_name:
        df = df.limit(500000)  # 500K lignes suffisent pour demo

    # Convertir en Pandas
    pdf = df.toPandas()

    # Écrire dans PostgreSQL
    pdf.to_sql(table_name, engine, schema='public', if_exists='replace', index=False)

    print(f" ✅ {len(pdf):,} lignes")

print("\n✅ Export terminé ! Connecter Superset à PostgreSQL maintenant.")
```

### Puis dans Superset

```
Settings → + DATABASE → PostgreSQL
URI: postgresql://postgres:postgres@postgres:5432/hopital
TEST CONNECTION → CONNECT
```

### SQL Lab

```sql
SELECT
    t.annee,
    COUNT(*) as nb_consultations,
    COUNT(DISTINCT f.id_patient) as patients_uniques
FROM gold_fait_consultation f
JOIN gold_dim_temps t ON f.id_temps = t.id_temps
GROUP BY t.annee
ORDER BY t.annee
```

---

## 📊 COMPARAISON OPTIONS

| Option | Temps setup | Performance | Complexité | Pour soutenance |
|--------|-------------|-------------|------------|-----------------|
| **PostgreSQL** | 5 min | Moyenne | Facile | ✅ OUI |
| DuckDB | 10 min | Excellente | Moyenne | ✅ OK |
| Hive sans partition | 20 min | Moyenne | Difficile | ❌ Non |
| Trino | 30 min | Excellente | Difficile | ❌ Non |

---

## 🚀 ACTION IMMÉDIATE

**Copie-colle ce code dans Jupyter** (nouvelle cellule) :

```python
from sqlalchemy import create_engine

engine = create_engine('postgresql://postgres:postgres@postgres:5432/hopital')

print("📊 Export rapide Gold Layer → PostgreSQL\n")

# Dimensions (petites, on charge tout)
for name, path in [
    ("gold_dim_temps", "/home/jovyan/data/gold/dim_temps"),
    ("gold_dim_patient", "/home/jovyan/data/gold/dim_patient"),
    ("gold_dim_diagnostic", "/home/jovyan/data/gold/dim_diagnostic"),
    ("gold_dim_professionnel", "/home/jovyan/data/gold/dim_professionnel"),
    ("gold_dim_etablissement", "/home/jovyan/data/gold/dim_etablissement"),
]:
    df = spark.read.parquet(path).toPandas()
    df.to_sql(name, engine, if_exists='replace', index=False)
    print(f"✅ {name}: {len(df):,} lignes")

# Fait (on limite à 200K pour la démo)
df_fait = spark.read.parquet("/home/jovyan/data/gold/fait_consultation").limit(200000).toPandas()
df_fait.to_sql("gold_fait_consultation", engine, if_exists='replace', index=False)
print(f"✅ gold_fait_consultation: {len(df_fait):,} lignes")

print("\n🎉 TERMINÉ ! Connecter Superset à PostgreSQL maintenant.")
```

**Exécute** → Attends 2-3 minutes → Superset !

---

**🎯 C'est la solution la plus rapide pour avoir Superset fonctionnel MAINTENANT !**
