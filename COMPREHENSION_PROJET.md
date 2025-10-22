# 🎓 COMPRENDRE LE PROJET - Architecture et Outils

**Projet** : CHU Data Lakehouse
**Auteurs** : Nejma MOUALHI | Brieuc OLIVIERI | Nicolas TAING

---

## 🏗️ ARCHITECTURE COMPLÈTE

```
┌─────────────────────────────────────────────────────────────┐
│  SOURCES DE DONNÉES                                          │
├─────────────────────────────────────────────────────────────┤
│  PostgreSQL : Base opérationnelle (patients, consultations) │
│  CSV : Fichiers plats (décès, satisfaction, établissements) │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│  TRAITEMENT (ETL)                                            │
├─────────────────────────────────────────────────────────────┤
│  Spark : Moteur de calcul distribué Big Data                │
│  (lecture, transformation, agrégation des millions de lignes)│
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│  STOCKAGE (Data Lakehouse)                                   │
├─────────────────────────────────────────────────────────────┤
│  MinIO : Stockage objet (comme AWS S3)                       │
│    • lakehouse/bronze/  : Données brutes                     │
│    • lakehouse/silver/  : Données nettoyées                  │
│    • lakehouse/gold/    : Modèle dimensionnel                │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│  ORCHESTRATION                                               │
├─────────────────────────────────────────────────────────────┤
│  Airflow : Planification et automatisation des pipelines    │
│  (lance les jobs Spark de manière automatique/programmée)   │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│  ANALYSE & VISUALISATION                                     │
├─────────────────────────────────────────────────────────────┤
│  Jupyter : Développement interactif (notebooks)              │
│  Superset : Dashboards BI pour les décideurs                │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔧 RÔLE DE CHAQUE OUTIL

### 1. **PostgreSQL** 🗄️
**Rôle** : Base de données opérationnelle (OLTP)
**Contient** :
- 100,000 patients
- 1,027,157 consultations
- 13 tables relationnelles
- + Les CSV qu'on a chargés

**Pourquoi ?** : C'est la source de vérité, les données "en production"

---

### 2. **Spark** ⚡
**Rôle** : Moteur de calcul Big Data (traitement distribué)

**Fait quoi concrètement ?**
- Lit des millions de lignes rapidement
- Transforme les données (nettoyage, agrégations)
- Joint plusieurs tables ensemble
- Calcule des statistiques complexes
- Écrit des résultats en Parquet/Delta Lake

**Exemple concret** :
```python
# Spark lit 1 million de consultations
df = spark.read.jdbc("postgresql://...", "Consultation")

# Calcule le nombre de consultations par année
result = df.groupBy("annee").count()

# Sauvegarde en Parquet dans MinIO
result.write.parquet("s3a://lakehouse/gold/stats")
```

**Pourquoi Spark ?**
- PostgreSQL galère avec 1M+ lignes en analyse
- Spark parallélise le travail → plus rapide
- Spark peut lire Parquet, CSV, JSON, etc.

---

### 3. **Jupyter** 📓
**Rôle** : Interface de développement interactive

**Fait quoi ?**
- Permet d'écrire du code Python/Spark cellule par cellule
- Visualise les résultats immédiatement
- Crée des graphiques (matplotlib, seaborn)
- Documente le code avec du Markdown

**Pourquoi Jupyter ?**
- **Pour le développement** : tester rapidement les transformations
- **Pour le Livrable 2** : notebooks = code + résultats + explications
- **Pour la démo** : exécuter devant le jury

**Alternatives** :
- Script Python classique (moins visuel)
- PySpark en ligne de commande (moins pratique)

---

### 4. **MinIO** 🪣
**Rôle** : Stockage objet (comme AWS S3, mais local)

**Contient** :
- **lakehouse/** : Votre Data Lakehouse
  - `bronze/` : Données brutes (copie de PostgreSQL + CSV)
  - `silver/` : Données nettoyées
  - `gold/` : Modèle dimensionnel (Star Schema)
- **warehouse/** : Réservé pour Spark SQL (tables Hive)

**Pourquoi MinIO ?**
- Stockage illimité (vs PostgreSQL limité)
- Format optimisé (Parquet = compression 10x)
- Versioning (Delta Lake garde l'historique)
- Compatible S3 (on peut migrer vers AWS après)

**Pourquoi vide ?**
- Normal ! Vous n'avez pas encore exécuté les notebooks
- Les notebooks écrivent dedans quand vous les lancez

---

### 5. **Airflow** 🔄
**Rôle** : Orchestrateur de workflows (ETL automatisé)

**Fait quoi ?**
```
Airflow DAG (pipeline) :
  1. Tous les jours à 2h du matin
  2. Lance le job Bronze (ingestion PostgreSQL)
  3. Puis lance le job Silver (nettoyage)
  4. Puis lance le job Gold (modèle dimensionnel)
  5. Envoie un email si erreur
