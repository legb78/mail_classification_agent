"""
Service de surveillance et récupération des emails via IMAP
"""

import imaplib
import ssl
from typing import List, Optional, Dict
from src.utils.logger import get_logger
from src.utils.config import EmailConfig


class EmailMonitor:
    """Surveille une boîte mail via IMAP et récupère les nouveaux emails"""
    
    def __init__(self, config: EmailConfig):
        """
        Initialise le moniteur email
        
        Args:
            config: Configuration email
        """
        self.config = config
        self.logger = get_logger(__name__)
        self.connection: Optional[imaplib.IMAP4_SSL] = None
    
    def connect(self) -> bool:
        """
        Établit la connexion IMAP
        
        Returns:
            True si la connexion réussit, False sinon
        """
        try:
            if not self.config.user or not self.config.password:
                self.logger.error("EMAIL_USER et EMAIL_PASSWORD sont requis")
                return False
            
            self.logger.info(f"Connexion à {self.config.host}:{self.config.port}")
            
            if self.config.use_ssl:
                # Créer un contexte SSL
                context = ssl.create_default_context()
                self.connection = imaplib.IMAP4_SSL(
                    self.config.host,
                    self.config.port,
                    ssl_context=context
                )
            else:
                self.connection = imaplib.IMAP4(self.config.host, self.config.port)
            
            # Authentification
            self.connection.login(self.config.user, self.config.password)
            
            # Sélectionner le dossier
            self.connection.select(self.config.folder)
            
            self.logger.info(f"Connexion réussie au dossier: {self.config.folder}")
            return True
            
        except imaplib.IMAP4.error as e:
            self.logger.error(f"Erreur IMAP: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Erreur lors de la connexion: {e}")
            return False
    
    def disconnect(self):
        """Ferme la connexion IMAP"""
        if self.connection:
            try:
                self.connection.close()
                self.connection.logout()
                self.logger.info("Connexion IMAP fermée")
            except Exception as e:
                self.logger.warning(f"Erreur lors de la fermeture: {e}")
            finally:
                self.connection = None
    
    def fetch_recent_emails(self, limit: int = 10) -> List[bytes]:
        """
        Récupère les emails récents
        
        Args:
            limit: Nombre maximum d'emails à récupérer
            
        Returns:
            Liste d'emails bruts en bytes
        """
        if not self.connection:
            self.logger.error("Pas de connexion IMAP active")
            return []
        
        try:
            # Rechercher les emails non lus
            status, messages = self.connection.search(None, 'UNSEEN')
            
            if status != 'OK':
                self.logger.warning("Aucun email non lu trouvé")
                return []
            
            email_ids = messages[0].split()
            
            # Limiter le nombre
            email_ids = email_ids[-limit:] if len(email_ids) > limit else email_ids
            
            emails = []
            for email_id in email_ids:
                try:
                    status, msg_data = self.connection.fetch(email_id, '(RFC822)')
                    if status == 'OK' and msg_data[0]:
                        emails.append(msg_data[0][1])
                except Exception as e:
                    self.logger.warning(f"Erreur lors de la récupération de l'email {email_id}: {e}")
            
            self.logger.info(f"{len(emails)} email(s) récupéré(s)")
            return emails
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération des emails: {e}")
            return []
    
    def fetch_all_emails(self, limit: int = 10) -> List[bytes]:
        """
        Récupère tous les emails (lus et non lus)
        
        Args:
            limit: Nombre maximum d'emails à récupérer
            
        Returns:
            Liste d'emails bruts en bytes
        """
        if not self.connection:
            self.logger.error("Pas de connexion IMAP active")
            return []
        
        try:
            # Rechercher tous les emails
            status, messages = self.connection.search(None, 'ALL')
            
            if status != 'OK':
                self.logger.warning("Aucun email trouvé")
                return []
            
            email_ids = messages[0].split()
            
            # Limiter le nombre
            email_ids = email_ids[-limit:] if len(email_ids) > limit else email_ids
            
            emails = []
            for email_id in email_ids:
                try:
                    status, msg_data = self.connection.fetch(email_id, '(RFC822)')
                    if status == 'OK' and msg_data[0]:
                        emails.append(msg_data[0][1])
                except Exception as e:
                    self.logger.warning(f"Erreur lors de la récupération de l'email {email_id}: {e}")
            
            self.logger.info(f"{len(emails)} email(s) récupéré(s)")
            return emails
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération des emails: {e}")
            return []
    
    def mark_as_read(self, email_id: bytes):
        """
        Marque un email comme lu
        
        Args:
            email_id: ID de l'email à marquer
        """
        if not self.connection:
            return
        
        try:
            self.connection.store(email_id, '+FLAGS', '\\Seen')
        except Exception as e:
            self.logger.warning(f"Erreur lors du marquage comme lu: {e}")
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()

