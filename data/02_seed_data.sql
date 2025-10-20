-- ============================================================
-- SCRIPT DE SEED - DONNÉES DE TEST CHU
-- ============================================================
-- Données réalistes pour tests et développement
-- ============================================================

-- ============================================================
-- SEED: Services (8 services)
-- ============================================================
INSERT INTO "Service" (nom_service, type_service, capacite_lits, etage, batiment) VALUES
('Urgences', 'Urgences', 30, 0, 'Bâtiment A'),
('Cardiologie', 'Médecine', 25, 2, 'Bâtiment B'),
('Pédiatrie', 'Médecine', 20, 3, 'Bâtiment C'),
('Chirurgie Générale', 'Chirurgie', 35, 1, 'Bâtiment B'),
('Maternité', 'Obstétrique', 40, 4, 'Bâtiment C'),
('Réanimation', 'Soins Intensifs', 15, 1, 'Bâtiment A'),
('Oncologie', 'Médecine', 30, 2, 'Bâtiment D'),
('Radiologie', 'Imagerie', 0, -1, 'Bâtiment A');

-- ============================================================
-- SEED: Médecins (20 médecins)
-- ============================================================
INSERT INTO "Medecin" (nom, prenom, specialite, telephone, email, id_service, date_embauche) VALUES
-- Urgences
('Dubois', 'Sophie', 'Médecine d''urgence', '01.45.67.89.01', 'sophie.dubois@chu.fr', 1, '2018-03-15'),
('Martin', 'Thomas', 'Médecine d''urgence', '01.45.67.89.02', 'thomas.martin@chu.fr', 1, '2019-09-01'),

-- Cardiologie
('Bernard', 'Claire', 'Cardiologie', '01.45.67.89.03', 'claire.bernard@chu.fr', 2, '2015-06-20'),
('Petit', 'Marc', 'Cardiologie', '01.45.67.89.04', 'marc.petit@chu.fr', 2, '2017-11-10'),

-- Pédiatrie
('Robert', 'Julie', 'Pédiatrie', '01.45.67.89.05', 'julie.robert@chu.fr', 3, '2016-02-28'),
('Richard', 'Antoine', 'Pédiatrie', '01.45.67.89.06', 'antoine.richard@chu.fr', 3, '2020-01-15'),

-- Chirurgie
('Durand', 'Laurent', 'Chirurgie générale', '01.45.67.89.07', 'laurent.durand@chu.fr', 4, '2012-05-01'),
('Simon', 'Isabelle', 'Chirurgie générale', '01.45.67.89.08', 'isabelle.simon@chu.fr', 4, '2014-09-15'),

-- Maternité
('Michel', 'Nathalie', 'Gynécologie-Obstétrique', '01.45.67.89.09', 'nathalie.michel@chu.fr', 5, '2013-07-20'),
('Lefebvre', 'Pierre', 'Gynécologie-Obstétrique', '01.45.67.89.10', 'pierre.lefebvre@chu.fr', 5, '2019-04-01'),

-- Réanimation
('Moreau', 'David', 'Réanimation', '01.45.67.89.11', 'david.moreau@chu.fr', 6, '2011-10-15'),
('Laurent', 'Anne', 'Réanimation', '01.45.67.89.12', 'anne.laurent@chu.fr', 6, '2016-12-01'),

-- Oncologie
('Garcia', 'François', 'Oncologie', '01.45.67.89.13', 'francois.garcia@chu.fr', 7, '2014-03-10'),
('Martinez', 'Marie', 'Oncologie', '01.45.67.89.14', 'marie.martinez@chu.fr', 7, '2018-06-25'),

-- Radiologie
('Roux', 'Patrick', 'Radiologie', '01.45.67.89.15', 'patrick.roux@chu.fr', 8, '2015-08-01'),
('Blanc', 'Caroline', 'Radiologie', '01.45.67.89.16', 'caroline.blanc@chu.fr', 8, '2020-02-15'),

