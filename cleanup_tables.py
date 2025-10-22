#!/usr/bin/env python3
"""
Script de nettoyage du metastore Hive - CHU Data Lakehouse
Usage : Exécuter dans Jupyter ou en standalone
"""

from pyspark.sql import SparkSession

# Créer session Spark avec la config qui évite les conflits
spark = SparkSession.builder \
    .appName("CHU_Cleanup_Metastore") \
    .config("spark.sql.hive.convertMetastoreParquet", "false") \
    .enableHiveSupport() \
    .getOrCreate()

print("=" * 60)
print("🧹 NETTOYAGE HIVE METASTORE - CHU Data Lakehouse")
print("=" * 60)

# Liste des tables à nettoyer
tables = [
    "dim_temps",
    "dim_patient",
    "dim_diagnostic",
    "dim_professionnel",
    "dim_etablissement",
    "fait_consultation"
]

print("\n📋 Tables à nettoyer :\n")

# Afficher les tables existantes
try:
    existing_tables = spark.sql("SHOW TABLES").collect()
    if existing_tables:
        for row in existing_tables:
            print(f"  - {row.tableName}")
    else:
        print("  (Aucune table trouvée)")
except Exception as e:
    print(f"  ⚠️  Impossible de lister les tables : {e}")

print("\n🗑️  Suppression des tables...\n")

# Supprimer chaque table
for table in tables:
    try:
        spark.sql(f"DROP TABLE IF EXISTS {table}")
        print(f"  ✅ {table} - supprimée")
    except Exception as e:
        print(f"  ❌ {table} - erreur : {e}")

print("\n" + "=" * 60)
print("✅ NETTOYAGE TERMINÉ")
print("=" * 60)

# Vérifier qu'il ne reste plus de tables
print("\n📋 Tables restantes :\n")
try:
    remaining_tables = spark.sql("SHOW TABLES").collect()
    if remaining_tables:
        for row in remaining_tables:
            print(f"  - {row.tableName}")
    else:
        print("  ✅ Aucune table (metastore propre)")
except Exception as e:
    print(f"  ⚠️  {e}")

print("\n" + "=" * 60)
print("🎯 PROCHAINE ÉTAPE :")
print("   Exécuter Notebook 05_Setup_Superset.ipynb")
print("   pour recréer les tables avec le bon schéma")
print("=" * 60)

spark.stop()
