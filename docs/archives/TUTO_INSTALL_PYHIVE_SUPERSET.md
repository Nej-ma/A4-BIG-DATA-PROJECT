# 🔧 TUTORIEL : Installer PyHive dans Superset

**Problème** : Apache Spark SQL n'apparaît pas dans la liste des bases de données Superset

**Cause** : Le driver PyHive n'est pas installé dans l'environnement Python de Superset

**Solution** : Installer PyHive dans le bon environnement Python

---

## 📋 CONTEXTE TECHNIQUE

### Pourquoi c'est compliqué ?

Superset utilise un **virtualenv Python** (`/app/.venv/`) mais quand on fait `pip install`, ça installe dans l'environnement **utilisateur** (`~/.local/`) au lieu du virtualenv.

**Résultat** : PyHive est installé mais Superset ne le voit pas !

### Architecture Superset

```
Container chu_superset
├─ /usr/local/bin/python       ← Python système (pas utilisé par Superset)
├─ /app/.venv/bin/python        ← Python virtualenv (UTILISÉ par Superset) ✅
└─ /app/superset_home/.local/   ← Installations pip en mode user (ignorées)
```

**Il faut installer PyHive dans `/app/.venv/`**

---

## 🚀 SOLUTION COMPLÈTE (COPIE-COLLE)

### Étape 1 : Installer pip dans le virtualenv (1 min)

**Commande** :
```bash
docker exec --user root chu_superset sh -c 'python -m ensurepip --default-pip && python -m pip install --upgrade pip setuptools wheel'
```

**Ce que ça fait** :
- `docker exec --user root` : Exécute en tant que root (pour avoir les permissions)
- `chu_superset` : Nom du container Superset
- `python -m ensurepip` : Installe pip dans le virtualenv Python
- `python -m pip install --upgrade pip` : Met à jour pip à la dernière version

**Sortie attendue** :
```
Successfully installed pip-25.2 setuptools-80.9.0 wheel-0.45.1
```

---

### Étape 2 : Installer PyHive et dépendances (2 min)

**Commande** :
```bash
docker exec --user root chu_superset python -m pip install pyhive thrift thrift_sasl
```

**Ce que ça fait** :
- `python -m pip install` : Utilise le pip du virtualenv (pas le pip système)
- `pyhive` : Driver principal pour Hive/Spark SQL
- `thrift` : Protocole de communication avec Spark Thrift Server
- `thrift_sasl` : Authentification SASL (optionnel mais recommandé)

**Sortie attendue** :
```
Successfully installed future-1.0.0 pyhive-0.7.0
```

---

### Étape 3 : Vérifier l'installation (30s)

**Commande** :
```bash
docker exec chu_superset python -c "from pyhive import hive; print('✅ PyHive OK!')"
```

**Ce que ça fait** :
- Teste si Python peut importer le module `pyhive`

**Sortie attendue** :
```
✅ PyHive OK!
```

**Si erreur** : PyHive n'est pas installé correctement, reprends depuis l'étape 1

---

### Étape 4 : Redémarrer Superset (30s)

**Commande** :
```bash
docker restart chu_superset
```

**Ce que ça fait** :
- Redémarre le container Superset pour qu'il détecte le nouveau driver

**Attendre** : 20-30 secondes que Superset redémarre

**Vérifier** :
```bash
docker ps --filter "name=chu_superset"
```

**Doit afficher** : `Up X seconds (healthy)`

---

### Étape 5 : Vérifier dans Superset (1 min)

1. Va sur **http://localhost:8088**
2. Login : `admin` / `admin`
3. **Settings** ⚙️ → **Database Connections**
4. **+ DATABASE**
5. Cherche **"Apache Spark SQL"** dans la liste

**✅ SI VISIBLE** : C'est bon, PyHive est installé !

**❌ SI PAS VISIBLE** : Regarde la section Troubleshooting ci-dessous

---

## 🔍 TROUBLESHOOTING

### Problème 1 : "Permission denied" lors de l'installation

**Erreur** :
```
ERROR: Could not install packages due to an EnvironmentError: [Errno 13] Permission denied
```

**Solution** : Utilise `--user root`
```bash
docker exec --user root chu_superset python -m pip install pyhive thrift thrift_sasl
```

---

### Problème 2 : "No module named 'pip'"

**Erreur** :
```
/app/.venv/bin/python: No module named pip
```

**Solution** : Installe pip d'abord (Étape 1)
```bash
docker exec --user root chu_superset python -m ensurepip --default-pip
```

---

### Problème 3 : "ModuleNotFoundError: No module named 'pyhive'"

**Erreur quand tu testes** :
```bash
docker exec chu_superset python -c "from pyhive import hive"
# ModuleNotFoundError: No module named 'pyhive'
```

**Cause** : PyHive est installé en mode user au lieu du virtualenv

**Solution** : Utilise `python -m pip` au lieu de juste `pip`
```bash
docker exec --user root chu_superset python -m pip install pyhive thrift thrift_sasl
```

---

### Problème 4 : "C:/Program Files/Git/..." sur Windows Git Bash

**Erreur** :
```
exec: "C:/Program Files/Git/app/.venv/bin/pip": no such file or directory
```

**Cause** : Git Bash transforme les chemins Unix en chemins Windows

**Solutions** :

**Option A** : Utilise `sh -c` avec des quotes simples
```bash
docker exec --user root chu_superset sh -c 'python -m pip install pyhive'
```

**Option B** : Utilise PowerShell à la place de Git Bash
```powershell
docker exec --user root chu_superset python -m pip install pyhive thrift thrift_sasl
```

