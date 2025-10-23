# 🎯 PLAN DE FINALISATION LIVRABLE 2

**Date**: 23 Octobre 2025
**Objectif**: Finaliser le Livrable 2 conformément aux exigences

---

## 📋 RÉPONSES À VOS QUESTIONS

### ❓ Question 1: C'est quoi les "jobs"?

**Réponse**: Les **jobs** sont des **scripts Spark autonomes** (fichiers `.py`) qui peuvent être:
1. **Soumis à Spark Master** via `spark-submit`
2. **Orchestrés par Airflow** pour automatisation
3. **Exécutés indépendamment** des notebooks

**Différence Notebook vs Job**:

| Aspect | Notebook Jupyter | Spark Job (script .py) |
|--------|------------------|----------------------|
| **Usage** | Développement interactif | Production automatisée |
| **Exécution** | Manuelle, cellule par cellule | Automatique, script complet |
| **Orchestration** | Non orchestrable | Orchestrable par Airflow |
| **Logs** | Dans notebook | Dans Spark UI + logs files |
| **Livrable** | Oui (développement) | Oui (production) |

**Pourquoi Spark Master est vide?**
- Actuellement, vos notebooks utilisent Spark en **mode local** (`local[*]`)
- Spark Master (`http://localhost:8081`) n'est utilisé que si on soumet des jobs via `spark-submit`

---

### ❓ Question 2: Airflow et mode overwrite vs append

**Réponse CRITIQUE**: Actuellement vos notebooks utilisent `.mode("overwrite")` ce qui signifie:

```python
# Mode actuel (PROBLÉMATIQUE pour production)
df.write.mode("overwrite").parquet(path)
# ❌ Écrase TOUT à chaque exécution
# ❌ Si on ajoute 1 ligne au PostgreSQL, toutes les données sont réécrites
```

**Ce qu'il FAUT pour Livrable 2**:

#### Stratégie Bronze (Sources)
```python
# Bronze doit être COMPLET (snapshot)
df.write.mode("overwrite").parquet(bronze_path)
# ✅ Écrase = normal car c'est un snapshot des sources
# ✅ Si nouvelle ligne PostgreSQL, on re-extrait TOUT
```

#### Stratégie Silver/Gold (Traitement)
```python
# Option 1: Overwrite (plus simple pour Livrable 2)
df.write.mode("overwrite").parquet(silver_path)
# ✅ Acceptable pour prototype/livrable
# ❌ Non optimal pour production

# Option 2: Incremental (meilleur pour production)
df.write.mode("append") \
    .option("mergeSchema", "true") \
    .parquet(silver_path)
# ✅ Ajoute seulement nouvelles données
# ✅ Optimise temps d'exécution
# ⚠️ Nécessite gestion des doublons (MERGE/UPSERT)
```

**Recommandation pour VOTRE Livrable 2**:
- **Garder `overwrite` partout** (plus simple)
- **Documenter** que c'est un mode "full refresh"
- **Mentionner** dans le rapport que le mode incrémental serait implémenté en phase 2

**Comportement avec Airflow**:
```python
# Si vous relancez la pipeline Airflow:
1. Extraction Bronze: Écrase données Bronze (snapshot frais)
2. Transform Silver: Écrase données Silver (retraite TOUT Bronze)
3. Transform Gold: Écrase données Gold (retraite TOUT Silver)

# ✅ Garantit cohérence totale
# ❌ Prend du temps (mais acceptable pour vos volumes)
```

---

### ❓ Question 3: Comment intégrer Airflow?

**Réponse**: Créer un **DAG Airflow** qui orchestre vos jobs Spark:

```python
# airflow/dags/chu_etlt_pipeline.py
from airflow import DAG
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'chu_team',
    'depends_on_past': False,
    'start_date': datetime(2025, 10, 23),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'chu_etlt_pipeline',
    default_args=default_args,
    description='Pipeline ETLT complet CHU Data Lakehouse',
    schedule_interval='@daily',  # Exécute tous les jours à minuit
    catchup=False,
)

# Job 1: Extract Bronze
extract_bronze = SparkSubmitOperator(
    task_id='extract_bronze',
    application='/opt/spark-apps/01_extract_bronze.py',
    conn_id='spark_default',
    dag=dag,
)

# Job 2: Transform Silver
transform_silver = SparkSubmitOperator(
    task_id='transform_silver',
    application='/opt/spark-apps/02_transform_silver.py',
    conn_id='spark_default',
    dag=dag,
)

# Job 3: Transform Gold
transform_gold = SparkSubmitOperator(
    task_id='transform_gold',
    application='/opt/spark-apps/03_transform_gold.py',
    conn_id='spark_default',
    dag=dag,
)

# Job 4: Benchmarks
run_benchmarks = SparkSubmitOperator(
    task_id='run_benchmarks',
    application='/opt/spark-apps/04_benchmarks.py',
    conn_id='spark_default',
    dag=dag,
)

# Définir l'ordre d'exécution
extract_bronze >> transform_silver >> transform_gold >> run_benchmarks
```

