#!/bin/bash
set -e

echo "=========================================="
echo "Database Initialization Script"
echo "=========================================="

# Attendre que PostgreSQL soit prêt
echo "Waiting for PostgreSQL to be ready..."
until pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB" > /dev/null 2>&1; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 2
done

echo "PostgreSQL is ready!"

# Vérifier si la base de données est déjà peuplée
TABLE_COUNT=$(psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -tAc "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE';")

if [ "$TABLE_COUNT" -gt 0 ]; then
  echo "Database already contains $TABLE_COUNT tables. Skipping import."
  echo "To force reimport, delete the postgres volume first."
else
  echo "Database is empty. Starting import..."

  # Vérifier si le fichier dump existe
  if [ -f "/dumps/$DB_DUMP_FILE" ]; then
    echo "Found dump file: /dumps/$DB_DUMP_FILE"
    echo "Starting pg_restore..."

    # Restaurer le dump avec pg_restore
    pg_restore -U "$POSTGRES_USER" -d "$POSTGRES_DB" -v "/dumps/$DB_DUMP_FILE" 2>&1 || {
      echo "Warning: pg_restore completed with some errors (this is normal for owner changes)"
    }

    echo "=========================================="
    echo "Database import completed!"

    # Afficher le nombre de tables créées
    NEW_TABLE_COUNT=$(psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -tAc "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE';")
    echo "Total tables created: $NEW_TABLE_COUNT"

    # Afficher quelques statistiques
    echo "=========================================="
    echo "Database Statistics:"
    psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "SELECT schemaname, tablename, n_live_tup as row_count FROM pg_stat_user_tables ORDER BY n_live_tup DESC LIMIT 10;"
    echo "=========================================="
  else
    echo "ERROR: Dump file not found at /dumps/$DB_DUMP_FILE"
    exit 1
  fi
fi

echo "Database initialization complete!"
