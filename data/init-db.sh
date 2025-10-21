#!/bin/bash
set -e

# Script d'initialisation automatique de la base de données PostgreSQL
# Restore du dump DATA2023 au premier démarrage

DUMP_FILE="/docker-entrypoint-initdb.d/DATA 2024/BDD PostgreSQL/DATA2023"
DB_NAME="healthcare_data"
DB_USER="admin"

echo "=========================================="
echo "Initialisation de la base de données CHU"
echo "=========================================="

# Vérifier si le fichier dump existe
if [ ! -f "$DUMP_FILE" ]; then
    echo "❌ ERREUR: Le fichier dump n'existe pas: $DUMP_FILE"
    exit 1
fi

echo "✅ Fichier dump trouvé: $DUMP_FILE"
echo "📊 Taille: $(du -h "$DUMP_FILE" | cut -f1)"

# Attendre que PostgreSQL soit prêt
echo "⏳ Attente de PostgreSQL..."
until pg_isready -U "$DB_USER" -d "$DB_NAME" > /dev/null 2>&1; do
    sleep 1
done

echo "✅ PostgreSQL est prêt!"
echo "🔄 Restauration du dump en cours..."

# Restaurer le dump avec pg_restore
# Options:
#   -U: utilisateur
#   -d: base de données
#   -v: mode verbeux
#   --no-owner: ne pas restaurer les propriétaires
#   --no-acl: ne pas restaurer les privilèges
pg_restore -U "$DB_USER" -d "$DB_NAME" -v --no-owner --no-acl "$DUMP_FILE" 2>&1 || {
    echo "⚠️  Erreurs lors de la restauration (certaines peuvent être normales)"
}

echo "=========================================="
echo "✅ Initialisation terminée!"
echo "=========================================="
