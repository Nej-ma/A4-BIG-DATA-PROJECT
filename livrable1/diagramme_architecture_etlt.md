# Architecture ETLT - CHU Big Data

```mermaid
flowchart TB
    %% Styling
    classDef sourceBox fill:#e1f5fe,stroke:#01579b,stroke-width:2px;
    classDef etltBox fill:#f3e5f5,stroke:#4a148c,stroke-width:2px;
    classDef zoneBox fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px;
    classDef toolBox fill:#fff3e0,stroke:#e65100,stroke-width:2px;
    classDef securityBox fill:#ffebee,stroke:#b71c1c,stroke-width:2px;

    %% Sources de données
    subgraph SOURCES["SOURCES DE DONNÉES"]
        PG["PostgreSQL<br/>1M+ Consultations<br/>100K Patients<br/>1M+ Professionnels"]
        CSV["Fichiers CSV<br/>Établissements<br/>Satisfaction 27 fichiers<br/>Décès<br/>Hospitalisations"]
    end

    %% Pipeline ETLT
    subgraph PIPELINE["PIPELINE ETLT"]
        E["EXTRACT<br/>Apache Sqoop<br/>Apache Flume/NiFi"]
        T1["TRANSFORM 1<br/>Conformité RGPD/HDS<br/>Pseudonymisation<br/>Minimisation<br/>Normalisation"]
        L["LOAD<br/>Chargement HDFS<br/>Format Parquet/ORC<br/>Métadonnées"]
        T2["TRANSFORM 2<br/>Nettoyage métier<br/>Modélisation<br/>Agrégations"]
    end

    %% Data Lake Zones
    subgraph DATALAKE["DATA LAKE HDFS"]
        subgraph BRONZE["ZONE BRONZE"]
            BZ["Landing<br/>Données pseudonymisées<br/>Structure préservée<br/>Audit trail complet"]
        end

        subgraph SILVER["ZONE SILVER"]
            SZ["Intégration<br/>Données nettoyées<br/>Référentiels joints<br/>Doublons supprimés"]
        end

        subgraph GOLD["ZONE GOLD"]
            DIM["DIMENSIONS<br/>Temps Patient<br/>Établissement Diagnostic<br/>Professionnel Spécialité"]
            FAIT["TABLES DE FAITS<br/>Consultation<br/>Hospitalisation<br/>Décès Satisfaction"]
        end
    end

    %% Outils et Interfaces
    subgraph OUTILS["OUTILS & INTERFACES"]
        HIVE["Apache Hive<br/>Requêtage SQL<br/>Optimisation ORC"]
        BI["BUSINESS INTELLIGENCE<br/>Power BI<br/>Tableau<br/>Dashboards interactifs"]
    end

    %% Sécurité et Gouvernance
    subgraph SECURITE["SÉCURITÉ & GOUVERNANCE"]
        RANGER["Apache Ranger<br/>Contrôle d'accès<br/>RBAC granulaire"]
        KERBEROS["Kerberos<br/>Authentification<br/>Single Sign-On"]
        AIRFLOW["Apache Airflow<br/>Orchestration<br/>Monitoring<br/>Logs centralisés"]
    end

    %% Flux de données principaux
    PG --> E
    CSV --> E
    E --> T1
    T1 --> L
    L --> BZ
    BZ --> T2
    T2 --> SZ
    SZ --> DIM
    SZ --> FAIT
    DIM --> HIVE
    FAIT --> HIVE
    HIVE --> BI

    %% Flux de sécurité et gouvernance
    RANGER -.-> BZ
    RANGER -.-> SZ
    RANGER -.-> DIM
    RANGER -.-> FAIT
    KERBEROS -.-> HIVE
    AIRFLOW -.-> E
    AIRFLOW -.-> T1
    AIRFLOW -.-> T2

    %% Classes
    class PG,CSV sourceBox;
    class E,T1,L,T2 etltBox;
    class BZ,SZ,DIM,FAIT zoneBox;
    class HIVE,BI toolBox;
    class RANGER,KERBEROS,AIRFLOW securityBox;

```

## Instructions d'export :
1. Copier le code Mermaid ci-dessus
2. Aller sur https://mermaid.live/
3. Coller le code
4. Ajuster la taille du diagramme (zoom)
5. Exporter en PNG haute résolution (minimum 1920px de largeur)
6. Sauvegarder sous le nom `architecture_etlt.png`

## Conseils pour un meilleur rendu :
- Utiliser le mode "PNG" plutôt que SVG pour une meilleure compatibilité
- Choisir une résolution élevée (300 DPI minimum)
- Le diagramme utilisera des couleurs et icônes pour une meilleure lisibilité