# Guide d'Installation

## Prérequis

- Python 3.9 ou supérieur
- pip (gestionnaire de paquets Python)

## Installation

### 1. Cloner le repository

```bash
git clone https://github.com/legb78/mail_classification_agent.git
cd mail_classification_agent
```

### 2. Créer un environnement virtuel (recommandé)

**Windows PowerShell:**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**Linux/Mac:**
```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

**Note:** Si vous rencontrez des erreurs, installez les dépendances de base manuellement :
```bash
pip install pydantic-settings python-dotenv loguru groq
```

### 4. Configuration

1. Copier le fichier d'exemple :
   ```bash
   cp env.example .env
   ```

2. Éditer `.env` avec vos credentials :
   - Email (IMAP/SMTP)
   - Google Sheets API
   - **Groq API Key** (obligatoire pour la classification)

### 5. Obtenir une clé API Groq

1. Aller sur [console.groq.com](https://console.groq.com)
2. Créer un compte (gratuit)
3. Générer une clé API
4. Ajouter dans `.env` :
   ```env
   GROQ_API_KEY=gsk_votre_cle_api
   USE_GROQ_LLM=true
   ```

## Utilisation

### Exécution depuis la racine du projet

```bash
python main.py --help
python main.py --mode auto --interval 60
```

### Exécution depuis le répertoire src

```bash
cd src
python main.py --help
```

### Test de la classification Groq

```bash
python examples/test_classification.py
```

## Dépannage

### Erreur "ModuleNotFoundError: No module named 'src'"

✅ **Solution:** Exécutez depuis la racine du projet ou utilisez `python main.py` (fichier à la racine)

### Erreur "ModuleNotFoundError: No module named 'pydantic_settings'"

✅ **Solution:** Installez les dépendances :
```bash
pip install -r requirements.txt
```

### Erreur "GROQ_API_KEY est requis"

✅ **Solution:** Ajoutez votre clé API Groq dans le fichier `.env`

### Erreur lors de l'import depuis src/

✅ **Solution:** Le code a été corrigé pour ajouter automatiquement le répertoire parent au PYTHONPATH. Assurez-vous d'avoir la dernière version du code.

## Structure recommandée

```
mail_classification_agent/
├── main.py              # Point d'entrée (racine)
├── src/
│   └── main.py          # Point d'entrée (src)
├── examples/
│   └── test_classification.py
└── .env                 # Configuration
```

## Prochaines étapes

1. ✅ Configuration Groq terminée
2. ⏳ Implémenter les modules email (monitor, parser)
3. ⏳ Implémenter le client Google Sheets
4. ⏳ Implémenter les notifications
5. ⏳ Tester le pipeline complet

