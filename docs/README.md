# 📚 Documentation CHU Data Lakehouse - Livrable 2

**Projet**: CHU Data Lakehouse (Bronze → Silver → Gold)
**Équipe**: Nejma MOUALHI | Brieuc OLIVIERI | Nicolas TAING
**Formation**: CESI FISA A4 - Big Data
**Date**: Octobre 2025

---

## 📋 Fichiers Essentiels

### 🚀 Guide Principal
- **[GUIDE_UTILISATION.md](GUIDE_UTILISATION.md)** - Guide complet d'utilisation du projet

### 🎯 Résumé du Projet
- **[SYNTHESE_PROJET.md](SYNTHESE_PROJET.md)** - Résumé: découvertes, tables créées, conformité Livrable 1

### 🔧 Troubleshooting
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Solutions aux problèmes courants (Superset, PostgreSQL, etc.)

---

## 🗂️ Structure du Projet

```
projet_git/
├── docs/                           # Documentation (ce dossier)
│   ├── README.md                   # Ce fichier
│   ├── GUIDE_UTILISATION.md        # Guide complet
│   ├── SYNTHESE_PROJET.md          # Synthèse technique
│   ├── TROUBLESHOOTING.md          # Solutions problèmes
│   └── archives/                   # Anciens docs (référence)
│
├── jupyter/notebooks/              # Notebooks Spark
│   ├── 01_Extract_Bronze_SOURCES_DIRECTES.ipynb
│   ├── 02_Transform_Silver_CLEANING.ipynb
│   ├── 03_Transform_Gold_STAR_SCHEMA.ipynb
│   └── 06_Export_Gold_to_PostgreSQL.ipynb
│
├── spark/data/                     # Données lakehouse
│   ├── bronze/                     # Données brutes
│   ├── silver/                     # Données nettoyées
│   └── gold/                       # Star schema
│
├── docker-compose.yml              # Configuration Docker
└── README.md                       # README principal
```

---

## 🎯 Quick Start

### 1. Démarrer l'environnement
```bash
docker-compose up -d
```

### 2. Exécuter les notebooks (dans l'ordre)
1. Notebook 01 - Bronze (~2 min)
2. Notebook 02 - Silver (~3 min)
3. Notebook 03 - Gold (~3 min)
4. Notebook 06 - PostgreSQL export (~3 min)

### 3. Accéder aux services
- **Jupyter**: http://localhost:8888
- **Superset**: http://localhost:8088 (admin/admin123)
- **PostgreSQL**: localhost:5432

---

## 📊 Résultats Livrables

### Tables de Faits (4) - Conforme Livrable 1 ✅
1. **fait_consultation** (1M lignes)
2. **fait_hospitalisation** (82K lignes) - Découvert dans tables AAAA + date
3. **fait_deces** (620K lignes - 2019)
4. **fait_satisfaction** (8 lignes - 2019)

### Dimensions (5)
- dim_temps, dim_patient, dim_diagnostic, dim_professionnel, dim_etablissement

### Total: 9 tables dans PostgreSQL schema `gold`

---

## 🆘 Besoin d'aide ?

1. **Erreurs communes** → Voir [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
2. **Utilisation détaillée** → Voir [GUIDE_UTILISATION.md](GUIDE_UTILISATION.md)
3. **Contexte technique** → Voir [SYNTHESE_PROJET.md](SYNTHESE_PROJET.md)

---

**🎉 Bon courage pour votre Livrable 2 !**
