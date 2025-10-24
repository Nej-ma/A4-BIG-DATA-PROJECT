# CER - Prosit 1 : ARCHIE

## Définition des Mots-Clés

**Architecture Big Data** : Structure technique distribuée pour traiter des volumes massifs de données que les systèmes classiques ne peuvent gérer.

**Entreposage de données** : Centralisation de données hétérogènes dans un référentiel unique optimisé pour l'analyse décisionnelle.

**BDD multidimensionnelle** : Base organisée selon un modèle en étoile ou flocon permettant l'analyse selon plusieurs axes (temps, lieu, patient).

**ETL** : Extract-Transform-Load, processus d'extraction, transformation et chargement des données depuis les sources vers l'entrepôt.

**Hadoop (HDFS)** : Système de fichiers distribué qui découpe et réplique les données sur plusieurs machines pour paralléliser les traitements.

**Data Lake** : Réservoir stockant toutes les données brutes, structurées ou non, sans transformation préalable.

**CHU** : Cloud Healthcare Unit, groupe hospitalier nécessitant une infrastructure décisionnelle pour exploiter ses données médicales.

**Data Warehouse** : Entrepôt de données structurées, nettoyées et historisées, conçu pour l'analyse et le reporting.

**Modèle logique** : Représentation détaillée des entités, attributs et relations avant l'implémentation physique.

**Données physiques** : Implémentation concrète du modèle dans le système de stockage (tables, partitions, formats).

**MapReduce** : Paradigme de traitement parallèle divisant les tâches en phase Map (distribution) et Reduce (agrégation).

**Cloudera** : Distribution commerciale d'Hadoop incluant outils de gestion, sécurité et interface d'administration.

**Hive** : Entrepôt de données sur Hadoop permettant d'interroger HDFS avec du SQL.

**Power BI** : Outil Microsoft de visualisation et d'analyse de données par tableaux de bord interactifs.

**Stockage distribué** : Répartition des données sur plusieurs nœuds pour améliorer performance, disponibilité et tolérance aux pannes.

---

## Ressources
# PARTIE 2 : RESSOURCES (organisées par thèmes) - VERSION SYNTHÉTIQUE

---

## A. FONDAMENTAUX BIG DATA

### Qu'est-ce que le Big Data ?

**Définition simple**
Ensemble de technologies pour gérer des volumes de données trop grands pour les systèmes traditionnels.

**Le vrai problème : le débit disque**
- Capacité stockage : x100 000 en 30 ans
- Débit lecture : x100 seulement
- Résultat : on peut stocker 1000 fois plus, mais il faut 1000 fois plus de temps pour lire
- Solution : plusieurs disques en parallèle = plusieurs machines en parallèle

**Les 3V du Big Data**

**Volume**
- Données massives (téraoctets à pétaoctets)
- CHU : années d'historique patients, imagerie médicale

**Vélocité** 
- Vitesse de génération et traitement
- CHU : batch quotidien (suffit) ou temps réel (admissions urgences)

**Variété**
- Formats hétérogènes
- CHU : PostgreSQL (structuré), CSV (semi-structuré), notes médicales (non structuré)

**À retenir** : Big Data = trop de données pour une seule machine → distribuer sur plusieurs machines qui travaillent en parallèle.

---

### Architecture Big Data : Lambda

**Principe**
Combiner traitement historique (lent mais complet) et temps réel (rapide mais partiel).

**Schéma simple**
```
Sources → Data Lake (stockage brut)
              ↓
        ┌─────┴─────┐
     Batch      Speed
   (historique) (temps réel)
        └─────┬─────┘
              ↓
        Data Warehouse
              ↓
          Power BI
```

**Batch Layer**
- Traite TOUT l'historique
- Quotidien (la nuit)
- Lent mais exhaustif

**Speed Layer** 
- Traite nouveaux flux
- Continu
- Rapide mais incomplet

