"""
Google Sheets Writer Module

Handles Google Sheets API operations for writing email analysis results.
"""

import os
import logging
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)

# Google Sheets API scopes
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# Category to sheet name mapping
CATEGORY_SHEET_MAP = {
    'Technique': 'Technique',
    'Administratif': 'Administratif',
    'Accès/Authentification': 'Accès/Authentification',
    'Support utilisateur': 'Support utilisateur',
    'Bug/Dysfonctionnement': 'Bug/Dysfonctionnement'
}


class SheetsWriter:
    """Handles Google Sheets API operations."""
    
    def __init__(self, credentials_file: str, token_file: str, spreadsheet_id: str):
        """
        Initialize Sheets Writer.
        
        Args:
            credentials_file: Path to OAuth 2.0 credentials JSON file
            token_file: Path to save/load OAuth token
            spreadsheet_id: Google Sheets spreadsheet ID
        """
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.spreadsheet_id = spreadsheet_id
        self.service = None
        self.creds = None
        
    def authenticate(self):
        """Authenticate with Google Sheets API using OAuth 2.0."""
        try:
            # Load existing token if available
            if os.path.exists(self.token_file):
                self.creds = Credentials.from_authorized_user_file(self.token_file, SCOPES)
                logger.info("Loaded existing Sheets token")
            
            # If no valid credentials, get new ones
            if not self.creds or not self.creds.valid:
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    logger.info("Refreshing Sheets token")
                    self.creds.refresh(Request())
                else:
                    logger.info("Requesting new Sheets authorization")
                    if not os.path.exists(self.credentials_file):
                        raise FileNotFoundError(
                            f"Sheets credentials file not found: {self.credentials_file}\n"
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
                logger.info(f"Saved Sheets token to {self.token_file}")
            
            # Build Sheets service
            self.service = build('sheets', 'v4', credentials=self.creds)
            logger.info("Google Sheets API authenticated successfully")
            return True
            
        except Exception as e:
            logger.error(f"Sheets authentication failed: {str(e)}")
            raise
    
    def verify_sheets_exist(self):
        """
        Verify that all required category sheets exist in the spreadsheet.
        
        Raises:
            ValueError: If any required sheet is missing
        """
        try:
            if not self.service:
                raise RuntimeError("Sheets service not initialized. Call authenticate() first.")
            
            # Get all sheets in the spreadsheet
            spreadsheet = self.service.spreadsheets().get(
                spreadsheetId=self.spreadsheet_id
            ).execute()
            
            existing_sheets = [sheet['properties']['title'] for sheet in spreadsheet.get('sheets', [])]
            logger.info(f"Found sheets: {', '.join(existing_sheets)}")
            
            # Check for required sheets
            missing_sheets = []
            for category, sheet_name in CATEGORY_SHEET_MAP.items():
                if sheet_name not in existing_sheets:
                    missing_sheets.append(sheet_name)
            
            if missing_sheets:
                raise ValueError(
                    f"Missing required sheets: {', '.join(missing_sheets)}\n"
                    f"Please create these sheets in your spreadsheet: {', '.join(missing_sheets)}"
                )
            
            logger.info("All required sheets verified")
            
        except HttpError as e:
            logger.error(f"Error verifying sheets: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error verifying sheets: {str(e)}")
            raise
    
    def write_result(self, category: str, subject: str, urgency: str, summary: str):
        """
        Write a single result row to the appropriate category sheet.
        
        Args:
            category: Email category (must match CATEGORY_SHEET_MAP)
            subject: Email subject
            urgency: Urgency level
            summary: Email summary
        """
        try:
            if not self.service:
                raise RuntimeError("Sheets service not initialized. Call authenticate() first.")
            
            # Get sheet name for category
            sheet_name = CATEGORY_SHEET_MAP.get(category)
            if not sheet_name:
                raise ValueError(f"Unknown category: {category}")
            
            # Prepare row data
            row_data = [subject, urgency, summary]
            
            # Find next empty row
            range_name = f"{sheet_name}!A:A"
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            next_row = len(values) + 1
            
            # Write data
            range_to_update = f"{sheet_name}!A{next_row}:C{next_row}"
            body = {
                'values': [row_data]
            }
            
            self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=range_to_update,
                valueInputOption='RAW',
                body=body
            ).execute()
            
            logger.info(f"Written to {sheet_name}: {subject[:50]}...")
            
        except HttpError as e:
            logger.error(f"Error writing to sheet: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error writing to sheet: {str(e)}")
            raise
    
    def write_batch(self, results: list):
        """
        Write multiple results to their respective sheets.
        
        Args:
            results: List of result dictionaries with 'categorie', 'subject', 'urgence', 'synthese'
        """
        try:
            if not self.service:
                raise RuntimeError("Sheets service not initialized. Call authenticate() first.")
            
            # Group results by category
            by_category = {}
            for result in results:
                category = result.get('categorie', 'Support utilisateur')
                if category not in by_category:
                    by_category[category] = []
                by_category[category].append(result)
            
            # Write each category's results
            for category, category_results in by_category.items():
                sheet_name = CATEGORY_SHEET_MAP.get(category)
                if not sheet_name:
                    logger.warning(f"Unknown category '{category}', skipping")
                    continue
                
                # Prepare batch data
                rows_data = []
                for result in category_results:
                    rows_data.append([
                        result.get('subject', ''),
                        result.get('urgence', ''),
                        result.get('synthese', '')
                    ])
                
                # Find next empty row
                range_name = f"{sheet_name}!A:A"
                result_get = self.service.spreadsheets().values().get(
                    spreadsheetId=self.spreadsheet_id,
                    range=range_name
                ).execute()
                
                values = result_get.get('values', [])
                start_row = len(values) + 1
                
                # Write batch
                range_to_update = f"{sheet_name}!A{start_row}:C{start_row + len(rows_data) - 1}"
                body = {
                    'values': rows_data
                }
                
                self.service.spreadsheets().values().update(
                    spreadsheetId=self.spreadsheet_id,
                    range=range_to_update,
                    valueInputOption='RAW',
                    body=body
                ).execute()
                
                logger.info(f"Written {len(rows_data)} rows to {sheet_name}")
            
        except HttpError as e:
            logger.error(f"Error writing batch to sheets: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error writing batch: {str(e)}")
            raise

