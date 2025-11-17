# Architecture du Système

## Vue d'ensemble

L'agent de traitement automatique de tickets par e-mail est conçu comme un système modulaire et extensible, permettant la réception, classification et gestion automatique de tickets via e-mail.

## Architecture générale

```
┌─────────────────────────────────────────────────────────────┐
│                      Email Server                            │
│                    (IMAP/SMTP Server)                        │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Email Monitor Service                     │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  • Polling Service (intervalle configurable)        │  │
│  │  • Email Filtering (critères de sélection)            │  │
│  │  • Duplicate Detection (éviter les doublons)         │  │
│  └──────────────────────────────────────────────────────┘  │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   Email Processing Layer                     │
│  ┌──────────────────┐  ┌──────────────────┐              │
│  │  Email Parser    │  │  Content Extractor│              │
│  │  • Headers       │  │  • Text Body      │              │
│  │  • Metadata      │  │  • HTML Body      │              │
│  │  • Attachments   │  │  • Attachments   │              │
│  └──────────────────┘  └──────────────────┘              │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              Classification & Intelligence Layer             │
│  ┌──────────────────┐  ┌──────────────────┐              │
│  │  Text Preprocessor│  │  ML Classifier   │              │
│  │  • Cleaning      │  │  • Category       │              │
│  │  • Normalization │  │  • Priority       │              │
│  │  • Tokenization  │  │  • Urgency        │              │
│  └──────────────────┘  └──────────────────┘              │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Data Integration Layer                    │
│  ┌──────────────────┐  ┌──────────────────┐              │
│  │ Google Sheets API│  │  Notification     │              │
│  │  • Create Ticket │  │  • Slack         │              │
│  │  • Update Status │  │  • Email         │              │
│  │  • Log History   │  │  • Teams         │              │
│  └──────────────────┘  └──────────────────┘              │
└─────────────────────────────────────────────────────────────┘
```

## Composants détaillés

### 1. Email Monitor Service

**Responsabilités :**
- Surveiller la boîte mail en continu
- Détecter les nouveaux e-mails
- Filtrer les e-mails pertinents
- Éviter le traitement des doublons

**Implémentation :**
```python
class EmailMonitor:
    - connect_to_server()
    - poll_for_new_emails()
    - filter_emails()
    - mark_as_processed()
```

**Configuration :**
- Intervalle de polling : 60 secondes (configurable)
- Critères de filtrage : expéditeur, sujet, mots-clés
- Gestion des erreurs : retry avec backoff exponentiel

### 2. Email Parser

**Responsabilités :**
- Extraire les métadonnées (expéditeur, date, sujet)
- Parser le contenu (texte, HTML)
- Gérer les pièces jointes
- Normaliser les données

**Structure de données :**
```python
@dataclass
class EmailData:
    message_id: str
    sender_name: str
    sender_email: str
    subject: str
    body_text: str
    body_html: Optional[str]
    date: datetime
    attachments: List[Attachment]
    headers: Dict[str, str]
```

### 3. Classification Engine

**Architecture ML :**

```
Input Text
    │
    ▼
Preprocessing
    │
    ├─► Text Cleaning
    ├─► Tokenization
    ├─► Stop Words Removal
    └─► Stemming/Lemmatization
    │
    ▼
Feature Extraction
    │
    ├─► TF-IDF Vectorization
    ├─► Word Embeddings (optionnel)
    └─► Custom Features
    │
    ▼
Classification Models
    │
    ├─► Category Classifier (SVM/Random Forest)
    ├─► Priority Classifier (Regression)
    └─► Urgency Detector (Rule-based + ML)
    │
    ▼
Output
    │
    ├─► Category: Technique, Commercial, Support...
    ├─► Priority: Critique, Haute, Moyenne, Basse
    └─► Confidence Score
```

**Modèles utilisés :**
- **Catégorie** : Random Forest / SVM avec TF-IDF
- **Priorité** : Regression avec features custom
- **Urgence** : Règles métier + détection de mots-clés

### 4. Google Sheets Integration

**Structure du Sheet :**

