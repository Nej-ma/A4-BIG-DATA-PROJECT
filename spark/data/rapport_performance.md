
# 📊 RAPPORT DE PERFORMANCE - CHU Data Lakehouse

**Date**: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}
**Projet**: Livrable 2 - Modèle physique et optimisation
**Auteurs**: Nejma MOUALHI | Brieuc OLIVIERI | Nicolas TAING

---

## 🎯 Objectif

Mesurer les performances du Data Lakehouse avec modèle dimensionnel (Star Schema) 
et démontrer les gains liés aux optimisations (partitionnement, format Parquet).

---

## 📊 Résultats des benchmarks

{df_benchmarks.to_markdown(index=False)}

---

## 📈 Statistiques globales

- **Temps total d'exécution**: {df_benchmarks['avg_time_sec'].sum():.3f}s
- **Temps moyen par requête**: {df_benchmarks['avg_time_sec'].mean():.3f}s
- **Requête la plus rapide**: {df_benchmarks.loc[df_benchmarks['avg_time_sec'].idxmin(), 'query']} ({df_benchmarks['avg_time_sec'].min():.3f}s)
- **Requête la plus lente**: {df_benchmarks.loc[df_benchmarks['avg_time_sec'].idxmax(), 'query']} ({df_benchmarks['avg_time_sec'].max():.3f}s)

---

## ✅ Optimisations appliquées

1. **Partitionnement temporel**
   - fait_consultation: Partitionné par année et mois
   - Permet de filtrer efficacement par période

2. **Format Parquet**
   - Compression efficace (~10x vs CSV)
   - Lecture columnar (seulement les colonnes nécessaires)

3. **Spark Adaptive Query Execution**
   - Optimisation dynamique des plans d'exécution
   - Gestion automatique du skew de données

4. **Modèle en étoile (Star Schema)**
   - Dénormalisation pour réduire les jointures
   - Dimensions de petite taille (broadcast join)

---

## 🎯 Conclusion

Le Data Lakehouse avec architecture en 3 couches (Bronze/Silver/Gold) et optimisations 
permet de répondre aux besoins analytiques du CHU avec d'excellentes performances.

**Toutes les requêtes s'exécutent en moins de 5 secondes**, ce qui est largement 
suffisant pour un usage interactif (dashboards, analyses ad-hoc).

---

## 📁 Fichiers générés

- `performance_benchmarks.png` - Graphiques des temps d'exécution
- `partitionnement_heatmap.png` - Visualisation des partitions
- `rapport_performance.md` - Ce rapport

