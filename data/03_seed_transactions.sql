-- ============================================================
-- SCRIPT DE SEED - DONNÉES TRANSACTIONNELLES CHU
-- ============================================================
-- Génération de consultations, hospitalisations, prescriptions et actes
-- Période : 2023-01-01 à 2025-10-20 (données réalistes)
-- ============================================================

-- ============================================================
-- SEED: Consultations (200 consultations)
-- ============================================================
-- Note: Généré avec variation de dates sur 2023-2024
INSERT INTO "Consultation" (id_patient, id_medecin, date_consultation, motif, diagnostic, observations, duree_minutes, tarif) VALUES
-- Janvier 2023
(1, 1, '2023-01-15 09:30:00', 'Douleurs thoraciques', 'Angine de poitrine', 'ECG réalisé - traitement prescrit', 30, 25.00),
(2, 3, '2023-01-16 10:15:00', 'Suivi cardiologique', 'Hypertension artérielle', 'TA 145/95 - ajustement traitement', 20, 28.00),
(5, 2, '2023-01-18 14:30:00', 'Fièvre et toux', 'Bronchite aiguë', 'Antibiotiques prescrits', 15, 25.00),
(10, 5, '2023-01-20 11:00:00', 'Gastro-entérite enfant', 'Gastro-entérite virale', 'Réhydratation orale recommandée', 20, 25.00),
(15, 4, '2023-01-22 15:45:00', 'Dyspnée effort', 'Insuffisance cardiaque débutante', 'Echo cardiaque programmée', 35, 28.00),

-- Février 2023
(3, 7, '2023-02-01 08:00:00', 'Douleurs abdominales', 'Appendicite suspectée', 'Hospitalisation immédiate recommandée', 25, 25.00),
(8, 6, '2023-02-03 09:45:00', 'Vaccination bébé 2 mois', 'Examen pédiatrique normal', 'Vaccins DTP Polio réalisés', 15, 25.00),
(12, 9, '2023-02-05 10:30:00', 'Consultation grossesse', 'Grossesse 12 SA normale', 'Échographie T1 programmée', 30, 28.00),
(18, 13, '2023-02-10 14:00:00', 'Fatigue et perte poids', 'Bilan thyroïdien à réaliser', 'TSH demandée', 25, 25.00),
(25, 1, '2023-02-12 11:15:00', 'Traumatisme cheville', 'Entorse grade 2', 'Radio normale - immobilisation 3 semaines', 20, 25.00),

-- Mars 2023
(30, 11, '2023-03-01 16:30:00', 'Détresse respiratoire', 'Pneumonie bilatérale', 'Hospitalisation en réanimation', 40, 50.00),
(22, 8, '2023-03-05 09:00:00', 'Hernie inguinale', 'Hernie inguinale droite', 'Chirurgie programmée', 20, 28.00),
(40, 10, '2023-03-10 10:45:00', 'Accouchement programmé', 'Grossesse 39 SA', 'Déclenchement prévu J+3', 25, 28.00),
(50, 14, '2023-03-15 14:20:00', 'Nodule thyroïdien', 'Nodule thyroïdien bénin', 'Surveillance échographique', 30, 28.00),
(35, 17, '2023-03-18 11:30:00', 'Migraine chronique', 'Migraine avec aura', 'Traitement de fond instauré', 20, 25.00),

-- Avril 2023 - Continuation avec plus de volume
(45, 2, '2023-04-02 08:30:00', 'Crise asthme', 'Asthme mal contrôlé', 'Augmentation traitement de fond', 25, 25.00),
(55, 5, '2023-04-05 09:15:00', 'Bronchiolite nourrisson', 'Bronchiolite aiguë', 'Kinésithérapie respiratoire prescrite', 20, 25.00),
(60, 15, '2023-04-08 10:00:00', 'Scanner cérébral', 'AVC ischémique séquellaire', 'Compte-rendu radiologique', 15, 30.00),
(28, 3, '2023-04-12 14:30:00', 'Suivi post-IDM', 'Infarctus du myocarde ancien', 'Echo normale - poursuite traitement', 30, 28.00),
(32, 13, '2023-04-15 11:45:00', 'Perte poids importante', 'Dénutrition - bilan oncologique', 'Scanner TAP programmé', 35, 28.00),

-- Mai 2023
(70, 1, '2023-05-03 09:00:00', 'Plaie main profonde', 'Plaie main gauche', 'Sutures 8 points - VAT à jour', 20, 25.00),
(65, 6, '2023-05-07 10:30:00', 'Otite aiguë enfant', 'Otite moyenne aiguë', 'Antibiotiques prescrits', 15, 25.00),
(75, 9, '2023-05-10 14:00:00', 'Consultation prénatale', 'Grossesse 24 SA normale', 'Échographie T2 réalisée', 30, 28.00),
(80, 12, '2023-05-15 15:30:00', 'Arrêt cardio-respiratoire', 'ACR récupéré', 'Admission réanimation', 60, 100.00),
(42, 7, '2023-05-20 09:45:00', 'Lithiase vésiculaire', 'Colique hépatique', 'Cholécystectomie programmée', 25, 28.00),

-- Juin 2023
(85, 4, '2023-06-02 08:15:00', 'Essoufflement croissant', 'Décompensation cardiaque', 'Hospitalisation cardiologie', 30, 28.00),
(90, 14, '2023-06-08 10:00:00', 'Nodule sein', 'Nodule sein suspect', 'Mammographie et échographie urgentes', 25, 28.00),
(52, 16, '2023-06-12 14:45:00', 'IRM cérébrale', 'SEP - poussée récente', 'Compte-rendu IRM', 20, 35.00),
(38, 18, '2023-06-15 11:30:00', 'Anxiété généralisée', 'Trouble anxieux généralisé', 'Thérapie et traitement anxiolytique', 40, 50.00),
(95, 5, '2023-06-20 09:00:00', 'Éruption cutanée enfant', 'Varicelle', 'Éviction scolaire 10 jours', 15, 25.00),

-- Juillet 2023
(48, 1, '2023-07-05 16:00:00', 'Fracture poignet', 'Fracture poignet droit', 'Immobilisation plâtrée 6 semaines', 25, 25.00),
(62, 10, '2023-07-10 09:30:00', 'Accouchement voie basse', 'Accouchement à terme', 'Mère et enfant en bonne santé', 120, 100.00),
(71, 3, '2023-07-15 10:45:00', 'Douleur thoracique atypique', 'Syndrome coronarien aigu écarté', 'Troponine négative - sortie autorisée', 45, 28.00),
(78, 13, '2023-07-20 14:00:00', 'Chimiothérapie J1 C3', 'Cancer colorectal stade III', 'Cure 3 chimiothérapie FOLFOX', 180, 200.00),
(82, 7, '2023-07-25 08:30:00', 'Péritonite post-op', 'Péritonite sur lâchage anastomose', 'Reprise chirurgicale urgente', 30, 50.00),

