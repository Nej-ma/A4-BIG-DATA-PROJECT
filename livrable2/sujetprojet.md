Projet

    Introduction
    Sujet

Introduction

Le potentiel énorme associé aux données médicales a conduit le secteur de la santé à une transformation importante et rapide. Ainsi, les exigences de mise en place d'améliorations sont de plus en plus significatives. Pour progresser dans la bonne voie, les praticiens (médecins, personnel infirmier) et les administrateurs d'établissements doivent pouvoir accéder directement aux informations exploitables dans les données médicales, afin d'améliorer leurs performances et la qualité des soins de manière mesurable. La demande en matière d'informations exploitables découlant des données médicales intégrées se fait pressante. Les données relatives à l'affluence des patients, aux dossiers médicaux, au suivi des services, aux durées des cycles et sur la rentabilité des établissements recèlent d'importantes informations encore inexploitées, qui attendent d'être découvertes.

Pour toutes ces raisons, le secteur doit investir dans le développement des systèmes informatiques évolutifs, qui comprennent un ensemble d'outils et de mécanismes pour charger, extraire et traiter les données médicales. Ces systèmes parient sur la puissance de traitement parallèle et des ressources distribuées pour effectuer des transformations et des analyses complexes, pour optimiser la prise de décisions. Ainsi, pour rendre cette analyse possible, les entreprises ont besoin de nouvelles données agrégées, consolidées, historiques et synthétisées selon plusieurs axes. Le besoin d'une nouvelle architecture, qui stocke et traite ce type de données a émergé du domaine de la BI et a donné naissance aux infrastructures d'entreposage de données (datawarehouse et datamart). Ces dernières sont des structures qui intègrent des données pour l'analyse et la présentation d'informations pertinentes.

Par ailleurs, le développement d'un système décisionnel évolutif fait face à une série de défis techniques dont le paradigme des données massives (Big Data). Tout d'abord, en raison de la variété et du volume des sources de données disparates, il est difficile de recueillir et d'intégrer des données à partir d'emplacements distribués. Deuxièmement, les systèmes de données volumineux doivent stocker et gérer l'ensemble des données massives et hétérogènes recueillies et assurer une certaine performance en termes d'accès rapide, d'évolutivité et de protection de la vie privée.
Sujet
Énoncé
PROJET Cloud Healthcare Unit

Comme pour l'ensemble du secteur hospitalier, le groupe CHU (Cloud Healthcare Unit) a pris conscience de l'intérêt - voire de la nécessité - d'une transformation digitale majeure. Votre service est sollicité pour l'aider à mettre en place son propre entrepôt de données qui permettra au groupe d'exploiter la quantité considérable de données générées par les systèmes de gestion de soins ainsi que les systèmes FTP.

