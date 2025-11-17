"""
Point d'entrée principal de l'application (racine du projet)
"""

import sys
from pathlib import Path

# S'assurer que le répertoire courant est dans le PYTHONPATH
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Importer et exécuter le main depuis src
from src.main import main

if __name__ == "__main__":
    main()