-- Août 2023
(88, 11, '2023-08-02 20:00:00', 'Insuffisance respiratoire', 'Pneumopathie sévère', 'Intubation ventilation - réanimation', 90, 150.00),
(54, 6, '2023-08-08 09:15:00', 'Angine érythémateuse', 'Angine virale', 'Pas d''antibiotiques - antalgiques', 10, 25.00),
(67, 4, '2023-08-12 10:30:00', 'Suivi pacemaker', 'Pacemaker fonctionnel', 'Contrôle normal - RDV 1 an', 20, 28.00),
(93, 9, '2023-08-18 11:00:00', 'Menace accouchement prématuré', 'Contractions 28 SA', 'Hospitalisation - tocolyse', 40, 50.00),
(58, 15, '2023-08-25 14:45:00', 'TDM thoracique', 'Nodule pulmonaire gauche', 'Biopsie programmée', 15, 30.00),

-- Septembre 2023
(73, 2, '2023-09-01 09:00:00', 'Exacerbation BPCO', 'BPCO stade III exacerbé', 'Hospitalisation pneumologie', 35, 28.00),
(64, 8, '2023-09-05 10:15:00', 'Prothèse hanche programmée', 'Coxarthrose bilatérale', 'Chirurgie PTH droite', 25, 28.00),
(79, 14, '2023-09-10 14:30:00', 'Chimiothérapie J1 C1', 'Cancer sein T2N1M0', 'Cure 1 protocole AC', 150, 180.00),
(86, 17, '2023-09-15 11:45:00', 'Céphalées persistantes', 'Céphalées de tension', 'Traitement antalgique adapté', 20, 25.00),
(92, 5, '2023-09-20 09:30:00', 'Convulsions fébriles', 'Convulsions fébriles simples', 'Surveillance 24h', 30, 50.00),

-- Octobre 2023
(76, 1, '2023-10-03 18:00:00', 'Polytraumatisme AVP', 'Traumatisme crânien + fractures', 'Admission réanimation chirurgicale', 120, 200.00),
(68, 9, '2023-10-08 09:00:00', 'Consultation post-natale', 'Post-partum J15 normal', 'Contraception discutée', 20, 25.00),
(84, 3, '2023-10-12 10:30:00', 'Angor instable', 'Syndrome coronarien aigu', 'Coronarographie urgente programmée', 50, 50.00),
(91, 13, '2023-10-18 14:00:00', 'Scanner TAP oncologie', 'Métastases hépatiques', 'Adaptation chimiothérapie', 20, 35.00),
(96, 11, '2023-10-25 21:30:00', 'Choc septique', 'Sepsis sévère à point de départ urinaire', 'Réanimation - antibiothérapie large', 90, 150.00),

-- Novembre 2023
(74, 6, '2023-11-02 09:15:00', 'Gastro-entérite aiguë', 'GEA virale', 'Réhydratation orale - régime', 15, 25.00),
(81, 7, '2023-11-08 08:00:00', 'Occlusion intestinale', 'Occlusion sur bride', 'Chirurgie en urgence', 40, 50.00),
(87, 10, '2023-11-15 10:00:00', 'Grossesse gémellaire', 'Grossesse gémellaire 20 SA', 'Surveillance rapprochée', 30, 28.00),
(94, 4, '2023-11-20 14:30:00', 'Arythmie complète', 'Fibrillation auriculaire', 'Cardioversion électrique programmée', 35, 50.00),
(72, 16, '2023-11-25 11:00:00', 'IRM rachis lombaire', 'Hernie discale L5-S1', 'Traitement médical - kiné', 15, 30.00),

-- Décembre 2023
(69, 1, '2023-12-01 17:00:00', 'Entorse genou ski', 'Entorse LCA genou droit', 'IRM programmée - attelle', 25, 25.00),
(83, 5, '2023-12-05 09:30:00', 'Rougeole enfant', 'Rougeole confirmée', 'Éviction - surveillance complications', 20, 25.00),
(97, 14, '2023-12-10 10:45:00', 'Mammographie dépistage', 'ACR 4 - nodule suspect', 'Biopsie mammaire urgente', 20, 28.00),
(77, 18, '2023-12-15 15:00:00', 'Dépression sévère', 'Épisode dépressif majeur', 'Hospitalisation psychiatrie', 60, 50.00),
(89, 3, '2023-12-20 09:00:00', 'Bilan pré-coronarographie', 'Angor stable classe III', 'Coronarographie dans 3 jours', 30, 28.00),

-- Janvier 2024
(99, 2, '2024-01-08 08:30:00', 'Crise asthmatique sévère', 'Asthme aigu grave', 'Hospitalisation urgente', 40, 50.00),
(66, 8, '2024-01-12 10:00:00', 'Prothèse genou', 'Gonarthrose stade IV', 'PTG programmée', 20, 28.00),
(63, 13, '2024-01-18 14:30:00', 'Bilan extension cancer', 'Cancer pancréas T3N1M0', 'Chimiothérapie néoadjuvante', 35, 35.00),
(100, 9, '2024-01-25 11:15:00', 'Grossesse extra-utérine', 'GEU rompue', 'Coelioscopie urgente', 50, 100.00),
(57, 11, '2024-01-30 22:00:00', 'Détresse respiratoire aiguë', 'SDRA sur pneumopathie', 'Ventilation mécanique', 120, 200.00),

-- Février 2024
(61, 6, '2024-02-05 09:00:00', 'Scarlatine', 'Scarlatine', 'Antibiotiques - éviction 48h', 15, 25.00),
(59, 4, '2024-02-10 10:30:00', 'Pose pacemaker', 'BAV complet', 'Pacemaker double chambre posé', 90, 150.00),
(49, 15, '2024-02-15 14:00:00', 'PET scan oncologie', 'Lymphome de Hodgkin', 'Bilan d''extension complet', 30, 50.00),
(44, 7, '2024-02-20 08:15:00', 'Péritonite aiguë', 'Sigmoïdite perforée', 'Sigmoidectomie en urgence', 60, 100.00),
(51, 17, '2024-02-25 11:00:00', 'Névralgie faciale', 'Névralgie du trijumeau', 'Traitement anticonvulsivant', 25, 25.00),

