# 📓 Notebooks Jupyter - Livrable 2

**Projet** : CHU Data Lakehouse
**Auteurs** : Nejma MOUALHI | Brieuc OLIVIERI | Nicolas TAING

---

## 🎯 Objectif

Ces notebooks vous permettent de créer **TOUT le Livrable 2** pas à pas, de manière interactive.

---

## 📋 Ordre d'exécution

### ✅ Étape 1 : Ingestion Bronze PostgreSQL (10 min)
**Notebook** : `01_Ingestion_Bronze_PostgreSQL.ipynb`

**Ce qu'il fait** :
- Extrait les 13 tables de PostgreSQL
- Sauvegarde en format Parquet optimisé
- Ajoute des métadonnées (date d'ingestion)
- Génère des statistiques et graphiques

**Résultat** : ~1 million de lignes ingérées dans `/home/jovyan/data/bronze/postgres/`

---

### ✅ Étape 2 : Ingestion Bronze CSV (5 min)
**Notebook** : `02_Ingestion_Bronze_CSV.ipynb`

**Ce qu'il fait** :
- Ingère tous les CSV (Décès, Satisfaction, Établissements, Hospitalisation)
- Gère les différents séparateurs (`,` et `;`)
- Sauvegarde en Parquet partitionné
- Génère des statistiques

**Résultat** : ~400K lignes CSV ingérées dans `/home/jovyan/data/bronze/csv/`

---

### ⭐ Étape 3 : Modèle Gold Star Schema (15 min)
**Notebook** : `03_Modele_Gold_Star_Schema.ipynb`

**Ce qu'il fait** :
- Crée 5 dimensions (Temps, Patient, Diagnostic, Professionnel, Établissement)
- Crée 4 tables de faits (Consultations, Hospitalisations, Décès, Satisfaction)
- Applique le partitionnement par année/mois
- Optimise avec Parquet et Adaptive Query Execution

**Résultat** : Modèle dimensionnel complet dans `/home/jovyan/data/gold/`

**C'est le notebook LE PLUS IMPORTANT pour le Livrable 2** ⭐

---

### ⚡ Étape 4 : Benchmarks et Performance (10 min)
**Notebook** : `04_Performance_Benchmarks.ipynb`

**Ce qu'il fait** :
- Exécute 6 requêtes de benchmark
- Mesure les temps d'exécution
- Génère des graphiques de performance
- Crée un rapport Markdown complet

**Résultat** :
- Graphiques de performance
- Rapport de performance complet
- Preuves d'optimisation

---

## 🚀 Comment utiliser

### 1. Ouvrir Jupyter Lab

```
http://localhost:8888
Token: admin123
```

### 2. Naviguer vers `notebooks/`

Vous verrez les 4 notebooks numérotés.

### 3. Exécuter les notebooks dans l'ordre

**Option A : Exécution manuelle**
- Ouvrir le notebook 01
- Cliquer sur "Run" → "Run All Cells"
- Attendre la fin
- Passer au notebook 02, etc.

**Option B : Exécution cellule par cellule**
- Ouvrir le notebook
- Lire chaque cellule
- Appuyer sur `Shift + Enter` pour exécuter
- Observer les résultats

### 4. Récupérer les résultats

Tous les fichiers générés sont dans `/home/jovyan/data/` :

```
/home/jovyan/data/
├── bronze/
│   ├── postgres/           # Tables PostgreSQL en Parquet
│   └── csv/                # CSV en Parquet
├── gold/
│   ├── dim_temps/          # Dimension Temps
│   ├── dim_patient/        # Dimension Patient
│   ├── fait_consultation/  # Fait Consultations (partitionné)
│   └── ...
├── bronze_ingestion_stats.png
├── bronze_csv_stats.png
├── gold_star_schema_stats.png
├── performance_benchmarks.png
├── partitionnement_heatmap.png
└── rapport_performance.md
```

---

## 📊 Ce que vous obtenez pour le Livrable 2

### ✅ Scripts de création et chargement
- Notebooks exécutables (`.ipynb`)
- Code Python/Spark documenté
- Logs d'exécution avec statistiques

### ✅ Vérification des données
- Comptage des lignes ingérées
- Schémas des tables
- Aperçus des données

### ✅ Peuplement des tables
- Bronze : ~1.4 million lignes
- Gold : Modèle dimensionnel complet
- Partitions par année/mois

### ✅ Partitionnement et buckets
- Consultations partitionnées par année/mois
- Dimensions non partitionnées (petites tailles)
- Format Parquet optimisé

### ✅ Graphes de performance
- Temps d'exécution par requête
- Heatmap des partitions
- Comparaisons avant/après

### ✅ Requêtes de benchmark
- 6 requêtes SQL documentées
- Mesures de temps précises
- Variabilité des performances

---

## 🎓 Pour la soutenance

### Préparez :

1. **Captures d'écran des notebooks** montrant :
   - Les statistiques d'ingestion
   - Le modèle Gold créé
   - Les graphiques de performance

2. **Le rapport de performance** (`rapport_performance.md`)
   - Généré automatiquement par le notebook 04
   - Contient toutes les métriques

3. **Les graphiques** (PNG)
   - À inclure dans votre rapport final
   - Démontrent les optimisations

4. **Le code source** (notebooks)
   - Exportez en PDF ou HTML si besoin
   - Via Jupyter : File → Download as → PDF/HTML

---

## 💡 Conseils

### Si un notebook plante :
1. Redémarrez le kernel : Kernel → Restart Kernel
2. Ré-exécutez depuis le début
3. Vérifiez les logs d'erreur

### Si les données sont incorrectes :
1. Supprimez le dossier `data/`
2. Relancez le notebook 01

### Pour accélérer :
- Vous pouvez **skipper le notebook 02** (CSV) si vous manquez de temps
- Le notebook 03 (Gold) fonctionne sans les CSV
- Concentrez-vous sur les consultations (données PostgreSQL)

---

## ❓ Questions fréquentes

### Q: Combien de temps ça prend ?
**R**: Environ 40 minutes pour tout exécuter (10+5+15+10)

### Q: Puis-je exécuter plusieurs fois ?
**R**: Oui ! Les notebooks utilisent `mode("overwrite")`, vous pouvez les relancer.

### Q: Les résultats sont où ?
**R**: Dans `/home/jovyan/data/` (accessible via l'interface Jupyter)

### Q: Comment télécharger les fichiers ?
**R**:
1. Clic droit sur le fichier dans Jupyter
2. "Download"

### Q: Spark plante avec "Out of Memory" ?
**R**:
- Redémarrez Docker
- Ou réduisez la taille des données (filtrez par année)

---

## 🎯 Checklist Livrable 2

Après avoir exécuté tous les notebooks, vérifiez que vous avez :

- [ ] ✅ Bronze PostgreSQL ingéré (~1M lignes)
- [ ] ✅ Bronze CSV ingéré (~400K lignes)
- [ ] ✅ 5 dimensions créées
- [ ] ✅ 4 tables de faits créées
- [ ] ✅ Partitionnement appliqué
- [ ] ✅ 6 requêtes de benchmark exécutées
- [ ] ✅ Graphiques générés (5 PNG)
- [ ] ✅ Rapport de performance créé

**Si tout est ✅, votre Livrable 2 est COMPLET !** 🎉

---

**Bonne chance pour votre projet !** 🚀
