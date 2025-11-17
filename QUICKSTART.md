# Guide de Démarrage Rapide

## Installation rapide

```bash
# 1. Cloner le repository
git clone https://github.com/legb78/mail_classification_agent.git
cd mail_classification_agent

# 2. Créer l'environnement virtuel
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Configurer les variables d'environnement
cp env.example .env
# Éditer .env avec vos credentials

# 5. Configurer Google Sheets API
# - Télécharger credentials.json depuis Google Cloud Console
# - Placer le fichier à la racine du projet
# - Partager votre Google Sheet avec l'email du service account

# 6. Obtenir une clé API Groq
# - Aller sur https://console.groq.com
# - Créer un compte et générer une clé API
# - Ajouter GROQ_API_KEY dans le fichier .env

# 7. Tester la classification
python examples/test_classification.py

# 8. Lancer l'agent
python src/main.py --mode auto
```

## Configuration minimale

### Fichier .env

```env
# Email (obligatoire)
EMAIL_USER=votre-email@gmail.com
EMAIL_PASSWORD=votre-mot-de-passe-app

# Google Sheets (obligatoire)
GOOGLE_SHEETS_ID=votre-sheet-id

# Groq API (obligatoire pour la classification)
GROQ_API_KEY=gsk_votre_cle_api_groq
GROQ_MODEL=llama-3.1-70b-versatile
USE_GROQ_LLM=true
```

### Obtenir une clé API Groq

1. Aller sur [console.groq.com](https://console.groq.com)
2. Créer un compte (gratuit)
3. Aller dans "API Keys"
4. Créer une nouvelle clé API
5. Copier la clé et l'ajouter dans `.env`

### Google Sheets

Créer un Google Sheet avec les colonnes suivantes :
- ID
- Date
- Expéditeur
- Email
- Sujet
- Catégorie
- Priorité
- Statut
- Description
- Traité par
- Notes

## Test rapide

```bash
# Test de la classification Groq
python examples/test_classification.py

# Mode test (sans écriture)
python src/main.py --mode manual --email-id <id> --dry-run

# Mode automatique
python src/main.py --mode auto --interval 60
```

## Modèles Groq disponibles

- `llama-3.1-70b-versatile` (recommandé) - Meilleure précision
- `llama-3.1-8b-instant` - Plus rapide
- `mixtral-8x7b-32768` - Bon compromis
- `gemma2-9b-it` - Modèle Google

Changez le modèle dans `.env` :
```env
GROQ_MODEL=llama-3.1-8b-instant
```

## Structure des fichiers créés

```
mail_classification_agent/
├── README.md                 # Documentation principale
├── ARCHITECTURE.md           # Vue synthétique de l'architecture
├── QUICKSTART.md            # Ce fichier
├── CONTRIBUTING.md          # Guide de contribution
├── requirements.txt         # Dépendances Python
├── setup.py                 # Configuration du package
├── .gitignore              # Fichiers à ignorer
├── env.example             # Exemple de configuration
├── docs/
│   ├── architecture.md     # Documentation détaillée de l'architecture
│   └── groq_integration.md # Documentation Groq
├── examples/
│   └── test_classification.py  # Script de test
└── src/
    ├── __init__.py
    ├── main.py             # Point d'entrée principal
    ├── classification/
    │   ├── __init__.py
    │   └── classifier.py  # Classificateur Groq
    └── utils/
        ├── config.py       # Gestion de la configuration
        └── logger.py       # Configuration du logging
```

## Prochaines étapes

1. **Tester la classification** :
   ```bash
   python examples/test_classification.py
   ```

2. **Implémenter les modules manquants** :
   - `src/email/monitor.py` - Surveillance de la boîte mail
   - `src/email/parser.py` - Parsing des e-mails
   - `src/sheets/client.py` - Client Google Sheets
   - `src/notification/slack.py` - Notifications Slack

3. **Intégrer dans le pipeline** :
   - Connecter le classificateur au processeur d'emails
   - Créer les tickets dans Google Sheets
   - Ajouter les notifications

4. **Déploiement** :
   - Configurer le service daemon
   - Mettre en place le monitoring
   - Configurer les backups

## Support

Pour toute question :
- Email : ticketsdata5@gmail.com
- Issues : [GitHub Issues](https://github.com/legb78/mail_classification_agent/issues)
- Documentation Groq : [docs/groq_integration.md](docs/groq_integration.md)
