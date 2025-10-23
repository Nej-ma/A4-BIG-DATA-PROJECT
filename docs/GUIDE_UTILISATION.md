# 🚀 GUIDE D'UTILISATION - CHU Data Lakehouse

**Version**: 1.0
**Date**: Octobre 2025

---

## 📋 Table des Matières

1. [Démarrage Rapide](#-d%C3%A9marrage-rapide)
2. [Exécution des Notebooks](#-ex%C3%A9cution-des-notebooks)
3. [Configuration Superset](#-configuration-superset)
4. [Requêtes SQL Utiles](#-requ%C3%AAtes-sql-utiles)
5. [Commandes Docker](#-commandes-docker)
6. [Troubleshooting](#-troubleshooting)

---

## 🚀 Démarrage Rapide

### Pré-requis
- Docker Desktop installé et démarré
- 8GB RAM minimum alloués à Docker
- Ports disponibles: 8888 (Jupyter), 8088 (Superset), 5432 (PostgreSQL)

### Démarrer l'environnement

```bash
# Dans le dossier du projet
cd "c:\Users\littl\Desktop\Big DATA\projet_git"

# Démarrer tous les services
docker-compose up -d

# Vérifier que tout est démarré
docker ps
```

**Attendu**: 5 containers running
- `chu_jupyter` (port 8888)
- `chu_superset` (port 8088)
- `chu_postgres` (port 5432)
- `chu_spark_master` (port 7077)
- `chu_spark_worker`

---

## 📓 Exécution des Notebooks

### Accès Jupyter
**URL**: http://localhost:8888

**Ordre d'exécution** (IMPORTANT):

### 1. Notebook 01 - Bronze Layer (~2 min)
**Fichier**: `01_Extract_Bronze_SOURCES_DIRECTES.ipynb`

**Fonction**: Extraction des données brutes
- 13 tables PostgreSQL
- 4 fichiers CSV (dont décès filtrés 2019)

**Sortie**: `spark/data/bronze/`

---

### 2. Notebook 02 - Silver Layer (~3 min)
**Fichier**: `02_Transform_Silver_CLEANING.ipynb`

**Fonction**: Nettoyage + Pseudonymisation
- Hash SHA-256 pour nom/prénom/email
- Suppression données sensibles
- Formatage dates

**Sortie**: `spark/data/silver/`

---

### 3. Notebook 03 - Gold Layer (~3 min)
**Fichier**: `03_Transform_Gold_STAR_SCHEMA.ipynb`

**Fonction**: Création Star Schema
- 5 dimensions
- **4 tables de faits** (incluant `fait_hospitalisation`)

**Sortie**: `spark/data/gold/`

**Tables créées**:
```
Dimensions (5):
- dim_temps
- dim_patient
- dim_diagnostic
- dim_professionnel
- dim_etablissement

Faits (4):
- fait_consultation      (1,027,157 lignes)
- fait_hospitalisation   (82,216 lignes) ← NOUVEAU
- fait_deces            (620,625 lignes)
- fait_satisfaction     (8 lignes)
```

---

### 4. Notebook 06 - Export PostgreSQL (~3 min)
**Fichier**: `06_Export_Gold_to_PostgreSQL.ipynb`

**Fonction**: Export vers PostgreSQL pour Superset
- Création schema `gold`
- Export des 9 tables

**Vérification**:
```bash
docker exec chu_postgres psql -U admin -d healthcare_data -c "
SELECT tablename FROM pg_tables WHERE schemaname = 'gold' ORDER BY tablename;
"
```

---

## 🎨 Configuration Superset

### Première connexion

1. **Installer driver PostgreSQL** (une seule fois):
```bash
docker exec --user root chu_superset pip install psycopg2-binary
docker restart chu_superset
# Attendre 30 secondes
```

2. **Accéder à Superset**:
- URL: http://localhost:8088
- Login: `admin`
- Password: `admin123`

3. **Ajouter connexion PostgreSQL**:
- Settings → Database Connections → + DATABASE
- Type: **PostgreSQL**
- SQLAlchemy URI:
  ```
  postgresql://admin:admin123@chu_postgres:5432/healthcare_data
  ```
- Display Name: `CHU_Gold`
- Advanced → SQL Lab: ✅ Cocher les 2 options
- Test Connection → CONNECT

4. **Utiliser SQL Lab**:
- SQL Lab → SQL Editor
- Database: `CHU_Gold`
- Schema: **`gold`**
- Tu verras les 9 tables!

---

## 📊 Requêtes SQL Utiles

### Test de connexion
```sql
SELECT COUNT(*) FROM gold.fait_consultation;
-- Résultat: 1,027,157
```

### Consultations par année
```sql
SELECT
    t.annee,
    COUNT(*) as nb_consultations,
    COUNT(DISTINCT f.id_patient) as patients_uniques
FROM gold.fait_consultation f
JOIN gold.dim_temps t ON f.id_temps = t.id_temps
GROUP BY t.annee
ORDER BY t.annee;
```

### Hospitalisations: durée moyenne
```sql
SELECT
    EXTRACT(YEAR FROM h.date_entree) as annee,
    COUNT(*) as nb_hospitalisations,
    ROUND(AVG(h.duree_sejour_jours), 2) as duree_moyenne_jours,
    MIN(h.duree_sejour_jours) as min_jours,
    MAX(h.duree_sejour_jours) as max_jours
FROM gold.fait_hospitalisation h
GROUP BY EXTRACT(YEAR FROM h.date_entree)
ORDER BY annee;
```

### Top 10 diagnostics
```sql
SELECT
    d.libelle,
    d.categorie,
    COUNT(*) as nb_consultations
FROM gold.fait_consultation c
JOIN gold.dim_diagnostic d ON c.code_diag = d.code_diag
GROUP BY d.libelle, d.categorie
ORDER BY nb_consultations DESC
LIMIT 10;
```

### Décès 2019 par mois
```sql
SELECT
    t.mois,
    t.nom_mois,
    COUNT(*) as nb_deces,
    ROUND(AVG(d.age_deces), 1) as age_moyen
FROM gold.fait_deces d
JOIN gold.dim_temps t ON d.id_temps = t.id_temps
GROUP BY t.mois, t.nom_mois
ORDER BY t.mois;
```

---

## 🐳 Commandes Docker

### État des services
```bash
# Voir tous les containers
docker ps

# Voir les logs d'un service
docker logs chu_jupyter --tail 50
docker logs chu_superset --tail 50
docker logs chu_postgres --tail 50
```

### Redémarrer un service
```bash
docker restart chu_jupyter
docker restart chu_superset
docker restart chu_postgres
```

### Arrêter/Démarrer tout
```bash
# Arrêter
docker-compose down

# Démarrer
docker-compose up -d
```

### Nettoyer les données (recommencer from scratch)
```bash
# ⚠️ ATTENTION: Supprime toutes les données!
docker exec chu_jupyter rm -rf /home/jovyan/data/bronze
docker exec chu_jupyter rm -rf /home/jovyan/data/silver
docker exec chu_jupyter rm -rf /home/jovyan/data/gold

# Supprimer schema gold PostgreSQL
docker exec chu_postgres psql -U admin -d healthcare_data -c "DROP SCHEMA IF EXISTS gold CASCADE;"

# Puis relancer notebooks 01 → 02 → 03 → 06
```

---

## 🔧 Troubleshooting

### Container pas démarré
```bash
docker start chu_jupyter
docker start chu_superset
docker start chu_postgres
```

### Port déjà utilisé
```bash
# Trouver le process
netstat -ano | findstr :8888

# Ou changer le port dans docker-compose.yml
```

### Erreur "Could not load database driver: PostgresEngineSpec"
```bash
# Réinstaller driver
docker exec --user root chu_superset pip install psycopg2-binary
docker restart chu_superset
```

### Table manquante dans PostgreSQL
```bash
# Vérifier tables existantes
docker exec chu_postgres psql -U admin -d healthcare_data -c "\dt gold.*"

# Re-exécuter Notebook 06 si manquante
```

### Notebook Jupyter ne se connecte pas
```bash
# Redémarrer
docker restart chu_jupyter

# Voir le token
docker logs chu_jupyter 2>&1 | grep token
```

### Pour plus de solutions
Voir **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)**

---

## 📈 Métriques du Projet

### Volumétrie
| Layer | Tables | Lignes | Temps Traitement |
|-------|--------|--------|------------------|
| Bronze | 17 | ~4M | ~2 min |
| Silver | 13 | ~3.5M | ~3 min |
| Gold | 9 | ~2.9M | ~3 min |
| PostgreSQL | 9 | ~2.9M | ~3 min |

### Tables de Faits
| Fait | Lignes | Période | Source |
|------|--------|---------|--------|
| fait_consultation | 1,027,157 | 2015-2023 | Consultation |
| fait_hospitalisation | 82,216 | 2013-2025 | AAAA + date |
| fait_deces | 620,625 | 2019 | CSV filtré |
| fait_satisfaction | 8 | 2019 | CSV |

---

## ✅ Checklist Livrable 2

- [ ] Docker compose fonctionne
- [ ] Notebooks 01→02→03→06 exécutés sans erreur
- [ ] 9 tables dans PostgreSQL schema gold
- [ ] Superset connecté et fonctionnel
- [ ] Au moins 1 dashboard créé
- [ ] Documentation complète
- [ ] Screenshots dashboards
- [ ] Tests requêtes SQL validés

---

**🎉 Guide Complet - Bonne chance pour votre Livrable 2 !**
