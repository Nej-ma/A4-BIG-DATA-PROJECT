# 🔧 FIX MINIO - Volume Partagé Avec Jupyter

## ❌ PROBLÈME IDENTIFIÉ

**Symptôme** : Les notebooks 1-3 s'exécutent avec succès (2.8M+ lignes dans Gold), mais MinIO est vide.

**Cause racine** :
```yaml
# AVANT (docker-compose.yml)
minio:
  volumes:
    - minio_data:/data  # ← Volume Docker isolé

jupyter:
  volumes:
    - ./spark/data:/home/jovyan/data  # ← Répertoire local différent
```

**Résultat** :
- Jupyter écrit dans `./spark/data/` sur le disque local
- MinIO lit depuis `minio_data` (volume Docker isolé)
- Aucune donnée visible dans MinIO !

---

## ✅ SOLUTION APPLIQUÉE

**Modification** : Changement du volume MinIO pour partager le même répertoire que Jupyter.

```yaml
# APRÈS (docker-compose.yml)
minio:
  volumes:
    - ./spark/data:/data  # ✅ FIXÉ : Partage le même répertoire que Jupyter

jupyter:
  volumes:
    - ./spark/data:/home/jovyan/data  # ← Même répertoire
```

**Résultat attendu** :
- Jupyter écrit dans `/home/jovyan/data/` → `./spark/data/` (hôte)
- MinIO lit depuis `/data/` → `./spark/data/` (hôte)
- **Les données sont maintenant partagées !** 🎉

---

## 🚀 ÉTAPES POUR APPLIQUER LE FIX

### 1. Redémarrer MinIO avec la nouvelle configuration

```bash
# Arrêter MinIO
docker compose stop minio

# Supprimer le container MinIO (pas de perte de données)
docker compose rm -f minio

# Relancer MinIO avec le nouveau volume
docker compose up -d minio
```

### 2. Vérifier que MinIO a bien démarré

```bash
# Vérifier le statut
docker compose ps minio

# Vérifier les logs
docker logs chu_minio
```

Vous devriez voir :
```
API: http://172.x.x.x:9000
Console: http://172.x.x.x:9001

Documentation: https://min.io/docs/minio/linux/index.html
```

### 3. Recréer les buckets MinIO

Le container `minio_setup` doit recréer les buckets automatiquement :

```bash
# Relancer le setup
docker compose up -d minio_setup

# Vérifier les logs
docker logs chu_minio_setup
```

Vous devriez voir :
```
✅ Buckets Delta Lake créés avec succès!
```

### 4. Vérifier les données dans MinIO Console

1. Ouvrir MinIO Console : **http://localhost:9001**
2. Login : `minioadmin` / `minioadmin123`
3. Cliquer sur **"Buckets"**
4. Vous devriez maintenant voir :
   - **Bucket `lakehouse`** avec les dossiers suivants :
     - `bronze/` → Données brutes (13 tables PostgreSQL + 3 CSV)
     - `silver/` → Données nettoyées et anonymisées (12 tables)
     - `gold/` → Star Schema (5 dimensions + 3 faits)

---

## 📊 VÉRIFICATION DES DONNÉES

### Dans MinIO Console (http://localhost:9001)

**Bronze layer** :
```
lakehouse/
  └── bronze/
      ├── postgres/
      │   ├── Patient/
      │   ├── Consultation/
      │   ├── Diagnostic/
      │   └── ... (10 autres tables)
      └── csv/
          ├── etablissement_sante/
          ├── satisfaction_2019/
          └── deces_2019/
```

**Silver layer** :
```
lakehouse/
  └── silver/
      ├── patient/
      ├── consultation/
      ├── etablissement/
      ├── satisfaction/
      ├── deces/
      └── ... (7 tables de référence)
```

**Gold layer** :
```
lakehouse/
  └── gold/
      ├── dim_temps/
      ├── dim_patient/
      ├── dim_diagnostic/
      ├── dim_professionnel/
      ├── dim_etablissement/
      ├── fait_consultation/
      │   ├── annee=2020/
      │   │   ├── mois=01/
      │   │   ├── mois=02/
      │   │   └── ...
      │   └── annee=2021/
      ├── fait_deces/
      │   └── annee=2019/
      │       ├── mois=01/
      │       └── ...
      └── fait_satisfaction/
          └── annee=2019/
```

---

## 🔍 DIAGNOSTIC SI TOUJOURS VIDE

### Vérifier que les données existent localement

```bash
# Lister le contenu de ./spark/data/
ls ./spark/data/

# Vous devriez voir les dossiers : bronze/, silver/, gold/
```

Si les dossiers existent :

```bash
# Vérifier Bronze
ls ./spark/data/bronze/

# Vérifier Silver
ls ./spark/data/silver/

# Vérifier Gold
ls ./spark/data/gold/
```

### Vérifier le montage de MinIO

```bash
# Inspecter le container MinIO
docker inspect chu_minio | grep -A 10 "Mounts"
```

Vous devriez voir :
```json
"Mounts": [
    {
        "Type": "bind",
        "Source": "C:\\Users\\littl\\Desktop\\Big DATA\\projet_git\\spark\\data",
        "Destination": "/data",
        ...
    }
]
```

### Forcer MinIO à réindexer

Si les données existent localement mais ne sont pas visibles dans MinIO :

```bash
# Redémarrer MinIO
docker compose restart minio

# Attendre 10 secondes
# Puis rafraîchir la page MinIO Console
```

---

## ⚠️ IMPORTANT

**Les notebooks n'ont PAS besoin d'être modifiés !**

Comme vous l'avez dit : *"Sinon les scripts notebook fonctionnent nickels donc ça pas besoin de toucher"*

✅ Les notebooks écrivent déjà dans `/home/jovyan/data/`
✅ Ce changement rend juste ces données visibles dans MinIO
✅ Aucune modification de code nécessaire

---

## 📝 RÉSUMÉ

| Avant | Après |
|-------|-------|
| Jupyter → `./spark/data/` ✅ | Jupyter → `./spark/data/` ✅ |
| MinIO → `minio_data` (isolé) ❌ | MinIO → `./spark/data/` ✅ |
| **Résultat** : MinIO vide | **Résultat** : MinIO montre les données |

---

**Exécutez les commandes de la section "ÉTAPES POUR APPLIQUER LE FIX" et vos données apparaîtront dans MinIO !** 🎉
