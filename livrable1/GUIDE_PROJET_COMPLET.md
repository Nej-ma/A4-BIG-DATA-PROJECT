# 📘 Guide Complet - Projet Big Data CHU

## 🎯 Vue d'ensemble du projet

Vous devez réaliser un système décisionnel Big Data pour le groupe hospitalier CHU, avec 3 livrables sur le semestre.

### Les 3 livrables

| Livrable | Contenu | État | Outil principal |
|----------|---------|------|-----------------|
| **Livrable 1** | Référentiel de données (modèle conceptuel, architecture) | ✅ **FAIT** | LaTeX |
| **Livrable 2** | Implémentation physique, jobs ETL, optimisation | 🚧 **EN COURS** | Airflow + Spark |
| **Livrable 3** | Présentation, dashboards, storytelling | ⏳ **À VENIR** | Superset + PowerPoint |

---

## 📦 Livrable 1 - Référentiel de données (✅ TERMINÉ)

### Ce qui a été fait

Vous avez déjà réalisé le **Livrable 1** (`Livrable1.tex` compilé en PDF) contenant :

✅ Architecture ETLT avec zones Bronze/Silver/Gold
✅ Modèle en constellation (4 faits + 8 dimensions)
✅ Identification des sources de données
✅ Description des jobs d'alimentation
✅ Respect RGPD/HDS

**Fichier** : `Livrable1.pdf`

**Note** : Dans votre livrable, vous mentionnez Talend et Cloudera. Avec cette nouvelle stack, vous devez **mettre à jour** ces références par :
- Talend → **Apache Airflow**
- Cloudera/HDFS → **MinIO (S3)**
- Hive → **Apache Spark**
- Power BI → **Apache Superset** (ou vous pouvez garder Power BI si vous y avez accès)

---

## 🔧 Livrable 2 - Implémentation physique (🚧 EN COURS)

### Objectif

Passer de la conception (Livrable 1) à l'implémentation réelle avec :
1. Jobs ETL fonctionnels
2. Modèle physique créé
3. Données chargées
4. Tests de performance
5. Optimisations (partitionnement, bucketing)

### Votre stack moderne (remplace Talend + Cloudera)

| Fonction | Outil | Port | Accès |
|----------|-------|------|-------|
| Base de données | PostgreSQL 15 | 5432 | `admin` / `admin123` |
| Interface DB | pgAdmin 4 | 5050 | http://localhost:5050 |
| Data Lake | MinIO (S3) | 9000/9001 | http://localhost:9001 |
| Orchestration ETL | Apache Airflow | 8080 | http://localhost:8080 |
| Traitement distribué | Apache Spark | 8081 | http://localhost:8081 |
| Analyse | Jupyter Lab | 8888 | http://localhost:8888 |
| Visualisation | Apache Superset | 8088 | http://localhost:8088 |

### Plan d'action pour le Livrable 2

#### Phase 1 : Préparation (1-2 jours)

**1.1 Démarrer la stack**
```bash
# Double-clic sur START_BIGDATA_STACK.bat
# Ou :
docker-compose -f docker-compose.bigdata.yml up -d
```

