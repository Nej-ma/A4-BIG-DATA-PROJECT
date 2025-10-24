# Modèle Conceptuel de Données (MCD) - Base Healthcare Data

## Diagramme ER en Mermaid

```mermaid
erDiagram
    Patient ||--o{ Consultation : "consulte"
    Patient ||--o{ Adher : "souscrit"
    Professionnel_de_sante ||--o{ Consultation : "effectue"
    Specialites ||--o{ Professionnel_de_sante : "possede"
    Mutuelle ||--o{ Consultation : "rembourse"
    Mutuelle ||--o{ Adher : "couvre"
    Diagnostic ||--o{ Consultation : "etablit"
    Consultation ||--o{ Prescription : "genere"
    Consultation ||--o{ Salle : "se_deroule_dans"
    Medicaments ||--o{ Prescription : "prescrit"

    Patient {
        integer Id_patient PK "Identifiant unique du patient"
        varchar Nom "Nom du patient"
        varchar Prenom "Prénom du patient"
        varchar Sexe "Sexe (Homme/Femme)"
        varchar Adresse "Adresse complète"
        varchar Ville "Ville de résidence"
        varchar Code_postal "Code postal"
        varchar Pays "Code pays (2 lettres)"
        varchar EMail "Adresse email"
        varchar Tel "Numéro de téléphone"
        varchar Date "Date de naissance"
        integer Age "Age du patient"
        varchar Num_Secu "Numéro de sécurité sociale"
        varchar Groupe_sanguin "Groupe sanguin (A, B, AB, O)"
        varchar Poid "Poids en kg"
        varchar Taille "Taille en cm"
    }

    Professionnel_de_sante {
        varchar Identifiant PK "Identifiant unique RPPS/ADELI"
        varchar Civilite "Civilité (Dr, Pr, etc.)"
        varchar Categorie_professionnelle "Catégorie (Médecin, Infirmier, etc.)"
        varchar Nom "Nom du professionnel"
        varchar Prenom "Prénom du professionnel"
        varchar Profession "Profession exacte"
        varchar Type_identifiant "Type d'identifiant (RPPS/ADELI)"
        varchar Code_specialite FK "Code de la spécialité"
    }

    Specialites {
        varchar Code_specialite PK "Code unique de la spécialité"
        varchar Fonction "Fonction du professionnel"
        varchar Specialite "Nom de la spécialité"
    }

    Consultation {
        integer Num_consultation PK "Numéro unique de consultation (auto-increment)"
        integer Id_mut FK "Identifiant de la mutuelle"
        integer Id_patient FK "Identifiant du patient"
        varchar Id_prof_sante FK "Identifiant du professionnel"
        varchar Code_diag FK "Code du diagnostic"
        varchar Motif "Motif de la consultation"
        date Date "Date de la consultation"
        time Heure_debut "Heure de début"
        time Heure_fin "Heure de fin"
    }

    Diagnostic {
        varchar Code_diag PK "Code unique du diagnostic (CIM-10)"
        varchar Diagnostic "Libellé du diagnostic"
    }

    Mutuelle {
        integer Id_Mut PK "Identifiant unique de la mutuelle"
        varchar Nom "Nom de la mutuelle"
        varchar Adresse "Adresse de la mutuelle"
    }

    Adher {
        integer Id_patient FK "Identifiant du patient"
        integer Id_mut FK "Identifiant de la mutuelle"
    }

    Prescription {
        integer Num_consultation FK "Numéro de consultation"
        varchar Code_CIS FK "Code CIS du médicament"
    }

    Medicaments {
        varchar Code_CIS PK "Code CIS unique du médicament"
        varchar Denomination "Dénomination du médicament"
        varchar Forme_pharmaceutique "Forme (comprimé, sirop, etc.)"
        varchar Voies_d_administration "Voies d'administration"
        varchar Statut_administratif "Statut administratif"
        varchar Type_de_procedure "Type de procédure d'autorisation"
        varchar Etat_de_commercialisation "État de commercialisation"
        varchar Date_AMM "Date d'autorisation de mise sur le marché"
        varchar StatutBdm "Statut dans la base de données"
        varchar Num_autorisation_europeenne "Numéro d'autorisation européenne"
        varchar Titulaire "Titulaire de l'AMM"
        varchar Surveillance_renforcee "Surveillance renforcée (Oui/Non)"
    }

    Salle {
        varchar Id_salle PK "Identifiant unique de la salle"
        integer Num_consultation FK "Numéro de consultation"
        varchar Code_bloc "Code du bloc opératoire"
        varchar Num_etage "Numéro d'étage"
        varchar Num_salle "Numéro de salle"
    }

    Laboratoire {
        integer Id_labo PK "Identifiant unique du laboratoire"
        varchar Laboratoire "Nom du laboratoire"
        varchar Pays "Pays du laboratoire"
    }
```

## Description des Relations

### Relations Principales

1. **Patient - Consultation** (1,N)
   - Un patient peut avoir plusieurs consultations
   - Une consultation concerne un seul patient

2. **Professionnel_de_sante - Consultation** (1,N)
   - Un professionnel de santé peut effectuer plusieurs consultations
   - Une consultation est effectuée par un seul professionnel

3. **Specialites - Professionnel_de_sante** (1,N)
   - Une spécialité peut être exercée par plusieurs professionnels
   - Un professionnel possède une spécialité

4. **Diagnostic - Consultation** (1,N)
   - Un diagnostic peut être établi lors de plusieurs consultations
   - Une consultation établit un diagnostic

5. **Mutuelle - Consultation** (1,N)
   - Une mutuelle peut rembourser plusieurs consultations
   - Une consultation est remboursée par une mutuelle

6. **Patient - Adher - Mutuelle** (N,M)
   - Table d'association pour la relation plusieurs-à-plusieurs
   - Un patient peut avoir plusieurs mutuelles
   - Une mutuelle peut couvrir plusieurs patients

7. **Consultation - Prescription - Medicaments** (N,M)
   - Table d'association pour les prescriptions
   - Une consultation peut générer plusieurs prescriptions de médicaments
   - Un médicament peut être prescrit lors de plusieurs consultations

8. **Consultation - Salle** (1,N)
   - Une consultation se déroule dans une salle
   - Une salle peut accueillir plusieurs consultations

9. **Laboratoire**
   - Table indépendante contenant les informations des laboratoires pharmaceutiques

### Cardinalités

- **Patient** : Entité principale (1,N vers Consultation et Adher)
- **Consultation** : Entité centrale reliant Patient, Professionnel, Diagnostic, Mutuelle, Prescription et Salle
- **Adher** : Table d'association entre Patient et Mutuelle
- **Prescription** : Table d'association entre Consultation et Medicaments

## Notes Techniques

- **Clés primaires (PK)** : Identifiées pour chaque entité
- **Clés étrangères (FK)** : Relations établies via des contraintes FOREIGN KEY
- **Contraintes NOT VALID** : Présentes dans la base pour permettre l'insertion de données existantes
- **Auto-increment** : Num_consultation est généré automatiquement (GENERATED ALWAYS AS IDENTITY)
- **Tables supplémentaires** : AAAA et date ne sont pas incluses dans le MCD (probablement des tables de travail/temporaires)

## Schéma de Base de Données

- **Base** : healthcare_data
- **SGBD** : PostgreSQL 15 (Alpine)
- **Encodage** : UTF8
- **13 tables** au total dont 11 tables métier principales