-- Médecins polyvalents
('Lopez', 'Jean', 'Médecine générale', '01.45.67.89.17', 'jean.lopez@chu.fr', 1, '2017-05-20'),
('Fontaine', 'Sylvie', 'Médecine générale', '01.45.67.89.18', 'sylvie.fontaine@chu.fr', 2, '2019-11-01'),
('Girard', 'Olivier', 'Anesthésie', '01.45.67.89.19', 'olivier.girard@chu.fr', 6, '2013-01-15'),
('Dupont', 'Laure', 'Psychiatrie', '01.45.67.89.20', 'laure.dupont@chu.fr', 1, '2021-03-01');

-- ============================================================
-- SEED: Patients (100 patients avec données PII)
-- ============================================================
INSERT INTO "Patient" (nom, prenom, date_naissance, sexe, numero_securite_sociale, adresse, code_postal, ville, telephone, email, groupe_sanguin, date_inscription) VALUES
-- Patients 1-20
('Durand', 'Jean', '1965-03-15', 'M', '165037512345678', '12 rue de la Paix', '75001', 'Paris', '06.12.34.56.78', 'jean.durand@email.fr', 'A+', '2023-01-15'),
('Martin', 'Marie', '1978-07-22', 'F', '278077512345679', '45 avenue des Champs', '75008', 'Paris', '06.23.45.67.89', 'marie.martin@email.fr', 'O+', '2023-02-20'),
('Bernard', 'Pierre', '1982-11-30', 'M', '182117512345680', '8 boulevard Victor Hugo', '69003', 'Lyon', '06.34.56.78.90', 'pierre.bernard@email.fr', 'B+', '2023-03-10'),
('Dubois', 'Sophie', '1990-05-18', 'F', '290057512345681', '23 rue du Commerce', '13001', 'Marseille', '06.45.67.89.01', 'sophie.dubois@email.fr', 'AB+', '2023-01-25'),
('Thomas', 'Luc', '1955-09-12', 'M', '155097512345682', '67 avenue de la République', '31000', 'Toulouse', '06.56.78.90.12', 'luc.thomas@email.fr', 'O-', '2023-04-05'),
('Robert', 'Claire', '1988-02-28', 'F', '288027512345683', '34 rue Saint-Antoine', '44000', 'Nantes', '06.67.89.01.23', 'claire.robert@email.fr', 'A-', '2023-02-15'),
('Petit', 'Marc', '1972-06-14', 'M', '172067512345684', '89 boulevard de la Liberté', '59000', 'Lille', '06.78.90.12.34', 'marc.petit@email.fr', 'B-', '2023-05-20'),
('Richard', 'Julie', '1995-12-03', 'F', '295127512345685', '56 avenue Jean Jaurès', '67000', 'Strasbourg', '06.89.01.23.45', 'julie.richard@email.fr', 'AB-', '2023-03-30'),
('Moreau', 'David', '1968-04-25', 'M', '168047512345686', '12 rue de la Gare', '33000', 'Bordeaux', '06.90.12.34.56', 'david.moreau@email.fr', 'A+', '2023-01-10'),
('Simon', 'Isabelle', '1985-08-17', 'F', '285087512345687', '78 avenue du Général de Gaulle', '06000', 'Nice', '06.01.23.45.67', 'isabelle.simon@email.fr', 'O+', '2023-06-12'),
('Laurent', 'Anne', '1992-01-09', 'F', '292017512345688', '45 rue de la Mairie', '35000', 'Rennes', '06.12.34.56.79', 'anne.laurent@email.fr', 'B+', '2023-02-28'),
('Lefebvre', 'Pierre', '1960-10-21', 'M', '160107512345689', '23 boulevard Haussmann', '75009', 'Paris', '06.23.45.67.80', 'pierre.lefebvre@email.fr', 'A-', '2023-04-15'),
('Michel', 'Nathalie', '1987-03-07', 'F', '287037512345690', '67 rue de Rivoli', '75004', 'Paris', '06.34.56.78.91', 'nathalie.michel@email.fr', 'O-', '2023-05-01'),
('Garcia', 'François', '1975-07-19', 'M', '175077512345691', '34 avenue Foch', '69006', 'Lyon', '06.45.67.89.02', 'francois.garcia@email.fr', 'AB+', '2023-01-20'),
('Martinez', 'Marie', '1993-11-26', 'F', '293117512345692', '89 rue de la Paix', '13006', 'Marseille', '06.56.78.90.13', 'marie.martinez@email.fr', 'B-', '2023-03-25'),
('Roux', 'Patrick', '1970-05-08', 'M', '170057512345693', '12 boulevard de la Plage', '44100', 'Nantes', '06.67.89.01.24', 'patrick.roux@email.fr', 'A+', '2023-02-10'),
('Blanc', 'Caroline', '1989-09-14', 'F', '289097512345694', '56 avenue de la Mer', '06200', 'Nice', '06.78.90.12.35', 'caroline.blanc@email.fr', 'O+', '2023-06-20'),
('Lopez', 'Jean', '1963-02-02', 'M', '163027512345695', '78 rue du Port', '33100', 'Bordeaux', '06.89.01.23.46', 'jean.lopez@email.fr', 'B+', '2023-04-08'),
('Fontaine', 'Sylvie', '1991-06-28', 'F', '291067512345696', '23 avenue des Fleurs', '31100', 'Toulouse', '06.90.12.34.57', 'sylvie.fontaine@email.fr', 'AB-', '2023-05-15'),
('Girard', 'Olivier', '1977-12-11', 'M', '177127512345697', '45 rue de l''Église', '67100', 'Strasbourg', '06.01.23.45.68', 'olivier.girard@email.fr', 'A-', '2023-03-05'),

