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

# Single sheet name for all tickets
TICKETS_SHEET_NAME = 'Tickets'


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
        Verify that the tickets sheet exists in the spreadsheet.
        Creates it automatically if missing.
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
            
            # Check if tickets sheet exists and create if missing
            if TICKETS_SHEET_NAME not in existing_sheets:
                logger.info(f"Creating missing sheet: {TICKETS_SHEET_NAME}")
                self._create_sheets([TICKETS_SHEET_NAME])
                logger.info(f"Successfully created sheet '{TICKETS_SHEET_NAME}'")
            
            # Verify headers exist in the sheet
            self._ensure_headers()
            
            logger.info("Tickets sheet verified and ready")
            
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
        Ensure that the tickets sheet has the required headers.
        """
        try:
            headers = ['Sujet', 'Catégorie', 'Urgence', 'Synthèse']
            
            # Check if headers exist
            range_name = f"{TICKETS_SHEET_NAME}!A1:D1"
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
                logger.info(f"Added headers to sheet '{TICKETS_SHEET_NAME}'")
            else:
                logger.debug(f"Headers already exist in sheet '{TICKETS_SHEET_NAME}'")
                    
        except HttpError as e:
            logger.error(f"Error ensuring headers: {str(e)}")
            raise
    
    def write_result(self, category: str, subject: str, urgency: str, summary: str):
        """
        Write a single result row to the tickets sheet.
        
        Args:
            category: Email category
            subject: Email subject
            urgency: Urgency level
            summary: Email summary
        """
        try:
            if not self.service:
                raise RuntimeError("Sheets service not initialized. Call authenticate() first.")
            
            # Prepare row data with category included
            row_data = [subject, category, urgency, summary]
            
            # Find next empty row
            range_name = f"{TICKETS_SHEET_NAME}!A:A"
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            next_row = len(values) + 1
            
            # Write data
            range_to_update = f"{TICKETS_SHEET_NAME}!A{next_row}:D{next_row}"
            body = {
                'values': [row_data]
            }
            
            self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=range_to_update,
                valueInputOption='RAW',
                body=body
            ).execute()
            
            logger.info(f"Written to {TICKETS_SHEET_NAME}: {subject[:50]}... ({category})")
            
        except HttpError as e:
            logger.error(f"Error writing to sheet: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error writing to sheet: {str(e)}")
            raise
    
    def write_batch(self, results: list):
        """
        Write multiple results to the tickets sheet.
        
        Args:
            results: List of result dictionaries with 'categorie', 'subject', 'urgence', 'synthese'
        """
        try:
            if not self.service:
                raise RuntimeError("Sheets service not initialized. Call authenticate() first.")
            
            if not results:
                logger.warning("No results to write")
                return
            
            # Prepare batch data with category included
            rows_data = []
            for result in results:
                rows_data.append([
                    result.get('subject', ''),
                    result.get('categorie', 'Support utilisateur'),
                    result.get('urgence', ''),
                    result.get('synthese', '')
                ])
            
            # Find next empty row
            range_name = f"{TICKETS_SHEET_NAME}!A:A"
            result_get = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=range_name
            ).execute()
            
            values = result_get.get('values', [])
            start_row = len(values) + 1
            
            # Write batch
            range_to_update = f"{TICKETS_SHEET_NAME}!A{start_row}:D{start_row + len(rows_data) - 1}"
            body = {
                'values': rows_data
            }
            
            self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=range_to_update,
                valueInputOption='RAW',
                body=body
            ).execute()
            
            logger.info(f"Written {len(rows_data)} rows to {TICKETS_SHEET_NAME}")
            
        except HttpError as e:
            logger.error(f"Error writing batch to sheets: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error writing batch: {str(e)}")
            raise

