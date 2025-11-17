# Configuration Rapide de Groq

## 🚀 Démarrage en 5 minutes

### Étape 1 : Obtenir une clé API Groq

1. Aller sur [console.groq.com](https://console.groq.com)
2. Créer un compte (gratuit, pas de carte bancaire requise)
3. Cliquer sur "API Keys" dans le menu
4. Cliquer sur "Create API Key"
5. Copier la clé (format: `gsk_...`)

### Étape 2 : Configurer le fichier .env

Ouvrir le fichier `.env` et ajouter :

```env
GROQ_API_KEY=gsk_votre_cle_api_ici
GROQ_MODEL=llama-3.1-70b-versatile
USE_GROQ_LLM=true
```

### Étape 3 : Tester la configuration

```bash
python examples/test_classification.py
```

Vous devriez voir les résultats de classification pour plusieurs exemples de tickets.

## 📊 Modèles disponibles

| Modèle | Vitesse | Précision | Usage recommandé |
|--------|---------|-----------|------------------|
| `llama-3.1-70b-versatile` | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Production (recommandé) |
| `llama-3.1-8b-instant` | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | Tests rapides |
| `mixtral-8x7b-32768` | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Bon compromis |
| `gemma2-9b-it` | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Alternative Google |

## 💰 Coûts

Groq offre un **tier gratuit généreux** :
- **Gratuit** : Jusqu'à 14,400 requêtes/jour
- **Payant** : À partir de $0.27 par million de tokens

Pour la classification de tickets, le tier gratuit est généralement suffisant.

## 🔧 Personnalisation

### Changer le modèle

Dans `.env` :
```env
GROQ_MODEL=llama-3.1-8b-instant  # Plus rapide
```

### Personnaliser les catégories

Dans `.env` :
```env
CLASSIFICATION_CATEGORIES=Technique,Commercial,Support,Facturation,Autre
CLASSIFICATION_PRIORITIES=Critique,Haute,Moyenne,Basse
```

### Ajuster la température (cohérence)

Modifier dans `src/classification/classifier.py` :
```python
temperature=0.3,  # Plus bas = plus cohérent, Plus haut = plus créatif
```

## 🐛 Dépannage

### Erreur "GROQ_API_KEY est requis"

✅ Vérifiez que la clé est bien dans `.env` :
```bash
# Windows PowerShell
Get-Content .env | Select-String "GROQ_API_KEY"

# Linux/Mac
grep GROQ_API_KEY .env
```

### Erreur "Invalid API key"

✅ Vérifiez que :
- La clé commence par `gsk_`
- La clé n'a pas d'espaces avant/après
- Le compte Groq est actif

### Classification toujours "Autre"

✅ Vérifiez que :
- `USE_GROQ_LLM=true` dans `.env`
- La clé API est valide
- Le modèle est correctement configuré

### Réponses lentes

✅ Essayez un modèle plus rapide :
```env
GROQ_MODEL=llama-3.1-8b-instant
```

## 📚 Ressources

- [Documentation Groq](https://console.groq.com/docs)
- [Modèles disponibles](https://console.groq.com/docs/models)
- [Guide d'intégration complet](docs/groq_integration.md)

## ✅ Checklist de vérification

- [ ] Compte Groq créé
- [ ] Clé API générée
- [ ] `GROQ_API_KEY` ajoutée dans `.env`
- [ ] `USE_GROQ_LLM=true` dans `.env`
- [ ] Test de classification réussi
- [ ] Modèle choisi selon vos besoins

## 🎯 Exemple d'utilisation

```python
from src.classification.classifier import TicketClassifier
from src.utils.config import load_config

config = load_config()
classifier = TicketClassifier(config.classification)

# Classifier un ticket
result = classifier.classify(
    subject="Problème de connexion",
    body="Je ne peux plus me connecter depuis ce matin.",
    sender_email="user@example.com"
)

print(f"Catégorie: {result['category']}")
print(f"Priorité: {result['priority']}")
```

C'est tout ! Vous êtes prêt à utiliser Groq pour classifier vos tickets. 🎉

