"""
Module de configuration pour charger les credentials et paramètres.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Charger les variables d'environnement depuis .env
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)


class Config:
    """Configuration centralisée de l'application."""

    # Credentials INPI
    INPI_USERNAME = os.getenv('INPI_USERNAME', '')
    INPI_PASSWORD = os.getenv('INPI_PASSWORD', '')

    # API INPI settings
    INPI_BASE_URL = "https://registre-national-entreprises.inpi.fr/api"
    INPI_RATE_LIMIT = 5  # requêtes par minute
    INPI_CACHE_DURATION = 3600  # 1 heure en secondes

    @classmethod
    def validate_inpi_credentials(cls) -> bool:
        """
        Vérifie que les credentials INPI sont configurés.

        Returns:
            True si les credentials sont présents
        """
        return bool(cls.INPI_USERNAME and cls.INPI_PASSWORD)

    @classmethod
    def get_inpi_credentials(cls) -> dict:
        """
        Retourne les credentials INPI.

        Returns:
            Dict avec username et password
        """
        return {
            'username': cls.INPI_USERNAME,
            'password': cls.INPI_PASSWORD
        }