**Avantages Airflow**:
- ✅ Visualisation du pipeline
- ✅ Retry automatique en cas d'erreur
- ✅ Logs centralisés
- ✅ Alertes email si échec
- ✅ Schedule automatique (daily, weekly, etc.)

---

## 📊 ÉTAT ACTUEL vs EXIGENCES LIVRABLE 2

### ✅ Ce que vous AVEZ déjà

| Exigence | Statut | Fichier |
|----------|--------|---------|
| Script création tables | ✅ **FAIT** | 03_Transform_Gold_STAR_SCHEMA.ipynb |
| Script chargement données | ✅ **FAIT** | 01_Extract + 02_Transform |
| Vérification données | ✅ **FAIT** | 06_Export_Gold_to_PostgreSQL.ipynb |
| Script peuplement | ✅ **FAIT** | Notebooks 01-03 |
| Modèle dimensionnel | ✅ **FAIT** | 5 dims + 4 faits |
| Export PostgreSQL | ✅ **FAIT** | Notebook 06 |

### ⚠️ Ce qu'il MANQUE pour Livrable 2

| Exigence | Statut | Action requise |
|----------|--------|----------------|
| **Script partitionnement** | 🟡 **PARTIEL** | Déjà fait dans Gold, documenter |
| **Script buckets** | ❌ **MANQUANT** | Non applicable (pas Hive) |
| **Jobs Spark (.py)** | ❌ **MANQUANT** | Convertir notebooks → jobs |
| **DAG Airflow** | ❌ **MANQUANT** | Créer dag_etlt.py |
| **Graphes performance** | ❌ **MANQUANT** | Créer notebook benchmarks |
| **Requêtes benchmark** | 🟡 **PARTIEL** | Notebook 04 existe, enrichir |
| **Rapport LaTeX** | 🟡 **PARTIEL** | Corriger volumétries réelles |

---

## 🎯 PLAN D'ACTION DÉTAILLÉ

### Phase 1: Créer les Jobs Spark (2h)

**Objectif**: Convertir notebooks en scripts Python autonomes

**Actions**:
1. Créer `spark/jobs/01_extract_bronze.py` depuis notebook 01
2. Créer `spark/jobs/02_transform_silver.py` depuis notebook 02
3. Créer `spark/jobs/03_transform_gold.py` depuis notebook 03
4. Créer `spark/jobs/04_benchmarks.py` depuis notebook 04

**Template job Spark**:
```python
# spark/jobs/01_extract_bronze.py
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
import logging

# Configuration logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_spark_session():
    """Crée session Spark avec config optimale"""
    return SparkSession.builder \
        .appName("CHU - Extract Bronze") \
        .config("spark.sql.adaptive.enabled", "true") \
        .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
        .getOrCreate()

def extract_postgres_tables(spark):
    """Extrait toutes tables PostgreSQL vers Bronze"""
    logger.info("Starting PostgreSQL extraction...")

    jdbc_url = "jdbc:postgresql://chu_postgres:5432/healthcare_data"
    properties = {
        "user": "admin",
        "password": "admin123",
        "driver": "org.postgresql.Driver"
    }

    tables = ["Patient", "Consultation", "AAAA", "date", ...]

    for table in tables:
        logger.info(f"Extracting table: {table}")
        df = spark.read.jdbc(jdbc_url, table, properties=properties)

        # Ajouter metadata
        df = df.withColumn("ingestion_timestamp", current_timestamp()) \
               .withColumn("ingestion_date", current_date())

        # Écrire en Parquet
        output_path = f"/home/jovyan/data/bronze/postgres/{table}"
        df.write.mode("overwrite") \
          .option("compression", "snappy") \
          .partitionBy("ingestion_date") \
          .parquet(output_path)

        count = df.count()
        logger.info(f"✅ {table}: {count} lignes extraites")

def extract_csv_files(spark):
    """Extrait fichiers CSV vers Bronze"""
    logger.info("Starting CSV extraction...")
    # ... code extraction CSV ...

def main():
    """Point d'entrée principal"""
    spark = create_spark_session()

    try:
        extract_postgres_tables(spark)
        extract_csv_files(spark)
        logger.info("✅ Extraction Bronze terminée avec succès")
    except Exception as e:
        logger.error(f"❌ Erreur extraction: {str(e)}")
        raise
    finally:
        spark.stop()

if __name__ == "__main__":
    main()
```