| Colonne | Type | Description |
|---------|------|-------------|
| ID | String | Identifiant unique du ticket |
| Date | DateTime | Date de réception |
| Expéditeur | String | Nom de l'expéditeur |
| Email | String | Email de l'expéditeur |
| Sujet | String | Sujet de l'email |
| Catégorie | String | Catégorie classifiée |
| Priorité | String | Priorité assignée |
| Statut | String | Nouveau, En cours, Résolu |
| Description | Text | Corps du message |
| Traité par | String | Agent/équipe assigné |
| Notes | Text | Notes additionnelles |

**Opérations :**
- Création de ticket (append)
- Mise à jour de statut (update)
- Recherche de doublons (query)
- Historique des modifications (logging)

### 5. Notification Service

**Canaux de notification :**
- **Slack** : Webhook pour notifications critiques
- **Email** : Notifications aux équipes
- **Microsoft Teams** : Intégration Teams (optionnel)

**Types de notifications :**
- Nouveau ticket créé
- Ticket critique détecté
- Erreur de traitement
- Statistiques quotidiennes

## Flux de données

### Flux principal

```
1. Email reçu → Email Server
2. Email Monitor détecte nouveau message
3. Email Parser extrait les données
4. Classification Engine classe le ticket
5. Google Sheets API crée le ticket
6. Notification Service alerte les équipes
7. Email marqué comme traité
```

### Gestion des erreurs

```
┌─────────────────┐
│  Error Occurs   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Error Handler  │
│  • Log Error    │
│  • Retry Logic   │
│  • Fallback      │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌──────┐  ┌──────┐
│Retry │  │Alert │
└──────┘  └──────┘
```

## Sécurité

### Authentification
- **Email** : OAuth 2.0 ou App Password
- **Google Sheets** : Service Account avec JSON credentials
- **API Keys** : Stockées dans variables d'environnement

### Données sensibles
- Aucune donnée sensible dans les logs
- Chiffrement des credentials
- Accès limité aux ressources Google

### Validation
- Validation des entrées (Pydantic)
- Sanitization du contenu HTML
- Vérification des types de fichiers joints

## Performance

### Optimisations
- **Caching** : Cache des modèles ML en mémoire
- **Batch Processing** : Traitement par lots des emails
- **Async Operations** : Opérations asynchrones pour I/O
- **Connection Pooling** : Pool de connexions IMAP

### Métriques
- Temps de traitement moyen : < 2 secondes par email
- Throughput : 100+ emails/heure
- Latence Google Sheets API : < 500ms

## Scalabilité

### Architecture horizontale
- Plusieurs instances peuvent tourner en parallèle
- Utilisation de locks distribués (Redis) pour éviter les doublons
- Load balancing possible avec message queue

### Extension future
- Support de multiples boîtes mail
- Intégration avec systèmes de ticketing (Jira, Zendesk)
- API REST pour accès externe
- Dashboard web pour monitoring

## Monitoring & Logging

### Logs structurés
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "level": "INFO",
  "component": "email_monitor",
  "action": "email_processed",
  "email_id": "msg_12345",
  "ticket_id": "TKT-2024-001",
  "category": "Technique",
  "priority": "Haute",
  "processing_time_ms": 1250
}
```

### Métriques collectées
- Nombre d'emails traités
- Taux de classification correcte
- Temps de traitement
- Erreurs par type
- Utilisation des ressources

## Déploiement

### Environnements
- **Development** : Local avec mock Google Sheets
- **Staging** : Test avec données réelles
- **Production** : Service daemon avec monitoring

### Déploiement recommandé
- **Container** : Docker pour isolation
- **Orchestration** : Docker Compose ou Kubernetes
- **Scheduling** : Systemd ou Cron pour daemon
- **CI/CD** : GitHub Actions ou GitLab CI

## Maintenance

### Tâches régulières
- Entraînement périodique du modèle ML
- Nettoyage des logs anciens
- Vérification de la santé du système
- Mise à jour des dépendances

### Backup
- Backup des modèles ML
- Export périodique des tickets
- Sauvegarde de la configuration

