"""
Script d'exemple pour tester la classification avec Groq
"""

import sys
from pathlib import Path

# Ajouter le répertoire src au path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.config import load_config
from src.utils.logger import setup_logger, get_logger
from src.classification.classifier import TicketClassifier


def main():
    """Test de la classification avec Groq"""
    
    # Charger la configuration
    try:
        config = load_config()
    except Exception as e:
        print(f"Erreur lors du chargement de la configuration: {e}")
        print("\nAssurez-vous d'avoir configuré le fichier .env avec:")
        print("- GROQ_API_KEY=votre-cle-api")
        print("- USE_GROQ_LLM=true")
        sys.exit(1)
    
    # Configurer le logger
    setup_logger(
        log_level=config.logging.level,
        log_file=None  # Pas de fichier pour les tests
    )
    
    logger = get_logger(__name__)
    
    # Vérifier la configuration Groq
    if not config.classification.use_groq:
        print("⚠️  USE_GROQ_LLM est désactivé. Activez-le dans le fichier .env")
        sys.exit(1)
    
    if not config.classification.groq_api_key:
        print("❌ GROQ_API_KEY n'est pas configurée dans le fichier .env")
        print("Obtenez votre clé sur: https://console.groq.com")
        sys.exit(1)
    
    # Initialiser le classificateur
    try:
        classifier = TicketClassifier(config.classification)
        print(f"✅ Classificateur Groq initialisé avec le modèle: {config.classification.groq_model}\n")
    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation du classificateur: {e}")
        sys.exit(1)
    
    # Exemples de tickets à classifier
    test_cases = [
        {
            "subject": "Bug critique - Application inaccessible",
            "body": "Bonjour, l'application est complètement inaccessible depuis ce matin. Tous les utilisateurs sont bloqués. C'est urgent !",
            "sender": "admin@company.com"
        },
        {
            "subject": "Demande de devis",
            "body": "Je souhaiterais obtenir un devis pour votre solution premium. Pouvez-vous me contacter ?",
            "sender": "client@example.com"
        },
        {
            "subject": "Question sur la facturation",
            "body": "Bonjour, j'ai une question concernant ma dernière facture. Le montant semble incorrect.",
            "sender": "user@example.com"
        },
        {
            "subject": "Problème de connexion",
            "body": "Je rencontre des difficultés pour me connecter à mon compte. Le mot de passe ne fonctionne pas.",
            "sender": "support@example.com"
        }
    ]
    
    print("=" * 70)
    print("TEST DE CLASSIFICATION AVEC GROQ LLM")
    print("=" * 70)
    print()
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"📧 Ticket #{i}")
        print(f"Sujet: {test_case['subject']}")
        print(f"Expéditeur: {test_case['sender']}")
        print(f"Contenu: {test_case['body'][:100]}...")
        print()
        
        try:
            result = classifier.classify(
                subject=test_case['subject'],
                body=test_case['body'],
                sender_email=test_case['sender']
            )
            
            print(f"✅ Résultat de la classification:")
            print(f"   📁 Catégorie: {result['category']}")
            print(f"   ⚡ Priorité: {result['priority']}")
            print(f"   📊 Confiance: {result['confidence']:.2%}")
            print(f"   💭 Raisonnement: {result['reasoning']}")
            
            # Test d'extraction d'informations
            info = classifier.extract_key_information(
                subject=test_case['subject'],
                body=test_case['body']
            )
            
            if info:
                print(f"   📋 Informations extraites:")
                if info.get('main_issue'):
                    print(f"      - Problème: {info['main_issue']}")
                if info.get('product_service') and info['product_service'] != "N/A":
                    print(f"      - Produit: {info['product_service']}")
                if info.get('reference_number') and info['reference_number'] != "N/A":
                    print(f"      - Référence: {info['reference_number']}")
            
        except Exception as e:
            print(f"❌ Erreur lors de la classification: {e}")
            logger.exception("Erreur détaillée")
        
        print()
        print("-" * 70)
        print()
    
    print("✅ Tests terminés !")


if __name__ == "__main__":
    main()