---

### Phase 2: Créer DAG Airflow (1h)

**Fichier**: `airflow/dags/chu_etlt_dag.py`

**Contenu**: (voir exemple ci-dessus)

**Test**:
```bash
# 1. Vérifier DAG détecté
docker exec chu_airflow_webserver airflow dags list | grep chu_etlt

# 2. Activer DAG dans UI
# http://localhost:8080 → Toggle ON

# 3. Trigger manuel
docker exec chu_airflow_webserver airflow dags trigger chu_etlt_pipeline
```

---

### Phase 3: Benchmarks Performance (2h)

**Créer**: `jupyter/notebooks/07_Benchmarks_Performance_Detailles.ipynb`

**Contenu**:

#### 1. Définir 6 requêtes de référence

```python
# Q1: Comptage total consultations
query_1 = """
SELECT COUNT(*) as total_consultations
FROM gold.fait_consultation
"""

# Q2: Agrégation par spécialité
query_2 = """
SELECT p.specialite,
       COUNT(*) as nb_consultations,
       AVG(f.duree_sejour_jours) as duree_moy
FROM gold.fait_consultation f
JOIN gold.dim_professionnel p ON f.id_professionnel = p.id_professionnel_hash
GROUP BY p.specialite
ORDER BY nb_consultations DESC
"""

# Q3: Analyse temporelle avec partition pruning
query_3 = """
SELECT t.annee, t.mois,
       COUNT(*) as nb_consultations
FROM gold.fait_consultation f
JOIN gold.dim_temps t ON f.id_temps = t.id_temps
WHERE t.annee = 2015 AND t.mois BETWEEN 6 AND 12
GROUP BY t.annee, t.mois
ORDER BY t.annee, t.mois
"""

# Q4: Top 10 diagnostics
query_4 = """
SELECT d.code_diag, d.libelle,
       COUNT(*) as nb_occurrences
FROM gold.fait_consultation f
JOIN gold.dim_diagnostic d ON f.code_diag = d.code_diag
GROUP BY d.code_diag, d.libelle
ORDER BY nb_occurrences DESC
LIMIT 10
"""

# Q5: Satisfaction par établissement
query_5 = """
SELECT e.nom_etablissement,
       AVG(s.score_satisfaction) as satisfaction_moy,
       COUNT(*) as nb_evaluations
FROM gold.fait_satisfaction s
JOIN gold.dim_etablissement e ON s.code_etablissement = e.code_etablissement
GROUP BY e.nom_etablissement
HAVING nb_evaluations > 5
ORDER BY satisfaction_moy DESC
"""

# Q6: Hospitalisations par durée séjour
query_6 = """
SELECT
    CASE
        WHEN duree_sejour_jours = 0 THEN '0 jour'
        WHEN duree_sejour_jours = 1 THEN '1 jour'
        WHEN duree_sejour_jours BETWEEN 2 AND 7 THEN '2-7 jours'
        ELSE '7+ jours'
    END as duree_categorie,
    COUNT(*) as nb_hospitalisations
FROM gold.fait_hospitalisation
GROUP BY duree_categorie
ORDER BY duree_categorie
"""
```

#### 2. Mesurer temps d'exécution

```python
import time
import matplotlib.pyplot as plt
import pandas as pd

def benchmark_query(spark, query, query_name, runs=3):
    """Exécute query N fois et retourne stats"""
    times = []

    for i in range(runs):
        # Clear cache pour mesure réelle
        spark.catalog.clearCache()

        start_time = time.time()
        result = spark.sql(query)
        result.collect()  # Force execution
        end_time = time.time()

        elapsed = end_time - start_time
        times.append(elapsed)
        print(f"  Run {i+1}: {elapsed:.2f}s")

    return {
        'query': query_name,
        'min': min(times),
        'max': max(times),
        'avg': sum(times) / len(times),
        'median': sorted(times)[len(times)//2]
    }

# Exécuter tous benchmarks
queries = [
    (query_1, "Q1: Count consultations"),
    (query_2, "Q2: Agrégation spécialité"),
    (query_3, "Q3: Analyse temporelle"),
    (query_4, "Q4: Top 10 diagnostics"),
    (query_5, "Q5: Satisfaction"),
    (query_6, "Q6: Hospitalisations durée"),
]

results = []
for query, name in queries:
    print(f"\n🔍 Benchmark: {name}")
    result = benchmark_query(spark, query, name)
    results.append(result)
    print(f"   ✅ Temps médian: {result['median']:.2f}s")

# Créer DataFrame résultats
df_results = pd.DataFrame(results)
print("\n📊 RÉSULTATS BENCHMARKS:")
print(df_results.to_string(index=False))
```