-- Patients 21-40 (avec plus de diversité)
('Dupont', 'Laure', '1984-04-16', 'F', '284047512345698', '67 boulevard Voltaire', '75011', 'Paris', '06.12.34.56.80', 'laure.dupont@email.fr', 'O-', '2023-01-30'),
('Boyer', 'Antoine', '1969-08-23', 'M', '169087512345699', '12 rue Pasteur', '59800', 'Lille', '06.23.45.67.81', 'antoine.boyer@email.fr', 'B+', '2023-02-25'),
('Rousseau', 'Emma', '1996-12-05', 'F', '296127512345700', '89 avenue Mozart', '75016', 'Paris', '06.34.56.78.92', 'emma.rousseau@email.fr', 'A+', '2023-04-18'),
('Leclerc', 'Lucas', '1961-01-19', 'M', '161017512345701', '34 rue de la Fontaine', '69001', 'Lyon', '06.45.67.89.03', 'lucas.leclerc@email.fr', 'O+', '2023-05-22'),
('Bonnet', 'Léa', '1994-05-27', 'F', '294057512345702', '56 boulevard Saint-Michel', '75005', 'Paris', '06.56.78.90.14', 'lea.bonnet@email.fr', 'AB+', '2023-03-12'),
('André', 'Hugo', '1973-09-08', 'M', '173097512345703', '78 avenue Pasteur', '13002', 'Marseille', '06.67.89.01.25', 'hugo.andre@email.fr', 'B-', '2023-06-08'),
('François', 'Chloé', '1986-02-14', 'F', '286027512345704', '23 rue Victor Hugo', '31200', 'Toulouse', '06.78.90.12.36', 'chloe.francois@email.fr', 'A-', '2023-01-28'),
('Mercier', 'Louis', '1998-06-30', 'M', '298067512345705', '45 avenue de la Gare', '44200', 'Nantes', '06.89.01.23.47', 'louis.mercier@email.fr', 'O-', '2023-02-14'),
('Guerin', 'Camille', '1976-10-12', 'F', '276107512345706', '67 rue de la République', '67200', 'Strasbourg', '06.90.12.34.58', 'camille.guerin@email.fr', 'B+', '2023-04-22'),
('Fournier', 'Arthur', '1983-03-24', 'M', '183037512345707', '12 boulevard de la Paix', '33200', 'Bordeaux', '06.01.23.45.69', 'arthur.fournier@email.fr', 'A+', '2023-05-30'),
('Morel', 'Manon', '1971-07-06', 'F', '271077512345708', '89 avenue Jean Jaurès', '06100', 'Nice', '06.12.34.56.81', 'manon.morel@email.fr', 'O+', '2023-03-18'),
('Giraud', 'Nathan', '1997-11-18', 'M', '297117512345709', '34 rue de la Liberté', '35200', 'Rennes', '06.23.45.67.82', 'nathan.giraud@email.fr', 'AB-', '2023-06-25'),
('Lambert', 'Sarah', '1964-04-01', 'F', '264047512345710', '56 boulevard Haussmann', '75008', 'Paris', '06.34.56.78.93', 'sarah.lambert@email.fr', 'B-', '2023-02-05'),
('Renard', 'Gabriel', '1992-08-13', 'M', '292087512345711', '78 rue de Rivoli', '75001', 'Paris', '06.45.67.89.04', 'gabriel.renard@email.fr', 'A-', '2023-04-25'),
('Vincent', 'Inès', '1979-12-25', 'F', '279127512345712', '23 avenue Foch', '69003', 'Lyon', '06.56.78.90.15', 'ines.vincent@email.fr', 'O-', '2023-01-12'),
('Muller', 'Tom', '1988-05-07', 'M', '288057512345713', '45 rue de la Paix', '13003', 'Marseille', '06.67.89.01.26', 'tom.muller@email.fr', 'AB+', '2023-05-08'),
('Faure', 'Zoé', '1966-09-19', 'F', '266097512345714', '67 boulevard de la Plage', '44300', 'Nantes', '06.78.90.12.37', 'zoe.faure@email.fr', 'B+', '2023-03-20'),
('Garnier', 'Ethan', '1995-01-31', 'M', '295017512345715', '12 avenue de la Mer', '06300', 'Nice', '06.89.01.23.48', 'ethan.garnier@email.fr', 'A+', '2023-06-15'),
('Barbier', 'Jade', '1974-06-13', 'F', '274067512345716', '89 rue du Port', '33300', 'Bordeaux', '06.90.12.34.59', 'jade.barbier@email.fr', 'O+', '2023-02-22'),
('Robin', 'Raphaël', '1981-10-25', 'M', '281107512345717', '34 avenue des Fleurs', '31300', 'Toulouse', '06.01.23.45.70', 'raphael.robin@email.fr', 'B-', '2023-04-30'),