```

**Pourquoi Airflow ?**
- Automatise les pipelines (au lieu de lancer manuellement)
- Gère les dépendances (Silver attend Bronze)
- Retry automatique si échec
- Monitoring visuel

**Pour le Livrable 2** : Pas obligatoire (mais bonus++)
**Pour le Livrable 3** : Probablement demandé

---

### 6. **Superset** 📊
**Rôle** : Outil de BI (Business Intelligence) / Dashboards

**Fait quoi ?**
- Se connecte aux données (PostgreSQL, Spark SQL)
- Crée des graphiques interactifs (barres, lignes, cartes)
- Construit des tableaux de bord
- Partage avec les décideurs (médecins, direction)

**Exemple dashboard** :
```
┌─────────────────────────────────────┐
│  CHU Dashboard - Vue d'ensemble     │
├─────────────────────────────────────┤
│  📈 Consultations par mois          │
│  📊 Top 10 diagnostics              │
│  🗺️  Carte des décès par région     │
│  ⭐ Satisfaction moyenne : 72%      │
└─────────────────────────────────────┘
```

**Pour le Livrable 2** : Pas obligatoire
**Pour le Livrable 3** : Sûrement demandé (storytelling)

---

## 🎯 POUR LE LIVRABLE 2 (CE QU'ON FAIT LÀ)

### Objectif du Livrable 2 :
**"Modèle physique et optimisation"**

### Ce qu'il faut livrer :
1. ✅ **Script de création et chargement de données**
   - → Notebooks 01 et 03 (fait !)

2. ✅ **Vérification des données**
   - → Chaque notebook affiche les comptages

3. ✅ **Script de peuplement des tables**
   - → Notebook 01 (Bronze) + Notebook 03 (Gold)

4. ✅ **Partitionnement et buckets**
   - → Notebook 03 (fait_consultation partitionné par année/mois)

5. ✅ **Graphes de performance**
   - → Notebook 04 génère les PNG

6. ✅ **Requêtes de benchmark**
   - → Notebook 04 (6 requêtes SQL)

### Outils utilisés pour Livrable 2 :
- ✅ **PostgreSQL** : Source de données
- ✅ **Spark** : Traitement et transformations
- ✅ **Jupyter** : Développement et documentation
- ✅ **MinIO** : Stockage du lakehouse
- ❌ **Airflow** : Pas obligatoire (mais je vais le réparer)
- ❌ **Superset** : Pas obligatoire pour L2

---

## 🚀 POUR LE LIVRABLE 3 (Suite du projet)

### Objectif probable :
**"Présentation des résultats et storytelling"**

### Ce qui sera demandé :
1. **Dashboards interactifs** → Superset
2. **Pipelines automatisés** → Airflow
3. **Analyses complexes** → Jupyter + Spark
4. **Storytelling** → Présentation avec graphiques

### Outils qui deviendront importants :
- ⭐ **Superset** : Dashboards pour la soutenance
- ⭐ **Airflow** : Montrer l'automatisation
- ⭐ **Jupyter** : Analyses exploratoires

---

## 📋 WORKFLOW COMPLET (Comment ça marche ensemble)

### Workflow Manuel (Livrable 2 - ce qu'on fait maintenant) :

```
1. PostgreSQL (source)
      ↓ Jupyter Notebook 01
2. Spark lit PostgreSQL
      ↓ Spark transforme
3. Spark écrit dans MinIO (Bronze)
      ↓ Jupyter Notebook 03
4. Spark lit Bronze
      ↓ Spark crée le modèle Gold
5. Spark écrit dans MinIO (Gold)
      ↓ Jupyter Notebook 04
6. Spark fait des requêtes
      ↓ Génère graphiques
7. Résultats PNG + Rapport
```

### Workflow Automatisé (Livrable 3 - probable) :

```
1. Airflow DAG déclenché (tous les jours 2h)
      ↓
2. Airflow lance Spark Job Bronze
      ↓
3. Airflow lance Spark Job Silver
      ↓
4. Airflow lance Spark Job Gold
      ↓
5. Airflow met à jour Superset
      ↓
6. Dashboards actualisés automatiquement
```

---

## 🔧 POURQUOI AIRFLOW ET SUPERSET NE MARCHENT PAS ?

**Airflow** : Erreur CSRF (problème de sécurité web)
**Superset** : Probablement même genre de problème

**Pas grave pour le Livrable 2** car :
- Pas obligatoires maintenant
- Je vais les réparer pour le Livrable 3
- Jupyter suffit largement pour L2

---

## ✅ CE QU'IL FAUT FAIRE MAINTENANT (Livrable 2)

### Étapes restantes :

1. ✅ **PostgreSQL** : Prêt (100K patients + CSV chargés)

2. ⏳ **Exécuter Notebook 01** : Ingestion Bronze
   - Lit PostgreSQL → Écrit MinIO/bronze/
   - Durée : 5 minutes
   - **Résultat** : MinIO aura des données !

3. ⏳ **Exécuter Notebook 03** : Modèle Gold
   - Lit Bronze → Crée Star Schema → Écrit MinIO/gold/
   - Durée : 15 minutes
   - **C'est le cœur du Livrable 2** ⭐

4. ⏳ **Exécuter Notebook 04** : Benchmarks
   - Fait des requêtes → Mesure temps → Graphiques
   - Durée : 10 minutes
   - **Résultat** : PNG + Rapport

5. ✅ **Livrable 2 terminé !**

---

## 💡 RÉSUMÉ EN 3 PHRASES

1. **Spark** = cerveau qui calcule (transforme 1M lignes en quelques secondes)
2. **Jupyter** = interface pour coder et voir les résultats (pour L2)
3. **MinIO** = disque dur du lakehouse (stocke Bronze/Silver/Gold)
4. **Airflow** = robot qui lance tout automatiquement (pour L3)
5. **Superset** = écran pour les décideurs (dashboards pour L3)

---

**Maintenant je répare Airflow et Superset, puis vous pourrez lancer les notebooks !**