Le but est de pouvoir répondre à la variété des besoins et exigences d'accès et d'analyse des utilisateurs. Pour cela, le groupe CHU attend :

    Une solution complète en terme de modèles, d'outils et d'architecture qui permette d'extraire et de stocker les données, pour pouvoir ensuite les explorer et les visualiser suivant différents critères

    Une solution d'intégration de données des fichiers distribués dans une source unique persistante

    Recenser les besoins des utilisateurs (praticiens, chef d'établissement) en termes d'analyse des données pour l'exploitation directe sur le suivi des patients et des décès au niveau national et à long terme

    Des préconisations en termes d'outillage d'intégration, de stockage et de logiciel de visualisation adapté ainsi que l'exploration de données en toute sécurité afin de favoriser une meilleure prise de décision.

Cette étude tente de répondre et relever tous ces défis dans le secteur de la santé. Ainsi, le développement d'une solution doit répondre aux exigences d'infrastructure qu'imposent les données médicales, tels que le ratio coût-efficacité, la sécurité, l'élasticité, et la scalabilité.

 
Les données

Il s'agit de données provenant d'historiques des systèmes de gestion des soins (incluant les fichiers de satisfaction et de décès sur FTP). Ils contiennent des données d'exploitation sur plusieurs années. L'infrastructure de données adoptée devra être gouvernée avec une haute sécurité vu la sensibilité des informations qui seront traitées.

Voici un bref descriptif des sources de données mises à disposition :

    Une BDD PostgreSQL qui gère les soins-medico-administratives des patients

    Une BDD exportée en csv sur la gestion des établissements hospitaliers de France

    Des fichiers plats sur des notes de satisfactions émises par des patients sur différents établissements de santé

    Des fichiers qui exposent le répertoire de décès en France

     

Besoins utilisateurs

Une première consultation a permis de mettre en évidence le type d'analyses souhaitées par les utilisateurs :

    Taux de consultation des patients dans un établissement X sur une période de temps Y

    Taux de consultation des patients par rapport à un diagnostic X sur une période de temps Y

    Taux global d'hospitalisation des patients dans une période donnée Y

    Taux d'hospitalisation des patients par rapport à des diagnostics sur une période donnée

    Taux d'hospitalisation par sexe, par âge

    Taux de consultation par professionnel

    Nombre de décès par localisation (région) et sur l'année 2019

    Taux global de satisfaction par région sur l'année 2020

 
Les étapes du projet

Les grandes phases envisagées du projet sont les suivantes :

    Etude de l'architecture à mettre en place

    Modélisation conceptuelle des données

    Implémentation physique des données

    Exploitation, mesure de performance, optimisation

     

Mise en oeuvre

Ce projet est à réaliser en groupe de 3 élèves (à défaut 4).

Vous disposez chacun d'un environnement virtualisé avec les outils nécessaires et avec suffisamment de ressources pour réaliser tous les traitements attendus.

A chaque étape, pensez à analyser les tâches qui peuvent être parallélisées et à la manière de synchroniser les données entre vous pour optimiser le travail de groupe.

Il s'agit d'un projet fil rouge couvrant l'ensemble du bloc. Les 4 boucles qui la composent sont contextualisées au projet. Tout ce que vous allez étudier et réaliser dans ces boucles fera avancer le projet.

 
Livrables attendus

    Livrable 1 : Référentiel de données

    Modèle conceptuel des données et jobs nécessaires pour alimenter le schéma décisionnel

    Description :

        Modélisation des différents axes d'analyse ainsi que les mesures

        Développement des jobs d'alimentation du schéma décisionnel

        Description de l'architecture de l’entrepôt de données

    Format : Rapport

     

    Livrable 2 : Modèle physique et optimisation

    Modèle physique et évaluation de performance par rapport aux temps de réponse des requêtes réalisées sur les tables.

    Description :

        Script pour la création et le chargement de données dans les tables

        Vérification des données présentes et accès aux données à travers les tables

        Script montrant le peuplement des tables

        Script pour le partitionnement et les buckets

        Graphes montrant les temps de réponses pour évaluer la performance d'accès à l'entrepôt de données

        Requêtes faisant foi pour l'évaluation de la performance

    Format : Rapport + zip contenant les différents jobs

     

    Livrable 3 : Présentation des résultats et storytelling

    La soutenance du projet doit refléter l'interprétation des résultats d'analyse à travers un tableau de bord. Il va falloir construire un récit convaincant basé sur des résultats des requêtes et des analyses complexes à travers des graphiques et des tableaux qui aident à soutenir le message de votre histoire pour influencer et informer les décideurs et les praticiens du groupe CHU.

    Votre présentation se focalisera sur les aspects suivants :

        Présentation de la méthodologie adoptée pour la conception et l'implémentation du système décisionnel Big Data pour la santé

        Spécification des besoins en matière de pilotage de l'activité médicale des patients

        Conception et constitution de l'entrepôt de données

        Restitution et storytelling

        Démonstration technique

    Format : Présentation orale de 20min +10min de questions/réponses