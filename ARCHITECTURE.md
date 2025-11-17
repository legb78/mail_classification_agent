# Architecture du Système - Vue Synthétique

## Vue d'ensemble

Système modulaire de traitement automatique de tickets par e-mail avec classification intelligente et intégration Google Sheets.

## Architecture en couches

```
┌─────────────────────────────────────────────────────────┐
│                    COUCHE PRÉSENTATION                   │
│  • Logs structurés                                       │
│  • Monitoring & Métriques                               │
│  • Notifications (Slack, Email, Teams)                 │
└─────────────────────────────────────────────────────────┘
                            ▲
                            │
┌─────────────────────────────────────────────────────────┐
│                    COUCHE MÉTIER                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │ Classification│  │ Data Extract│  │ Ticket Mgmt  │ │
│  │   Engine      │  │   Service   │  │   Service    │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────┘
                            ▲
                            │
┌─────────────────────────────────────────────────────────┐
│                    COUCHE ACCÈS DONNÉES                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │ Email Monitor│  │ Email Parser  │  │ Sheets API   │ │
│  │   Service    │  │   Service    │  │   Client     │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────┘
                            ▲
                            │
┌─────────────────────────────────────────────────────────┐
│                    COUCHE INFRASTRUCTURE                │
│  • IMAP/SMTP Server                                      │
│  • Google Sheets API                                     │
│  • File System (Models, Logs)                           │
└─────────────────────────────────────────────────────────┘
```

## Composants principaux

### 1. Email Monitor Service
- **Rôle** : Surveillance continue de la boîte mail
- **Technologie** : IMAP avec polling
- **Fréquence** : Configurable (défaut: 60s)

### 2. Email Processing Pipeline
```
Email → Parser → Extractor → Classifier → Ticket Creator
```

### 3. Classification Engine
- **Méthode** : Machine Learning (scikit-learn)
- **Modèles** : 
  - Catégorie : Random Forest
  - Priorité : Regression
- **Features** : TF-IDF + features custom

### 4. Google Sheets Integration
- **API** : Google Sheets API v4
- **Authentification** : Service Account
- **Opérations** : Create, Read, Update

### 5. Notification Service
- **Canaux** : Slack, Email, Teams
- **Déclencheurs** : Nouveau ticket, Ticket critique, Erreurs

## Flux de traitement

```
1. [Email Server] Nouveau message reçu
   ↓
2. [Email Monitor] Détection du nouveau message
   ↓
3. [Email Parser] Extraction des données
   ↓
4. [Content Extractor] Nettoyage et préparation
   ↓
5. [Classifier] Classification (catégorie + priorité)
   ↓
6. [Ticket Manager] Création du ticket dans Google Sheets
   ↓
7. [Notification] Alerte aux équipes
   ↓
8. [Email Monitor] Marquage comme traité
```

## Structure de données

### EmailData
```python
{
    "message_id": str,
    "sender": {
        "name": str,
        "email": str
    },
    "subject": str,
    "body": {
        "text": str,
        "html": Optional[str]
    },
    "date": datetime,
    "attachments": List[Attachment],
    "headers": Dict[str, str]
}
```

### Ticket
```python
{
    "id": str,
    "date": datetime,
    "sender_name": str,
    "sender_email": str,
    "subject": str,
    "category": str,
    "priority": str,
    "status": str,
    "description": str,
    "assigned_to": Optional[str],
    "notes": Optional[str]
}
```

## Sécurité

- ✅ Credentials dans variables d'environnement
- ✅ Service Account pour Google Sheets
- ✅ App Password pour Gmail
- ✅ Validation des entrées
- ✅ Logs sans données sensibles

## Performance

- **Traitement** : < 2s par email
- **Throughput** : 100+ emails/heure
- **Latence API** : < 500ms

## Scalabilité

- Architecture modulaire
- Support multi-instances
- Cache des modèles ML
- Traitement asynchrone possible

## Technologies

- **Langage** : Python 3.9+
- **ML** : scikit-learn, NLTK, spaCy
- **APIs** : Google Sheets API, IMAP
- **Data** : pandas, numpy
- **Utils** : loguru, pydantic, schedule

