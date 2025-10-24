# Schéma UML des données PostgreSQL - CHU

```mermaid
erDiagram
    Patient {
        int Id_patient PK
        varchar Nom
        varchar Prenom
        varchar Sexe
        varchar Date
        int Age
        varchar Num_Secu
        varchar EMail
        varchar Tel
        varchar Adresse
        varchar Ville
        varchar Code_postal
        varchar Pays
        varchar Groupe_sanguin
        varchar Poid
        varchar Taille
    }
    
    Consultation {
        int Num_consultation PK
        int Id_patient FK
        varchar Id_prof_sante FK
        varchar Code_diag FK
        int Id_mut FK
        date Date
        time Heure_debut
        time Heure_fin
        varchar Motif
    }
    
    Professionnel_de_sante {
        varchar Identifiant PK
        varchar Civilite
        varchar Categorie_professionnelle
        varchar Nom
        varchar Prenom
        varchar Profession
        varchar Type_identifiant
        varchar Code_specialite FK
    }
    
    Diagnostic {
        varchar Code_diag PK
        varchar Diagnostic
    }
    
    Mutuelle {
        int Id_mut PK
        varchar Nom_mutuelle
        varchar Adresse
    }
    
    Specialites {
        varchar Code_specialite PK
        varchar Libelle_specialite
    }

    Patient ||--o{ Consultation : "a"
    Consultation }o--|| Professionnel_de_sante : "effectuee_par"
    Consultation }o--|| Diagnostic : "concerne"
    Consultation }o--|| Mutuelle : "couverte_par"
    Professionnel_de_sante }o--|| Specialites : "specialite"
```

## Instructions d'export :
1. Copier le code Mermaid ci-dessus
2. Aller sur https://mermaid.live/
3. Coller le code
4. Ajuster la taille si nécessaire
5. Exporter en PNG (haute résolution) ou SVG
6. Sauvegarder sous le nom `uml_postgresql.png`