# 📝 INSTRUCTION : Filtrer décès 2019 uniquement

## 🎯 Objectif

Modifier le Notebook 01 pour charger **uniquement les décès de 2019** au lieu des 25M de lignes.

---

## ✏️ MODIFICATION À FAIRE

### Notebook : `01_Extract_Bronze_SOURCES_DIRECTES.ipynb`

### Cellule à modifier : Cellule 11 (Export deces)

**Remplace** cette partie :

```python
# Lecture CSV COMPLET (sans filtrage année)
df_deces_full = spark.read \
    .option("header", "true") \
    .option("inferSchema", "true") \
    .option("mode", "PERMISSIVE") \
    .option("multiLine", "false") \
    .csv(f"{DATA_DIR}/DECES EN FRANCE/deces.csv")

# Repartitionner pour optimiser l'écriture
df_deces_full = df_deces_full.repartition(20)

row_count = df_deces_full.count()
```

**PAR** :

```python
# Lecture CSV avec filtrage 2019 uniquement
df_deces_raw = spark.read \
    .option("header", "true") \
    .option("inferSchema", "true") \
    .option("mode", "PERMISSIVE") \
    .option("multiLine", "false") \
    .csv(f"{DATA_DIR}/DECES EN FRANCE/deces.csv")

# FILTRAGE : Ne garder que 2019
print("🔍 Filtrage des décès 2019 uniquement...")
df_deces_full = df_deces_raw.filter(col("datdec").startswith("2019"))

row_count = df_deces_full.count()
print(f"📊 Total 2019: {row_count:,} lignes (filtré depuis 25M)")
```

---

## 📊 AVANT vs APRÈS

### AVANT
- **Lignes chargées** : 25,088,208 (toutes les années)
- **Temps** : ~178 secondes
- **Taille Bronze** : ~2.5 GB

### APRÈS
- **Lignes chargées** : ~600,000 (2019 uniquement)
- **Temps** : ~10-15 secondes
- **Taille Bronze** : ~60 MB

**Gain** : 97% de données en moins ! 🚀

---

## 🔍 VÉRIFICATION

Après modification, la sortie devrait ressembler à :

```
================================================================================
🔄 Extract CSV: deces (FILTRÉ 2019 UNIQUEMENT)
📁 Fichier: /home/jovyan/DATA_2024/DECES EN FRANCE/deces.csv
================================================================================
🔍 Filtrage des décès 2019 uniquement...
📊 Total 2019: 612,432 lignes (filtré depuis 25M)
✅ FILTRAGE 2019 appliqué
💾 Sauvegardé: /home/jovyan/data/bronze/csv/deces
⏱️  Temps: 12.34s
✅ deces 2019 OK (612,432 lignes)
```

---

## 💡 POURQUOI CE CHANGEMENT ?

### Justification métier
- **Satisfaction** : Données 2019 uniquement
- **Décès** : On aligne sur la même année de référence
- **Cohérence** : Toutes les analyses sur 2019

### Avantages techniques
- ✅ **Performance** : 98% de données en moins
- ✅ **Stockage** : 2.4 GB économisés
- ✅ **Traitement** : Pipeline 15x plus rapide
- ✅ **Coûts** : Moins de ressources Spark nécessaires

---

## 📝 CHANGEMENTS DOCUMENTAIRES

### Mettre à jour la description

**Cellule markdown** (début du notebook) :

Changer :
```markdown
- ✅ **Décès COMPLET** (25M lignes - SANS FILTRAGE)
```

En :
```markdown
- ✅ **Décès 2019** (~600K lignes - FILTRÉ)
```

---

## ✅ APRÈS MODIFICATION

### Actions à faire :

1. **Supprimer l'ancien Bronze** (optionnel mais recommandé) :
   ```bash
   docker exec chu_jupyter rm -rf /home/jovyan/data/bronze/csv/deces
   ```

2. **Relancer Notebook 01** :
   - Kernel → Restart Kernel
   - Run → Run All Cells

3. **Vérifier** :
   ```python
   df = spark.read.parquet("/home/jovyan/data/bronze/csv/deces")
   print(f"Décès en Bronze : {df.count():,}")
   df.select("datdec").show(5)
   ```

   Toutes les dates doivent commencer par "2019".

4. **Relancer Notebook 02** (Silver) et **Notebook 03** (Gold)
   - Les tables `fait_deces` seront plus petites
   - Le traitement sera beaucoup plus rapide

---

## �� IMPACT SUR LES NOTEBOOKS SUIVANTS

### Notebook 02 (Silver)
- ✅ Aucune modification nécessaire
- ✅ Le filtrage est déjà fait en amont

### Notebook 03 (Gold)
- ✅ Aucune modification nécessaire
- ✅ `fait_deces` sera créé avec ~600K lignes au lieu de 25M

### Notebook 06 (Export PostgreSQL)
- ✅ Export `fait_deces` sera 40x plus rapide (30 secondes au lieu de 10 minutes)

---

## 💪 ACTION IMMÉDIATE

**Tu peux faire ça maintenant** :

1. Ouvre Notebook 01
2. Modifie la cellule 11 avec le code ci-dessus
3. Kernel → Restart
4. Run All

**Temps total** : 5-10 minutes (au lieu de 3 heures avant)

**Puis** :
- Relance Notebooks 02, 03
- Le Notebook 06 tournera beaucoup plus vite

---

**C'est parti ! 🚀**
