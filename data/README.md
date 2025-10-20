# 📦 data/ - Données sources du projet CHU

---

## 📋 Contenu

Ce dossier contient les scripts SQL d'initialisation de la base de données PostgreSQL :

- **01_init_schema.sql** : Création du schéma complet (8 tables)
- **02_seed_data.sql** : Chargement des dimensions (100 patients, 20 médecins, etc.)
- **03_seed_transactions.sql** : Chargement des faits (consultations, hospitalisations, etc.)

**Total : 357 enregistrements** prêts pour l'analyse.

---

## 🔄 Initialisation automatique

PostgreSQL exécute automatiquement tous les fichiers `.sql` de ce dossier au **premier démarrage** (par ordre alphabétique).

```yaml
# Configuration dans docker-compose.yml
postgres:
  volumes:
    - ./data:/docker-entrypoint-initdb.d
```

**Important** : L'initialisation ne s'exécute que si aucun volume PostgreSQL n'existe.

Pour réinitialiser :
```bash
docker-compose down -v
docker-compose up --build -d
```

---

## ✅ Vérification après import

Une fois `docker-compose up -d` lancé, vérifiez que les données sont bien importées :

### Via pgAdmin (http://localhost:5050)

1. Connectez-vous avec `admin@chu.fr` / `admin123`
2. Ajoutez un serveur :
   - Host : `chu_postgres`
   - Port : `5432`
   - Database : `healthcare_data`
   - User : `admin`
   - Password : `admin123`
3. Explorez les tables et vérifiez le nombre de lignes

### Via ligne de commande

```bash
docker exec -it chu_postgres psql -U admin -d healthcare_data

# Puis dans psql :
\dt                                    # Lister les tables
SELECT COUNT(*) FROM "Patient";        # Compter les patients
SELECT COUNT(*) FROM "Consultation";   # Compter les consultations
\q                                     # Quitter
```

---

## 🚨 IMPORTANT - Données fictives

✅ **Les données de ce projet sont FICTIVES** et générées pour l'apprentissage.

**Attention** : Ces données contiennent des informations PII (nom, prénom, NSS, adresse) pour permettre de tester les transformations RGPD (pseudonymisation).

⚠️ **NE JAMAIS utiliser de vraies données patients** dans ce projet.

---

## 📝 Checklist

- [ ] Scripts SQL présents dans `data/`
- [ ] Docker Desktop lancé
- [ ] `docker-compose up --build -d` exécuté
- [ ] Attendre 2-3 minutes que PostgreSQL démarre
- [ ] Vérifier dans pgAdmin que les 8 tables existent
- [ ] Vérifier le nombre total de lignes : 357

---

**Bon courage ! 🚀**