**Pour le CHU**
- Batch obligatoire : calculs sur 2015-2024
- Speed optionnel : si besoin dashboards temps réel

**À retenir** : Lambda = batch (tout l'historique, lent) + speed (nouvelles données, rapide). CHU utilise principalement batch.

---

## B. STOCKAGE

### HDFS : Hadoop Distributed File System

**Principe de base**
Système de fichiers qui découpe les données sur plusieurs machines.

**Comment ça marche**
```
Fichier 1 Go
    ↓
Découpé en 8 blocs de 128 Mo
    ↓
Chaque bloc sur 3 machines différentes (réplication)
    ↓
Lecture parallèle : 8 machines lisent en même temps
```

**Avantages**
- Capacité illimitée (ajouter des machines)
- Haute disponibilité (si machine tombe, 2 autres copies)
- Lecture rapide (parallèle sur toutes les machines)

**Architecture**
- **NameNode** : chef, sait où sont les blocs
- **DataNodes** : stockent les blocs physiquement

**À retenir** : HDFS découpe gros fichiers en blocs, réplique 3 fois, distribue sur plein de machines. Permet de dépasser capacité d'une seule machine.

---

### Data Lake

**Définition**
Réservoir qui stocke TOUTES les données en format brut.

**Caractéristiques**
- Accepte tout format (CSV, JSON, images, vidéos)
- Aucune transformation à l'entrée
- Structure définie à la lecture (schema-on-read)
- Pas cher (stockage distribué)

**Organisation recommandée**
```
/raw/     → Bronze : données brutes intactes
/staging/ → Silver : données nettoyées  
/curated/ → Gold : données prêtes pour analyse
```

**Avantages**
- Flexibilité : stocke tout sans se poser de questions
- Archive complète : toujours possibilité de revenir en arrière
- Coût faible

**Risque : Data Swamp (marais)**
- Désordre si pas de gouvernance
- Données perdues, doublons
- Qualité variable

**Pour le CHU**
- /raw/ : CSV bruts, exports PostgreSQL bruts
- /staging/ : nettoyage, validation
- /curated/ : tables finales pour Power BI

**À retenir** : Data Lake = tout stocker en brut. Flexible mais risque de bordel sans organisation.

---

### Data Warehouse

**Définition**
Base de données structurée et nettoyée pour l'analyse.

**Caractéristiques**
- Schéma fixe défini à l'avance
- Données nettoyées et validées
- Modèle dimensionnel (étoile)
- Optimisé pour requêtes rapides

**Modèle en étoile**
```
         [dim_patient]
               |
[dim_temps]--[fait_sejours]--[dim_etablissement]
               |
         [dim_diagnostic]
```

**Tables de faits** : mesures numériques (durée séjour, coût, nombre)
**Tables de dimensions** : contexte (qui, quand, où, quoi)

**Avantages**
- Requêtes rapides (index, pré-agrégations)
- Qualité garantie (validation à l'entrée)
- Facile à utiliser (SQL standard)

**Inconvénients**
- Rigide (difficile de changer schéma)
- Coûteux (serveurs puissants)

**Pour le CHU**
- Tables Hive dans /curated/
- Modèle étoile avec fait_sejours au centre
- Power BI se connecte ici

**À retenir** : Data Warehouse = données structurées et propres, rapides à requêter. Complémentaire du Data Lake.

---

### Data Lake vs Data Warehouse

| Aspect | Data Lake | Data Warehouse |
|--------|-----------|----------------|
| **Données** | Brutes, tout format | Structurées, nettoyées |
| **Schéma** | À la lecture | À l'écriture |
| **Utilisateurs** | Data scientists | Analystes business |
| **Flexibilité** | Haute | Faible |
| **Performance** | Variable | Rapide |
| **Coût** | Faible | Élevé |

**Le CHU a besoin des DEUX**
- Lake (/raw/) : stocker tout, archive légale
- Warehouse (/curated/) : requêtes rapides Power BI

**À retenir** : Pas Lake OU Warehouse, mais Lake ET Warehouse. Complémentaires.

---

### Formats de fichiers

**CSV** : à éviter
- Texte non compressé
- Lent à lire
- Usage CHU : ingestion uniquement, convertir immédiatement

**Parquet** : le standard Big Data
- Format colonnaire binaire
- Compression excellente (80% d'économie espace)
- Lecture 10x plus rapide que CSV
- Usage CHU : partout sauf ingestion initiale

**Comparaison**
```
Fichier 10M lignes patients :
- CSV : 2,5 Go, lecture 45 sec
- Parquet : 350 Mo, lecture 3 sec
```

**À retenir** : Toujours convertir CSV → Parquet. Gain énorme espace et vitesse.

---

## C. TRAITEMENT

### ETL vs ELT

**ETL (traditionnel)**
Extract → Transform → Load
- Transformation sur serveur dédié
- Validé avant chargement
- Lent pour Big Data

**ELT (Big Data)**
Extract → Load → Transform
- Chargement brut dans Data Lake
- Transformation distribuée sur cluster
- Rapide, scalable

**Pour le CHU : ELT**
```
PostgreSQL → Sqoop → HDFS /raw/ (brut)
                          ↓
                     Hive/Spark transforme
                          ↓
                     /curated/ (propre)
```

**À retenir** : ELT charge brut puis transforme. Profite de puissance cluster.

---

### Batch vs Streaming

**Batch**
- Traite par lots périodiques (nuit, semaine)
- Tout l'historique recalculé
- Latence heures/jours

**Streaming**
- Traite flux continu en temps réel
- Seulement nouvelles données
- Latence secondes

**Pour le CHU**
- Batch suffit : calculs historiques 2015-2024
- Streaming optionnel : si alertes temps réel nécessaires

**À retenir** : Batch pour historiques, streaming pour temps réel. CHU commence par batch.

---

## D. OUTILS

### Hadoop

**Composants**
- **HDFS** : stockage distribué
- **YARN** : gestionnaire ressources (alloue CPU/RAM aux jobs)
- **MapReduce** : traitement distribué (ancien, remplacé par Spark)

**À retenir** : Hadoop = plateforme, pas un logiciel unique. HDFS + YARN + outils.

---

### Hive

**Principe**
SQL sur Hadoop. Traduit requêtes SQL en jobs distribués.

**Architecture**
```
Power BI (SQL)
    ↓
HiveServer2
    ↓
Metastore (catalogue tables)
    ↓
HDFS (données Parquet)
```

**Exemple**
```sql
SELECT service, COUNT(*) 
FROM sejours 
WHERE annee = 2020 
GROUP BY service;

→ Hive distribue sur cluster
→ Résultat en secondes même sur 100 Go
```

**Pour le CHU**
- Tables Hive = Data Warehouse
- Power BI se connecte via JDBC
- Analystes utilisent SQL standard

**À retenir** : Hive permet d'utiliser SQL sur Big Data. Transparent pour utilisateurs.

---

### Spark

**Principe**
Moteur de calcul ultra-rapide. Traite en mémoire (pas disque comme MapReduce).

**Avantages**
- 10x à 100x plus rapide que MapReduce
- API Python, Scala, SQL
- Batch et streaming

**Pour le CHU**
- Transformations lourdes (/raw/ → /curated/)
- Alternative à Hive pour jobs complexes

**À retenir** : Spark = MapReduce version moderne et rapide. Traite en RAM.

---

### Cloudera

**Principe**
Distribution Hadoop packagée avec interface de gestion.

**Contient**
- Hadoop, Hive, Spark pré-installés
- Cloudera Manager : interface web monitoring
- Sécurité intégrée (Kerberos, Ranger)

**Pour le CHU**
- Archie a installé Cloudera
- Tout est déjà packagé
- Interface pour surveiller cluster

**À retenir** : Cloudera = Hadoop + outils + interface. Facilite déploiement.

---

### Sqoop

**Principe**
Transfère données entre bases relationnelles et Hadoop.

**Usage CHU**
```bash
sqoop import \
  --connect jdbc:postgresql://chu/soins \
  --table consultations \
  --target-dir /raw/consultations \
  --num-mappers 8
```

- 8 lectures parallèles de PostgreSQL
- Import direct dans HDFS
- Conversion en Parquet possible

**À retenir** : Sqoop extrait données depuis PostgreSQL vers HDFS.

---

### Power BI

**Principe**
Outil de visualisation et tableaux de bord.

**Connexion CHU**
```
Power BI → JDBC → HiveServer2 → Tables Hive → HDFS
```

**Usage**
- Analystes créent dashboards interactifs
- SQL transparent (Power BI génère automatiquement)
- Répond aux 8 besoins utilisateurs CHU

**À retenir** : Power BI = interface pour utilisateurs finaux. Se connecte à Hive.

---

### Airflow (orchestration)

**Principe**
Planificateur de jobs. Automatise flux de travail.

**Exemple CHU**
```
DAG quotidien 02h00 :
1. Sqoop import PostgreSQL
2. Hive nettoyage
3. Hive transformation
4. Refresh Power BI
```

**À retenir** : Airflow planifie et enchaîne jobs automatiquement.

---

## E. SPÉCIFICITÉS SANTÉ

### HDS : Hébergement Données de Santé

**Obligations légales**
- Certification HDS obligatoire
- Chiffrement données
- Authentification forte (Kerberos)
- Audit tous les accès
- Conservation logs 7 ans

**Pour le CHU**
- Sécurité dès le début, pas après
- Cloudera a modules sécurité (Ranger)
- Données sensibles : anonymisation/pseudonymisation

**À retenir** : HDS = contraintes légales strictes. Sécurité non négociable pour données santé.

---

## F. ARCHITECTURE COMPLÈTE CHU

### Schéma global

```
┌─────────────────────────────────┐
│  SOURCES                         │
│  PostgreSQL, CSV, FTP            │
└─────────┬───────────────────────┘
          ↓
┌─────────────────────────────────┐
│  INGESTION (Sqoop, Flume)        │
└─────────┬───────────────────────┘
          ↓
┌─────────────────────────────────┐
│  DATA LAKE (HDFS)                │
│  /raw/ → /staging/ → /curated/   │
└─────────┬───────────────────────┘
          ↓
┌─────────────────────────────────┐
│  TRANSFORMATION (Hive/Spark)     │
│  Nettoyage, enrichissement       │
└─────────┬───────────────────────┘
          ↓
┌─────────────────────────────────┐
│  DATA WAREHOUSE (Tables Hive)    │
│  Modèle dimensionnel             │
└─────────┬───────────────────────┘
          ↓
┌─────────────────────────────────┐
│  VISUALISATION (Power BI)        │
└─────────────────────────────────┘
```

### Flux détaillé CHU

**1. Ingestion (nuit)**
- Sqoop : PostgreSQL → /raw/ (Parquet)
- Flume : CSV FTP → /raw/

**2. Transformation (Hive)**
- Nettoyage : /raw/ → /staging/ (supprimer NULL, doublons)
- Enrichissement : /staging/ → /curated/ (ajouter libellés, calculer agrégats)

**3. Data Warehouse**
- Tables Hive partitionnées par année/mois
- Modèle étoile : fait_sejours + dimensions

**4. Restitution**
- Power BI lit tables Hive
- 8 analyses utilisateurs disponibles

**Orchestration**
- Airflow planifie tout automatiquement chaque nuit

**Sécurité**
- Kerberos : authentification
- Ranger : droits d'accès
- Chiffrement : données au repos et transit

---

## G. POINTS CLÉS POUR LE PROJET

### Ce qu'Archie a fait (probablement)
- Installé Cloudera
- Créé architecture Lambda (schéma)
- Mis données dans "Mes documents"
- Environnement virtualisé avec outils

### Problèmes identifiés (prosit)
- Architecture "trop complexe"
- Difficile de faire lien avec implémentation
- Données "pas exploitables sous cette forme"
- "Performance intenable"

### Ce qu'il faut faire
1. **Auditer travail Archie**
   - Architecture claire ou confuse ?
   - Outils installés fonctionnels ?
   - Où sont les données vraiment ?

2. **Simplifier si nécessaire**
   - Éliminer complexité inutile
   - Documenter flux

3. **Organiser données**
   - Créer structure /raw/, /staging/, /curated/
   - Convertir CSV en Parquet

4. **Modéliser**
   - Schéma étoile pour Data Warehouse
   - Dimensions + faits pour 8 analyses

5. **Optimiser**
   - Partitionner tables par année/mois
   - Format Parquet partout

6. **Sécuriser**
   - HDS : chiffrement, audit
   - Pas stocker données sensibles non anonymisées

---

## SYNTHÈSE CONCEPTS

**Big Data** = volumes trop gros pour une machine → distribuer

**HDFS** = fichiers découpés sur plein de machines en parallèle

**Data Lake** = stockage brut de tout, flexible

**Data Warehouse** = données structurées propres, rapides

**ELT** = charger brut puis transformer (vs ETL transformer puis charger)

**Batch** = traitement périodique historique complet

**Hadoop** = plateforme Big Data (HDFS + YARN + outils)

**Hive** = SQL sur Hadoop

**Spark** = calcul ultra-rapide en mémoire

**Parquet** = format colonnaire compressé (80% gain espace, 10x vitesse)

**Cloudera** = Hadoop packagé avec interface

**Lambda** = batch (historique) + streaming (temps réel)

**HDS** = contraintes légales santé (chiffrement, audit)

---

**À retenir pour le CER** : Comprendre le flux complet sources → ingestion → Data Lake → transformation → Data Warehouse → visualisation. Tout le reste est détail d'implémentation.


# AUDIT DU TRAVAIL D'ARCHIE

## Ce qu'on voit dans son schéma

**Infrastructure mise en place**
- Cloudera installé
- HDFS pour le stockage
- Hive pour le SQL
- Power BI pour la visualisation
- Sources : PostgreSQL, CSV, Excel

**Architecture générale**
Sources → ETL → HDFS → Hive → Power BI

C'est cohérent sur le papier, ça suit la logique Big Data classique.

---

## Les problèmes remontés dans le prosit

**"Architecture plus complexe que prévu"**
- Le schéma est théorique, manque de détails pratiques
- On sait pas où vont les fichiers concrètement
- Trop conceptuel, pas assez opérationnel

**"Difficile de faire le lien avec l'implémentation"**
- Aucun chemin HDFS précisé (/raw/, /staging/, /curated/)
- Pas de noms de tables Hive
- Pas de scripts ETL visibles
- Le schéma dit "ETL" mais comment ? avec quoi ?

**"Données dans Mes documents pas exploitables sous cette forme"**
- Les données sont restées en CSV brut quelque part
- Probablement pas uploadées dans HDFS
- Pas de tables Hive créées dessus
- Donc impossible de les requêter

**"Performance intenable"**
- Si c'est du CSV non converti en Parquet = 10x plus lent
- Pas de partitionnement = scan complet à chaque requête
- Requêtes qui prennent plusieurs minutes au lieu de secondes

**"Données très personnelles"**
- Pas d'anonymisation visible
- Pas de sécurité mentionnée (Kerberos, Ranger)
- Risque HDS non traité

---

## Ce qui manque concrètement

**Documentation**
- Pas de doc des chemins HDFS
- Pas de liste des tables créées
- Pas de scripts de transformation
- Pas de procédure pour refaire

**Implémentation physique**
- Données probablement encore en local (pas dans HDFS)
- Tables Hive probablement pas créées
- Jobs ETL probablement pas codés
- Power BI probablement pas branché

**Optimisations**
- CSV alors que devrait être Parquet
- Pas de partition par année/mois
- Pas de stats sur les tables

**Sécurité**
- Rien sur l'anonymisation
- Rien sur le chiffrement
- Rien sur les droits d'accès
- HDS pas adressé

---

## Vérifications à faire rapidement

**Étape 1 : Vérifier que Cloudera tourne**
```bash
# Accéder à l'interface
http://localhost:7180

# Checker que HDFS, YARN, Hive sont en vert
```

**Étape 2 : Trouver les données**
```bash
# Elles sont où ?
ls ~/Documents/  # En local ?
hdfs dfs -ls /   # Dans HDFS ?

# Quelle taille ?
du -sh ~/Documents/*.csv
```

**Étape 3 : Vérifier tables Hive**
```bash
# Se connecter à Hive
beeline -u "jdbc:hive2://localhost:10000"

# Lister
SHOW DATABASES;
SHOW TABLES;

# Si vide = rien n'a été fait
```

**Étape 4 : Tester une requête**
```sql
SELECT COUNT(*) FROM sejours WHERE annee = 2020;

# Si erreur "table not found" = pas créée
# Si > 30 secondes = problème de performance
```

---

## Diagnostic probable

Archie a fait :
- Installation Cloudera : OK
- Schéma théorique : OK  
- Récupération données : OK (dans Mes documents)

Archie a PAS fait :
- Upload données dans HDFS
- Création tables Hive
- Scripts ETL
- Connexion Power BI
- Sécurisation

En gros : l'infra est là mais les données sont pas dedans.

---

## Ce qu'il faut faire pour finir

**Jour 1 : Mettre les données dans HDFS**
```bash
# Créer les dossiers
hdfs dfs -mkdir /chu/raw/
hdfs dfs -mkdir /chu/staging/
hdfs dfs -mkdir /chu/curated/

# Uploader les CSV
hdfs dfs -put sejours.csv /chu/raw/sejours/

# Créer tables Hive externes
CREATE EXTERNAL TABLE raw_sejours (...)
LOCATION '/chu/raw/sejours/';
```

**Jour 2-3 : Transformer et optimiser**
```sql
# Convertir en Parquet
CREATE TABLE staging_sejours
STORED AS PARQUET
AS SELECT * FROM raw_sejours;

# Partitionner
CREATE TABLE curated_sejours (...)
PARTITIONED BY (annee INT, mois INT)
STORED AS PARQUET;

# Peupler
INSERT INTO curated_sejours PARTITION (annee, mois)
SELECT *, YEAR(date), MONTH(date) FROM staging_sejours;
```

**Jour 4 : Modèle dimensionnel**
Créer les tables :
- fact_sejours
- dim_patient
- dim_etablissement  
- dim_temps
- dim_diagnostic

**Jour 5 : Power BI**
- Se connecter en JDBC sur Hive
- Faire les requêtes pour les 8 analyses
- Créer les dashboards

**Jour 6 : Sécurité HDS**
- Activer chiffrement HDFS
- Configurer Ranger pour les droits
- Anonymiser les données sensibles
- Activer les logs audit

---

## Conclusion

**Situation actuelle**
Archie a installé la plateforme mais pas fini le boulot. Les données sont là mais pas exploitables.

**Ce qu'il reste à faire**
Environ 6 jours de travail pour avoir un système fonctionnel.

**Risques**
- Si on corrige pas le format CSV = lenteur insupportable
- Si on sécurise pas = non conforme HDS
- Si on modélise pas = impossible de répondre aux 8 analyses demandées

**Recommandation**
Reprendre étape par étape en mode pragmatique :
1. Données dans HDFS
2. Tables Hive qui marchent
3. Conversion Parquet
4. Modèle dimensionnel
5. Power BI
6. Sécurité

Pas chercher la perfection, juste que ça marche et que ça respecte HDS.