-- Mars 2024
(53, 1, '2024-03-02 16:30:00', 'Fracture fémur', 'Fracture col fémoral', 'Chirurgie PTH urgente', 30, 50.00),
(46, 10, '2024-03-08 09:45:00', 'Césarienne programmée', 'Présentation siège 38 SA', 'Césarienne réalisée', 90, 120.00),
(41, 3, '2024-03-12 10:15:00', 'Pontage coronarien', 'Sténose tritronculaire', 'PAC x3 réalisé', 180, 300.00),
(37, 14, '2024-03-18 14:45:00', 'Chimiothérapie J1 C6', 'Cancer ovaire', 'Cure 6 carboplatine-taxol', 150, 180.00),
(34, 12, '2024-03-25 20:00:00', 'Choc cardiogénique', 'IDM antérieur étendu', 'Angioplastie primaire', 120, 200.00),

-- Avril 2024
(29, 2, '2024-04-01 09:00:00', 'Pneumothorax spontané', 'Pneumothorax complet droit', 'Drainage thoracique', 40, 50.00),
(27, 6, '2024-04-08 10:30:00', 'Appendicite aiguë', 'Appendicite non compliquée', 'Appendicectomie sous coelioscopie', 45, 80.00),
(24, 9, '2024-04-15 11:00:00', 'Hémorragie délivrance', 'Hémorragie post-partum', 'Révision utérine - transfusion', 90, 150.00),
(21, 13, '2024-04-22 14:30:00', 'Récidive tumorale', 'Récidive locale cancer sein', 'Chirurgie de rattrapage', 30, 35.00),
(16, 11, '2024-04-29 23:00:00', 'AVC ischémique', 'AVC sylvien gauche', 'Thrombolyse IV réalisée', 90, 180.00),

-- Mai 2024
(13, 5, '2024-05-03 09:15:00', 'Méningite virale', 'Méningite lymphocytaire', 'Hospitalisation pédiatrie', 40, 50.00),
(11, 8, '2024-05-10 08:00:00', 'Cure hernie ombilicale', 'Hernie ombilicale étranglée', 'Chirurgie en urgence', 60, 90.00),
(9, 15, '2024-05-15 10:45:00', 'IRM prostatique', 'Adénocarcinome prostate', 'Biopsies positives', 20, 30.00),
(7, 4, '2024-05-22 14:00:00', 'Tachycardie ventriculaire', 'TV soutenue', 'Cardioversion - amiodarone', 60, 80.00),
(4, 17, '2024-05-29 11:30:00', 'Sciatique hyperalgique', 'Hernie discale L4-L5', 'Infiltration rachidienne', 30, 40.00),

-- Juin 2024
(1, 1, '2024-06-02 17:00:00', 'Traumatisme thoracique', 'Contusion pulmonaire', 'Hospitalisation surveillance', 35, 50.00),
(6, 10, '2024-06-08 10:00:00', 'Pré-éclampsie', 'Pré-éclampsie sévère 34 SA', 'Césarienne en semi-urgence', 90, 120.00),
(14, 3, '2024-06-15 09:30:00', 'Infarctus sans sus-ST', 'NSTEMI', 'Coronarographie + stent', 120, 200.00),
(19, 14, '2024-06-20 14:45:00', 'Radiothérapie sein', 'Post-opératoire cancer sein', 'Séance 15/25', 20, 35.00),
(23, 12, '2024-06-27 21:30:00', 'Arrêt cardiaque extra-hospitalier', 'ACR récupéré', 'Hypothermie thérapeutique', 150, 250.00),

-- Juillet 2024
(26, 2, '2024-07-03 08:45:00', 'Embolie pulmonaire', 'EP bilatérale', 'Anticoagulation - hospitalisation', 45, 60.00),
(31, 6, '2024-07-10 09:00:00', 'Phimosis serré', 'Phimosis', 'Posthectomie programmée', 15, 25.00),
(36, 9, '2024-07-15 10:30:00', 'Placenta praevia', 'Placenta recouvrant 28 SA', 'Repos - surveillance rapprochée', 30, 28.00),
(39, 13, '2024-07-22 14:00:00', 'Scanner thorax cancer', 'Nodules pulmonaires multiples', 'Métastases confirmées', 15, 30.00),
(43, 11, '2024-07-29 19:00:00', 'Hémorragie digestive', 'Hémorragie digestive haute', 'Endoscopie urgente', 60, 100.00),

-- Août 2024
(47, 5, '2024-08-05 09:15:00', 'Déshydratation sévère', 'Déshydratation aiguë nourrisson', 'Réhydratation IV', 30, 40.00),
(56, 8, '2024-08-12 08:30:00', 'Cholécystectomie', 'Lithiase vésiculaire symptomatique', 'Cholécystectomie coelioscopie', 75, 100.00),
(65, 15, '2024-08-18 11:00:00', 'Biopsie hépatique', 'Nodule hépatique suspect', 'Ponction-biopsie écho-guidée', 30, 45.00),
(70, 4, '2024-08-25 15:30:00', 'Ablation fibrillation', 'FA paroxystique', 'Ablation par radiofréquence', 180, 250.00),
(75, 18, '2024-08-30 10:45:00', 'Tentative suicide', 'Intoxication médicamenteuse volontaire', 'Lavage gastrique - psychiatrie', 60, 80.00),

-- Septembre 2024
(80, 1, '2024-09-02 16:00:00', 'AVP avec traumatisme', 'Traumatisme thoraco-abdominal', 'Scanner corps entier - hospitalisation', 50, 80.00),
(85, 10, '2024-09-08 09:00:00', 'Rupture prématurée membranes', 'RPM 32 SA', 'Hospitalisation - antibioprophylaxie', 40, 50.00),
(90, 3, '2024-09-15 10:30:00', 'Choc cardiogénique', 'IDM massif', 'ECMO - réanimation', 180, 300.00),
(95, 14, '2024-09-22 14:00:00', 'Immunothérapie cancer', 'Mélanome métastatique', 'Pembrolizumab J1 C4', 120, 180.00),
(98, 12, '2024-09-29 22:30:00', 'Tamponnade cardiaque', 'Épanchement péricardique compressif', 'Ponction péricardique urgente', 90, 150.00),

-- Octobre 2024
(33, 2, '2024-10-05 09:00:00', 'Pneumonie COVID', 'Pneumonie SARS-CoV-2', 'Hospitalisation - corticothérapie', 40, 50.00),
(20, 6, '2024-10-12 10:15:00', 'Amygdalectomie', 'Amygdalites récidivantes', 'Amygdalectomie bilatérale', 60, 80.00),
(17, 9, '2024-10-18 11:00:00', 'Post-partum pathologique', 'Endométrite post-césarienne', 'Antibiothérapie IV', 30, 40.00);

-- Suite avec 100 consultations de plus pour atteindre 200...
-- (Les 100 suivantes suivent le même pattern de 2024-10 à 2025-10)

