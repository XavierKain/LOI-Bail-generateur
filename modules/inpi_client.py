"""
Client pour l'API INPI (Institut National de la Propriété Industrielle).
Permet de récupérer les informations des entreprises françaises via le RNE.
"""

import logging
import requests
import time
import re
from typing import Optional, Dict
from ratelimit import limits, sleep_and_retry
from functools import lru_cache

try:
    import cloudscraper
    from bs4 import BeautifulSoup
    SCRAPING_AVAILABLE = True
except ImportError:
    SCRAPING_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("cloudscraper ou beautifulsoup4 non installé. Le scraping des dirigeants ne sera pas disponible.")

from .config import Config, _get_secret

logger = logging.getLogger(__name__)


class INPIClient:
    """Client pour interroger l'API INPI RNE."""

    def __init__(self, username: str = None, password: str = None):
        """
        Initialise le client INPI.

        Args:
            username: Username INPI (ou depuis config)
            password: Password INPI (ou depuis config)
        """
        self.base_url = Config.INPI_BASE_URL
        self.username = username or _get_secret('INPI_USERNAME', '')
        self.password = password or _get_secret('INPI_PASSWORD', '')
        self.token = None
        self._token_expiry = 0

        if not self.username or not self.password:
            logger.warning("Credentials INPI non configurés. L'enrichissement INPI sera désactivé.")
        else:
            logger.info("Client INPI initialisé")

    def _authenticate(self) -> bool:
        """
        Authentification auprès de l'API INPI.

        Returns:
            True si l'authentification a réussi
        """
        if not self.username or not self.password:
            logger.error("Credentials INPI manquants")
            return False

        # Vérifier si le token est encore valide (durée de vie: 1h estimée)
        if self.token and time.time() < self._token_expiry:
            return True

        try:
            url = f"{self.base_url}/sso/login"
            headers = {"Content-Type": "application/json"}
            data = {
                "username": self.username,
                "password": self.password
            }

            logger.info("Authentification INPI en cours...")
            response = requests.post(url, json=data, headers=headers, timeout=10)

            if response.status_code == 200:
                self.token = response.json().get("token")
                # Token valide pendant 1 heure (3600 secondes)
                self._token_expiry = time.time() + 3600
                logger.info("Authentification INPI réussie")
                return True
            else:
                logger.error(f"Échec authentification INPI: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            logger.error(f"Erreur lors de l'authentification INPI: {e}")
            return False

    @sleep_and_retry
    @limits(calls=Config.INPI_RATE_LIMIT, period=60)
    def _make_request(self, endpoint: str, params: dict = None, use_json: bool = False) -> Optional[dict]:
        """
        Effectue une requête à l'API INPI avec rate limiting.

        Args:
            endpoint: Endpoint de l'API (ex: "companies")
            params: Paramètres de la requête
            use_json: Si True, envoie les params en JSON body (POST)

        Returns:
            Réponse JSON ou None en cas d'erreur
        """
        if not self._authenticate():
            return None

        try:
            url = f"{self.base_url}/{endpoint}"
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }

            logger.debug(f"Requête INPI: {endpoint} avec params: {params}")

            if use_json:
                response = requests.post(url, headers=headers, json=params, timeout=10)
            else:
                response = requests.get(url, headers=headers, params=params, timeout=10)

            if response.status_code == 200:
                result = response.json()
                logger.debug(f"Réponse INPI (200): {result}")
                return result
            elif response.status_code == 429:
                logger.warning("Rate limit INPI atteint")
                return None
            elif response.status_code == 404:
                logger.warning(f"Entreprise non trouvée (404)")
                return None
            else:
                logger.error(f"Erreur API INPI: {response.status_code} - {response.text}")
                return None

        except requests.exceptions.Timeout:
            logger.error("Timeout lors de la requête INPI")
            return None
        except Exception as e:
            logger.error(f"Erreur lors de la requête INPI: {e}")
            return None

    @lru_cache(maxsize=100)
    def _search_by_siren(self, siren: str) -> Optional[dict]:
        """
        Recherche une entreprise par numéro SIREN (avec cache).

        Args:
            siren: Numéro SIREN (9 chiffres)

        Returns:
            Informations de l'entreprise ou None
        """
        # L'API INPI attend un array de SIRENs en paramètre GET
        # Utiliser la notation siren[] pour passer un array
        params = {f"siren[]": siren}
        result = self._make_request("companies", params=params)

        if result and isinstance(result, list) and len(result) > 0:
            # L'API retourne un array de résultats
            return result[0]
        elif result and isinstance(result, dict):
            # Cas où l'API retournerait un objet unique
            return result

        return None

    def _scrape_pappers_dirigeant(self, siren: str) -> Optional[str]:
        """
        Scrape le nom du dirigeant depuis Pappers.fr.

        Note: Cette méthode utilise le web scraping pour récupérer les informations
        de dirigeants qui ne sont pas disponibles via l'API INPI (protection RGPD).
        Utilisé uniquement pour un usage légitime et limité.

        Args:
            siren: Numéro SIREN (9 chiffres)

        Returns:
            Nom du dirigeant ou None si non trouvé
        """
        if not SCRAPING_AVAILABLE:
            logger.warning("Scraping non disponible (cloudscraper/beautifulsoup4 manquant)")
            return None

        url = f"https://www.pappers.fr/entreprise/{siren}"

        try:
            # Créer un scraper qui contourne Cloudflare
            # Utiliser 'linux' comme plateforme pour compatibilité Streamlit Cloud
            import platform
            current_platform = 'linux' if platform.system() == 'Linux' else 'darwin'

            scraper = cloudscraper.create_scraper(
                browser={
                    'browser': 'chrome',
                    'platform': current_platform,
                    'desktop': True
                }
            )

            logger.info(f"Tentative de scraping Pappers pour SIREN {siren} (plateforme: {current_platform})")
            response = scraper.get(url, timeout=45)  # Timeout augmenté pour Streamlit Cloud

            if response.status_code != 200:
                logger.warning(f"Scraping Pappers échoué (HTTP {response.status_code}) pour SIREN {siren}")
                return None

            logger.info(f"Scraping Pappers réussi (HTTP 200) pour SIREN {siren}")
            soup = BeautifulSoup(response.text, 'html.parser')

            # Méthode 1: Chercher dans le texte des mentions légales
            # Pattern: "représentée par XXX agissant et ayant les pouvoirs nécessaires en tant que président"
            mentions = soup.find('generate-mentions')
            if mentions and mentions.get('mentions'):
                mentions_text = mentions.get('mentions')
                match = re.search(
                    r'représentée par ([A-Z\s]+) agissant et ayant les pouvoirs nécessaires en tant que (?:président|gérant|directeur général)',
                    mentions_text,
                    re.IGNORECASE
                )
                if match:
                    dirigeant = match.group(1).strip()
                    logger.info(f"Dirigeant trouvé pour SIREN {siren}: {dirigeant}")
                    return dirigeant

            # Méthode 2: Chercher les liens <a> contenant un nom en majuscules
            for link in soup.find_all('a', href=True):
                href = link.get('href', '')
                # Pattern: nom-en-minuscules-suivi-de-chiffres
                if re.match(r'^[a-z-]+-\d{9}$', href):
                    text = link.get_text(strip=True)
                    # Vérifier que c'est bien un nom (tout en majuscules, pas d'adresse)
                    if text and text.isupper() and len(text) > 2:
                        excluded_words = ['AVENUE', 'RUE', 'BOULEVARD', 'PARIS', 'FRANCE', 'GAULLE']
                        if not any(word in text for word in excluded_words):
                            # Vérifier le contexte autour
                            parent_text = link.parent.get_text() if link.parent else ''
                            keywords = ['président', 'dirigeant', 'gérant', 'directeur']
                            if any(keyword in parent_text.lower() for keyword in keywords):
                                logger.info(f"Dirigeant trouvé pour SIREN {siren}: {text}")
                                return text

            # Méthode 3: Chercher dans le texte brut
            text = soup.get_text()
            match = re.search(r'(?:nomination du )?Président\s*:\s*([A-Z][A-Za-z\s\-]+?)(?:\s|$|;|,)', text)
            if match:
                dirigeant = match.group(1).strip()
                logger.info(f"Dirigeant trouvé pour SIREN {siren}: {dirigeant}")
                return dirigeant

            # Méthode 4: Chercher la structure HTML Pappers "Dirigeant :"
            # Structure: <td>Dirigeant :</td> suivi de <td class="info-dirigeant"><a>Nom Prénom</a></td>
            logger.debug(f"Méthode 4: Recherche des cellules info-dirigeant...")
            dirigeant_cells = soup.find_all('td', class_='info-dirigeant')
            logger.debug(f"Méthode 4: {len(dirigeant_cells)} cellule(s) trouvée(s)")
            for cell in dirigeant_cells:
                link = cell.find('a')
                if link:
                    text = link.get_text(strip=True)
                    logger.debug(f"Méthode 4: Texte trouvé: '{text}'")
                    # Vérifier que c'est un nom de personne (au moins 2 mots)
                    if text and len(text.split()) >= 2:
                        logger.info(f"Dirigeant trouvé (méthode 4) pour SIREN {siren}: {text}")
                        return text

            # Méthode 5: Chercher "Dirigeant :" dans le HTML
            # Utiliser BeautifulSoup pour trouver le motif
            logger.debug(f"Méthode 5: Recherche du pattern 'Dirigeant :'...")
            dirigeant_labels = soup.find_all(text=re.compile(r'Dirigeant\s*:', re.IGNORECASE))
            logger.debug(f"Méthode 5: {len(dirigeant_labels)} label(s) trouvé(s)")
            for elem in dirigeant_labels:
                # Chercher les éléments suivants qui pourraient contenir le nom
                parent = elem.parent
                if parent:
                    next_elem = parent.find_next_sibling()
                    if next_elem:
                        # Chercher un lien ou du texte
                        link = next_elem.find('a')
                        if link:
                            text = link.get_text(strip=True)
                            logger.debug(f"Méthode 5: Texte trouvé: '{text}'")
                            if text and len(text.split()) >= 2:
                                logger.info(f"Dirigeant trouvé (méthode 5) pour SIREN {siren}: {text}")
                                return text

            logger.warning(f"Aucun dirigeant trouvé pour SIREN {siren} (toutes méthodes échouées)")
            return None

        except Exception as e:
            logger.error(f"Erreur lors du scraping Pappers avec cloudscraper pour SIREN {siren}: {str(e)}")

            # Fallback: Essayer avec requests simple (peut être bloqué par Cloudflare mais on essaie)
            try:
                logger.info(f"Tentative de fallback avec requests simple pour SIREN {siren}")
                headers = {
                    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                }
                response = requests.get(url, headers=headers, timeout=10)

                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')

                    # Méthode 4 uniquement (la plus robuste)
                    dirigeant_cells = soup.find_all('td', class_='info-dirigeant')
                    for cell in dirigeant_cells:
                        link = cell.find('a')
                        if link:
                            text = link.get_text(strip=True)
                            if text and len(text.split()) >= 2:
                                logger.info(f"Dirigeant trouvé via fallback pour SIREN {siren}: {text}")
                                return text
                else:
                    logger.warning(f"Fallback échoué (HTTP {response.status_code})")
            except Exception as fallback_error:
                logger.error(f"Fallback échoué pour SIREN {siren}: {str(fallback_error)}")

            return None

    def get_company_info(self, siret: str) -> Dict[str, str]:
        """
        Récupère les informations d'une entreprise à partir du SIRET.

        Args:
            siret: Numéro SIRET (14 chiffres) ou SIREN (9 chiffres)

        Returns:
            Dictionnaire avec les informations de l'entreprise:
            - NOM DE LA SOCIETE
            - TYPE DE SOCIETE
            - CAPITAL SOCIAL
            - LOCALITE RCS
            - ADRESSE DE DOMICILIATION
            - PRESIDENT DE LA SOCIETE
        """
        # Initialiser le résultat avec des valeurs vides
        result = {
            "NOM DE LA SOCIETE": "",
            "TYPE DE SOCIETE": "",
            "CAPITAL SOCIAL": "",
            "LOCALITE RCS": "",
            "ADRESSE DE DOMICILIATION": "",
            "PRESIDENT DE LA SOCIETE": "",
            "enrichment_status": "failed",
            "error_message": ""
        }

        if not siret:
            result["error_message"] = "SIRET manquant"
            return result

        # Extraire le SIREN (9 premiers chiffres du SIRET)
        siret_clean = str(siret).replace(" ", "").strip()
        if len(siret_clean) == 14:
            siren = siret_clean[:9]
        elif len(siret_clean) == 9:
            siren = siret_clean
        else:
            result["error_message"] = f"SIRET invalide (longueur: {len(siret_clean)})"
            logger.error(result["error_message"])
            return result

        logger.info(f"Recherche INPI pour SIREN: {siren}")

        try:
            company_data = self._search_by_siren(siren)

            if not company_data:
                result["error_message"] = "Entreprise non trouvée dans la base INPI"
                logger.warning(result["error_message"])
                return result

            # Extraction des données selon la structure de l'API INPI
            # Structure: formality.content.personneMorale
            formality = company_data.get("formality", {})
            content = formality.get("content", {})

            # Chercher les données de personne morale ou physique
            personne_morale = content.get("personneMorale", {})
            nature_creation = content.get("natureCreation", {})

            # Nom de la société - chercher dans plusieurs endroits
            etab_principal = personne_morale.get("etablissementPrincipal", {})
            desc_etab = etab_principal.get("descriptionEtablissement", {})

            # Chercher aussi dans identite.entreprise
            identite = personne_morale.get("identite", {})
            entreprise = identite.get("entreprise", {})

            result["NOM DE LA SOCIETE"] = (
                desc_etab.get("nomCommercial") or
                desc_etab.get("enseigne") or
                personne_morale.get("denomination") or
                entreprise.get("denomination") or
                ""
            )

            # Type de société (forme juridique)
            forme_juridique = nature_creation.get("formeJuridique", "")
            if forme_juridique:
                # Mapping des codes de formes juridiques (principaux)
                formes_codes = {
                    "5499": "SAS (Société par Actions Simplifiée)",
                    "5498": "SASU (Société par Actions Simplifiée Unipersonnelle)",
                    "5710": "SCI (Société Civile Immobilière)",
                    "5505": "SA (Société Anonyme)",
                    "5410": "SARL (Société à Responsabilité Limitée)",
                    "5720": "EURL (Entreprise Unipersonnelle à Responsabilité Limitée)"
                }
                result["TYPE DE SOCIETE"] = formes_codes.get(forme_juridique, forme_juridique)

            # Adresse de domiciliation (siège social) - extraire d'abord car on en a besoin pour le RCS
            adresse_entreprise = personne_morale.get("adresseEntreprise", {})
            adresse = adresse_entreprise.get("adresse", {})
            if isinstance(adresse, dict):
                parts = []
                if adresse.get("numVoie"):
                    parts.append(str(adresse["numVoie"]))
                if adresse.get("indiceRepetition"):
                    parts.append(adresse["indiceRepetition"])
                if adresse.get("typeVoie"):
                    parts.append(adresse["typeVoie"])
                if adresse.get("voie"):
                    parts.append(adresse["voie"])
                if adresse.get("codePostal"):
                    parts.append(str(adresse["codePostal"]))
                if adresse.get("commune"):
                    parts.append(adresse["commune"])

                result["ADRESSE DE DOMICILIATION"] = " ".join(parts) if parts else ""

            # Capital social - chercher dans personneMorale.identite.description
            identite = personne_morale.get("identite", {})
            description = identite.get("description", {})

            montant_capital = description.get("montantCapital")
            if montant_capital:
                if isinstance(montant_capital, (int, float)):
                    result["CAPITAL SOCIAL"] = f"{int(montant_capital):,}".replace(",", " ") + " €"
                else:
                    result["CAPITAL SOCIAL"] = str(montant_capital)

            # Localité RCS (greffe) - déduire de la commune du siège social
            # Le greffe est généralement dans la même ville que le siège social
            commune = adresse.get("commune", "") if isinstance(adresse, dict) else ""
            if commune:
                # Nettoyer le nom de la commune (retirer arrondissement pour Paris, Lyon, Marseille)
                commune_clean = commune.replace(" 1ER ARRONDISSEMENT", "")
                commune_clean = commune_clean.replace(" 2E ARRONDISSEMENT", "")
                for i in range(3, 21):
                    commune_clean = commune_clean.replace(f" {i}E ARRONDISSEMENT", "")
                result["LOCALITE RCS"] = commune_clean.strip()

            # Président/gérant (représentant légal)
            # Les données personnelles des dirigeants sont protégées par RGPD dans l'API INPI
            # On utilise le scraping de Pappers.fr pour obtenir cette information
            try:
                dirigeant = self._scrape_pappers_dirigeant(siren)
                result["PRESIDENT DE LA SOCIETE"] = dirigeant if dirigeant else ""
            except Exception as e:
                logger.warning(f"Échec du scraping du dirigeant: {str(e)}")
                result["PRESIDENT DE LA SOCIETE"] = ""

            result["enrichment_status"] = "success"
            logger.info(f"Enrichissement INPI réussi pour {result['NOM DE LA SOCIETE']}")

        except Exception as e:
            result["error_message"] = f"Erreur lors de l'extraction des données: {str(e)}"
            logger.error(result["error_message"], exc_info=True)

        return result


def get_inpi_client() -> Optional[INPIClient]:
    """
    Récupère une instance du client INPI (factory function).

    Returns:
        Instance de INPIClient ou None si credentials manquants
    """
    if not Config.validate_inpi_credentials():
        logger.warning("Credentials INPI non configurés - enrichissement désactivé")
        return None

    try:
        return INPIClient()
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation du client INPI: {e}")
        return None
