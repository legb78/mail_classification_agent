"""
Main Orchestrator

Coordinates Gmail reading, Groq analysis, and Google Sheets writing.
"""

import os
import sys
import logging
from dotenv import load_dotenv
from gmail_reader import GmailReader
from groq_agent import GroqAgent
from sheets_writer import SheetsWriter

# Configure logging
def setup_logging(log_level: str = "INFO"):
    """Configure logging to both console and file."""
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Set up logging format
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, log_level.upper(), logging.INFO),
        format=log_format,
        datefmt=date_format,
        handlers=[
            logging.FileHandler('logs/app.log', encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )


def load_config():
    """Load configuration from .env file."""
    load_dotenv()
    
    config = {
        'groq_api_key': os.getenv('GROQ_API_KEY'),
        'gmail_credentials_file': os.getenv('GMAIL_CREDENTIALS_FILE'),
        'gmail_token_file': os.getenv('GMAIL_TOKEN_FILE', 'credentials/gmail_token.json'),
        'sheets_credentials_file': os.getenv('SHEETS_CREDENTIALS_FILE'),
        'sheets_token_file': os.getenv('SHEETS_TOKEN_FILE', 'credentials/sheets_token.json'),
        'spreadsheet_id': os.getenv('SPREADSHEET_ID'),
        'batch_size': int(os.getenv('BATCH_SIZE', '20')),
        'log_level': os.getenv('LOG_LEVEL', 'INFO')
    }
    
    # Validate required configuration
    required = [
        'groq_api_key',
        'gmail_credentials_file',
        'sheets_credentials_file',
        'spreadsheet_id'
    ]
    
    missing = [key for key in required if not config[key]]
    if missing:
        raise ValueError(
            f"Missing required configuration in .env file: {', '.join(missing)}\n"
            "Please check your .env file and ensure all required values are set."
        )
    
    return config


def main():
    """Main execution function."""
    logger = logging.getLogger(__name__)
    
    try:
        # Load configuration
        logger.info("Loading configuration...")
        config = load_config()
        
        # Setup logging with configured level
        setup_logging(config['log_level'])
        logger.info("Logging configured")
        
        # Initialize modules
        logger.info("Initializing modules...")
        gmail_reader = GmailReader(
            credentials_file=config['gmail_credentials_file'],
            token_file=config['gmail_token_file']
        )
        
        groq_agent = GroqAgent(api_key=config['groq_api_key'])
        
        sheets_writer = SheetsWriter(
            credentials_file=config['sheets_credentials_file'],
            token_file=config['sheets_token_file'],
            spreadsheet_id=config['spreadsheet_id']
        )
        
        # Authenticate with APIs
        logger.info("Authenticating with Gmail API...")
        gmail_reader.authenticate()
        
        logger.info("Authenticating with Google Sheets API...")
        sheets_writer.authenticate()
        
        # Verify sheets exist
        logger.info("Verifying Google Sheets structure...")
        sheets_writer.verify_sheets_exist()
        
        # Get unread emails
        logger.info("Fetching unread emails...")
        email_ids = gmail_reader.get_unread_emails(max_results=100)
        
        if not email_ids:
            logger.info("No unread emails found. Exiting.")
            return
        
        logger.info(f"Found {len(email_ids)} unread emails to process")
        
        # Process emails in batches
        batch_size = config['batch_size']
        total_processed = 0
        total_failed = 0
        
        for i in range(0, len(email_ids), batch_size):
            batch_ids = email_ids[i:i + batch_size]
            batch_num = i // batch_size + 1
            total_batches = (len(email_ids) + batch_size - 1) // batch_size
            
            logger.info(f"Processing batch {batch_num}/{total_batches} ({len(batch_ids)} emails)")
            
            # Extract email content
            emails = []
            for email_id in batch_ids:
                try:
                    email_content = gmail_reader.get_email_content(email_id)
                    emails.append(email_content)
                except Exception as e:
                    logger.error(f"Failed to extract email {email_id}: {str(e)}")
                    total_failed += 1
                    continue
            
            if not emails:
                logger.warning(f"No emails extracted from batch {batch_num}")
                continue
            
            # Analyze with Groq
            logger.info(f"Analyzing {len(emails)} emails with Groq API...")
            try:
                analysis_results = groq_agent.analyze_batch(emails, batch_size=batch_size)
            except Exception as e:
                logger.error(f"Failed to analyze batch {batch_num}: {str(e)}")
                total_failed += len(emails)
                continue
            
            # Combine email content with analysis results
            if len(emails) != len(analysis_results):
                logger.warning(
                    f"Mismatch: {len(emails)} emails but {len(analysis_results)} analysis results. "
                    "Some emails may have failed analysis."
                )
            
            results_to_write = []
            for email, analysis in zip(emails, analysis_results):
                result = {
                    'email_id': email['id'],
                    'subject': email['subject'],
                    'categorie': analysis.get('categorie', 'Support utilisateur'),
                    'urgence': analysis.get('urgence', 'Modérée'),
                    'synthese': analysis.get('synthese', 'Synthèse non disponible')
                }
                results_to_write.append(result)
            
            # Write to Google Sheets
            logger.info(f"Writing {len(results_to_write)} results to Google Sheets...")
            try:
                sheets_writer.write_batch(results_to_write)
            except Exception as e:
                logger.error(f"Failed to write batch {batch_num} to sheets: {str(e)}")
                total_failed += len(results_to_write)
                continue
            
            # Mark emails as read (only after successful sheet write)
            logger.info(f"Marking {len(results_to_write)} emails as read...")
            for result in results_to_write:
                try:
                    gmail_reader.mark_as_read(result['email_id'])
                    total_processed += 1
                except Exception as e:
                    logger.error(f"Failed to mark email {result['email_id']} as read: {str(e)}")
                    # Don't count as failed since it was already written to sheets
        
        # Summary
        logger.info("=" * 60)
        logger.info("Processing complete!")
        logger.info(f"Total emails processed: {total_processed}")
        logger.info(f"Total emails failed: {total_failed}")
        logger.info("=" * 60)
        
    except KeyboardInterrupt:
        logger.warning("Process interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