-- Patients 41-60
('Perrin', 'Léna', '1999-03-09', 'F', '299037512345718', '56 rue de l''Église', '67300', 'Strasbourg', '06.12.34.56.82', 'lena.perrin@email.fr', 'A-', '2023-01-08'),
('Meyer', 'Mathis', '1967-07-21', 'M', '167077512345719', '78 boulevard Voltaire', '75010', 'Paris', '06.23.45.67.83', 'mathis.meyer@email.fr', 'O-', '2023-05-18'),
('Colin', 'Lola', '1993-11-03', 'F', '293117512345720', '23 rue Pasteur', '59900', 'Lille', '06.34.56.78.94', 'lola.colin@email.fr', 'B+', '2023-03-28'),
('Chevalier', 'Adam', '1975-02-15', 'M', '175027512345721', '45 avenue Mozart', '75017', 'Paris', '06.45.67.89.05', 'adam.chevalier@email.fr', 'AB+', '2023-06-10'),
('Bertrand', 'Alice', '1990-06-27', 'F', '290067512345722', '67 rue de la Fontaine', '69002', 'Lyon', '06.56.78.90.16', 'alice.bertrand@email.fr', 'A+', '2023-02-18'),
('Clement', 'Mathéo', '1962-10-09', 'M', '162107512345723', '12 boulevard Saint-Michel', '75006', 'Paris', '06.67.89.01.27', 'matheo.clement@email.fr', 'O+', '2023-04-12'),
('Dumas', 'Louise', '1985-01-21', 'F', '285017512345724', '89 avenue Pasteur', '13004', 'Marseille', '06.78.90.12.38', 'louise.dumas@email.fr', 'B-', '2023-05-25'),
('Denis', 'Noah', '1998-05-04', 'M', '298057512345725', '34 rue Victor Hugo', '31400', 'Toulouse', '06.89.01.23.49', 'noah.denis@email.fr', 'AB-', '2023-01-16'),
('Masson', 'Mia', '1972-09-16', 'F', '272097512345726', '56 avenue de la Gare', '44400', 'Nantes', '06.90.12.34.60', 'mia.masson@email.fr', 'A-', '2023-03-08'),
('Roussel', 'Enzo', '1987-12-28', 'M', '287127512345727', '78 rue de la République', '67400', 'Strasbourg', '06.01.23.45.71', 'enzo.roussel@email.fr', 'O-', '2023-06-22'),
('Legrand', 'Juliette', '1965-04-10', 'F', '265047512345728', '23 boulevard de la Paix', '33400', 'Bordeaux', '06.12.34.56.83', 'juliette.legrand@email.fr', 'B+', '2023-02-28'),
('Henry', 'Maxime', '1994-08-22', 'M', '294087512345729', '45 avenue Jean Jaurès', '06400', 'Nice', '06.23.45.67.84', 'maxime.henry@email.fr', 'A+', '2023-05-05'),
('Lemoine', 'Clara', '1976-12-04', 'F', '276127512345730', '67 rue de la Liberté', '35400', 'Rennes', '06.34.56.78.95', 'clara.lemoine@email.fr', 'O+', '2023-01-22'),
('Rolland', 'Timéo', '1991-03-17', 'M', '291037512345731', '12 boulevard Haussmann', '75007', 'Paris', '06.45.67.89.06', 'timeo.rolland@email.fr', 'AB+', '2023-04-18'),
('Leroux', 'Rose', '1969-07-29', 'F', '269077512345732', '89 rue de Rivoli', '75002', 'Paris', '06.56.78.90.17', 'rose.leroux@email.fr', 'B-', '2023-06-05'),
('Caron', 'Théo', '1996-11-11', 'M', '296117512345733', '34 avenue Foch', '69004', 'Lyon', '06.67.89.01.28', 'theo.caron@email.fr', 'A-', '2023-03-15'),
('Mathieu', 'Anna', '1973-02-23', 'F', '273027512345734', '56 rue de la Paix', '13005', 'Marseille', '06.78.90.12.39', 'anna.mathieu@email.fr', 'O-', '2023-02-08'),
('Aubert', 'Sacha', '1989-06-06', 'M', '289067512345735', '78 boulevard de la Plage', '44500', 'Nantes', '06.89.01.23.50', 'sacha.aubert@email.fr', 'B+', '2023-05-20'),
('Fernandez', 'Romane', '1963-10-18', 'F', '263107512345736', '23 avenue de la Mer', '06500', 'Nice', '06.90.12.34.61', 'romane.fernandez@email.fr', 'AB-', '2023-01-05'),
('Vidal', 'Paul', '1992-01-30', 'M', '292017512345737', '45 rue du Port', '33500', 'Bordeaux', '06.01.23.45.72', 'paul.vidal@email.fr', 'A+', '2023-04-28'),

