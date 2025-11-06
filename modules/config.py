"""
Module de configuration pour charger les credentials et paramètres.
Supporte à la fois les fichiers .env locaux et Streamlit Secrets pour le déploiement.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Charger les variables d'environnement depuis .env (développement local)
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)


def _get_secret(key: str, default: str = '') -> str:
    """
    Récupère un secret depuis Streamlit Secrets (production) ou .env (local).

    Args:
        key: Nom de la clé de configuration
        default: Valeur par défaut si non trouvée

    Returns:
        Valeur de la configuration
    """
    # Essayer d'abord Streamlit Secrets (production)
    try:
        import streamlit as st
        if hasattr(st, 'secrets') and key in st.secrets:
            return st.secrets[key]
    except (ImportError, FileNotFoundError, KeyError):
        pass

    # Fallback sur variables d'environnement (.env local)
    return os.getenv(key, default)


class Config:
    """Configuration centralisée de l'application."""

    # Credentials INPI - récupérés dynamiquement depuis Streamlit Secrets ou .env
    INPI_USERNAME = _get_secret('INPI_USERNAME', '')
    INPI_PASSWORD = _get_secret('INPI_PASSWORD', '')

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
        # Récupérer les credentials dynamiquement pour supporter Streamlit Secrets
        username = _get_secret('INPI_USERNAME', '')
        password = _get_secret('INPI_PASSWORD', '')
        return bool(username and password)

    @classmethod
    def get_inpi_credentials(cls) -> dict:
        """
        Retourne les credentials INPI.

        Returns:
            Dict avec username et password
        """
        return {
            'username': _get_secret('INPI_USERNAME', ''),
            'password': _get_secret('INPI_PASSWORD', '')
        }
