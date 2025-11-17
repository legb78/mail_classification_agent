# Agent de Traitement Automatique de Tickets par E-mail

Système automatisé de traitement et classification de tickets reçus par e-mail, avec intégration Google Sheets et classification intelligente.

## 📋 Table des matières

- [Vue d'ensemble](#vue-densemble)
- [Architecture](#architecture)
- [Fonctionnalités](#fonctionnalités)
- [Installation](#installation)
- [Configuration](#configuration)
  - [Configuration Groq LLM](#configuration-groq-llm)
- [Utilisation](#utilisation)
- [Structure du projet](#structure-du-projet)
- [Technologies utilisées](#technologies-utilisées)

## 🎯 Vue d'ensemble

Cet agent automatise le traitement des e-mails entrants pour :
- **Réceptionner** les e-mails de tickets
- **Classifier** automatiquement les demandes par catégorie et priorité
- **Extraire** les informations pertinentes (nom, problème, contexte)
- **Créer** des tickets structurés dans Google Sheets
- **Notifier** les équipes concernées

## 🏗️ Architecture

```
┌─────────────────┐
│   Email Server  │
│   (IMAP/SMTP)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Email Monitor  │
│   (Polling)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Email Processor │
│  (Extraction)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Classifier AI  │
│  (NLP/ML Model) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Ticket Creator  │
│  (Google Sheets)│
└─────────────────┘
```

### Composants principaux

1. **Email Monitor** : Surveille la boîte mail en continu
2. **Email Parser** : Extrait le contenu et métadonnées des e-mails
3. **Classification Engine** : Classe les tickets par catégorie/priorité
4. **Data Extractor** : Extrait les informations structurées
5. **Google Sheets API** : Crée et met à jour les tickets
6. **Notification Service** : Envoie des notifications aux équipes

## ✨ Fonctionnalités

### Classification automatique
- **Classification intelligente** via **Groq LLM** (modèles Llama, Mixtral)
- Catégories : Technique, Commercial, Support, Facturation, Autre
- Priorités : Critique, Haute, Moyenne, Basse
- Détection de l'urgence basée sur le contenu et le contexte
- Extraction d'informations structurées (problème principal, référence, etc.)

### Extraction d'informations
- Nom et email de l'expéditeur
- Sujet et corps du message
- Pièces jointes (si présentes)
- Métadonnées (date, heure, timezone)

### Intégration Google Sheets
- Création automatique de tickets
- Mise à jour en temps réel
- Historique des modifications
- Tableau de bord de suivi

## 🚀 Installation

### Prérequis

- Python 3.9+
- Compte Google avec accès Google Sheets API
- Compte email avec accès IMAP/SMTP
- Clés API Google (credentials.json)

### Installation des dépendances

```bash
# Cloner le repository
git clone <repository-url>
cd mail_classification_agent

# Créer un environnement virtuel
python -m venv venv

# Activer l'environnement virtuel
# Sur Windows:
venv\Scripts\activate
# Sur Linux/Mac:
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
```

## ⚙️ Configuration

### 1. Configuration des variables d'environnement

Créer un fichier `.env` à la racine du projet :

```env
# Email Configuration
EMAIL_HOST=imap.gmail.com
EMAIL_PORT=993
EMAIL_USER=votre-email@gmail.com
EMAIL_PASSWORD=votre-mot-de-passe-app
EMAIL_FOLDER=INBOX

# Google Sheets Configuration
GOOGLE_SHEETS_ID=votre-sheet-id
GOOGLE_CREDENTIALS_PATH=credentials.json
GOOGLE_SHEET_NAME=Tickets

# Classification Configuration - Groq LLM
GROQ_API_KEY=votre-cle-api-groq
GROQ_MODEL=llama-3.1-70b-versatile
USE_GROQ_LLM=true

# Notification Configuration
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
TEAMS_WEBHOOK_URL=https://outlook.office.com/webhook/...

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/agent.log
```

**Important** : Obtenez votre clé API Groq sur [console.groq.com](https://console.groq.com)

#### Configuration Groq LLM

1. Créer un compte sur [console.groq.com](https://console.groq.com) (gratuit)
2. Générer une clé API dans la section "API Keys"
3. Ajouter la clé dans `.env` :
   ```env
   GROQ_API_KEY=gsk_votre_cle_api
   GROQ_MODEL=llama-3.1-70b-versatile
   USE_GROQ_LLM=true
   ```
4. Tester la configuration :
   ```bash
   python examples/test_classification.py
   ```

📖 **Documentation complète** : Voir [GROQ_SETUP.md](GROQ_SETUP.md) et [docs/groq_integration.md](docs/groq_integration.md)

### 2. Configuration Google Sheets API

1. Aller sur [Google Cloud Console](https://console.cloud.google.com/)
2. Créer un nouveau projet ou sélectionner un projet existant
3. Activer l'API Google Sheets
4. Créer des identifiants (Service Account)
5. Télécharger le fichier JSON des identifiants
6. Renommer le fichier en `credentials.json` et le placer à la racine du projet
7. Partager votre Google Sheet avec l'email du service account

### 3. Structure du Google Sheet

Le Google Sheet doit contenir les colonnes suivantes :

| ID | Date | Expéditeur | Email | Sujet | Catégorie | Priorité | Statut | Description | Traité par | Notes |
|----|-----|------------|-------|-------|-----------|----------|--------|-------------|------------|-------|

## 📖 Utilisation

### Mode manuel (test)

```bash
python src/main.py --mode manual --email-id <email-id>
```

### Mode automatique (production)

```bash
python src/main.py --mode auto --interval 60
```

### Mode test (test de connexion email)

Teste la connexion à votre boîte mail et récupère quelques emails pour vérification :

```bash
python main.py --mode test
```

Avec classification Groq :
```bash
python main.py --mode test --verbose
```

### Mode daemon (service)

```bash
python main.py --mode daemon
```

### Options de ligne de commande

```bash
python main.py [OPTIONS]

Options:
  --mode {manual,auto,daemon,test}  Mode d'exécution
  --interval INTEGER                Intervalle de vérification en secondes (défaut: 60)
  --email-id TEXT                   ID de l'email à traiter (mode manual)
  --config PATH                     Chemin vers le fichier de configuration
  --verbose                         Mode verbose
  --dry-run                         Mode test sans écriture dans Google Sheets
```

## 📁 Structure du projet

```
mail_classification_agent/
├── src/
│   ├── __init__.py
│   ├── main.py                 # Point d'entrée principal
│   ├── email/
│   │   ├── __init__.py
│   │   ├── monitor.py          # Surveillance de la boîte mail
│   │   ├── parser.py           # Parsing des e-mails
│   │   └── extractor.py        # Extraction d'informations
│   ├── classification/
│   │   ├── __init__.py
│   │   ├── classifier.py      # Moteur de classification
│   │   ├── models.py           # Modèles ML
│   │   └── preprocessor.py     # Préprocessing du texte
│   ├── sheets/
│   │   ├── __init__.py
│   │   ├── client.py           # Client Google Sheets
│   │   └── ticket_manager.py  # Gestion des tickets
│   ├── notification/
│   │   ├── __init__.py
│   │   ├── slack.py            # Notifications Slack
│   │   └── email_notifier.py   # Notifications par email
│   └── utils/
│       ├── __init__.py
│       ├── logger.py            # Configuration du logging
│       └── config.py            # Gestion de la configuration
├── models/
│   └── classification_model.pkl # Modèle de classification
├── logs/
│   └── agent.log               # Fichiers de logs
├── tests/
│   ├── __init__.py
│   ├── test_email_parser.py
│   ├── test_classifier.py
│   └── test_sheets_client.py
├── docs/
│   ├── architecture.md         # Documentation architecture
│   └── api.md                  # Documentation API
├── .env.example                # Exemple de fichier .env
├── .gitignore
├── requirements.txt            # Dépendances Python
├── README.md                   # Ce fichier
└── setup.py                    # Configuration du package
```

## 🛠️ Technologies utilisées

### Core
- **Python 3.9+** : Langage principal
- **imaplib/smtplib** : Gestion des e-mails
- **google-api-python-client** : Intégration Google Sheets
- **pandas** : Manipulation de données

### Machine Learning & LLM
- **groq** : API Groq pour classification LLM (recommandé)
- **scikit-learn** : Classification ML classique (optionnel)
- **nltk/spaCy** : Traitement du langage naturel

### Utilitaires
- **python-dotenv** : Gestion des variables d'environnement
- **pydantic** : Validation de données
- **loguru** : Logging avancé
- **schedule** : Planification des tâches

### Tests
- **pytest** : Framework de tests
- **pytest-cov** : Couverture de code

## 🔧 Développement

### Exécuter les tests

```bash
pytest tests/ -v
```

### Linting

```bash
flake8 src/
black src/
```

### Entraîner le modèle de classification

```bash
python scripts/train_model.py --data data/training_data.csv
```

## 📊 Monitoring

### Logs

Les logs sont disponibles dans `logs/agent.log` avec rotation automatique.

### Métriques

- Nombre de tickets traités
- Taux de classification correcte
- Temps de traitement moyen
- Erreurs et exceptions

## 🔒 Sécurité

- Les identifiants sont stockés dans des variables d'environnement
- Utilisation de mots de passe d'application pour Gmail
- Accès Google Sheets via Service Account
- Logs sans informations sensibles

## 🤝 Contribution

1. Fork le projet
2. Créer une branche (`git checkout -b feature/AmazingFeature`)
3. Commit les changements (`git commit -m 'Add some AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## 📝 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 📧 Contact

Pour toute question ou suggestion :
- Email : ticketsdata5@gmail.com
- Issues : [GitHub Issues](https://github.com/your-repo/issues)

## 🙏 Remerciements

- Google Sheets API
- Communauté Python
- Bibliothèques open-source utilisées

