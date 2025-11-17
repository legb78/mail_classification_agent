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

# Urgency to sheet name mapping
URGENCY_SHEET_MAP = {
    'Critique': 'Critique',
    'Élevée': 'Élevée',
    'Modérée': 'Modérée',
    'Faible': 'Faible',
    'Anodine': 'Anodine'
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
        Verify that all required urgency sheets exist in the spreadsheet.
        Creates missing sheets automatically.
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
            
            # Check for required urgency sheets and create missing ones
            missing_sheets = []
            for urgency, sheet_name in URGENCY_SHEET_MAP.items():
                if sheet_name not in existing_sheets:
                    missing_sheets.append(sheet_name)
            
            if missing_sheets:
                logger.info(f"Creating missing sheets: {', '.join(missing_sheets)}")
                self._create_sheets(missing_sheets)
                logger.info(f"Successfully created {len(missing_sheets)} sheet(s)")
            
            # Verify headers exist in each sheet
            self._ensure_headers()
            
            logger.info("All required urgency sheets verified and ready")
            
        except HttpError as e:
            logger.error(f"Error verifying sheets: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error verifying sheets: {str(e)}")
            raise
    
    def _create_sheets(self, sheet_names):
        """
        Create new sheets in the spreadsheet.
        
        Args:
            sheet_names: List of sheet names to create
        """
        try:
            requests = []
            for sheet_name in sheet_names:
                requests.append({
                    'addSheet': {
                        'properties': {
                            'title': sheet_name
                        }
                    }
                })
            
            body = {
                'requests': requests
            }
            
            self.service.spreadsheets().batchUpdate(
                spreadsheetId=self.spreadsheet_id,
                body=body
            ).execute()
            
            logger.info(f"Created sheets: {', '.join(sheet_names)}")
            
        except HttpError as e:
            logger.error(f"Error creating sheets: {str(e)}")
            raise
    
    def _ensure_headers(self):
        """
        Ensure that each urgency sheet has the required headers.
        """
        try:
            headers = ['Sujet', 'Catégorie', 'Synthèse']
            
            for urgency, sheet_name in URGENCY_SHEET_MAP.items():
                # Check if headers exist
                range_name = f"{sheet_name}!A1:C1"
                result = self.service.spreadsheets().values().get(
                    spreadsheetId=self.spreadsheet_id,
                    range=range_name
                ).execute()
                
                values = result.get('values', [])
                
                # If no headers or headers don't match, add them
                if not values or values[0] != headers:
                    body = {
                        'values': [headers]
                    }
                    self.service.spreadsheets().values().update(
                        spreadsheetId=self.spreadsheet_id,
                        range=range_name,
                        valueInputOption='RAW',
                        body=body
                    ).execute()
                    logger.info(f"Added headers to sheet '{sheet_name}'")
                else:
                    logger.debug(f"Headers already exist in sheet '{sheet_name}'")
                    
        except HttpError as e:
            logger.error(f"Error ensuring headers: {str(e)}")
            raise
    
    def write_result(self, category: str, subject: str, urgency: str, summary: str):
        """
        Write a single result row to the appropriate urgency sheet.
        
        Args:
            category: Email category
            subject: Email subject
            urgency: Urgency level (must match URGENCY_SHEET_MAP)
            summary: Email summary
        """
        try:
            if not self.service:
                raise RuntimeError("Sheets service not initialized. Call authenticate() first.")
            
            # Get sheet name for urgency
            sheet_name = URGENCY_SHEET_MAP.get(urgency)
            if not sheet_name:
                # Try to find closest match
                urgency_lower = urgency.lower()
                for urg, sheet in URGENCY_SHEET_MAP.items():
                    if urg.lower() in urgency_lower or urgency_lower in urg.lower():
                        sheet_name = sheet
                        break
                if not sheet_name:
                    logger.warning(f"Unknown urgency '{urgency}', defaulting to 'Modérée'")
                    sheet_name = 'Modérée'
            
            # Prepare row data (without urgency column since it's the sheet name)
            row_data = [subject, category, summary]
            
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
            
            logger.info(f"Written to {sheet_name}: {subject[:50]}... ({category})")
            
        except HttpError as e:
            logger.error(f"Error writing to sheet: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error writing to sheet: {str(e)}")
            raise
    
    def write_batch(self, results: list):
        """
        Write multiple results to their respective urgency sheets.
        
        Args:
            results: List of result dictionaries with 'categorie', 'subject', 'urgence', 'synthese'
        """
        try:
            if not self.service:
                raise RuntimeError("Sheets service not initialized. Call authenticate() first.")
            
            if not results:
                logger.warning("No results to write")
                return
            
            # Group results by urgency
            by_urgency = {}
            for result in results:
                urgency = result.get('urgence', 'Modérée')
                # Normalize urgency to match sheet names
                urgency_normalized = None
                urgency_lower = urgency.lower()
                for urg, sheet in URGENCY_SHEET_MAP.items():
                    if urg.lower() == urgency_lower or urg.lower() in urgency_lower or urgency_lower in urg.lower():
                        urgency_normalized = urg
                        break
                if not urgency_normalized:
                    logger.warning(f"Unknown urgency '{urgency}', defaulting to 'Modérée'")
                    urgency_normalized = 'Modérée'
                
                if urgency_normalized not in by_urgency:
                    by_urgency[urgency_normalized] = []
                by_urgency[urgency_normalized].append(result)
            
            # Write each urgency's results to its sheet
            for urgency, urgency_results in by_urgency.items():
                sheet_name = URGENCY_SHEET_MAP.get(urgency)
                if not sheet_name:
                    logger.warning(f"Unknown urgency '{urgency}', skipping")
                    continue
                
                # Prepare batch data (without urgency column since it's the sheet name)
                rows_data = []
                for result in urgency_results:
                    rows_data.append([
                        result.get('subject', ''),
                        result.get('categorie', 'Support utilisateur'),
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