**1.2 Charger les données dans PostgreSQL**
- Via pgAdmin (http://localhost:5050)
- Importer votre dump `DATA 2024`
- Vérifier que les tables sont présentes :
  - `patient` (~100K lignes)
  - `consultation` (~1M lignes)
  - `professionnel` (~1M lignes)
  - `diagnostic` (~15K lignes)
  - `medicaments`
  - `mutuelle`

**1.3 Préparer les fichiers CSV**
- Placer tous les CSV dans `DATA 2024/`
- Établissements (FINESS)
- Satisfaction (2014-2020)
- Décès
- Hospitalisation

#### Phase 2 : Développement des jobs ETL (3-5 jours)

**2.1 Jobs d'extraction (E)**

Le DAG fourni (`airflow/dags/chu_etl_pipeline.py`) contient déjà :
- `extract_from_postgres` : Extraction PostgreSQL → Bronze
- `extract_csv_files` : Extraction CSV → Bronze

**Actions** :
1. Vérifier que les chemins de fichiers sont corrects
2. Tester le DAG dans Airflow
3. Vérifier que les données arrivent dans MinIO (bucket `bronze`)

**2.2 Jobs de transformation T1 (Conformité RGPD)**

**Tâches à développer** :

```python
# Dans chu_etl_pipeline.py, compléter :

def transform_t1_patient():
    """
    - Pseudonymiser : nom, prenom, email, telephone, num_secu_social
    - Créer tranches d'âge
    - Supprimer colonnes PII
    """

def transform_t1_consultation():
    """
    - Normaliser dates
    - Valider FK (id_patient, id_professionnel, id_diagnostic)
    """

def transform_t1_etablissement():
    """
    - Nettoyer adresses
    - Valider codes FINESS
    - Détecter doublons
    """

def transform_t1_satisfaction():
    """
    - Harmoniser les 27 fichiers CSV (2014-2020)
    - Uniformiser les colonnes
    - Agréger par établissement/année
    """

def transform_t1_deces():
    """
    - Pseudonymiser identifiants
    - Normaliser localisation (région/département)
    """
```

**2.3 Jobs de transformation T2 (Modèle dimensionnel)**

**Dimensions à créer** :

```python
# Déjà fourni :
- dim_temps : Calendrier 2014-2025
- dim_patient : À partir de patient_clean (Silver)

# À développer :
- dim_etablissement : Jointure PostgreSQL + CSV FINESS
- dim_diagnostic : À partir de table diagnostic
- dim_professionnel : À partir de table professionnel
- dim_specialite : Référentiel des spécialités médicales
- dim_mutuelle : À partir de table mutuelle
- dim_type_enquete : Typologie des enquêtes satisfaction
```

**Tables de faits à créer** :

```python
# 1. FAIT_CONSULTATION
def create_fait_consultation():
    """
    Jointure :
    - consultation (PostgreSQL)
    - dim_temps
    - dim_patient
    - dim_professionnel
    - dim_diagnostic
    - dim_etablissement
    - dim_mutuelle

    Mesures :
    - nb_consultations (count)
    - duree_consultation_moyenne
    """

# 2. FAIT_HOSPITALISATION
def create_fait_hospitalisation():
    """
    Jointure :
    - hospitalisation (CSV)
    - dim_temps (date_entree, date_sortie)
    - dim_patient
    - dim_etablissement
    - dim_diagnostic

    Mesures :
    - nb_hospitalisations
    - duree_sejour (date_sortie - date_entree)
    - duree_sejour_moyenne
    """

# 3. FAIT_DECES
def create_fait_deces():
    """
    Jointure :
    - deces (CSV)
    - dim_temps (date_deces)
    - dim_patient
    - dim_localisation (région/département)

    Mesures :
    - nb_deces
    - age_moyen_deces
    """

# 4. FAIT_SATISFACTION
def create_fait_satisfaction():
    """
    Jointure :
    - satisfaction (CSV agrégé)
    - dim_temps (annee)
    - dim_etablissement
    - dim_type_enquete

    Mesures :
    - note_satisfaction_moyenne
    - nb_reponses
    - taux_satisfaction (note >= 8)
    """
```

#### Phase 3 : Optimisation (2-3 jours)

**3.1 Partitionnement Spark**

Dans `spark/apps/chu_spark_processing.py` :

```python
# Partitionner par année pour les consultations
df_fait_consultation.write \
    .partitionBy("annee") \
    .mode("overwrite") \
    .parquet("s3a://gold/faits/fait_consultation")

# Partitionner par région pour les décès
df_fait_deces.write \
    .partitionBy("region") \
    .mode("overwrite") \
    .parquet("s3a://gold/faits/fait_deces")
```

**3.2 Bucketing (optionnel)**

```python
# Bucketing sur id_patient pour optimiser les jointures
df.write \
    .bucketBy(50, "id_patient") \
    .sortBy("date_consultation") \
    .saveAsTable("fait_consultation_bucketed")
```

**3.3 Format Parquet vs CSV**

- **Bronze** : CSV (tel quel)
- **Silver** : CSV ou Parquet
- **Gold** : **Parquet** (compression Snappy)

Avantages Parquet :
- Stockage colonnaire (requêtes plus rapides)
- Compression efficace (~10x moins d'espace)
- Métadonnées intégrées

#### Phase 4 : Tests de performance (1-2 jours)

**4.1 Requêtes de test**

Dans Jupyter (`jupyter/notebooks/`), créer un notebook `02_Tests_Performance.ipynb` :

```python
import time
import pandas as pd
from sqlalchemy import create_engine

engine = create_engine('postgresql://admin:admin123@postgres:5432/healthcare_data')

# Test 1 : Taux de consultation par année
start = time.time()
df = pd.read_sql("""
    SELECT
        EXTRACT(YEAR FROM date_consultation) as annee,
        COUNT(*) as nb_consultations
    FROM consultation
    GROUP BY annee
    ORDER BY annee
""", engine)
duration_1 = time.time() - start
print(f"Requête 1 : {duration_1:.2f}s")

# Test 2 : Taux d'hospitalisation par diagnostic
start = time.time()
df = pd.read_sql("""
    SELECT
        d.libelle_diagnostic,
        COUNT(*) as nb_hospitalisations,
        AVG(h.duree_sejour) as duree_moyenne
    FROM hospitalisation h
    JOIN diagnostic d ON h.id_diagnostic = d.id_diagnostic
    GROUP BY d.libelle_diagnostic
    ORDER BY nb_hospitalisations DESC
    LIMIT 20
""", engine)
duration_2 = time.time() - start
print(f"Requête 2 : {duration_2:.2f}s")

# ... autres requêtes
```

**4.2 Comparer avec/sans optimisation**

Mesurer :
- Temps de réponse des requêtes
- Taille des fichiers (CSV vs Parquet)
- Utilisation mémoire Spark

**Graphes de performance** :
```python
import matplotlib.pyplot as plt

tests = ['Req 1', 'Req 2', 'Req 3', 'Req 4']
temps_sans_optim = [12.5, 23.1, 45.3, 18.7]
temps_avec_optim = [2.3, 5.4, 8.1, 3.2]

plt.figure(figsize=(10, 6))
x = range(len(tests))
plt.bar([i-0.2 for i in x], temps_sans_optim, width=0.4, label='Sans optimisation', color='coral')
plt.bar([i+0.2 for i in x], temps_avec_optim, width=0.4, label='Avec optimisation', color='steelblue')
plt.xlabel('Requêtes')
plt.ylabel('Temps (secondes)')
plt.title('Impact de l\'optimisation sur les temps de réponse')
plt.xticks(x, tests)
plt.legend()
plt.grid(axis='y', alpha=0.3)
plt.savefig('performance_comparison.png', dpi=300, bbox_inches='tight')
plt.show()
```

#### Phase 5 : Rédaction du Livrable 2 (2-3 jours)

**Structure du rapport** :

```
1. Introduction
   - Rappel de l'architecture (Livrable 1)
   - Objectifs du Livrable 2

2. Implémentation des jobs ETL
   2.1 Jobs d'extraction (E)
       - PostgreSQL → Bronze
       - CSV → Bronze
       - Capture d'écran Airflow DAG

   2.2 Jobs de transformation T1 (Conformité)
       - Pseudonymisation (code + résultats)
       - Normalisation
       - Validation qualité

   2.3 Jobs de transformation T2 (Modèle dimensionnel)
       - Création des 8 dimensions
       - Création des 4 tables de faits
       - Captures d'écran MinIO (buckets)

3. Modèle physique
   3.1 Schémas des tables (DDL SQL)
   3.2 Volumétrie réelle
   3.3 Organisation du Data Lake (Bronze/Silver/Gold)

4. Optimisations
   4.1 Partitionnement (code + résultats)
   4.2 Bucketing (si implémenté)
   4.3 Format Parquet (comparaison tailles)

5. Tests de performance
   5.1 Requêtes de test
   5.2 Temps de réponse (tableaux + graphes)
   5.3 Analyse des résultats

6. Conclusion
   - Bilan des performances
   - Difficultés rencontrées
   - Améliorations possibles

Annexes :
- Code complet des jobs Airflow
- Scripts Spark
- Requêtes SQL de test
```

**Éléments à inclure** :

📸 **Captures d'écran** :
- Airflow : DAG en exécution (Graph View)
- MinIO : Buckets bronze/silver/gold avec fichiers
- Spark UI : Jobs en cours
- Jupyter : Notebook avec résultats
- pgAdmin : Tables créées

📊 **Graphiques** :
- Évolution des temps de réponse
- Comparaison taille CSV vs Parquet
- Distribution des données par partition

📝 **Code** :
- Jobs Airflow complets (annexe)
- Jobs Spark (annexe)
- Requêtes SQL de validation

---

## 🎨 Livrable 3 - Présentation et storytelling (⏳ À VENIR)

### Objectif

Présenter les résultats d'analyse à travers des dashboards et un storytelling convaincant.

### Préparation

**3.1 Créer les dashboards dans Superset**

Accéder à http://localhost:8088

**Dashboards à créer** :

1. **Vue d'ensemble CHU**
   - KPI : Total patients, consultations, hospitalisations
   - Évolution mensuelle des consultations
   - Distribution sexe/âge des patients

2. **Analyse médicale**
   - Top 10 diagnostics
   - Taux d'hospitalisation par diagnostic
   - Durée moyenne de séjour par pathologie

3. **Performance établissements**
   - Consultations par établissement
   - Taux de satisfaction par région
   - Cartographie des établissements

4. **Qualité des soins**
   - Évolution satisfaction 2014-2020
   - Corrélation satisfaction / durée séjour
   - Indicateurs qualité

**3.2 Storytelling**

**Structure de la présentation (20 min)** :

```
1. Introduction (2 min)
   - Contexte du projet CHU
   - Problématique Big Data dans la santé
   - Objectifs du système décisionnel

2. Méthodologie (5 min)
   - Architecture ETLT choisie
   - Stack technologique moderne
   - Conformité RGPD/HDS

3. Modèle décisionnel (3 min)
   - Constellation (4 faits + 8 dimensions)
   - Volumétrie réelle
   - Optimisations mises en place

4. Résultats et analyses (7 min)
   ⭐ STORYTELLING avec dashboards
   - Insight 1 : "La consultation augmente de 15% chaque année"
   - Insight 2 : "Les diagnostics cardiaques représentent 25% des hospitalisations"
   - Insight 3 : "La satisfaction moyenne a progressé de 12% depuis 2014"
   - Recommandations pour le CHU

5. Démonstration technique (3 min)
   - Live demo : Pipeline Airflow
   - Live demo : Dashboard interactif Superset
   - Architecture complète

6. Questions/Réponses (10 min)
```

**3.3 Support de présentation**

- PowerPoint ou Google Slides
- Inclure captures d'écran des dashboards
- Graphiques clairs et impactants
- Palette de couleurs cohérente
- Animations sobres

---

## 📊 Correspondance objectifs pédagogiques

Votre stack couvre **TOUS** les objectifs :

| Code | Objectif | Solution dans votre stack |
|------|----------|---------------------------|
| [1] | Contraintes RGPD | Pseudonymisation SHA-256 dans T1 |
| [2] | 5V du Big Data | Volume (1M+ consultations), Variété (PostgreSQL+CSV), Vélocité (Airflow daily), Véracité (validation T1), Valeur (KPIs) |
| [2] | Architecture BigData | Architecture complète fournie (Bronze/Silver/Gold) |
| [2] | Infrastructure distribuée | MinIO (stockage S3) + Spark (traitement distribué) |
| [2] | Cloud storage | MinIO = S3-compatible (AWS/Azure/GCP) |
| [3] | MapReduce | Spark = MapReduce amélioré (jobs fournis) |
| [2] | Systèmes fichiers distribués | MinIO = Object Storage distribué |
| [2] | Entreposage de données | Data Warehouse en zone Gold |
| [3] | Modèle dimensionnel | Constellation 4 faits + 8 dimensions |
| [1] | Difficultés traitements distribués | Gestion erreurs Airflow, partitionnement Spark |
| [3] | Alimenter Data Mart | Pipeline Airflow complet |
| [3] | Requêtes SQL multi-tables | Jupyter + PostgreSQL |
| [3] | Traduire demande en requêtes | Requêtes métier fournies |
| [3] | ETL | Airflow (remplace Talend) |
| [4] | Qualifier données | Validation qualité en T1 |
| [4] | Stratégie d'analyse | Méthodologie ETLT documentée |
| [3] | Anonymisation RGPD | Pseudonymisation systématique |
| [3] | Organisation Data Lake | Bronze/Silver/Gold |
| [2] | Types bases NoSQL | MinIO = Object Storage (clé-valeur) |
| [2] | ACID vs BASE | PostgreSQL (ACID) vs MinIO (BASE) |
| [3] | Intégrer données NoSQL | Airflow → MinIO |
| [4] | Sélectionner stockage | PostgreSQL (OLTP) + MinIO (OLAP) |
| [3] | Exploiter environnement Big Data | Stack complète opérationnelle |
| [3] | MapReduce | Spark jobs fournis |
| [4] | Optimiser modèle physique | Partitionnement + Parquet |
| [4] | Graphes KPI | Superset + Jupyter (graphiques fournis) |
| [4] | Visualisation UX | Dashboards Superset interactifs |

✅ **100% des objectifs couverts !**

---

## 🎯 Planning suggéré

### Semaine 1-2 : Livrable 1
✅ **FAIT** - Vous l'avez déjà terminé

### Semaine 3-5 : Livrable 2
- **Semaine 3** : Démarrage stack + Jobs extraction (E)
- **Semaine 4** : Jobs T1 (conformité) + T2 (dimensions)
- **Semaine 5** : Tables de faits + Optimisations + Tests performance

### Semaine 6-7 : Livrable 2 (suite)
- **Semaine 6** : Rédaction rapport + Captures d'écran
- **Semaine 7** : Relecture + Finalisation

### Semaine 8-10 : Livrable 3
- **Semaine 8** : Dashboards Superset
- **Semaine 9** : Storytelling + Présentation PowerPoint
- **Semaine 10** : Répétition + Ajustements

---

## 🛠️ Ressources et aide

### Documentation fournie
- `README_STACK.md` : Documentation complète de la stack
- `QUICK_START.md` : Guide de démarrage rapide
- `docker-compose.bigdata.yml` : Configuration des services
- `airflow/dags/chu_etl_pipeline.py` : DAG ETL de base
- `spark/apps/chu_spark_processing.py` : Jobs Spark
- `jupyter/notebooks/01_Analyse_Exploratoire_CHU.ipynb` : Analyse exploratoire

### Liens utiles
- **Airflow** : https://airflow.apache.org/docs/
- **Spark** : https://spark.apache.org/docs/latest/
- **MinIO** : https://min.io/docs/
- **Superset** : https://superset.apache.org/docs/intro
- **Pandas** : https://pandas.pydata.org/docs/
- **PySpark** : https://spark.apache.org/docs/latest/api/python/

### Commandes de secours

```bash
# Tout réinitialiser
docker-compose -f docker-compose.bigdata.yml down -v
docker system prune -a

# Voir les logs
docker-compose -f docker-compose.bigdata.yml logs -f [service]

# Redémarrer un service
docker-compose -f docker-compose.bigdata.yml restart [service]

# Accéder à PostgreSQL
docker exec -it chu_postgres psql -U admin -d healthcare_data
```

---

## ✅ Checklist finale

### Livrable 2

- [ ] Stack Docker démarrée et fonctionnelle
- [ ] Données chargées dans PostgreSQL (1M+ consultations)
- [ ] Fichiers CSV accessibles dans `DATA 2024/`
- [ ] DAG Airflow `chu_etl_pipeline` exécuté avec succès
- [ ] Buckets MinIO bronze/silver/gold remplis
- [ ] 8 dimensions créées dans Gold
- [ ] 4 tables de faits créées dans Gold
- [ ] Partitionnement Spark implémenté
- [ ] Tests de performance réalisés (graphes)
- [ ] Rapport Livrable 2 rédigé
- [ ] Captures d'écran incluses
- [ ] Code en annexe
- [ ] Relecture complète

### Livrable 3

- [ ] Dashboards Superset créés (4 minimum)
- [ ] KPIs calculés et validés
- [ ] Storytelling rédigé
- [ ] Présentation PowerPoint créée
- [ ] Démonstration technique préparée
- [ ] Répétition effectuée (timing 20 min)
- [ ] Questions/réponses anticipées

---

## 🎉 Conclusion

Vous avez maintenant :
✅ Un **stack moderne** qui remplace Talend + Cloudera
✅ Une **architecture complète** Big Data opérationnelle
✅ Des **outils performants** (Airflow, Spark, Superset)
✅ Une **base solide** pour les livrables 2 et 3
✅ Une **documentation complète** pour vous guider

**N'oubliez pas** :
- Travaillez en équipe (3-4 personnes)
- Testez régulièrement
- Documentez au fur et à mesure
- Demandez de l'aide si besoin
- Amusez-vous avec les données ! 😊

**Bonne chance pour votre projet ! 🚀**

---

**Contacts** :
- Équipe : Nejma MOUALHI, Brieuc OLIVIERI, Nicolas TAING
- Formation : CESI FISA A4
- Année : 2025-2026
