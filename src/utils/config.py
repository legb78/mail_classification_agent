"""
Gestion de la configuration de l'application
"""

import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class EmailConfig(BaseSettings):
    """Configuration pour la connexion email"""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    host: str = Field(default="imap.gmail.com", alias="EMAIL_HOST")
    port: int = Field(default=993, alias="EMAIL_PORT")
    user: Optional[str] = Field(default=None, alias="EMAIL_USER")
    password: Optional[str] = Field(default=None, alias="EMAIL_PASSWORD")
    folder: str = Field(default="INBOX", alias="EMAIL_FOLDER")
    use_ssl: bool = Field(default=True, alias="EMAIL_USE_SSL")


class GoogleSheetsConfig(BaseSettings):
    """Configuration pour Google Sheets"""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    sheet_id: Optional[str] = Field(default=None, alias="GOOGLE_SHEETS_ID")
    credentials_path: str = Field(default="credentials.json", alias="GOOGLE_CREDENTIALS_PATH")
    sheet_name: str = Field(default="Tickets", alias="GOOGLE_SHEET_NAME")


class ClassificationConfig(BaseSettings):
    """Configuration pour la classification"""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Groq API Configuration
    groq_api_key: Optional[str] = Field(default=None, alias="GROQ_API_KEY")
    groq_model: str = Field(default="llama-3.1-70b-versatile", alias="GROQ_MODEL")
    use_groq: bool = Field(default=True, alias="USE_GROQ_LLM")
    
    # Legacy ML Configuration (optionnel)
    model_path: str = Field(default="models/classification_model.pkl", alias="CLASSIFICATION_MODEL_PATH")
    confidence_threshold: float = Field(default=0.7, alias="CONFIDENCE_THRESHOLD")
    enable_ml: bool = Field(default=False, alias="ENABLE_ML_CLASSIFICATION")
    
    # Classification categories (format: "Cat1,Cat2,Cat3")
    categories_str: str = Field(
        default="Technique,Commercial,Support,Facturation,Autre",
        alias="CLASSIFICATION_CATEGORIES"
    )
    
    # Priority levels (format: "Prio1,Prio2,Prio3")
    priorities_str: str = Field(
        default="Critique,Haute,Moyenne,Basse",
        alias="CLASSIFICATION_PRIORITIES"
    )
    
    @property
    def categories(self) -> list:
        """Retourne la liste des catégories"""
        return [c.strip() for c in self.categories_str.split(",")]
    
    @property
    def priorities(self) -> list:
        """Retourne la liste des priorités"""
        return [p.strip() for p in self.priorities_str.split(",")]


class NotificationConfig(BaseSettings):
    """Configuration pour les notifications"""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    slack_webhook_url: Optional[str] = Field(default=None, alias="SLACK_WEBHOOK_URL")
    teams_webhook_url: Optional[str] = Field(default=None, alias="TEAMS_WEBHOOK_URL")
    enabled: bool = Field(default=True, alias="NOTIFICATION_ENABLED")


class ProcessingConfig(BaseSettings):
    """Configuration pour le traitement"""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    polling_interval: int = Field(default=60, alias="POLLING_INTERVAL")
    batch_size: int = Field(default=10, alias="BATCH_SIZE")
    max_retries: int = Field(default=3, alias="MAX_RETRIES")
    retry_delay: int = Field(default=5, alias="RETRY_DELAY")


class LoggingConfig(BaseSettings):
    """Configuration pour le logging"""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    level: str = Field(default="INFO", alias="LOG_LEVEL")
    file: str = Field(default="logs/agent.log", alias="LOG_FILE")
    rotation: str = Field(default="10 MB", alias="LOG_ROTATION")
    retention: str = Field(default="30 days", alias="LOG_RETENTION")


class Settings(BaseSettings):
    """Configuration globale de l'application"""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    email: EmailConfig
    google_sheets: GoogleSheetsConfig
    classification: ClassificationConfig
    notification: NotificationConfig
    processing: ProcessingConfig
    logging: LoggingConfig


def load_config() -> Settings:
    """Charge la configuration depuis les variables d'environnement"""
    return Settings(
        email=EmailConfig(),
        google_sheets=GoogleSheetsConfig(),
        classification=ClassificationConfig(),
        notification=NotificationConfig(),
        processing=ProcessingConfig(),
        logging=LoggingConfig(),
    )

