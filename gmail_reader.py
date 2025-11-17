"""
Gmail Reader Module

Handles Gmail API connection, reading unread emails, and marking them as read.
"""

import os
import base64
import logging
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.modify']


class GmailReader:
    """Handles Gmail API operations."""
    
    def __init__(self, credentials_file, token_file):
        """
        Initialize Gmail Reader.
        
        Args:
            credentials_file: Path to OAuth 2.0 credentials JSON file
            token_file: Path to save/load OAuth token
        """
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.service = None
        self.creds = None
        
    def authenticate(self):
        """Authenticate with Gmail API using OAuth 2.0."""
        try:
            # Load existing token if available
            if os.path.exists(self.token_file):
                self.creds = Credentials.from_authorized_user_file(self.token_file, SCOPES)
                logger.info("Loaded existing Gmail token")
            
            # If no valid credentials, get new ones
            if not self.creds or not self.creds.valid:
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    logger.info("Refreshing Gmail token")
                    self.creds.refresh(Request())
                else:
                    logger.info("Requesting new Gmail authorization")
                    if not os.path.exists(self.credentials_file):
                        raise FileNotFoundError(
                            f"Gmail credentials file not found: {self.credentials_file}\n"
                            "Please download OAuth 2.0 credentials from Google Cloud Console."
                        )
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_file, SCOPES
                    )
                    self.creds = flow.run_local_server(port=0)
                
                # Save credentials for next run
                os.makedirs(os.path.dirname(self.token_file), exist_ok=True)
                with open(self.token_file, 'w') as token:
                    token.write(self.creds.to_json())
                logger.info(f"Saved Gmail token to {self.token_file}")
            
            # Build Gmail service
            self.service = build('gmail', 'v1', credentials=self.creds)
            logger.info("Gmail API authenticated successfully")
            return True
            
        except Exception as e:
            logger.error(f"Gmail authentication failed: {str(e)}")
            raise
    
    def get_unread_emails(self, max_results=100):
        """
        Get list of unread email IDs.
        
        Args:
            max_results: Maximum number of emails to retrieve
            
        Returns:
            List of email message IDs
        """
        try:
            if not self.service:
                raise RuntimeError("Gmail service not initialized. Call authenticate() first.")
            
            # Query for unread emails
            results = self.service.users().messages().list(
                userId='me',
                q='is:unread',
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            logger.info(f"Found {len(messages)} unread emails")
            return [msg['id'] for msg in messages]
            
        except HttpError as e:
            logger.error(f"Error fetching unread emails: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error getting unread emails: {str(e)}")
            raise
    
    def get_email_content(self, message_id):
        """
        Extract subject and body from an email message.
        
        Args:
            message_id: Gmail message ID
            
        Returns:
            Dictionary with 'id', 'subject', 'body', 'snippet'
        """
        try:
            if not self.service:
                raise RuntimeError("Gmail service not initialized. Call authenticate() first.")
            
            # Get message details
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()
            
            # Extract headers
            headers = message['payload'].get('headers', [])
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
            
            # Extract body
            body = self._extract_body(message['payload'])
            
            # Get snippet as fallback
            snippet = message.get('snippet', '')
            
            result = {
                'id': message_id,
                'subject': subject,
                'body': body or snippet,
                'snippet': snippet
            }
            
            logger.debug(f"Extracted email: {subject[:50]}...")
            return result
            
        except HttpError as e:
            logger.error(f"Error fetching email {message_id}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error extracting email {message_id}: {str(e)}")
            raise
    
    def _extract_body(self, payload):
        """
        Recursively extract plain text body from email payload.
        
        Args:
            payload: Email payload structure
            
        Returns:
            Plain text body string
        """
        body = ""
        
        if 'parts' in payload:
            # Multipart message
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    data = part['body'].get('data')
                    if data:
                        body += base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                elif part['mimeType'] == 'text/html':
                    # Fallback to HTML if no plain text
                    if not body:
                        data = part['body'].get('data')
                        if data:
                            html_body = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                            # Simple HTML stripping (basic)
                            import re
                            body = re.sub('<[^<]+?>', '', html_body)
                elif 'parts' in part:
                    # Nested parts
                    body += self._extract_body(part)
        else:
            # Single part message
            if payload.get('mimeType') == 'text/plain':
                data = payload['body'].get('data')
                if data:
                    body = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
            elif payload.get('mimeType') == 'text/html':
                data = payload['body'].get('data')
                if data:
                    html_body = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                    import re
                    body = re.sub('<[^<]+?>', '', html_body)
        
        return body.strip()
    
    def mark_as_read(self, message_id):
        """
        Mark an email as read.
        
        Args:
            message_id: Gmail message ID to mark as read
        """
        try:
            if not self.service:
                raise RuntimeError("Gmail service not initialized. Call authenticate() first.")
            
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            
            logger.debug(f"Marked email {message_id} as read")
            
        except HttpError as e:
            logger.error(f"Error marking email {message_id} as read: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error marking email {message_id} as read: {str(e)}")
            raise

