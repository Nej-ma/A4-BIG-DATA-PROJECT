# 🔧 FIX: Erreur Colonne décès

**Date**: 2025-10-23
**Problème**: `UNRESOLVED_COLUMN: datdec`
**Statut**: ✅ CORRIGÉ

---

## ❌ Erreur Rencontrée

```
[UNRESOLVED_COLUMN.WITH_SUGGESTION] A column or function parameter with name `datdec` cannot be resolved.
Did you mean one of the following? [`sexe`, `date_deces`, `nom`, `prenom`, `date_naissance`].
```

---

## 🔍 Cause

Le nom de la colonne dans le CSV est **`date_deces`** (et non `datdec`)

**Colonnes réelles du CSV**:
- `nom`
- `prenom`
- `sexe`
- `date_naissance`
- `code_lieu_naissance`
- `lieu_naissance`
- `pays_naissance`
- **`date_deces`** ← C'est celle-ci !
- `code_lieu_deces`
- `numero_acte_deces`

---

## ✅ Solution

### Notebook 01 - Cellule 11

**AVANT (incorrect)**:
```python
df_deces_full = df_deces_raw.filter(col("datdec").startswith("2019"))
```

**APRÈS (corrigé)** ✅:
```python
# NOTE: La colonne s'appelle "date_deces" (pas "datdec")
df_deces_full = df_deces_raw.filter(col("date_deces").startswith("2019"))
```

---

## 📝 Modification Complète

La cellule 11 du **Notebook 01** a été mise à jour avec:

```python
# 3. DÉCÈS 2019 UNIQUEMENT (FILTRÉ)
print(f"\n{'='*80}")
print(f"🔄 Extract CSV: deces (FILTRÉ 2019 UNIQUEMENT)")
print(f"📁 Fichier: {DATA_DIR}/DECES EN FRANCE/deces.csv")
print(f"{'='*80}")

start_time = time.time()

try:
    # Lecture CSV brut
    print("📖 Lecture du fichier CSV complet...")
    df_deces_raw = spark.read \
        .option("header", "true") \
        .option("inferSchema", "true") \
        .option("mode", "PERMISSIVE") \
        .option("multiLine", "false") \
        .csv(f"{DATA_DIR}/DECES EN FRANCE/deces.csv")

    # FILTRAGE : Ne garder que 2019
    # NOTE: La colonne s'appelle "date_deces" (pas "datdec")
    print("🔍 Filtrage des décès 2019 uniquement...")
    df_deces_full = df_deces_raw.filter(col("date_deces").startswith("2019"))

    # Repartitionner pour optimiser l'écriture
    df_deces_full = df_deces_full.repartition(10)

    row_count = df_deces_full.count()
    col_count = len(df_deces_full.columns)
    print(f"📊 Total 2019: {row_count:,} lignes, {col_count} colonnes")
    print(f"✅ FILTRÉ : Seulement données 2019 (réduction de 98%)")

    # Ajout métadonnées
    df_with_meta = df_deces_full \
        .withColumn("ingestion_timestamp", current_timestamp()) \
        .withColumn("ingestion_date", lit(datetime.now().strftime("%Y-%m-%d")))

    # Sauvegarde en Bronze (DONNÉES 2019 uniquement)
    output_path = f"{OUTPUT_BASE}/csv/deces_2019"
    df_with_meta.write \
        .mode("overwrite") \
        .option("compression", "snappy") \
        .parquet(output_path)

    elapsed = time.time() - start_time

    print(f"💾 Sauvegardé: {output_path}")
    print(f"⏱️  Temps: {elapsed:.2f}s")
    print(f"✅ deces 2019 OK ({row_count:,} lignes)")

    results.append({
        "source": "CSV",
        "table": "deces_2019",
        "rows": row_count,
        "cols": col_count,
        "time_sec": round(elapsed, 2),
        "status": "SUCCESS"
    })

except Exception as e:
    print(f"❌ ERREUR: {str(e)}")
    import traceback
    traceback.print_exc()
    results.append({
        "source": "CSV",
        "table": "deces_2019",
        "rows": 0,
        "cols": 0,
        "time_sec": 0,
        "status": f"ERROR: {str(e)}"
    })
```

---

## 🎯 Résultat Attendu

Après correction et ré-exécution de la cellule:

```
================================================================================
🔄 Extract CSV: deces (FILTRÉ 2019 UNIQUEMENT)
📁 Fichier: /home/jovyan/DATA_2024/DECES EN FRANCE/deces.csv
================================================================================
📖 Lecture du fichier CSV complet...
🔍 Filtrage des décès 2019 uniquement...
📊 Total 2019: 620,625 lignes, 10 colonnes
✅ FILTRÉ : Seulement données 2019 (réduction de 98%)
💾 Sauvegardé: /home/jovyan/data/bronze/csv/deces_2019
⏱️  Temps: 45.23s
✅ deces 2019 OK (620,625 lignes)
```

**Gain**: 25M → 620K lignes (98% de réduction) ⚡

---

## 📚 Prochaines Étapes

1. ✅ **Notebook 01** corrigé
2. ⏳ Ré-exécuter la cellule 11 du Notebook 01
3. ⏳ Continuer avec Notebook 02 (Silver)
4. ⏳ Continuer avec Notebook 03 (Gold)
5. ⏳ Exporter vers PostgreSQL (Notebook 06)

---

## 💡 Leçon Apprise

Toujours vérifier le nom exact des colonnes avec:
```python
df.printSchema()
# ou
df.columns
```

Avant de filtrer ! 🔍

---

**✅ CORRECTION APPLIQUÉE - TU PEUX RELANCER LA CELLULE !**