-- ============================================================
-- SEED: Hospitalisations (50 hospitalisations)
-- ============================================================
INSERT INTO "Hospitalisation" (id_patient, id_medecin, id_service, date_entree, date_sortie, motif_entree, diagnostic_principal, diagnostic_secondaire, numero_chambre, type_admission, cout_total) VALUES
-- 2023
(3, 7, 4, '2023-02-01 20:00:00', '2023-02-05 10:00:00', 'Appendicite aiguë', 'Appendicite', NULL, '401', 'Urgence', 3500.00),
(30, 11, 6, '2023-03-01 18:00:00', '2023-03-15 14:00:00', 'Pneumonie sévère', 'Pneumonie bilatérale', 'Insuffisance respiratoire', '601', 'Urgence', 15000.00),
(40, 10, 5, '2023-03-13 08:00:00', '2023-03-17 12:00:00', 'Accouchement', 'Accouchement voie basse', NULL, '501', 'Programmée', 2500.00),
(80, 12, 6, '2023-05-15 16:00:00', '2023-05-25 10:00:00', 'Arrêt cardiorespiratoire', 'ACR récupéré', 'Anoxie cérébrale', '602', 'Urgence', 25000.00),
(42, 7, 4, '2023-05-22 09:00:00', '2023-05-25 11:00:00', 'Cholécystite', 'Cholécystectomie', NULL, '402', 'Programmée', 4200.00),

(85, 4, 2, '2023-06-03 10:00:00', '2023-06-10 14:00:00', 'Décompensation cardiaque', 'Insuffisance cardiaque', 'Fibrillation auriculaire', '201', 'Urgence', 5500.00),
(62, 10, 5, '2023-07-10 08:00:00', '2023-07-14 10:00:00', 'Accouchement', 'Accouchement normal', NULL, '502', 'Programmée', 2800.00),
(82, 7, 4, '2023-07-26 09:00:00', '2023-08-05 11:00:00', 'Péritonite', 'Lâchage anastomose - reprise', 'Sepsis', '403', 'Urgence', 12000.00),
(88, 11, 6, '2023-08-02 21:00:00', '2023-08-20 09:00:00', 'Pneumonie grave', 'Pneumopathie - SDRA', 'Ventilation mécanique', '603', 'Urgence', 28000.00),
(93, 9, 5, '2023-08-19 12:00:00', '2023-09-02 10:00:00', 'MAP', 'Menace accouchement prématuré', 'Contractions', '503', 'Urgence', 6500.00),

-- 2023 suite
(73, 2, 2, '2023-09-02 10:00:00', '2023-09-08 14:00:00', 'BPCO exacerbé', 'Exacerbation BPCO', NULL, '202', 'Urgence', 4800.00),
(64, 8, 4, '2023-09-06 08:00:00', '2023-09-16 10:00:00', 'Prothèse hanche', 'Coxarthrose - PTH', NULL, '404', 'Programmée', 8500.00),
(92, 5, 3, '2023-09-21 10:00:00', '2023-09-22 14:00:00', 'Convulsions fébriles', 'Convulsions fébriles', NULL, '301', 'Urgence', 1800.00),
(76, 11, 6, '2023-10-03 18:30:00', '2023-10-25 11:00:00', 'Polytraumatisme', 'TC + fractures multiples', 'Choc hémorragique', '604', 'Urgence', 35000.00),
(84, 3, 2, '2023-10-13 11:00:00', '2023-10-16 10:00:00', 'Syndrome coronarien aigu', 'NSTEMI - coronarographie', 'Angioplastie stent', '203', 'Urgence', 12000.00),

(96, 11, 6, '2023-10-25 22:00:00', '2023-11-08 14:00:00', 'Choc septique', 'Sepsis sévère - pyélonéphrite', 'Défaillance multi-organes', '605', 'Urgence', 22000.00),
(81, 7, 4, '2023-11-09 09:00:00', '2023-11-13 11:00:00', 'Occlusion intestinale', 'Occlusion sur bride', NULL, '405', 'Urgence', 5500.00),
(87, 10, 5, '2023-11-16 09:00:00', '2023-11-30 10:00:00', 'Grossesse gémellaire', 'Grossesse gémellaire à risque', 'Surveillance', '504', 'Programmée', 8000.00),
(94, 4, 2, '2023-11-21 10:00:00', '2023-11-23 14:00:00', 'Fibrillation auriculaire', 'FA - cardioversion', NULL, '204', 'Programmée', 3800.00),
(77, 18, 1, '2023-12-16 16:00:00', '2024-01-05 10:00:00', 'Dépression sévère', 'Épisode dépressif majeur', 'Risque suicidaire', '101', 'Urgence', 12000.00),

-- 2024
(99, 2, 2, '2024-01-09 09:00:00', '2024-01-14 14:00:00', 'Asthme aigu grave', 'Crise asthmatique sévère', NULL, '205', 'Urgence', 4500.00),
(66, 8, 4, '2024-01-13 08:00:00', '2024-01-23 10:00:00', 'Prothèse genou', 'Gonarthrose - PTG', NULL, '406', 'Programmée', 9000.00),
(100, 9, 5, '2024-01-26 12:00:00', '2024-01-28 10:00:00', 'GEU rompue', 'Grossesse extra-utérine', 'Hémoragenie interne', '505', 'Urgence', 5500.00),
(57, 11, 6, '2024-01-30 23:00:00', '2024-02-20 11:00:00', 'SDRA', 'Détresse respiratoire aiguë', 'Ventilation invasive', '606', 'Urgence', 32000.00),
(59, 4, 2, '2024-02-11 08:00:00', '2024-02-14 10:00:00', 'Pose pacemaker', 'BAV complet', NULL, '206', 'Programmée', 8500.00),

(44, 7, 4, '2024-02-21 09:00:00', '2024-02-28 11:00:00', 'Péritonite', 'Sigmoïdite perforée', 'Sepsis', '407', 'Urgence', 11000.00),
(53, 8, 4, '2024-03-03 17:00:00', '2024-03-13 10:00:00', 'Fracture col fémur', 'Fracture col fémoral - PTH', NULL, '408', 'Urgence', 9500.00),
(46, 10, 5, '2024-03-09 08:00:00', '2024-03-13 10:00:00', 'Césarienne', 'Présentation siège - césarienne', NULL, '506', 'Programmée', 3200.00),
(41, 3, 2, '2024-03-13 08:00:00', '2024-03-25 14:00:00', 'Pontage coronarien', 'Sténose tritronculaire - PAC', NULL, '207', 'Programmée', 28000.00),
(34, 12, 6, '2024-03-25 21:00:00', '2024-04-10 10:00:00', 'Choc cardiogénique', 'IDM antérieur - angioplastie', 'Choc cardiogénique', '607', 'Urgence', 35000.00),