#### 3. Générer graphiques

```python
import matplotlib.pyplot as plt
import seaborn as sns

# Style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)

# Graphique 1: Temps médian par requête
fig, ax = plt.subplots()
ax.barh(df_results['query'], df_results['median'], color='steelblue')
ax.set_xlabel('Temps d\'exécution (secondes)')
ax.set_title('Performance des Requêtes Analytiques\n(Temps médian sur 3 runs)')
ax.grid(axis='x', alpha=0.3)
plt.tight_layout()
plt.savefig('/home/jovyan/data/benchmark_queries_median.png', dpi=300)
plt.show()

# Graphique 2: Min/Max/Avg
fig, ax = plt.subplots()
x = range(len(df_results))
ax.plot(x, df_results['min'], marker='o', label='Min', color='green')
ax.plot(x, df_results['avg'], marker='s', label='Moyenne', color='blue')
ax.plot(x, df_results['max'], marker='^', label='Max', color='red')
ax.set_xticks(x)
ax.set_xticklabels([q.split(':')[0] for q in df_results['query']], rotation=45)
ax.set_ylabel('Temps (secondes)')
ax.set_title('Variabilité des Temps d\'Exécution')
ax.legend()
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig('/home/jovyan/data/benchmark_queries_variability.png', dpi=300)
plt.show()

# Graphique 3: Comparaison avant/après optimisation
# (Simulé pour démonstration - remplacer par vos vraies mesures)
comparaison = pd.DataFrame({
    'Query': ['Q1', 'Q2', 'Q3', 'Q4', 'Q5', 'Q6'],
    'Avant (CSV non partitionné)': [45.0, 38.5, 52.3, 29.7, 18.4, 23.1],
    'Après (Parquet partitionné)': [1.2, 2.3, 3.1, 1.5, 2.7, 1.8]
})

fig, ax = plt.subplots()
x = range(len(comparaison))
width = 0.35
ax.bar([i - width/2 for i in x], comparaison['Avant (CSV non partitionné)'],
       width, label='Avant optimisation', color='coral')
ax.bar([i + width/2 for i in x], comparaison['Après (Parquet partitionné)'],
       width, label='Après optimisation', color='lightgreen')
ax.set_xticks(x)
ax.set_xticklabels(comparaison['Query'])
ax.set_ylabel('Temps d\'exécution (secondes)')
ax.set_title('Impact des Optimisations\n(Partition + Parquet + AQE)')
ax.legend()
ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig('/home/jovyan/data/benchmark_before_after.png', dpi=300)
plt.show()
```

#### 4. Export résultats

```python
# Export CSV pour LaTeX
df_results.to_csv('/home/jovyan/data/benchmark_results.csv', index=False)

# Export JSON
import json
with open('/home/jovyan/data/benchmark_results.json', 'w') as f:
    json.dump(results, f, indent=2)

print("\n✅ Résultats exportés:")
print("  - benchmark_results.csv")
print("  - benchmark_results.json")
print("  - benchmark_queries_median.png")
print("  - benchmark_queries_variability.png")
print("  - benchmark_before_after.png")
```

---

### Phase 4: Corriger Volumétries LaTeX (30min)

**Problème**: Votre `livrable2.tex` contient des volumétries **fictives** (ex: 1,023,456 consultations)

**Solution**: Remplacer par les **vraies volumétries** de vos données

**Actions**:
1. Exécuter un notebook qui compte les lignes réelles
2. Mettre à jour `livrable2.tex` avec les vrais chiffres