-- Patients 61-80
('Philippe', 'Eva', '1978-05-13', 'F', '278057512345738', '67 avenue des Fleurs', '31500', 'Toulouse', '06.12.34.56.84', 'eva.philippe@email.fr', 'O+', '2023-06-18'),
('Gonzalez', 'Axel', '1986-09-25', 'M', '286097512345739', '12 rue de l''Église', '67500', 'Strasbourg', '06.23.45.67.85', 'axel.gonzalez@email.fr', 'B-', '2023-03-02'),
('Sanchez', 'Maëlys', '1964-12-07', 'F', '264127512345740', '89 boulevard Voltaire', '75012', 'Paris', '06.34.56.78.96', 'maelys.sanchez@email.fr', 'A-', '2023-05-12'),
('Joly', 'Robin', '1995-04-20', 'M', '295047512345741', '34 rue Pasteur', '59100', 'Lille', '06.45.67.89.07', 'robin.joly@email.fr', 'O-', '2023-02-15'),
('Picard', 'Lily', '1971-08-02', 'F', '271087512345742', '56 avenue Mozart', '75018', 'Paris', '06.56.78.90.18', 'lily.picard@email.fr', 'AB+', '2023-06-28'),
('Renaud', 'Nolan', '1997-11-14', 'M', '297117512345743', '78 rue de la Fontaine', '69005', 'Lyon', '06.67.89.01.29', 'nolan.renaud@email.fr', 'B+', '2023-01-18'),
('Roy', 'Margaux', '1968-03-27', 'F', '268037512345744', '23 boulevard Saint-Michel', '75013', 'Paris', '06.78.90.12.40', 'margaux.roy@email.fr', 'A+', '2023-04-08'),
('Lucas', 'Kylian', '1993-07-09', 'M', '293077512345745', '45 avenue Pasteur', '13006', 'Marseille', '06.89.01.23.51', 'kylian.lucas@email.fr', 'O+', '2023-05-28'),
('Remy', 'Elena', '1975-10-21', 'F', '275107512345746', '67 rue Victor Hugo', '31600', 'Toulouse', '06.90.12.34.62', 'elena.remy@email.fr', 'B-', '2023-02-20'),
('Brunet', 'Hugo', '1991-02-03', 'M', '291027512345747', '12 avenue de la Gare', '44600', 'Nantes', '06.01.23.45.73', 'hugo.brunet@email.fr', 'AB-', '2023-06-12'),
('Schmitt', 'Louane', '1962-06-16', 'F', '262067512345748', '89 rue de la République', '67600', 'Strasbourg', '06.12.34.56.85', 'louane.schmitt@email.fr', 'A-', '2023-03-22'),
('Brun', 'Tom', '1988-10-28', 'M', '288107512345749', '34 boulevard de la Paix', '33600', 'Bordeaux', '06.23.45.67.86', 'tom.brun@email.fr', 'O-', '2023-01-28'),
('Blanchard', 'Océane', '1974-01-10', 'F', '274017512345750', '56 avenue Jean Jaurès', '06600', 'Nice', '06.34.56.78.97', 'oceane.blanchard@email.fr', 'B+', '2023-05-15'),
('Guillot', 'Nathan', '1999-05-23', 'M', '299057512345751', '78 rue de la Liberté', '35600', 'Rennes', '06.45.67.89.08', 'nathan.guillot@email.fr', 'A+', '2023-02-25'),
('Rousseau', 'Nina', '1967-09-05', 'F', '267097512345752', '23 boulevard Haussmann', '75014', 'Paris', '06.56.78.90.19', 'nina.rousseau@email.fr', 'O+', '2023-06-08'),
('Weber', 'Mathis', '1996-12-17', 'M', '296127512345753', '45 rue de Rivoli', '75003', 'Paris', '06.67.89.01.30', 'mathis.weber@email.fr', 'AB+', '2023-04-02'),
('Lacroix', 'Emma', '1972-04-30', 'F', '272047512345754', '67 avenue Foch', '69006', 'Lyon', '06.78.90.12.41', 'emma.lacroix@email.fr', 'B-', '2023-01-15'),
('Dupuis', 'Louis', '1990-08-12', 'M', '290087512345755', '12 rue de la Paix', '13007', 'Marseille', '06.89.01.23.52', 'louis.dupuis@email.fr', 'A-', '2023-05-22'),
('Marchand', 'Zoé', '1965-11-24', 'F', '265117512345756', '89 boulevard de la Plage', '44700', 'Nantes', '06.90.12.34.63', 'zoe.marchand@email.fr', 'O-', '2023-03-10'),
('Fleury', 'Gabriel', '1994-03-08', 'M', '294037512345757', '34 avenue de la Mer', '06700', 'Nice', '06.01.23.45.74', 'gabriel.fleury@email.fr', 'B+', '2023-06-20'),