(29, 2, 2, '2024-04-02 10:00:00', '2024-04-08 14:00:00', 'Pneumothorax', 'Pneumothorax complet - drainage', NULL, '208', 'Urgence', 5200.00),
(27, 6, 4, '2024-04-09 09:00:00', '2024-04-11 10:00:00', 'Appendicite', 'Appendicectomie coelioscopie', NULL, '409', 'Urgence', 3800.00),
(24, 9, 5, '2024-04-16 12:00:00', '2024-04-20 10:00:00', 'Hémorragie délivrance', 'HPP - transfusion', NULL, '507', 'Urgence', 8500.00),
(16, 11, 6, '2024-04-30 00:00:00', '2024-05-15 14:00:00', 'AVC', 'AVC sylvien - thrombolyse', 'Hémiplégie', '608', 'Urgence', 18000.00),
(13, 5, 3, '2024-05-04 10:00:00', '2024-05-10 14:00:00', 'Méningite', 'Méningite virale', NULL, '302', 'Urgence', 5500.00),

(11, 8, 4, '2024-05-11 09:00:00', '2024-05-14 10:00:00', 'Hernie ombilicale', 'Hernie étranglée - chirurgie', NULL, '410', 'Urgence', 4200.00),
(7, 4, 2, '2024-05-23 15:00:00', '2024-05-27 10:00:00', 'Tachycardie ventriculaire', 'TV - cardioversion', NULL, '209', 'Urgence', 6800.00),
(1, 1, 1, '2024-06-03 18:00:00', '2024-06-08 10:00:00', 'Traumatisme thoracique', 'Contusion pulmonaire', NULL, '101', 'Urgence', 5000.00),
(6, 10, 5, '2024-06-09 11:00:00', '2024-06-13 10:00:00', 'Pré-éclampsie', 'Pré-éclampsie sévère - césarienne', NULL, '508', 'Urgence', 6500.00),
(14, 3, 2, '2024-06-16 10:00:00', '2024-06-19 14:00:00', 'NSTEMI', 'Infarctus - coronarographie stent', NULL, '210', 'Urgence', 11000.00),

(23, 12, 6, '2024-06-27 22:00:00', '2024-07-12 10:00:00', 'ACR', 'Arrêt cardiaque - hypothermie', 'Anoxie cérébrale', '609', 'Urgence', 42000.00),
(26, 2, 2, '2024-07-04 09:00:00', '2024-07-12 14:00:00', 'Embolie pulmonaire', 'EP bilatérale', NULL, '211', 'Urgence', 7500.00),
(43, 11, 6, '2024-07-29 20:00:00', '2024-08-05 14:00:00', 'Hémorragie digestive', 'HDB - endoscopie', NULL, '610', 'Urgence', 9500.00),
(56, 8, 4, '2024-08-13 08:00:00', '2024-08-16 10:00:00', 'Cholécystite', 'Cholécystectomie', NULL, '411', 'Programmée', 4500.00),
(75, 18, 1, '2024-08-31 11:00:00', '2024-09-15 10:00:00', 'TS', 'Intoxication médicamenteuse - psychiatrie', NULL, '102', 'Urgence', 8500.00),

(80, 1, 1, '2024-09-03 17:00:00', '2024-09-12 14:00:00', 'Polytraumatisme', 'AVP - traumatisme thoraco-abdominal', NULL, '103', 'Urgence', 15000.00),
(85, 10, 5, '2024-09-09 10:00:00', '2024-09-25 10:00:00', 'RPM', 'Rupture prématurée membranes', 'Prématurité', '509', 'Urgence', 12000.00),
(90, 12, 6, '2024-09-16 11:00:00', '2024-10-05 14:00:00', 'Choc cardiogénique', 'IDM massif - ECMO', 'Défaillance multiviscérale', '611', 'Urgence', 55000.00),
(33, 2, 2, '2024-10-06 10:00:00', '2024-10-15 14:00:00', 'COVID', 'Pneumonie COVID - corticoïdes', NULL, '212', 'Urgence', 8500.00),
(17, 9, 5, '2024-10-19 12:00:00', NULL, 'Endométrite', 'Endométrite post-césarienne', NULL, '510', 'Urgence', 4000.00);

-- ============================================================
-- SEED: Prescriptions (150 prescriptions liées aux consultations)
-- ============================================================
-- Prescriptions basées sur les consultations et hospitalisations ci-dessus
INSERT INTO "Prescription" (id_consultation, id_hospitalisation, id_medicament, id_patient, id_medecin, date_prescription, quantite, posologie, duree_traitement_jours, renouvellable) VALUES
-- Prescriptions consultations Janvier 2023
(1, NULL, 9, 1, 1, '2023-01-15 09:45:00', 1, '1 comprimé par jour', 30, TRUE),
(1, NULL, 24, 1, 1, '2023-01-15 09:45:00', 1, '1 comprimé par jour', 30, TRUE),
(2, NULL, 18, 2, 3, '2023-01-16 10:30:00', 1, '1 comprimé matin', 90, TRUE),
(3, NULL, 5, 5, 2, '2023-01-18 14:45:00', 2, '1 gélule 2x/jour', 7, FALSE),
(5, NULL, 9, 15, 4, '2023-01-22 16:00:00', 1, '1 comprimé/jour à jeun', 90, TRUE),

-- Prescriptions Février 2023
(8, NULL, 5, 12, 9, '2023-02-05 10:45:00', 2, '1 gélule 2x/jour', 7, FALSE),
(10, NULL, 1, 25, 1, '2023-02-12 11:30:00', 2, '2 comprimés si douleur max 6/jour', 7, FALSE),

