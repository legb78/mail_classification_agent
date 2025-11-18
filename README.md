# Email Ticket Processing Agent with Groq API

An automated email ticket processing system that reads Gmail emails, classifies them using Groq AI, and writes results to Google Sheets organized by category.

## Features

- **Gmail Integration**: Automatically reads unread emails from Gmail inbox
- **AI Classification**: Uses Groq API to classify emails into 5 categories:
  - Technique
  - Administratif
  - Accès/Authentification
  - Support utilisateur
  - Bug/Dysfonctionnement
- **Urgency Detection**: Determines urgency level (Critique, Élevée, Modérée, Faible, Anodine)
- **Summary Generation**: Creates concise summaries (2-3 lines) for each email
- **Google Sheets Integration**: Automatically writes results to appropriate category sheets
- **Batch Processing**: Processes emails in configurable batches (default: 20)
- **Error Handling**: Robust error handling with logging

## Setup

### Prerequisites

- Python 3.8 or higher
- Gmail account with API access enabled
- Google Cloud Project with Gmail API and Google Sheets API enabled
- Groq API key

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd mail_classification_agent
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up Google Cloud credentials:

   **For Gmail API:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one
   - Enable Gmail API
   - Create OAuth 2.0 credentials (Desktop app)
   - Download credentials as `credentials/gmail_credentials.json`

   **For Google Sheets API:**
   - Enable Google Sheets API in the same project
   - Create OAuth 2.0 credentials (Desktop app) or reuse existing
   - Download credentials as `credentials/sheets_credentials.json`

4. Set up Groq API:
   - Get your API key from [Groq Console](https://console.groq.com/)
   - Add it to `.env` file

5. Configure environment variables:
```bash
cp .env.example .env
```

Edit `.env` and fill in:
- `GROQ_API_KEY`: Your Groq API key
- `GMAIL_CREDENTIALS_FILE`: Path to Gmail OAuth credentials
- `SHEETS_CREDENTIALS_FILE`: Path to Sheets OAuth credentials
- `SPREADSHEET_ID`: Your Google Sheets spreadsheet ID
- `BATCH_SIZE`: Number of emails to process per batch (default: 20)
- `PROCESS_ALL_EMAILS`: Set to `true` to process all emails (read and unread), `false` for unread only (default: false)
- `MAX_EMAILS_TO_PROCESS`: Maximum emails to process when `PROCESS_ALL_EMAILS=true` (default: 500)

6. Prepare Google Sheets:
   - Create a Google Sheets spreadsheet
   - The script will automatically create 5 sheets organized by category:
     - `Technique`
     - `Administratif`
     - `Accès/Authentification`
     - `Support utilisateur`
     - `Bug/Dysfonctionnement`
   - Each sheet will have headers: `Sujet`, `Urgence`, `Synthèse`
   - Copy the spreadsheet ID from the URL (the long string between `/d/` and `/edit`)

## Usage

Run the main script:
```bash
python main.py
```

On first run, you'll be prompted to authorize:
1. Gmail access (opens browser, sign in, grant permissions)
2. Google Sheets access (opens browser, sign in, grant permissions)

After authorization, tokens will be saved and reused automatically.

## How It Works

1. **Email Reading**: 
   - By default: Reads unread emails from Gmail inbox
   - If `PROCESS_ALL_EMAILS=true`: Reads all emails (read and unread) from inbox
2. **AI Analysis**: Sends each email (subject + body) to Groq API for analysis
3. **Classification**: Groq returns category, urgency level, and summary
4. **Sheet Writing**: Writes results to category-based sheets (Technique, Administratif, Accès/Authentification, Support utilisateur, Bug/Dysfonctionnement) with columns: Sujet, Urgence, Synthèse
5. **Email Marking**: 
   - Marks processed emails as read only if processing unread emails
   - Skips marking as read when processing all emails (to avoid marking already-read emails)

## Logging

Logs are written to:
- Console (INFO level and above)
- `app.log` file (all levels)

## Error Handling

The system handles:
- API failures (with retry logic)
- Malformed emails
- JSON parsing errors
- Missing sheets
- Network issues

Processing continues even if individual emails fail.

## Configuration

All configuration is done via `.env` file:
- `BATCH_SIZE`: Number of emails processed per batch
- `LOG_LEVEL`: Logging verbosity (DEBUG, INFO, WARNING, ERROR)

## License

MIT License