-- Patients 81-100
('Costa', 'Jade', '1976-06-20', 'F', '276067512345758', '56 rue du Port', '33700', 'Bordeaux', '06.12.34.56.86', 'jade.costa@email.fr', 'AB-', '2023-02-12'),
('Perez', 'Raphaël', '1992-10-02', 'M', '292107512345759', '78 avenue des Fleurs', '31700', 'Toulouse', '06.23.45.67.87', 'raphael.perez@email.fr', 'A+', '2023-05-08'),
('Rey', 'Léna', '1969-01-14', 'F', '269017512345760', '23 rue de l''Église', '67700', 'Strasbourg', '06.34.56.78.98', 'lena.rey@email.fr', 'O+', '2023-01-25'),
('Da Silva', 'Mathéo', '1998-05-27', 'M', '298057512345761', '45 boulevard Voltaire', '75015', 'Paris', '06.45.67.89.09', 'matheo.dasilva@email.fr', 'B-', '2023-04-15'),
('Olivier', 'Alice', '1973-09-09', 'F', '273097512345762', '67 rue Pasteur', '59200', 'Lille', '06.56.78.90.20', 'alice.olivier@email.fr', 'A-', '2023-06-25'),
('Roche', 'Noah', '1987-12-21', 'M', '287127512345763', '12 avenue Mozart', '75019', 'Paris', '06.67.89.01.31', 'noah.roche@email.fr', 'O-', '2023-03-18'),
('Marty', 'Mia', '1964-04-04', 'F', '264047512345764', '89 rue de la Fontaine', '69007', 'Lyon', '06.78.90.12.42', 'mia.marty@email.fr', 'AB+', '2023-02-05'),
('Lopez', 'Enzo', '1995-08-17', 'M', '295087512345765', '34 boulevard Saint-Michel', '75020', 'Paris', '06.89.01.23.53', 'enzo.lopez@email.fr', 'B+', '2023-05-30'),
('Aubry', 'Juliette', '1971-11-29', 'F', '271117512345766', '56 avenue Pasteur', '13008', 'Marseille', '06.90.12.34.64', 'juliette.aubry@email.fr', 'A+', '2023-01-12'),
('Hubert', 'Maxime', '1999-03-13', 'M', '299037512345767', '78 rue Victor Hugo', '31800', 'Toulouse', '06.01.23.45.75', 'maxime.hubert@email.fr', 'O+', '2023-04-22'),
('Benoit', 'Clara', '1966-07-26', 'F', '266077512345768', '23 avenue de la Gare', '44800', 'Nantes', '06.12.34.56.87', 'clara.benoit@email.fr', 'B-', '2023-06-15'),
('Poirier', 'Timéo', '1993-11-08', 'M', '293117512345769', '45 rue de la République', '67800', 'Strasbourg', '06.23.45.67.88', 'timeo.poirier@email.fr', 'AB-', '2023-03-05'),
('Leroy', 'Rose', '1975-02-20', 'F', '275027512345770', '67 boulevard de la Paix', '33800', 'Bordeaux', '06.34.56.78.99', 'rose.leroy@email.fr', 'A-', '2023-05-18'),
('Bouvier', 'Théo', '1991-06-03', 'M', '291067512345771', '12 avenue Jean Jaurès', '06800', 'Nice', '06.45.67.89.10', 'theo.bouvier@email.fr', 'O-', '2023-02-28'),
('Adam', 'Anna', '1968-09-15', 'F', '268097512345772', '89 rue de la Liberté', '35800', 'Rennes', '06.56.78.90.21', 'anna.adam@email.fr', 'B+', '2023-06-10'),
('Rousseau', 'Sacha', '1997-12-27', 'M', '297127512345773', '34 boulevard Haussmann', '75021', 'Paris', '06.67.89.01.32', 'sacha.rousseau@email.fr', 'A+', '2023-01-20'),
('Prevost', 'Romane', '1974-05-10', 'F', '274057512345774', '56 rue de Rivoli', '75022', 'Paris', '06.78.90.12.43', 'romane.prevost@email.fr', 'O+', '2023-04-08'),
('Carpentier', 'Paul', '1990-09-22', 'M', '290097512345775', '78 avenue Foch', '69008', 'Lyon', '06.89.01.23.54', 'paul.carpentier@email.fr', 'AB+', '2023-05-25'),
('Guillot', 'Eva', '1962-12-04', 'F', '262127512345776', '23 rue de la Paix', '13009', 'Marseille', '06.90.12.34.65', 'eva.guillot@email.fr', 'B-', '2023-03-12'),
('Lemaire', 'Axel', '1989-04-17', 'M', '289047512345777', '45 boulevard de la Plage', '44900', 'Nantes', '06.01.23.45.76', 'axel.lemaire@email.fr', 'A-', '2023-06-28');

