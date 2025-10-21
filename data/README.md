# Dézippé le dossier DATA 2024 ici.

SI CA MARCHE PAS DIRECTEMENT LANCER pour seed :

docker exec chu_postgres pg_restore -U admin -d healthcare_data -v --no-owner --no-acl "/docker-entrypoint-initdb.d/DATA 2024/BDD PostgreSQL/DATA2023"