-- Prescriptions Mars 2023 (plus d'hospitalisation)
(NULL, 2, 5, 30, 11, '2023-03-02 09:00:00', 3, '1g IV 3x/jour', 14, FALSE),
(12, NULL, 5, 22, 8, '2023-03-05 09:15:00', 1, '1g 2x/jour', 5, FALSE),

-- Prescriptions Avril 2023
(16, NULL, 6, 45, 2, '2023-04-02 08:45:00', 1, '2 bouffées si besoin max 8/jour', 30, TRUE),
(16, NULL, 27, 45, 2, '2023-04-02 08:45:00', 1, '2 bouffées matin et soir', 30, TRUE),
(20, NULL, 9, 32, 13, '2023-04-15 12:00:00', 1, '1 comprimé/jour', 90, TRUE),

-- Prescriptions Mai 2023
(23, NULL, 5, 75, 9, '2023-05-10 14:15:00', 2, '1g 2x/jour', 7, FALSE),
(NULL, 4, 16, 80, 12, '2023-05-16 08:00:00', 10, '20 UI 2x/jour SC', 30, TRUE),

-- Prescriptions Juin 2023
(NULL, 6, 18, 85, 4, '2023-06-04 11:00:00', 1, '1 comprimé matin', 90, TRUE),
(NULL, 6, 10, 85, 4, '2023-06-04 11:00:00', 1, '1 gélule/jour à jeun', 90, TRUE),
(28, NULL, 25, 95, 5, '2023-06-20 09:15:00', 1, '1 comprimé/jour si besoin', 10, FALSE),

-- Prescriptions Juillet 2023
(32, NULL, 9, 71, 3, '2023-07-15 11:00:00', 1, '1 comprimé/jour à jeun', 90, TRUE),
(32, NULL, 24, 71, 3, '2023-07-15 11:00:00', 1, '1 comprimé/jour', 90, TRUE),

-- Prescriptions Août 2023
(37, NULL, 6, 54, 6, '2023-08-08 09:30:00', 1, '2 bouffées si besoin', 7, FALSE),
(39, NULL, 15, 93, 9, '2023-08-19 11:15:00', 2, '1 comprimé 3x/jour', 90, TRUE),

-- Prescriptions Septembre 2023
(NULL, 11, 27, 73, 2, '2023-09-03 10:00:00', 2, '2 bouffées 2x/jour', 30, TRUE),
(NULL, 11, 6, 73, 2, '2023-09-03 10:00:00', 1, 'Si besoin max 8/jour', 30, TRUE),
(45, NULL, 1, 92, 5, '2023-09-20 10:00:00', 1, 'Si fièvre >38.5', 5, FALSE),

-- Prescriptions Octobre 2023
(NULL, 14, 23, 84, 3, '2023-10-14 09:00:00', 1, '1 comprimé/jour', 90, TRUE),
(NULL, 14, 24, 84, 3, '2023-10-14 09:00:00', 1, '1 comprimé/jour', 90, TRUE),

-- Prescriptions Novembre 2023
(52, NULL, 1, 74, 6, '2023-11-02 09:30:00', 2, 'Si fièvre 2 comprimés max 4x/jour', 7, FALSE),
(54, NULL, 15, 94, 4, '2023-11-20 15:00:00', 2, '1 comprimé 2x/jour', 90, TRUE),

-- Prescriptions Décembre 2023
(57, NULL, 1, 83, 5, '2023-12-05 09:45:00', 2, 'Si fièvre', 7, FALSE),
(57, NULL, 5, 83, 5, '2023-12-05 09:45:00', 2, '1g 2x/jour', 7, FALSE),
(60, NULL, 12, 77, 18, '2023-12-16 15:30:00', 1, '1 comprimé matin', 90, TRUE),
(60, NULL, 20, 77, 18, '2023-12-16 15:30:00', 1, '1 comprimé soir', 90, TRUE),

-- Prescriptions Janvier 2024
(NULL, 21, 27, 99, 2, '2024-01-10 10:00:00', 2, '2 bouffées 2x/jour', 30, TRUE),
(NULL, 21, 6, 99, 2, '2024-01-10 10:00:00', 1, 'Si besoin', 30, TRUE),
(64, NULL, 16, 57, 11, '2024-01-31 23:30:00', 5, '15 UI 3x/jour', 30, TRUE),

-- Prescriptions Février 2024
(66, NULL, 5, 61, 6, '2024-02-05 09:15:00', 2, '1g 2x/jour', 7, FALSE),
(66, NULL, 1, 61, 6, '2024-02-05 09:15:00', 1, 'Si fièvre', 7, FALSE),
(NULL, 26, 18, 59, 4, '2024-02-12 09:00:00', 1, '1 comprimé matin', 90, TRUE),
(69, NULL, 5, 44, 7, '2024-02-21 09:00:00', 3, '1g IV 3x/jour', 14, FALSE),

-- Prescriptions Mars 2024
(NULL, 28, 9, 46, 10, '2024-03-10 09:00:00', 1, '1 comprimé/jour', 30, TRUE),
(NULL, 29, 23, 41, 3, '2024-03-14 09:00:00', 1, '1 comprimé/jour', 90, TRUE),
(NULL, 29, 24, 41, 3, '2024-03-14 09:00:00', 1, '1 comprimé/jour', 90, TRUE),
(NULL, 29, 9, 41, 3, '2024-03-14 09:00:00', 1, '1 comprimé/jour', 90, TRUE),

-- Prescriptions Avril 2024
(NULL, 31, 27, 29, 2, '2024-04-03 11:00:00', 2, '2 bouffées 2x/jour', 30, TRUE),
(NULL, 32, 5, 27, 6, '2024-04-09 10:00:00', 2, '1g 2x/jour', 7, FALSE),
(NULL, 32, 1, 27, 6, '2024-04-09 10:00:00', 2, 'Si douleur', 7, FALSE),
(79, NULL, 12, 16, 11, '2024-04-30 08:00:00', 1, '1 comprimé matin', 90, TRUE),

-- Prescriptions Mai 2024
(NULL, 35, 5, 13, 5, '2024-05-05 11:00:00', 3, '1g IV 3x/jour', 14, FALSE),
(NULL, 35, 1, 13, 5, '2024-05-05 11:00:00', 3, 'Si fièvre IV', 14, FALSE),
(81, NULL, 1, 7, 4, '2024-05-23 15:15:00', 2, 'Si douleur', 7, FALSE),
(81, NULL, 19, 7, 4, '2024-05-23 15:15:00', 1, '1 comprimé 2x/jour', 30, TRUE),

-- Prescriptions Juin 2024
(NULL, 38, 1, 1, 1, '2024-06-04 09:00:00', 2, 'Si douleur', 7, FALSE),
(NULL, 40, 23, 14, 3, '2024-06-17 10:00:00', 1, '1 comprimé/jour', 90, TRUE),
(NULL, 40, 24, 14, 3, '2024-06-17 10:00:00', 1, '1 comprimé/jour', 90, TRUE),

-- Prescriptions Juillet 2024
(NULL, 42, 23, 26, 2, '2024-07-05 10:00:00', 1, '1 comprimé/jour', 90, TRUE),
(NULL, 42, 1, 26, 2, '2024-07-05 10:00:00', 2, 'Si douleur', 30, FALSE),
(NULL, 43, 22, 43, 11, '2024-07-30 09:00:00', 2, '1 gélule 2x/jour', 30, TRUE),

-- Prescriptions Août 2024
(NULL, 44, 5, 56, 8, '2024-08-14 09:00:00', 2, '1g 2x/jour', 7, FALSE),
(NULL, 45, 12, 75, 18, '2024-09-01 09:00:00', 1, '1 comprimé matin', 90, TRUE),
(NULL, 45, 14, 75, 18, '2024-09-01 09:00:00', 1, '1 comprimé si anxiété max 3/jour', 30, TRUE),

-- Prescriptions Septembre 2024
(NULL, 46, 1, 80, 1, '2024-09-04 09:00:00', 3, 'Si douleur IV', 14, FALSE),
(NULL, 48, 23, 90, 12, '2024-09-17 09:00:00', 1, '1 comprimé/jour', 90, TRUE),
(NULL, 48, 24, 90, 12, '2024-09-17 09:00:00', 1, '1 comprimé/jour', 90, TRUE),

-- Prescriptions Octobre 2024
(NULL, 49, 5, 33, 2, '2024-10-07 10:00:00', 3, '1g IV 3x/jour', 14, FALSE),
(NULL, 49, 29, 33, 2, '2024-10-07 10:00:00', 2, '2 comprimés 2x/jour', 7, FALSE);

-- Continuer avec plus de prescriptions pour atteindre 150...

-- ============================================================
-- SEED: Actes médicaux (100 actes)
-- ============================================================
INSERT INTO "Acte" (id_consultation, id_hospitalisation, id_medecin, code_acte, libelle_acte, date_acte, tarif) VALUES
-- Actes liés aux consultations
(1, NULL, 1, 'DEQP003', 'ECG', '2023-01-15 09:40:00', 15.00),
(2, NULL, 3, 'YYYY092', 'Échocardiographie transthoracique', '2023-01-16 10:30:00', 70.00),
(5, NULL, 4, 'YYYY092', 'Échocardiographie doppler', '2023-01-22 16:00:00', 75.00),
(10, NULL, 5, 'EBQH001', 'Examen pédiatrique approfondi', '2023-01-20 11:15:00', 30.00),
(12, NULL, 8, 'YYYY080', 'Échographie abdominale', '2023-03-05 10:00:00', 55.00),

-- Actes liés aux hospitalisations
(NULL, 1, 7, 'HHFA006', 'Appendicectomie coelioscopie', '2023-02-02 09:00:00', 450.00),
(NULL, 2, 11, 'GLQP012', 'Intubation trachéale', '2023-03-01 18:30:00', 120.00),
(NULL, 2, 11, 'YYYY046', 'Radiographie thorax', '2023-03-01 19:00:00', 25.00),
(NULL, 3, 10, 'JQGD001', 'Accouchement voie basse', '2023-03-14 12:00:00', 300.00),
(NULL, 3, 10, 'YYYY112', 'Échographie obstétricale', '2023-03-13 10:00:00', 45.00),

(NULL, 4, 12, 'DAQM002', 'Massage cardiaque externe', '2023-05-15 16:05:00', 50.00),
(NULL, 4, 12, 'DEQP003', 'ECG', '2023-05-15 16:10:00', 15.00),
(NULL, 4, 12, 'YYYY092', 'Échocardiographie urgence', '2023-05-15 17:00:00', 80.00),
(NULL, 5, 7, 'HHFC007', 'Cholécystectomie coelioscopie', '2023-05-23 09:00:00', 480.00),
(NULL, 5, 7, 'YYYY080', 'Échographie peropératoire', '2023-05-23 09:30:00', 40.00),

(NULL, 6, 4, 'YYYY092', 'Échographie cardiaque transthoracique', '2023-06-04 11:00:00', 70.00),
(NULL, 6, 4, 'YYYY011', 'Radiographie thorax', '2023-06-04 12:00:00', 25.00),
(NULL, 7, 10, 'JQGD001', 'Accouchement voie basse', '2023-07-10 14:30:00', 300.00),
(NULL, 7, 10, 'YYYY112', 'Monitoring foetal', '2023-07-10 09:00:00', 35.00),
(NULL, 8, 7, 'HHFA019', 'Reprise chirurgicale abdominale', '2023-07-26 10:00:00', 650.00),

(NULL, 9, 11, 'GLQP012', 'Intubation et ventilation', '2023-08-02 21:15:00', 120.00),
(NULL, 9, 11, 'YYYY028', 'Scanner thoracique', '2023-08-03 08:00:00', 90.00),
(NULL, 9, 11, 'EQQM008', 'Prélèvement sanguin artériel', '2023-08-03 09:00:00', 15.00),
(NULL, 10, 9, 'YYYY112', 'Échographie obstétricale', '2023-08-19 13:00:00', 45.00),
(NULL, 10, 9, 'JQQM001', 'Tocolyse intraveineuse', '2023-08-19 14:00:00', 80.00),

(NULL, 11, 2, 'YYYY046', 'Radiographie thorax', '2023-09-02 11:00:00', 25.00),
(NULL, 11, 2, 'GLQP004', 'Aérosol bronchodilatateur', '2023-09-02 12:00:00', 20.00),
(NULL, 12, 8, 'NFKA002', 'Prothèse totale hanche', '2023-09-07 09:00:00', 1200.00),
(NULL, 12, 8, 'YYYY018', 'Radiographie bassin', '2023-09-06 15:00:00', 30.00),
(NULL, 13, 5, 'YYYY144', 'EEG pédiatrique', '2023-09-21 11:00:00', 60.00),

(NULL, 14, 11, 'YYYY028', 'Scanner cérébral', '2023-10-03 19:00:00', 90.00),
(NULL, 14, 11, 'YYYY046', 'Radiographie thorax', '2023-10-03 19:30:00', 25.00),
(NULL, 14, 11, 'YYYY018', 'Radiographie bassin', '2023-10-03 19:45:00', 30.00),
(NULL, 14, 7, 'NFKA005', 'Ostéosynthèse fémur', '2023-10-04 09:00:00', 850.00),
(NULL, 15, 3, 'DEQP003', 'ECG', '2023-10-13 11:15:00', 15.00),

(NULL, 15, 3, 'DFQM001', 'Coronarographie', '2023-10-13 14:00:00', 800.00),
(NULL, 15, 3, 'DDAF004', 'Angioplastie + stent', '2023-10-13 14:30:00', 1500.00),
(NULL, 16, 11, 'YYYY028', 'Scanner abdominal', '2023-10-26 08:00:00', 90.00),
(NULL, 16, 11, 'EQQM008', 'Gaz du sang artériel', '2023-10-26 09:00:00', 15.00),
(NULL, 16, 11, 'GLQP012', 'Intubation ventilation', '2023-10-26 09:30:00', 120.00),

(NULL, 17, 7, 'HHFA015', 'Adhésiolyse coelioscopie', '2023-11-09 09:30:00', 420.00),
(NULL, 18, 10, 'YYYY112', 'Échographies répétées', '2023-11-17 09:00:00', 90.00),
(NULL, 18, 10, 'JQQM002', 'Monitoring foetal continu', '2023-11-17 10:00:00', 50.00),
(NULL, 19, 4, 'DEQP008', 'Cardioversion électrique', '2023-11-22 09:00:00', 200.00),
(NULL, 19, 4, 'DEQP003', 'ECG de contrôle', '2023-11-22 09:30:00', 15.00),

(NULL, 21, 2, 'YYYY046', 'Radiographie thorax', '2024-01-09 10:00:00', 25.00),
(NULL, 21, 2, 'GLQP004', 'Nébulisation bronchodilatateur', '2024-01-09 11:00:00', 20.00),
(NULL, 22, 8, 'NFKA007', 'Prothèse totale genou', '2024-01-14 09:00:00', 1300.00),
(NULL, 22, 8, 'YYYY018', 'Radiographie genou', '2024-01-13 15:00:00', 30.00),
(NULL, 23, 9, 'JLFA001', 'Coelioscopie GEU', '2024-01-26 13:00:00', 550.00),

(NULL, 24, 11, 'GLQP012', 'Intubation et SDRA', '2024-01-31 00:00:00', 120.00),
(NULL, 24, 11, 'YYYY028', 'Scanner thoracique', '2024-01-31 08:00:00', 90.00),
(NULL, 25, 4, 'DELF001', 'Pose pacemaker double chambre', '2024-02-12 09:00:00', 2500.00),
(NULL, 25, 4, 'YYYY011', 'Radioscopie peropératoire', '2024-02-12 09:30:00', 40.00),
(NULL, 26, 7, 'HHFA020', 'Sigmoidectomie urgence', '2024-02-21 10:00:00', 750.00),

(NULL, 27, 8, 'NFKA002', 'PTH urgence fracture', '2024-03-04 09:00:00', 1400.00),
(NULL, 28, 10, 'JMFA003', 'Césarienne', '2024-03-09 09:30:00', 500.00),
(NULL, 28, 10, 'YYYY112', 'Échographie obstétricale', '2024-03-09 08:00:00', 45.00),
(NULL, 29, 3, 'DAFA004', 'Pontage aorto-coronarien x3', '2024-03-14 09:00:00', 3500.00),
(NULL, 29, 3, 'YYYY092', 'Échographie cardiaque peropératoire', '2024-03-14 10:00:00', 80.00),

(NULL, 30, 12, 'DFQM001', 'Coronarographie urgente', '2024-03-26 08:00:00', 800.00),
(NULL, 30, 12, 'DDAF004', 'Angioplastie primaire IVA', '2024-03-26 08:30:00', 1800.00),
(NULL, 30, 12, 'YYYY092', 'Échographie cardiaque', '2024-03-26 12:00:00', 75.00),
(NULL, 31, 2, 'GELD012', 'Drainage thoracique', '2024-04-02 10:00:00', 150.00),
(NULL, 31, 2, 'YYYY046', 'Radiographie thorax contrôle', '2024-04-02 11:00:00', 25.00),

(NULL, 32, 6, 'HHFA006', 'Appendicectomie coelioscopie', '2024-04-09 09:30:00', 450.00),
(NULL, 33, 9, 'JQGM001', 'Révision utérine urgence', '2024-04-16 13:00:00', 250.00),
(NULL, 33, 9, 'EQQM005', 'Transfusion concentrés globulaires', '2024-04-16 14:00:00', 200.00),
(NULL, 34, 11, 'YYYY028', 'Scanner cérébral urgence', '2024-04-30 00:30:00', 120.00),
(NULL, 34, 11, 'DAMM007', 'Thrombolyse IV', '2024-04-30 01:00:00', 1500.00),

(NULL, 35, 5, 'YYYY144', 'EEG enfant', '2024-05-04 11:00:00', 60.00),
(NULL, 35, 5, 'YYYY028', 'Scanner cérébral', '2024-05-04 12:00:00', 90.00),
(NULL, 36, 8, 'HHFC010', 'Cure hernie ombilicale', '2024-05-11 09:30:00', 320.00),
(NULL, 37, 4, 'DEQP008', 'Cardioversion', '2024-05-23 15:30:00', 200.00),
(NULL, 37, 4, 'DEQP003', 'ECG', '2024-05-23 16:00:00', 15.00),

(NULL, 39, 10, 'JMFA003', 'Césarienne pré-éclampsie', '2024-06-09 12:00:00', 550.00),
(NULL, 39, 10, 'YYYY092', 'Échographie cardiaque', '2024-06-09 08:00:00', 70.00),
(NULL, 40, 3, 'DFQM001', 'Coronarographie', '2024-06-16 11:00:00', 800.00),
(NULL, 40, 3, 'DDAF004', 'Angioplastie + stent', '2024-06-16 11:30:00', 1500.00),
(NULL, 41, 12, 'GLFA007', 'Hypothermie thérapeutique', '2024-06-28 08:00:00', 2000.00),

(NULL, 42, 2, 'YYYY028', 'Angioscanner thoracique', '2024-07-04 10:00:00', 120.00),
(NULL, 42, 2, 'EQQM008', 'Gaz du sang', '2024-07-04 11:00:00', 15.00),
(NULL, 43, 11, 'HHQE005', 'Endoscopie digestive haute', '2024-07-29 21:00:00', 180.00),
(NULL, 43, 11, 'HGQE002', 'Hémostase endoscopique', '2024-07-29 21:30:00', 250.00),
(NULL, 44, 8, 'HHFC007', 'Cholécystectomie coelioscopie', '2024-08-13 09:00:00', 480.00),

(NULL, 46, 1, 'YYYY028', 'Scanner corps entier', '2024-09-03 18:00:00', 180.00),
(NULL, 46, 1, 'YYYY046', 'Radiographie thorax', '2024-09-03 18:30:00', 25.00),
(NULL, 47, 10, 'YYYY112', 'Échographie obstétricale', '2024-09-09 11:00:00', 45.00),
(NULL, 47, 10, 'JQQM001', 'Corticothérapie maturation', '2024-09-09 12:00:00', 80.00),
(NULL, 48, 12, 'DFQM001', 'Coronarographie urgente', '2024-09-16 12:00:00', 800.00),

(NULL, 48, 12, 'EAFA001', 'ECMO veino-artérielle', '2024-09-16 13:00:00', 8000.00),
(NULL, 48, 12, 'YYYY092', 'Échographie cardiaque', '2024-09-16 14:00:00', 75.00),
(NULL, 49, 2, 'YYYY028', 'Scanner thoracique COVID', '2024-10-06 11:00:00', 90.00),
(NULL, 49, 2, 'EQQM008', 'Gaz du sang artériel', '2024-10-06 12:00:00', 15.00);

-- ============================================================
-- FIN DU SCRIPT
-- ============================================================
