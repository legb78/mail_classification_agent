# Guide de Test Email

## 🚀 Test rapide de votre boîte mail

Ce guide vous explique comment tester la connexion à votre boîte mail et récupérer quelques emails.

## 📋 Prérequis

1. **Configuration email** dans le fichier `.env` :
   ```env
   EMAIL_HOST=imap.gmail.com
   EMAIL_PORT=993
   EMAIL_USER=votre-email@gmail.com
   EMAIL_PASSWORD=votre-mot-de-passe-app
   EMAIL_FOLDER=INBOX
   EMAIL_USE_SSL=true
   ```

2. **Configuration Groq** (optionnel, pour la classification) :
   ```env
   GROQ_API_KEY=votre-cle-api-groq
   GROQ_MODEL=llama-3.1-70b-versatile
   USE_GROQ_LLM=true
   ```

## 🔐 Configuration Gmail

Pour Gmail, vous devez utiliser un **mot de passe d'application** :

1. Allez sur [myaccount.google.com](https://myaccount.google.com)
2. Sécurité → Validation en deux étapes (doit être activée)
3. Mots de passe des applications
4. Créez un nouveau mot de passe d'application
5. Utilisez ce mot de passe dans `EMAIL_PASSWORD`

## 🧪 Lancer le test

### Test basique (sans classification)

```bash
python main.py --mode test
```

### Test avec classification Groq

```bash
python main.py --mode test --verbose
```

## 📊 Résultats attendus

Le test va :

1. ✅ Se connecter à votre boîte mail
2. 📧 Récupérer les 5 derniers emails non lus (ou 3 emails récents si aucun non lu)
3. 🔍 Parser chaque email (sujet, expéditeur, corps)
4. 🤖 Classifier chaque email avec Groq (si configuré)
5. 📋 Afficher les résultats

### Exemple de sortie

```
============================================================
📧 3 email(s) trouvé(s)
============================================================

--- Email 1/3 ---
De: John Doe <john@example.com>
Sujet: Problème avec le service
Date: 2025-11-17 14:30:00
Corps (premiers 200 caractères): Bonjour, j'ai un problème avec...

🔍 Classification en cours...
✅ Catégorie: Technique
✅ Priorité: Haute
✅ Confiance: 85.00%
📋 Informations extraites: {'problem': 'problème avec le service'}
------------------------------------------------------------
```

## ⚠️ Dépannage

### Erreur d'authentification

```
ERROR: Erreur IMAP: [AUTHENTICATIONFAILED] Invalid credentials
```

**Solutions :**
- Vérifiez que `EMAIL_USER` et `EMAIL_PASSWORD` sont corrects
- Pour Gmail, utilisez un mot de passe d'application
- Vérifiez que la validation en deux étapes est activée

### Erreur de connexion

```
ERROR: Erreur lors de la connexion: [Errno 11001] getaddrinfo failed
```

**Solutions :**
- Vérifiez votre connexion internet
- Vérifiez que `EMAIL_HOST` est correct
- Vérifiez que le port `EMAIL_PORT` est correct (993 pour SSL)

### Aucun email trouvé

```
INFO: Aucun email trouvé dans la boîte mail
```

C'est normal si votre boîte mail est vide ou si tous les emails sont déjà lus.

## 🔄 Prochaines étapes

Une fois le test réussi :

1. ✅ Vérifiez que les emails sont correctement parsés
2. ✅ Vérifiez que la classification fonctionne (si Groq configuré)
3. 🚀 Passez au mode `auto` pour le traitement automatique

```bash
python main.py --mode auto --interval 60
```

## 📝 Notes

- Le mode `test` ne modifie **jamais** vos emails (ne les marque pas comme lus)
- Le mode `test` ne crée **pas** de tickets dans Google Sheets
- Utilisez `--dry-run` pour être sûr qu'aucune modification n'est effectuée

