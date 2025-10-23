# 🚀 GUIDE D'UTILISATION RAPIDE

**Pour**: Nejma MOUALHI | Brieuc OLIVIERI | Nicolas TAING
**Projet**: CHU Data Lakehouse - Livrable 2
**Date**: 2025-10-23

---

## 📋 ÉTAPES RAPIDES

### 1️⃣ Vérifier que Docker tourne

```bash
docker ps
```

**Attendu**: 5 containers running
- chu_postgres
- chu_spark_master
- chu_spark_worker
- chu_jupyter
- chu_superset

Si manquant:
```bash
docker-compose up -d
```

---

### 2️⃣ Ouvrir Jupyter

**URL**: http://localhost:8888

**Token**: Regarder dans les logs si demandé:
```bash
docker logs chu_jupyter 2>&1 | grep token
```

**Notebooks à exécuter** (dans l'ordre):
1. `01_Extract_Bronze_SOURCES_DIRECTES.ipynb` (~2 min)
2. `02_Transform_Silver_CLEANING.ipynb` (~3 min)
3. `03_Transform_Gold_STAR_SCHEMA.ipynb` (~2-3 min)
4. `06_Export_Gold_to_PostgreSQL.ipynb` (~3 min)

**⏱️ Temps total**: ~10-12 minutes

---

### 3️⃣ Vérifier PostgreSQL

```bash
# Voir les tables Gold
docker exec chu_postgres psql -U admin -d healthcare_data -c "
SELECT tablename,
       pg_size_pretty(pg_total_relation_size('gold.'||tablename)) as size
FROM pg_tables
WHERE schemaname = 'gold'
ORDER BY tablename;
"
```

**Attendu**: 9 tables
- 5 dimensions (dim_*)
- 4 faits (fait_*)

---

### 4️⃣ Configurer Superset (1ère fois uniquement)

```bash
# Installer driver PostgreSQL
docker exec --user root chu_superset pip install psycopg2-binary

# Redémarrer
docker restart chu_superset

# Attendre 30 secondes
```

**URL**: http://localhost:8088

**Login**: `admin` / `admin123`

**Ajouter connexion**:
1. Settings → Database Connections → + DATABASE
2. PostgreSQL
3. URI: `postgresql://admin:admin123@chu_postgres:5432/healthcare_data`
4. Display Name: `CHU_Gold`
5. Advanced → SQL Lab → ✅ Cocher les 2 options
6. Test Connection → CONNECT

---

### 5️⃣ Utiliser SQL Lab

1. SQL Lab → SQL Editor
2. Database: CHU_Gold
3. Schema: **gold**
4. Voir les 9 tables

**Requête test**:
```sql
SELECT COUNT(*) FROM gold.fait_consultation;
-- Résultat attendu: 1,027,157
```

---

## 📊 REQUÊTES UTILES

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

### Hospitalisations: durée moyenne par année

```sql
SELECT
    EXTRACT(YEAR FROM h.date_entree) as annee,
    COUNT(*) as nb_hospitalisations,
    ROUND(AVG(h.duree_sejour_jours), 2) as duree_moyenne_jours
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

### Décès par mois 2019

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

## 🔧 COMMANDES UTILES

### Voir l'état des containers

```bash
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

### Redémarrer un service

```bash
docker restart chu_jupyter
docker restart chu_superset
docker restart chu_postgres
```

### Voir les logs

```bash
docker logs chu_jupyter --tail 50
docker logs chu_superset --tail 50
docker logs chu_postgres --tail 50
```

### Nettoyer les données (recommencer from scratch)

```bash
# ⚠️  ATTENTION: Supprime toutes les données!
docker exec chu_jupyter rm -rf /home/jovyan/data/bronze
docker exec chu_jupyter rm -rf /home/jovyan/data/silver
docker exec chu_jupyter rm -rf /home/jovyan/data/gold

# Supprimer schema gold dans PostgreSQL
docker exec chu_postgres psql -U admin -d healthcare_data -c "DROP SCHEMA IF EXISTS gold CASCADE;"

# Relancer les notebooks 01 → 02 → 03 → 06
```

### Arrêter tout

```bash
docker-compose down
```

### Démarrer tout

```bash
docker-compose up -d
```

---

## 📂 STRUCTURE DES FICHIERS

```
projet_git/
├── docker-compose.yml           # Configuration Docker
├── jupyter/
│   └── notebooks/
│       ├── 01_Extract_Bronze_SOURCES_DIRECTES.ipynb    ← Bronze
│       ├── 02_Transform_Silver_CLEANING.ipynb          ← Silver
│       ├── 03_Transform_Gold_STAR_SCHEMA.ipynb         ← Gold (4 faits)
│       └── 06_Export_Gold_to_PostgreSQL.ipynb          ← PostgreSQL
├── spark/
│   └── data/
│       ├── bronze/   # Données brutes (Parquet)
│       ├── silver/   # Données nettoyées (Parquet)
│       └── gold/     # Star Schema (Parquet)
└── docs/
    ├── MISSION_ACCOMPLIE.md                   # Résumé complet
    ├── DECOUVERTE_FAIT_HOSPITALISATION.md     # Analyse hospitalisation
    ├── TROUBLESHOOTING_SUPERSET.md            # Résolution problèmes
    └── GUIDE_UTILISATION_RAPIDE.md            # Ce fichier
```

---

## 🎯 MÉTRIQUES CLÉS

### Volumétrie

| Layer | Tables | Lignes Total | Format |
|-------|--------|--------------|--------|
| Bronze | 17 | ~4M | Parquet |
| Silver | 13 | ~3.5M | Parquet |
| Gold | 9 | ~2.9M | Parquet |
| PostgreSQL | 9 | ~2.9M | SQL |

### Tables de Faits (Livrable 1)

| Fait | Lignes | Période | Partitionnement |
|------|--------|---------|-----------------|
| fait_consultation | 1,027,157 | 2015-2023 | année/mois |
| fait_hospitalisation | 82,216 | 2013-2025 | année/mois |
| fait_deces | 620,625 | 2019 | année/mois |
| fait_satisfaction | 8 | 2019 | année |

---

## 🐛 PROBLÈMES FRÉQUENTS

### "Container not found"

```bash
docker-compose up -d
```

### "Port already in use"

```bash
# Trouver le process
netstat -ano | findstr :8888
netstat -ano | findstr :8088

# Tuer le process ou changer le port dans docker-compose.yml
```

### "Out of memory"

```bash
# Augmenter la mémoire Docker Desktop
# Settings → Resources → Memory → 8GB minimum
```

### "Permission denied"

```bash
# Ajouter --user root
docker exec --user root chu_jupyter chmod -R 777 /home/jovyan/data
```

### "Table not found in Superset"

```bash
# Vérifier que la table existe
docker exec chu_postgres psql -U admin -d healthcare_data -c "\dt gold.*"

# Re-exécuter Notebook 06 si manquante
```

---

## 📞 AIDE RAPIDE

### Fichiers de documentation

- **[MISSION_ACCOMPLIE.md](MISSION_ACCOMPLIE.md)** - Résumé complet du projet
- **[DECOUVERTE_FAIT_HOSPITALISATION.md](DECOUVERTE_FAIT_HOSPITALISATION.md)** - Comment on a trouvé les hospitalisations
- **[TROUBLESHOOTING_SUPERSET.md](TROUBLESHOOTING_SUPERSET.md)** - Résolution erreurs Superset
- **[RECAP_DECOUVERTES_ACTIONS.md](RECAP_DECOUVERTES_ACTIONS.md)** - Actions réalisées

### Commande "tout vérifier"

```bash
# Vérifier que tout fonctionne
echo "=== DOCKER ==="
docker ps | grep chu_

echo ""
echo "=== JUPYTER ==="
curl -s http://localhost:8888 > /dev/null && echo "✅ Jupyter OK" || echo "❌ Jupyter KO"

echo ""
echo "=== SUPERSET ==="
curl -s http://localhost:8088 > /dev/null && echo "✅ Superset OK" || echo "❌ Superset KO"

echo ""
echo "=== POSTGRESQL ==="
docker exec chu_postgres psql -U admin -d healthcare_data -c "SELECT COUNT(*) FROM pg_tables WHERE schemaname = 'gold';"

echo ""
echo "=== GOLD TABLES ==="
docker exec chu_postgres psql -U admin -d healthcare_data -c "SELECT tablename FROM pg_tables WHERE schemaname = 'gold' ORDER BY tablename;"
```

---

## ✅ CHECKLIST FINALE

Avant de rendre le Livrable 2:

- [ ] Docker compose fonctionne
- [ ] Notebooks 01 → 02 → 03 → 06 exécutés sans erreur
- [ ] 9 tables dans PostgreSQL gold schema
- [ ] Superset connecté à PostgreSQL
- [ ] Au moins 1 dashboard créé dans Superset
- [ ] Documentation complète (ce fichier + MISSION_ACCOMPLIE.md)
- [ ] Screenshots des dashboards
- [ ] Tests de requêtes SQL validés

---

**🎉 BON COURAGE POUR VOTRE LIVRABLE 2 ! 🚀**
