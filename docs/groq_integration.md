# Intégration Groq LLM

## Vue d'ensemble

Le système utilise l'API Groq pour la classification intelligente des tickets par e-mail. Groq fournit des modèles LLM rapides et performants pour l'analyse et la classification de texte.

## Configuration

### 1. Obtenir une clé API Groq

1. Créer un compte sur [console.groq.com](https://console.groq.com)
2. Générer une clé API
3. Ajouter la clé dans le fichier `.env` :

```env
GROQ_API_KEY=votre-cle-api-groq
GROQ_MODEL=llama-3.1-70b-versatile
USE_GROQ_LLM=true
```

### 2. Modèles disponibles

Groq propose plusieurs modèles optimisés :

- `llama-3.1-70b-versatile` (recommandé) - Modèle polyvalent et performant
- `llama-3.1-8b-instant` - Plus rapide, moins précis
- `mixtral-8x7b-32768` - Bon compromis vitesse/précision
- `gemma2-9b-it` - Modèle Google optimisé

### 3. Configuration dans `.env`

```env
# Groq Configuration
GROQ_API_KEY=gsk_votre_cle_api_ici
GROQ_MODEL=llama-3.1-70b-versatile
USE_GROQ_LLM=true

# Catégories de classification
CLASSIFICATION_CATEGORIES=Technique,Commercial,Support,Facturation,Autre

# Niveaux de priorité
CLASSIFICATION_PRIORITIES=Critique,Haute,Moyenne,Basse
```

## Utilisation

### Classification basique

```python
from src.classification.classifier import TicketClassifier
from src.utils.config import ClassificationConfig, load_config

config = load_config()
classifier = TicketClassifier(config.classification)

result = classifier.classify(
    subject="Problème de connexion",
    body="Je ne peux plus me connecter à l'application depuis ce matin.",
    sender_email="user@example.com"
)

print(f"Catégorie: {result['category']}")
print(f"Priorité: {result['priority']}")
print(f"Confiance: {result['confidence']}")
print(f"Raisonnement: {result['reasoning']}")
```

### Extraction d'informations

```python
info = classifier.extract_key_information(
    subject="Bug dans le module de paiement",
    body="Le paiement échoue avec l'erreur 500..."
)

print(f"Problème principal: {info.get('main_issue')}")
print(f"Produit concerné: {info.get('product_service')}")
print(f"Référence: {info.get('reference_number')}")
```

## Format de réponse

Le classificateur retourne un dictionnaire avec :

```python
{
    "category": "Technique",      # Catégorie classifiée
    "priority": "Haute",          # Priorité assignée
    "confidence": 0.92,           # Score de confiance (0-1)
    "reasoning": "Le ticket décrit un problème technique..."  # Explication
}
```

## Avantages de Groq

1. **Rapidité** : Réponses en millisecondes grâce à l'infrastructure optimisée
2. **Précision** : Modèles LLM de pointe pour une meilleure compréhension
3. **Flexibilité** : Facilement adaptable aux besoins spécifiques
4. **Coût** : Tarification avantageuse par rapport aux autres APIs LLM
5. **Pas d'entraînement** : Pas besoin d'entraîner un modèle ML

## Gestion des erreurs

Le système inclut un mécanisme de fallback automatique :

- Si l'API Groq est indisponible → Classification basique par mots-clés
- Si la réponse JSON est invalide → Retry avec parsing amélioré
- Si le quota est dépassé → Mode fallback activé

## Optimisation

### Réduction des coûts

- Limiter la longueur du body analysé (déjà implémenté : 1000 caractères)
- Utiliser des modèles plus petits pour les cas simples
- Mettre en cache les classifications similaires

### Amélioration de la précision

- Ajuster le `temperature` (actuellement 0.3 pour plus de cohérence)
- Personnaliser le prompt système selon vos besoins
- Ajouter des exemples dans le prompt pour le few-shot learning

## Exemple de prompt personnalisé

Pour personnaliser le comportement, modifiez `_get_system_prompt()` dans `classifier.py` :

```python
def _get_system_prompt(self) -> str:
    return """Vous êtes un expert en classification de tickets pour [VOTRE ENTREPRISE].
    
Règles spécifiques:
- Les tickets de [DOMAINE] sont toujours classés comme "Technique"
- Les tickets avec [MOT_CLÉ] sont prioritaires "Critique"
- ...
"""
```

## Monitoring

Le système log automatiquement :
- Les classifications effectuées
- Les erreurs API
- Les temps de réponse
- Les scores de confiance

Consultez les logs dans `logs/agent.log` pour analyser les performances.

## Comparaison avec ML classique

| Critère | Groq LLM | ML Classique |
|---------|----------|--------------|
| Précision | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| Vitesse | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Coût | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Flexibilité | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| Entraînement requis | ❌ Non | ✅ Oui |

## Support

Pour toute question sur l'intégration Groq :
- Documentation Groq : https://console.groq.com/docs
- Issues GitHub : [Créer une issue](https://github.com/legb78/mail_classification_agent/issues)