**Script comptage**:
```python
# Compter toutes les tables Gold
tables_gold = [
    "dim_patient", "dim_temps", "dim_diagnostic",
    "dim_professionnel", "dim_etablissement",
    "fait_consultation", "fait_hospitalisation",
    "fait_deces", "fait_satisfaction"
]

volumetries = {}
for table in tables_gold:
    try:
        df = spark.read.parquet(f"/home/jovyan/data/gold/{table}")
        count = df.count()
        volumetries[table] = count
        print(f"✅ {table}: {count:,} lignes")
    except Exception as e:
        print(f"❌ {table}: Erreur - {str(e)}")

# Export pour LaTeX
import json
with open('/home/jovyan/data/volumetries_gold.json', 'w') as f:
    json.dump(volumetries, f, indent=2)
```

---

### Phase 5: Finaliser Livrable 2 (1h)

**Actions**:

1. **Mettre à jour livrable2.tex**:
   - Corriger volumétries (sections 2.2, 3.2, 3.3)
   - Ajouter résultats benchmarks réels (section 5)
   - Ajouter références aux jobs Spark

2. **Créer ZIP de soumission**:
```bash
cd /c/Users/littl/Desktop/Big\ DATA/projet_git

# Créer dossier livrable
mkdir -p livrable2/submission

# Copier notebooks
cp jupyter/notebooks/*.ipynb livrable2/submission/

# Copier jobs Spark
cp spark/jobs/*.py livrable2/submission/

# Copier DAG Airflow
cp airflow/dags/chu_etlt_dag.py livrable2/submission/

# Copier graphiques
cp jupyter/data/benchmark_*.png livrable2/submission/

# Créer ZIP
cd livrable2
zip -r livrable2_MOUALHI_OLIVIERI_TAING.zip submission/ livrable2.pdf

echo "✅ ZIP créé: livrable2_MOUALHI_OLIVIERI_TAING.zip"
```

3. **Compiler LaTeX**:
```bash
cd livrable2
pdflatex livrable2.tex
pdflatex livrable2.tex  # 2x pour références
```

---

## 📊 CHECKLIST FINALE LIVRABLE 2

### Scripts

- [ ] **01_extract_bronze.py** - Job Spark extraction
- [ ] **02_transform_silver.py** - Job Spark nettoyage
- [ ] **03_transform_gold.py** - Job Spark star schema
- [ ] **04_benchmarks.py** - Job Spark benchmarks
- [ ] **chu_etlt_dag.py** - DAG Airflow orchestration

### Notebooks

- [x] **01_Extract_Bronze_SOURCES_DIRECTES.ipynb** - Extraction
- [x] **02_Transform_Silver_NETTOYAGE.ipynb** - Nettoyage
- [x] **03_Transform_Gold_STAR_SCHEMA.ipynb** - Star Schema
- [x] **04_Performance_Benchmarks.ipynb** - Benchmarks basiques
- [ ] **07_Benchmarks_Performance_Detailles.ipynb** - Benchmarks complets
- [x] **06_Export_Gold_to_PostgreSQL.ipynb** - Export PostgreSQL

### Graphiques Performance

- [ ] **benchmark_queries_median.png** - Temps médian par requête
- [ ] **benchmark_queries_variability.png** - Min/Max/Avg
- [ ] **benchmark_before_after.png** - Avant/Après optimisations
- [ ] **partition_impact.png** - Impact partitionnement
- [ ] **parquet_vs_csv.png** - Parquet vs CSV

### Rapport LaTeX

- [ ] Corriger volumétries réelles (Section 2.2)
- [ ] Ajouter résultats benchmarks (Section 5)
- [ ] Ajouter graphiques performance (Section 5.3)
- [ ] Documenter jobs Spark (Section 3)
- [ ] Documenter DAG Airflow (Section 3.1)
- [ ] Compiler PDF final

### ZIP Soumission

- [ ] Notebooks (6 fichiers .ipynb)
- [ ] Jobs Spark (4 fichiers .py)
- [ ] DAG Airflow (1 fichier .py)
- [ ] Graphiques (5 fichiers .png)
- [ ] Rapport PDF (livrable2.pdf)
- [ ] README.md (instructions exécution)

---

## 🎯 PROCHAINES ÉTAPES

### Maintenant (Phase 1)
Je vais créer les jobs Spark en convertissant vos notebooks existants.

### Après validation (Phase 2)
Je créerai le DAG Airflow pour orchestrer ces jobs.

### Puis (Phase 3)
Je créerai le notebook de benchmarks détaillés avec graphiques.

### Enfin (Phase 4-5)
Je corrigerai le LaTeX et créerai le ZIP final.

---

**⏱️ Temps estimé total: 6-7 heures**

**🎯 Résultat: Livrable 2 complet et conforme aux exigences**