**Option C** : Utilise CMD (Command Prompt)
```cmd
docker exec --user root chu_superset python -m pip install pyhive thrift thrift_sasl
```

---

### Problème 5 : Apache Spark SQL toujours pas visible après redémarrage

**Vérifications** :

1. **PyHive est bien installé ?**
   ```bash
   docker exec chu_superset python -c "from pyhive import hive; print('OK')"
   ```

2. **Superset a bien redémarré ?**
   ```bash
   docker ps --filter "name=chu_superset"
   ```
   Doit dire `(healthy)`

3. **Logs Superset** :
   ```bash
   docker logs chu_superset --tail 50
   ```
   Cherche des erreurs d'import

4. **Essaie de forcer le refresh** : Vide le cache navigateur (Ctrl+Shift+Delete)

---

## 📚 EXPLICATION DÉTAILLÉE

### Pourquoi `python -m pip` au lieu de `pip` ?

**`pip install`** :
- Utilise le premier `pip` trouvé dans le PATH
- Peut être `/usr/local/bin/pip` (système)
- Installe en mode `--user` si pas de permissions

**`python -m pip install`** :
- Utilise le `pip` du Python en cours (`/app/.venv/bin/python`)
- Garantit l'installation dans le bon environnement
- Plus fiable dans un virtualenv

**Exemple** :
```bash
# Mauvais - peut installer au mauvais endroit
docker exec chu_superset pip install pyhive

# Bon - garantit l'installation dans le virtualenv
docker exec chu_superset python -m pip install pyhive
```

---

### Pourquoi `--user root` ?

**Sans root** :
- Utilise l'utilisateur par défaut du container (superset)
- Pas de permissions d'écriture dans `/app/.venv/`
- Installe en mode `--user` dans `~/.local/`

**Avec root** :
- Permissions complètes
- Peut écrire dans `/app/.venv/lib/python3.10/site-packages/`
- Installation globale dans le virtualenv

---

### Packages installés

| Package | Rôle |
|---------|------|
| **pyhive** | Driver principal pour Hive/Spark SQL |
| **thrift** | Protocole RPC utilisé par Spark Thrift Server |
| **thrift_sasl** | Authentification SASL pour Thrift |
| **future** | Compatibilité Python 2/3 (dépendance de PyHive) |
| **pure-sasl** | Implémentation SASL pure Python |

---

## ✅ CHECKLIST FINALE

Après avoir suivi le tutoriel :

- [ ] Étape 1 : pip installé dans virtualenv
- [ ] Étape 2 : PyHive installé sans erreur
- [ ] Étape 3 : Import PyHive fonctionne
- [ ] Étape 4 : Superset redémarré et healthy
- [ ] Étape 5 : Apache Spark SQL visible dans Superset

**Si toutes les cases sont cochées** → PyHive est installé ! ✅

---

## 🎯 COMMANDES RÉSUMÉES (COPIE-COLLE RAPIDE)

**Pour Windows Git Bash / Linux / Mac** :

```bash
# 1. Installer pip dans le virtualenv
docker exec --user root chu_superset sh -c 'python -m ensurepip --default-pip && python -m pip install --upgrade pip setuptools wheel'

# 2. Installer PyHive
docker exec --user root chu_superset python -m pip install pyhive thrift thrift_sasl

# 3. Vérifier
docker exec chu_superset python -c "from pyhive import hive; print('✅ PyHive OK!')"

# 4. Redémarrer Superset
docker restart chu_superset

# 5. Attendre 30s puis vérifier
sleep 30 && docker ps --filter "name=chu_superset"
```

**Pour PowerShell** :

```powershell
# 1. Installer pip
docker exec --user root chu_superset python -m ensurepip --default-pip
docker exec --user root chu_superset python -m pip install --upgrade pip setuptools wheel

# 2. Installer PyHive
docker exec --user root chu_superset python -m pip install pyhive thrift thrift_sasl

# 3. Vérifier
docker exec chu_superset python -c "from pyhive import hive; print('OK')"

# 4. Redémarrer
docker restart chu_superset

# 5. Attendre puis vérifier
Start-Sleep -Seconds 30
docker ps --filter "name=chu_superset"
```

---

## 💡 CONSEIL POUR TON AMIE

**Dis-lui** :

1. Le problème vient du fait que Superset utilise un virtualenv Python
2. Il faut installer PyHive DANS ce virtualenv, pas en mode user
3. La solution : utiliser `python -m pip` au lieu de `pip`
4. Et exécuter en tant que `root` pour avoir les permissions

**Copie-colle les 5 commandes résumées ci-dessus** et ça devrait marcher !

---

## 📖 POUR ALLER PLUS LOIN

### Vérifier quel Python utilise Superset

```bash
docker exec chu_superset which python
# Output: /app/.venv/bin/python
```

### Lister les packages installés

```bash
docker exec chu_superset python -m pip list | grep -i hive
# Output: PyHive  0.7.0
```

### Voir le chemin d'installation de PyHive

```bash
docker exec chu_superset python -c "import pyhive; print(pyhive.__file__)"
# Output: /app/.venv/lib/python3.10/site-packages/pyhive/__init__.py
```

### Tester la connexion Hive depuis Python

```bash
docker exec chu_superset python -c "
from pyhive import hive
conn = hive.Connection(host='spark-master', port=10000)
print('✅ Connexion Hive OK!')
"
```

---

**Bon courage à ton amie ! 💪**

**Si elle a encore des problèmes, dis-lui de vérifier la section Troubleshooting.**
