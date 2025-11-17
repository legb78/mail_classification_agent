"""
Point d'entrée principal de l'application
"""

import sys
import argparse
from pathlib import Path
from typing import Optional

# Ajouter le répertoire parent au PYTHONPATH pour permettre les imports
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.utils.config import load_config
from src.utils.logger import setup_logger, get_logger
from src.email.monitor import EmailMonitor
from src.email.parser import EmailParser
from src.classification.classifier import TicketClassifier


def main():
    """Fonction principale"""
    parser = argparse.ArgumentParser(
        description="Agent de traitement automatique de tickets par e-mail"
    )
    
    parser.add_argument(
        "--mode",
        choices=["manual", "auto", "daemon", "test"],
        default="auto",
        help="Mode d'exécution"
    )
    
    parser.add_argument(
        "--interval",
        type=int,
        default=60,
        help="Intervalle de vérification en secondes (mode auto)"
    )
    
    parser.add_argument(
        "--email-id",
        type=str,
        help="ID de l'email à traiter (mode manual)"
    )
    
    parser.add_argument(
        "--config",
        type=str,
        help="Chemin vers le fichier de configuration"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Mode verbose"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Mode test sans écriture dans Google Sheets"
    )
    
    args = parser.parse_args()
    
    # Charger la configuration
    try:
        config = load_config()
    except Exception as e:
        print(f"Erreur lors du chargement de la configuration: {e}")
        sys.exit(1)
    
    # Configurer le logger
    log_level = "DEBUG" if args.verbose else config.logging.level
    setup_logger(
        log_level=log_level,
        log_file=config.logging.file,
        rotation=config.logging.rotation,
        retention=config.logging.retention
    )
    
    logger = get_logger(__name__)
    logger.info("Démarrage de l'agent de traitement de tickets")
    logger.info(f"Mode: {args.mode}")
    
    if args.dry_run:
        logger.warning("Mode DRY-RUN activé - aucune modification ne sera effectuée")
    
    # TODO: Implémenter les différents modes
    # - Mode manual: traiter un email spécifique
    # - Mode auto: polling automatique
    # - Mode daemon: service en arrière-plan
    
    if args.mode == "manual":
        if not args.email_id:
            logger.error("L'option --email-id est requise en mode manual")
            sys.exit(1)
        logger.info(f"Traitement de l'email: {args.email_id}")
        # TODO: Implémenter le traitement manuel
    
    elif args.mode == "auto":
        logger.info(f"Polling automatique activé (intervalle: {args.interval}s)")
        # TODO: Implémenter le polling automatique
    
    elif args.mode == "daemon":
        logger.info("Mode daemon activé")
        # TODO: Implémenter le mode daemon
    
    elif args.mode == "test":
        logger.info("Mode test activé - Test de connexion et récupération d'emails")
        test_email_connection(config, logger, args.dry_run)
    
    logger.info("Arrêt de l'agent")


def test_email_connection(config, logger, dry_run: bool = False):
    """
    Teste la connexion email et récupère quelques emails pour test
    
    Args:
        config: Configuration de l'application
        logger: Logger
        dry_run: Mode test sans modification
    """
    # Vérifier la configuration email
    if not config.email.user or not config.email.password:
        logger.error("EMAIL_USER et EMAIL_PASSWORD doivent être configurés dans le fichier .env")
        logger.info("Ajoutez ces variables dans votre fichier .env:")
        logger.info("EMAIL_USER=votre-email@gmail.com")
        logger.info("EMAIL_PASSWORD=votre-mot-de-passe-app")
        return
    
    # Initialiser les composants
    email_monitor = EmailMonitor(config.email)
    email_parser = EmailParser()
    
    # Initialiser le classificateur si Groq est configuré
    classifier = None
    if config.classification.use_groq and config.classification.groq_api_key:
        try:
            classifier = TicketClassifier(config.classification)
            logger.info("Classificateur Groq initialisé")
        except Exception as e:
            logger.warning(f"Impossible d'initialiser le classificateur Groq: {e}")
            logger.warning("Les emails seront récupérés mais non classifiés")
    
    # Connexion
    logger.info("Tentative de connexion à la boîte mail...")
    if not email_monitor.connect():
        logger.error("Échec de la connexion à la boîte mail")
        return
    
    try:
        # Récupérer les emails récents
        logger.info("Récupération des emails récents...")
        emails = email_monitor.fetch_recent_emails(limit=5)
        
        if not emails:
            logger.info("Aucun email non lu trouvé. Récupération des derniers emails...")
            emails = email_monitor.fetch_all_emails(limit=3)
        
        if not emails:
            logger.info("Aucun email trouvé dans la boîte mail")
            return
        
        logger.info(f"\n{'='*60}")
        logger.info(f"📧 {len(emails)} email(s) trouvé(s)")
        logger.info(f"{'='*60}\n")
        
        # Traiter chaque email
        for i, raw_email in enumerate(emails, 1):
            try:
                # Parser l'email
                email_data = email_parser.parse_email(raw_email)
                
                logger.info(f"\n--- Email {i}/{len(emails)} ---")
                logger.info(f"De: {email_data['sender_name']} <{email_data['sender_email']}>")
                logger.info(f"Sujet: {email_data['subject']}")
                logger.info(f"Date: {email_data['date']}")
                logger.info(f"Corps (premiers 200 caractères): {email_data['body'][:200]}...")
                
                # Classification si disponible
                if classifier:
                    logger.info("\n🔍 Classification en cours...")
                    try:
                        classification = classifier.classify(
                            subject=email_data['subject'],
                            body=email_data['body'],
                            sender_email=email_data['sender_email']
                        )
                        
                        logger.info(f"✅ Catégorie: {classification.get('category', 'N/A')}")
                        logger.info(f"✅ Priorité: {classification.get('priority', 'N/A')}")
                        logger.info(f"✅ Confiance: {classification.get('confidence', 0):.2%}")
                        
                        if classification.get('extracted_info'):
                            logger.info(f"📋 Informations extraites: {classification['extracted_info']}")
                        
                    except Exception as e:
                        logger.error(f"Erreur lors de la classification: {e}")
                else:
                    logger.warning("⚠️  Classification non disponible (GROQ_API_KEY non configuré)")
                
                logger.info("-" * 60)
                
            except Exception as e:
                logger.error(f"Erreur lors du traitement de l'email {i}: {e}")
                continue
        
        logger.info(f"\n✅ Test terminé avec succès!")
        logger.info(f"📊 {len(emails)} email(s) traité(s)")
        
    finally:
        email_monitor.disconnect()


if __name__ == "__main__":
    main()

