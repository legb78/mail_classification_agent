"""
Configuration du système de logging
"""

import sys
from pathlib import Path
from loguru import logger
from typing import Optional


def setup_logger(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    rotation: str = "10 MB",
    retention: str = "30 days"
) -> None:
    """
    Configure le système de logging
    
    Args:
        log_level: Niveau de log (DEBUG, INFO, WARNING, ERROR)
        log_file: Chemin vers le fichier de log
        rotation: Rotation des logs (ex: "10 MB", "1 day")
        retention: Rétention des logs (ex: "30 days")
    """
    # Supprimer le handler par défaut
    logger.remove()
    
    # Ajouter handler pour la console
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
        level=log_level,
        colorize=True
    )
    
    # Ajouter handler pour le fichier si spécifié
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        logger.add(
            log_file,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function} - {message}",
            level=log_level,
            rotation=rotation,
            retention=retention,
            compression="zip",
            encoding="utf-8"
        )
    
    logger.info("Logger configuré avec succès")


def get_logger(name: str):
    """Retourne un logger pour un module spécifique"""
    return logger.bind(name=name)

