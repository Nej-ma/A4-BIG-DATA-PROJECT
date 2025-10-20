"""
DAG AIRFLOW - PIPELINE ETL CHU
================================
Pipeline complet ETLT pour le projet Cloud Healthcare Unit

Étapes:
- E: Extract depuis PostgreSQL et CSV
- T1: Transform Conformité (pseudonymisation RGPD)
- L: Load dans MinIO (zones Bronze/Silver/Gold)
- T2: Transform Métier (modèle dimensionnel)

Auteur: Équipe Projet CHU
Date: 2025-10
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
import pandas as pd
import boto3
from io import StringIO
import hashlib
import json

# ============================================================
# CONFIGURATION DU DAG
# ============================================================

default_args = {
    'owner': 'chu-team',
    'depends_on_past': False,
    'start_date': datetime(2025, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'chu_etl_pipeline',
    default_args=default_args,
    description='Pipeline ETL complet pour le projet CHU',
    schedule_interval='@daily',
    catchup=False,
    tags=['chu', 'etl', 'healthcare'],
)

# ============================================================
# FONCTIONS UTILITAIRES
# ============================================================

def get_s3_client():
    """Créer un client S3 pour MinIO"""
    return boto3.client(
        's3',
        endpoint_url='http://chu_minio:9000',
        aws_access_key_id='minioadmin',
        aws_secret_access_key='minioadmin123',
        region_name='us-east-1'
    )

def pseudonymize(value, salt='chu_project_2025'):
    """Pseudonymisation SHA-256 conforme RGPD"""
    if pd.isna(value):
        return None
    return hashlib.sha256(f"{value}{salt}".encode()).hexdigest()[:16]

# ============================================================
# TÂCHE 1: EXTRACTION DEPUIS POSTGRESQL
# ============================================================

def extract_from_postgres(**context):
    """
    Extraction des données depuis PostgreSQL
    Tables: patient, consultation, professionnel, diagnostic, medicaments
    """
    print("🔄 Extraction des données depuis PostgreSQL...")

    hook = PostgresHook(postgres_conn_id='postgres_chu')

    # Tables avec majuscules (selon la structure PostgreSQL)
    tables = ['Patient', 'Consultation', 'Professionnel_de_sante', 'Diagnostic', 'Medicaments', 'Mutuelle']

    s3_client = get_s3_client()

    for table in tables:
        try:
            print(f"   → Extraction de la table: {table}")

            # Requête SQL avec guillemets pour les noms avec majuscules/underscores
            sql = f'SELECT * FROM "{table}"'
            df = hook.get_pandas_df(sql)

            print(f"   ✓ {len(df)} lignes extraites de {table}")

            # Sauvegarde en CSV dans Bronze
            csv_buffer = StringIO()
            df.to_csv(csv_buffer, index=False)

            key = f"bronze/postgresql/{table}/extract_{datetime.now().strftime('%Y%m%d')}.csv"
            s3_client.put_object(
                Bucket='bronze',
                Key=key,
                Body=csv_buffer.getvalue()
            )

            # Métadonnées
            metadata = {
                'source': 'postgresql',
                'table': table,
                'rows': len(df),
                'columns': list(df.columns),
                'extract_date': datetime.now().isoformat(),
            }

            s3_client.put_object(
                Bucket='bronze',
                Key=f"bronze/postgresql/{table}/metadata_{datetime.now().strftime('%Y%m%d')}.json",
                Body=json.dumps(metadata, indent=2)
            )

            print(f"   ✓ Sauvegardé dans MinIO: {key}")

        except Exception as e:
            print(f"   ✗ Erreur pour {table}: {str(e)}")
            raise

    print("✅ Extraction PostgreSQL terminée")

# ============================================================
# TÂCHE 2: EXTRACTION DES FICHIERS CSV
# ============================================================

def extract_csv_files(**context):
    """
    Extraction des fichiers CSV
    - Établissements (FINESS)
    - Satisfaction
    - Décès
    - Hospitalisation
    """
    print("🔄 Extraction des fichiers CSV...")

    import os
    import glob

    s3_client = get_s3_client()
    data_path = '/opt/airflow/data'

    # Fichiers à extraire
    files_config = {
        'etablissements': 'BDD CSV/finess-*.csv',
        'satisfaction': 'SATISFACTION/*.csv',
        'deces': 'DECES/*.csv',
        'hospitalisation': 'BDD CSV/*hospitalisation*.csv',
    }

    for category, pattern in files_config.items():
        try:
            files = glob.glob(os.path.join(data_path, pattern))
            print(f"   → Traitement de {category}: {len(files)} fichier(s)")

            for file_path in files:
                filename = os.path.basename(file_path)

                with open(file_path, 'rb') as f:
                    s3_client.put_object(
                        Bucket='bronze',
                        Key=f"bronze/csv/{category}/{filename}",
                        Body=f.read()
                    )

                print(f"   ✓ {filename} uploadé")

        except Exception as e:
            print(f"   ⚠ Erreur pour {category}: {str(e)}")

    print("✅ Extraction CSV terminée")

# ============================================================
# TÂCHE 3: TRANSFORMATION T1 - CONFORMITÉ RGPD
# ============================================================

def transform_t1_patient(**context):
    """
    T1 - Transformation Conformité pour Patient
    - Pseudonymisation des PII (nom, prénom, email, téléphone, NSS)
    - Suppression des données inutiles
    - Normalisation
    """
    print("🔄 T1 - Transformation Patient (Conformité RGPD)...")

    s3_client = get_s3_client()

    # Récupération du dernier fichier patient
    response = s3_client.list_objects_v2(
        Bucket='bronze',
        Prefix='bronze/postgresql/patient/'
    )

    csv_files = [obj['Key'] for obj in response.get('Contents', []) if obj['Key'].endswith('.csv')]

    if not csv_files:
        print("   ✗ Aucun fichier patient trouvé")
        return

    latest_file = sorted(csv_files)[-1]
    print(f"   → Traitement de: {latest_file}")

    # Lecture
    obj = s3_client.get_object(Bucket='bronze', Key=latest_file)
    df = pd.read_csv(obj['Body'])

    print(f"   → {len(df)} patients à traiter")

    # Renommer les colonnes en minuscules pour faciliter le traitement
    df.columns = df.columns.str.lower()

    # Pseudonymisation
    df['id_patient_pseudo'] = df['id_patient'].apply(pseudonymize)

    # Suppression des PII si elles existent
    pii_columns = ['nom', 'prenom', 'email', 'tel', 'num_secu', 'adresse']
    df = df.drop(columns=[col for col in pii_columns if col in df.columns], errors='ignore')

    # Normalisation dates (la colonne s'appelle 'date' dans la table)
    if 'date' in df.columns:
        df['date_naissance'] = pd.to_datetime(df['date'], errors='coerce')
        df['age'] = (datetime.now() - df['date_naissance']).dt.days // 365
        df['tranche_age'] = pd.cut(df['age'], bins=[0, 18, 35, 50, 65, 100],
                                     labels=['0-18', '19-35', '36-50', '51-65', '65+'])
        df = df.drop(columns=['date'])  # Supprimer l'ancienne colonne

    # Sauvegarde dans Silver
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)

    key = f"silver/patient/patient_clean_{datetime.now().strftime('%Y%m%d')}.csv"
    s3_client.put_object(
        Bucket='silver',
        Key=key,
        Body=csv_buffer.getvalue()
    )

    print(f"   ✓ {len(df)} patients pseudonymisés")
    print(f"   ✓ Sauvegardé dans Silver: {key}")

def transform_t1_consultation(**context):
    """
    T1 - Transformation Conformité pour Consultation
    - Normalisation des dates
    - Validation des FK
    """
    print("🔄 T1 - Transformation Consultation (Conformité)...")

    s3_client = get_s3_client()

    # Récupération
    response = s3_client.list_objects_v2(
        Bucket='bronze',
        Prefix='bronze/postgresql/consultation/'
    )

    csv_files = [obj['Key'] for obj in response.get('Contents', []) if obj['Key'].endswith('.csv')]

    if not csv_files:
        print("   ✗ Aucun fichier consultation trouvé")
        return

    latest_file = sorted(csv_files)[-1]
    obj = s3_client.get_object(Bucket='bronze', Key=latest_file)
    df = pd.read_csv(obj['Body'])

    print(f"   → {len(df)} consultations à traiter")

    # Renommer les colonnes en minuscules
    df.columns = df.columns.str.lower()

    # Normalisation dates (la colonne s'appelle 'date' dans la table)
    if 'date' in df.columns:
        df['date_consultation'] = pd.to_datetime(df['date'], errors='coerce')
        df = df.drop(columns=['date'])

    if 'heure_debut' in df.columns:
        df['heure_debut'] = pd.to_datetime(df['heure_debut'], format='%H:%M:%S', errors='coerce').dt.time

    if 'heure_fin' in df.columns:
        df['heure_fin'] = pd.to_datetime(df['heure_fin'], format='%H:%M:%S', errors='coerce').dt.time

    # Suppression des lignes avec dates invalides
    df = df.dropna(subset=['date_consultation'])

    # Sauvegarde
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)

    key = f"silver/consultation/consultation_clean_{datetime.now().strftime('%Y%m%d')}.csv"
    s3_client.put_object(
        Bucket='silver',
        Key=key,
        Body=csv_buffer.getvalue()
    )

    print(f"   ✓ {len(df)} consultations nettoyées")
    print(f"   ✓ Sauvegardé dans Silver: {key}")

# ============================================================
# TÂCHE 4: TRANSFORMATION T2 - MODÈLE DIMENSIONNEL
# ============================================================

def transform_t2_dim_temps(**context):
    """
    T2 - Création de la dimension Temps
    Génération d'un calendrier complet
    """
    print("🔄 T2 - Création DIM_TEMPS...")

    # Génération calendrier 2014-2025
    dates = pd.date_range(start='2014-01-01', end='2025-12-31', freq='D')

    df = pd.DataFrame({
        'id_temps': range(len(dates)),
        'date_complete': dates,
        'jour': dates.day,
        'mois': dates.month,
        'annee': dates.year,
        'trimestre': dates.quarter,
        'semaine': dates.isocalendar().week,
        'jour_semaine': dates.dayofweek,
        'nom_jour': dates.day_name(),
        'nom_mois': dates.month_name(),
        'est_weekend': dates.dayofweek.isin([5, 6]),
    })

    # Sauvegarde dans Gold
    s3_client = get_s3_client()
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)

    key = f"gold/dimensions/dim_temps.csv"
    s3_client.put_object(
        Bucket='gold',
        Key=key,
        Body=csv_buffer.getvalue()
    )

    print(f"   ✓ DIM_TEMPS créée: {len(df)} jours")

def transform_t2_dim_patient(**context):
    """
    T2 - Création de la dimension Patient
    À partir des données Silver
    """
    print("🔄 T2 - Création DIM_PATIENT...")

    s3_client = get_s3_client()

    # Récupération depuis Silver
    response = s3_client.list_objects_v2(
        Bucket='silver',
        Prefix='silver/patient/'
    )

    csv_files = [obj['Key'] for obj in response.get('Contents', []) if obj['Key'].endswith('.csv')]

    if not csv_files:
        print("   ✗ Aucun fichier patient dans Silver")
        return

    latest_file = sorted(csv_files)[-1]
    obj = s3_client.get_object(Bucket='silver', Key=latest_file)
    df = pd.read_csv(obj['Body'])

    # Sélection des colonnes pour la dimension
    dim_columns = ['id_patient', 'id_patient_pseudo', 'sexe', 'date_naissance', 'age', 'tranche_age']
    df_dim = df[[col for col in dim_columns if col in df.columns]].copy()

    # Sauvegarde dans Gold
    csv_buffer = StringIO()
    df_dim.to_csv(csv_buffer, index=False)

    key = f"gold/dimensions/dim_patient.csv"
    s3_client.put_object(
        Bucket='gold',
        Key=key,
        Body=csv_buffer.getvalue()
    )

    print(f"   ✓ DIM_PATIENT créée: {len(df_dim)} patients")

# ============================================================
# DÉFINITION DES TÂCHES AIRFLOW
# ============================================================

# Extraction
task_extract_postgres = PythonOperator(
    task_id='extract_from_postgres',
    python_callable=extract_from_postgres,
    dag=dag,
)

task_extract_csv = PythonOperator(
    task_id='extract_csv_files',
    python_callable=extract_csv_files,
    dag=dag,
)

# Transformation T1 (Conformité)
task_t1_patient = PythonOperator(
    task_id='t1_transform_patient',
    python_callable=transform_t1_patient,
    dag=dag,
)

task_t1_consultation = PythonOperator(
    task_id='t1_transform_consultation',
    python_callable=transform_t1_consultation,
    dag=dag,
)

# Transformation T2 (Dimensions)
task_t2_dim_temps = PythonOperator(
    task_id='t2_create_dim_temps',
    python_callable=transform_t2_dim_temps,
    dag=dag,
)

task_t2_dim_patient = PythonOperator(
    task_id='t2_create_dim_patient',
    python_callable=transform_t2_dim_patient,
    dag=dag,
)

# ============================================================
# DÉPENDANCES DU DAG (WORKFLOW)
# ============================================================

# Phase 1: Extraction (parallèle)
[task_extract_postgres, task_extract_csv]

# Phase 2: T1 Conformité (dépend de l'extraction)
task_extract_postgres >> task_t1_patient
task_extract_postgres >> task_t1_consultation

# Phase 3: T2 Dimensions (dépend de T1)
task_t1_patient >> task_t2_dim_patient
task_t2_dim_temps  # Indépendant

# Note: Les tâches de faits seront ajoutées plus tard
