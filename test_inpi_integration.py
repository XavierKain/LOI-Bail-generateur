"""
Script de test pour l'intégration INPI.
Teste la connexion à l'API INPI et la récupération des données.
"""

import logging
from modules.inpi_client import INPIClient, get_inpi_client
from modules.config import Config

# Configuration du logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_config():
    """Test de la configuration."""
    logger.info("\n" + "="*80)
    logger.info("Test 1: Configuration")
    logger.info("="*80)

    logger.info(f"Username configuré: {Config.INPI_USERNAME}")
    logger.info(f"Password configuré: {'*' * len(Config.INPI_PASSWORD) if Config.INPI_PASSWORD else 'Non configuré'}")
    logger.info(f"Credentials valides: {Config.validate_inpi_credentials()}")

    assert Config.validate_inpi_credentials(), "Credentials INPI non configurés !"
    logger.info("✓ Configuration OK")


def test_authentication():
    """Test de l'authentification."""
    logger.info("\n" + "="*80)
    logger.info("Test 2: Authentification INPI")
    logger.info("="*80)

    client = INPIClient()
    success = client._authenticate()

    assert success, "Échec de l'authentification INPI"
    assert client.token, "Token INPI non récupéré"

    logger.info(f"✓ Authentification réussie")
    logger.info(f"Token obtenu: {client.token[:50]}...")


def test_search_company():
    """Test de recherche d'entreprise par SIRET."""
    logger.info("\n" + "="*80)
    logger.info("Test 3: Recherche d'entreprise")
    logger.info("="*80)

    client = get_inpi_client()
    assert client, "Client INPI non initialisé"

    # SIRET de test (Google France - public)
    # Remplacez par un vrai SIRET de test
    test_siret = "44306184100047"  # Google France

    logger.info(f"Recherche du SIRET: {test_siret}")

    company_info = client.get_company_info(test_siret)

    logger.info(f"\nRésultats:")
    logger.info(f"  Nom: {company_info.get('NOM DE LA SOCIETE')}")
    logger.info(f"  Type: {company_info.get('TYPE DE SOCIETE')}")
    logger.info(f"  Capital: {company_info.get('CAPITAL SOCIAL')}")
    logger.info(f"  RCS: {company_info.get('LOCALITE RCS')}")
    logger.info(f"  Adresse: {company_info.get('ADRESSE DE DOMICILIATION')}")
    logger.info(f"  Président: {company_info.get('PRESIDENT DE LA SOCIETE')}")
    logger.info(f"  Statut: {company_info.get('enrichment_status')}")

    if company_info.get('enrichment_status') != 'success':
        logger.warning(f"  Erreur: {company_info.get('error_message')}")
    else:
        logger.info("✓ Recherche réussie")

    # Vérifier que le statut est success et qu'au moins le nom est rempli
    assert company_info.get('enrichment_status') == 'success', "Enrichissement a échoué"
    assert company_info.get('NOM DE LA SOCIETE'), "Nom de société non récupéré"

    # Note: Certains champs (capital, RCS, président) peuvent ne pas être disponibles
    # via l'endpoint /companies et nécessiteraient des appels API supplémentaires


def test_invalid_siret():
    """Test avec un SIRET invalide."""
    logger.info("\n" + "="*80)
    logger.info("Test 4: SIRET invalide")
    logger.info("="*80)

    client = get_inpi_client()
    invalid_siret = "123"

    company_info = client.get_company_info(invalid_siret)

    assert company_info.get('enrichment_status') == 'failed', "Le SIRET invalide aurait dû échouer"
    logger.info(f"✓ Gestion d'erreur correcte: {company_info.get('error_message')}")


def test_cache():
    """Test du cache."""
    logger.info("\n" + "="*80)
    logger.info("Test 5: Cache des résultats")
    logger.info("="*80)

    client = get_inpi_client()
    test_siret = "44306184100047"

    # Premier appel
    import time
    start = time.time()
    company_info1 = client.get_company_info(test_siret)
    duration1 = time.time() - start

    # Deuxième appel (devrait utiliser le cache)
    start = time.time()
    company_info2 = client.get_company_info(test_siret)
    duration2 = time.time() - start

    logger.info(f"Durée 1er appel: {duration1:.3f}s")
    logger.info(f"Durée 2e appel (cache): {duration2:.3f}s")

    assert company_info1 == company_info2, "Les résultats devraient être identiques"
    logger.info("✓ Cache fonctionne correctement")


if __name__ == "__main__":
    logger.info("="*80)
    logger.info("TESTS INTÉGRATION INPI")
    logger.info("="*80)

    try:
        test_config()
        test_authentication()
        test_search_company()
        test_invalid_siret()
        test_cache()

        logger.info("\n" + "="*80)
        logger.info("✅ TOUS LES TESTS ONT RÉUSSI")
        logger.info("="*80)

    except AssertionError as e:
        logger.error(f"\n❌ Test échoué: {e}")
        exit(1)
    except Exception as e:
        logger.error(f"\n❌ Erreur inattendue: {e}", exc_info=True)
        exit(1)
