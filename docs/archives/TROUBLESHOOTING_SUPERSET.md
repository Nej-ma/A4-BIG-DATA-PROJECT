# 🔧 TROUBLESHOOTING: Superset + PostgreSQL

**Date**: 2025-10-23
**Problème résolu**: ✅ ERROR: Could not load database driver: PostgresEngineSpec

---

## ❌ Erreur Rencontrée

```
ERROR: Could not load database driver: PostgresEngineSpec
```

**Contexte**: Tentative de connexion Superset → PostgreSQL pour accéder au schema `gold`

---

## ✅ Solution Complète

### Étape 1: Installer le driver PostgreSQL dans Superset

```bash
# Installer psycopg2-binary (driver PostgreSQL pour Python)
docker exec --user root chu_superset pip install psycopg2-binary

# Attendre la fin de l'installation
# Output attendu: "Successfully installed psycopg2-binary-2.9.11"
```

### Étape 2: Redémarrer Superset

```bash
docker restart chu_superset

# Attendre 30 secondes que Superset redémarre
```

### Étape 3: Vérifier que Superset est accessible

```bash
# Ouvrir dans le navigateur
http://localhost:8088

# Login: admin / admin123
```

### Étape 4: Ajouter la connexion PostgreSQL

1. **Settings** → **Database Connections** → **+ DATABASE**

2. **Supported Databases**: Sélectionner **PostgreSQL**

3. **SQLAlchemy URI**:
   ```
   postgresql://admin:admin123@chu_postgres:5432/healthcare_data
   ```

4. **Display Name**: `CHU_Gold_PostgreSQL`

5. **ADVANCED** → **SQL Lab**:
   - ✅ Cocher "Expose database in SQL Lab"
   - ✅ Cocher "Allow this database to be explored"

6. **Test Connection** → Devrait afficher "Connection looks good!"

7. **CONNECT**

---

## 🔍 Problème Bonus: Table manquante

### Erreur dans Notebook 06

```
ERROR: relation "gold.fait_deces" does not exist
```

**Cause**: La cellule d'export pour `fait_deces` n'a pas été exécutée

### Solution

Dans **Notebook 06**, exécuter les cellules d'export manquantes:

```python
# Export fait_deces (si pas déjà fait)
print("📤 Export fait_deces (620K lignes, peut prendre 1-2 min)...")

export_to_postgres(
    parquet_path="/home/jovyan/data/gold/fait_deces",
    table_name="fait_deces"
)

print("✅ fait_deces exportée !")
```

### Vérifier les tables exportées

```bash
docker exec chu_postgres psql -U admin -d healthcare_data -c "
SELECT tablename
FROM pg_tables
WHERE schemaname = 'gold'
ORDER BY tablename;
"
```

**Résultat attendu** (9 tables):
```
dim_diagnostic
dim_etablissement
dim_patient
dim_professionnel
dim_temps
fait_consultation
fait_deces          ← Doit apparaître
fait_hospitalisation
fait_satisfaction
```

---

## 📋 Checklist Complète Superset

### ✅ Pré-requis

- [ ] Docker containers running: `docker ps`
  - `chu_superset` (port 8088)
  - `chu_postgres` (port 5432)

- [ ] Driver PostgreSQL installé:
  ```bash
  docker exec chu_superset pip show psycopg2-binary
  ```
  Si erreur → Réinstaller: `docker exec --user root chu_superset pip install psycopg2-binary`

- [ ] Tables Gold exportées vers PostgreSQL:
  ```bash
  docker exec chu_postgres psql -U admin -d healthcare_data -c "
  SELECT COUNT(*) FROM pg_tables WHERE schemaname = 'gold';
  "
  ```
  Résultat attendu: `9` tables

### ✅ Configuration Superset

1. [ ] Ouvrir http://localhost:8088
2. [ ] Login: `admin` / `admin123`
3. [ ] Settings → Database Connections
4. [ ] + DATABASE → PostgreSQL
5. [ ] URI: `postgresql://admin:admin123@chu_postgres:5432/healthcare_data`
6. [ ] Test Connection → "Connection looks good!"
7. [ ] Advanced → SQL Lab → Cocher les 2 options
8. [ ] CONNECT

### ✅ Utilisation

1. [ ] SQL Lab → SQL Editor
2. [ ] Database: CHU_Gold_PostgreSQL
3. [ ] Schema: **gold**
4. [ ] Voir les 9 tables disponibles
5. [ ] Tester une requête:
   ```sql
   SELECT COUNT(*) FROM gold.fait_consultation;
   ```

---

## 🚀 Requêtes de Test SQL Lab

### Test 1: Vérifier toutes les tables

```sql
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'gold'
ORDER BY tablename;
```

### Test 2: Consultations par année

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

### Test 3: Hospitalisations par durée

```sql
SELECT
    h.duree_sejour_jours,
    COUNT(*) as nb_hospitalisations
FROM gold.fait_hospitalisation h
GROUP BY h.duree_sejour_jours
ORDER BY h.duree_sejour_jours;
```

### Test 4: Décès par mois 2019

```sql
SELECT
    t.mois,
    COUNT(*) as nb_deces,
    ROUND(AVG(d.age_deces), 1) as age_moyen
FROM gold.fait_deces d
JOIN gold.dim_temps t ON d.id_temps = t.id_temps
GROUP BY t.mois
ORDER BY t.mois;
```

### Test 5: Top 10 diagnostics

```sql
SELECT
    diag.libelle,
    COUNT(*) as nb_consultations
FROM gold.fait_consultation c
JOIN gold.dim_diagnostic diag ON c.code_diag = diag.code_diag
GROUP BY diag.libelle
ORDER BY nb_consultations DESC
LIMIT 10;
```

---

## 🐛 Autres Erreurs Possibles

### Erreur 1: "Connection refused"

**Cause**: PostgreSQL container pas démarré

**Solution**:
```bash
docker ps | grep chu_postgres
# Si absent:
docker start chu_postgres
```

### Erreur 2: "Authentication failed"

**Cause**: Mauvais identifiants

**Solution**: Vérifier dans docker-compose.yml
```yaml
POSTGRES_USER: admin
POSTGRES_PASSWORD: admin123
```

### Erreur 3: "Schema gold does not exist"

**Cause**: Notebook 06 pas exécuté

**Solution**: Exécuter Notebook 06 pour créer le schema gold et exporter les tables

### Erreur 4: Container Superset crashé

**Cause**: Mémoire insuffisante ou erreur config

**Solution**:
```bash
# Voir les logs
docker logs chu_superset --tail 50

# Redémarrer
docker restart chu_superset

# Si ça ne marche pas, recréer
docker-compose up -d --force-recreate chu_superset
```

---

## 📚 Documentation Officielle

- **Superset**: https://superset.apache.org/docs/databases/postgresql
- **PostgreSQL**: https://www.postgresql.org/docs/
- **psycopg2**: https://www.psycopg.org/docs/

---

## ✅ Résumé: Solution Rapide

```bash
# 1. Installer driver PostgreSQL
docker exec --user root chu_superset pip install psycopg2-binary

# 2. Redémarrer Superset
docker restart chu_superset

# 3. Attendre 30 secondes puis ouvrir http://localhost:8088

# 4. Ajouter connexion:
# URI: postgresql://admin:admin123@chu_postgres:5432/healthcare_data

# 5. Sélectionner schema "gold" dans SQL Lab

# ✅ C'EST TOUT!
```

---

**🎉 Superset est maintenant connecté à ton Data Lakehouse Gold !**
