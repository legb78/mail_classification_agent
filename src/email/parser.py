"""
Parser pour extraire les informations des emails
"""

import email
from email import message as email_message
from email.header import decode_header
from typing import Dict, Optional, Tuple
from datetime import datetime
from src.utils.logger import get_logger


class EmailParser:
    """Parse les emails pour extraire les informations structurées"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
    
    def parse_email(self, raw_email: bytes) -> Dict[str, any]:
        """
        Parse un email brut et extrait les informations
        
        Args:
            raw_email: Email brut en bytes
            
        Returns:
            Dictionnaire contenant les informations de l'email
        """
        try:
            msg = email.message_from_bytes(raw_email)
            
            # Sujet
            subject = self._decode_header(msg.get("Subject", ""))
            
            # Expéditeur
            sender_name, sender_email = self._parse_address(msg.get("From", ""))
            
            # Date
            date_str = msg.get("Date", "")
            date = self._parse_date(date_str)
            
            # Corps du message
            body = self._extract_body(msg)
            
            # ID du message
            message_id = msg.get("Message-ID", "")
            
            # Références
            references = msg.get("References", "")
            in_reply_to = msg.get("In-Reply-To", "")
            
            result = {
                "subject": subject,
                "sender_name": sender_name,
                "sender_email": sender_email,
                "date": date,
                "body": body,
                "message_id": message_id,
                "references": references,
                "in_reply_to": in_reply_to,
                "raw_email": raw_email
            }
            
            self.logger.debug(f"Email parsé: {subject[:50]}...")
            return result
            
        except Exception as e:
            self.logger.error(f"Erreur lors du parsing de l'email: {e}")
            raise
    
    def _decode_header(self, header: str) -> str:
        """Décode un header email"""
        if not header:
            return ""
        
        decoded_parts = decode_header(header)
        decoded_string = ""
        
        for part, encoding in decoded_parts:
            if isinstance(part, bytes):
                if encoding:
                    decoded_string += part.decode(encoding)
                else:
                    decoded_string += part.decode('utf-8', errors='ignore')
            else:
                decoded_string += part
        
        return decoded_string.strip()
    
    def _parse_address(self, address_str: str) -> Tuple[str, str]:
        """Parse une adresse email"""
        if not address_str:
            return ("", "")
        
        try:
            name, email_addr = email.utils.parseaddr(address_str)
            return (name or "", email_addr or "")
        except Exception:
            return ("", address_str)
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse une date email"""
        if not date_str:
            return None
        
        try:
            return email.utils.parsedate_to_datetime(date_str)
        except Exception:
            return None
    
    def _extract_body(self, msg: email_message.Message) -> str:
        """Extrait le corps du message"""
        body = ""
        
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition", ""))
                
                # Ignorer les pièces jointes
                if "attachment" in content_disposition:
                    continue
                
                # Extraire le texte
                if content_type == "text/plain":
                    try:
                        payload = part.get_payload(decode=True)
                        if payload:
                            charset = part.get_content_charset() or "utf-8"
                            body += payload.decode(charset, errors='ignore')
                    except Exception as e:
                        self.logger.warning(f"Erreur lors de l'extraction du texte: {e}")
                
                elif content_type == "text/html":
                    # Si on a déjà du texte, on garde le texte
                    # Sinon, on peut extraire le HTML
                    if not body:
                        try:
                            payload = part.get_payload(decode=True)
                            if payload:
                                charset = part.get_content_charset() or "utf-8"
                                html_content = payload.decode(charset, errors='ignore')
                                # Simplification basique du HTML
                                body = self._html_to_text(html_content)
                        except Exception as e:
                            self.logger.warning(f"Erreur lors de l'extraction du HTML: {e}")
        else:
            # Message simple
            try:
                payload = msg.get_payload(decode=True)
                if payload:
                    charset = msg.get_content_charset() or "utf-8"
                    body = payload.decode(charset, errors='ignore')
            except Exception as e:
                self.logger.warning(f"Erreur lors de l'extraction du corps: {e}")
        
        return body.strip()
    
    def _html_to_text(self, html: str) -> str:
        """Convertit du HTML en texte simple (version basique)"""
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')
            return soup.get_text(separator='\n', strip=True)
        except ImportError:
            # Si BeautifulSoup n'est pas disponible, extraction basique
            import re
            # Supprimer les balises HTML
            text = re.sub(r'<[^>]+>', '', html)
            # Décoder les entités HTML
            text = text.replace('&nbsp;', ' ')
            text = text.replace('&amp;', '&')
            text = text.replace('&lt;', '<')
            text = text.replace('&gt;', '>')
            text = text.replace('&quot;', '"')
            return text.strip()