-- ============================================================
-- SEED: Médicaments (30 médicaments courants)
-- ============================================================
INSERT INTO "Medicament" (nom_commercial, denomination_commune, dosage, forme, laboratoire, prix_unitaire, remboursable) VALUES
('Doliprane', 'Paracétamol', '500mg', 'Comprimé', 'Sanofi', 2.50, TRUE),
('Efferalgan', 'Paracétamol', '1g', 'Comprimé effervescent', 'UPSA', 3.20, TRUE),
('Advil', 'Ibuprofène', '400mg', 'Comprimé', 'Pfizer', 4.50, TRUE),
('Spasfon', 'Phloroglucinol', '80mg', 'Comprimé', 'Teva', 5.10, TRUE),
('Amoxicilline', 'Amoxicilline', '1g', 'Gélule', 'Biogaran', 6.80, TRUE),
('Ventoline', 'Salbutamol', '100µg', 'Inhalateur', 'GSK', 8.20, TRUE),
('Levothyrox', 'Lévothyroxine', '75µg', 'Comprimé', 'Merck', 3.50, TRUE),
('Kardégic', 'Acide acétylsalicylique', '75mg', 'Poudre', 'Sanofi', 2.80, TRUE),
('Tahor', 'Atorvastatine', '20mg', 'Comprimé', 'Pfizer', 12.50, TRUE),
('Inexium', 'Esoméprazole', '40mg', 'Gélule', 'AstraZeneca', 15.20, TRUE),
('Crestor', 'Rosuvastatine', '10mg', 'Comprimé', 'AstraZeneca', 14.80, TRUE),
('Seroplex', 'Escitalopram', '10mg', 'Comprimé', 'Lundbeck', 18.50, TRUE),
('Xanax', 'Alprazolam', '0.25mg', 'Comprimé', 'Pfizer', 9.20, TRUE),
('Lexomil', 'Bromazépam', '6mg', 'Comprimé', 'Roche', 7.50, TRUE),
('Metformine', 'Metformine', '850mg', 'Comprimé', 'Mylan', 4.20, TRUE),
('Lantus', 'Insuline glargine', '100UI/ml', 'Injectable', 'Sanofi', 45.00, TRUE),
('Novonorm', 'Répaglinide', '2mg', 'Comprimé', 'Novo Nordisk', 22.50, TRUE),
('Coversyl', 'Périndopril', '5mg', 'Comprimé', 'Servier', 11.80, TRUE),
('Sectral', 'Acébutolol', '200mg', 'Comprimé', 'Sanofi', 8.50, TRUE),
('Laroxyl', 'Amitriptyline', '25mg', 'Comprimé', 'Roche', 6.20, TRUE),
('Deroxat', 'Paroxétine', '20mg', 'Comprimé', 'GSK', 16.50, TRUE),
('Mopral', 'Oméprazole', '20mg', 'Gélule', 'AstraZeneca', 7.80, TRUE),
('Xarelto', 'Rivaroxaban', '15mg', 'Comprimé', 'Bayer', 65.00, TRUE),
('Plavix', 'Clopidogrel', '75mg', 'Comprimé', 'Sanofi', 28.50, TRUE),
('Cetirizine', 'Cetirizine', '10mg', 'Comprimé', 'Biogaran', 3.50, TRUE),
('Spiriva', 'Tiotropium', '18µg', 'Inhalateur', 'Boehringer', 52.00, TRUE),
('Symbicort', 'Budésonide/Formotérol', '200/6µg', 'Inhalateur', 'AstraZeneca', 38.00, TRUE),
('Augmentin', 'Amoxicilline/Acide clavulanique', '1g/125mg', 'Comprimé', 'GSK', 9.50, TRUE),
('Celestene', 'Bétaméthasone', '2mg', 'Comprimé effervescent', 'MSD', 4.80, TRUE),
('Voltarene', 'Diclofénac', '50mg', 'Comprimé', 'Novartis', 5.20, TRUE);

-- ============================================================
-- FIN DU SCRIPT DE SEED
-- ============================================================
