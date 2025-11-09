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

try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

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

    def _extract_dirigeant_from_api(self, personne_morale: dict) -> Optional[str]:
        """
        Extrait le nom du dirigeant depuis les données INPI (composition.pouvoirs).

        Les données de dirigeants sont disponibles dans l'API INPI via composition.pouvoirs.
        Rôles à rechercher:
        - 30: Président
        - 71: Président SAS
        - 50: Gérant

        Args:
            personne_morale: Dict contenant les données personneMorale de l'API

        Returns:
            Nom complet du dirigeant ou None si non trouvé
        """
        try:
            composition = personne_morale.get("composition", {})
            pouvoirs = composition.get("pouvoirs", [])

            # Rôles de dirigeants principaux
            roles_dirigeants = ["30", "71", "50"]  # Président, Président SAS, Gérant

            for pouvoir in pouvoirs:
                role = pouvoir.get("roleEntreprise")
                type_personne = pouvoir.get("typeDePersonne")
                actif = pouvoir.get("actif", False)

                # Vérifier que c'est un dirigeant actif et une personne physique
                if actif and role in roles_dirigeants and type_personne == "INDIVIDU":
                    individu = pouvoir.get("individu", {})
                    desc = individu.get("descriptionPersonne", {})

                    nom = desc.get("nom", "")
                    prenoms = desc.get("prenoms", [])

                    if nom:
                        # Formater: "NOM Prénom" ou "Nom Prénom"
                        prenom = prenoms[0] if prenoms else ""
                        if prenom:
                            # Capitaliser correctement: "MOULIN" -> "Moulin", "LUC" -> "Luc"
                            nom_formatted = nom.capitalize() if nom.isupper() else nom
                            prenom_formatted = prenom.capitalize() if prenom.isupper() else prenom
                            dirigeant = f"{nom_formatted} {prenom_formatted}"
                        else:
                            dirigeant = nom.capitalize() if nom.isupper() else nom

                        logger.info(f"Dirigeant trouvé dans API INPI (rôle {role}): {dirigeant}")
                        return dirigeant

            logger.debug("Aucun dirigeant trouvé dans composition.pouvoirs")
            return None

        except Exception as e:
            logger.error(f"Erreur lors de l'extraction du dirigeant depuis l'API: {str(e)}")
            return None

    def _scrape_inpi_dirigeant(self, siren: str) -> Optional[str]:
        """
        Scrape le nom du dirigeant depuis data.inpi.fr avec BeautifulSoup.

        Note: Cette méthode utilise le web scraping léger (BeautifulSoup)
        compatible avec Streamlit Cloud pour récupérer le dirigeant.
        Utilisé uniquement pour un usage légitime et limité.

        Args:
            siren: Numéro SIREN (9 chiffres)

        Returns:
            Nom du dirigeant ou None si non trouvé
        """
        if not SCRAPING_AVAILABLE:
            logger.warning("BeautifulSoup non disponible")
            return None

        url = f"https://data.inpi.fr/entreprises/{siren}"

        try:
            logger.info(f"Tentative de scraping BeautifulSoup pour SIREN {siren}")

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=30)

            if response.status_code != 200:
                logger.warning(f"Scraping échoué (HTTP {response.status_code})")
                return None

            soup = BeautifulSoup(response.content, 'html.parser')

            # Chercher la section "Gestion et Direction"
            gestion_h3 = soup.find('h3', id='representants')
            if not gestion_h3:
                logger.warning("Section 'Gestion et Direction' non trouvée")
                return None

            # Trouver les blocs dirigeant
            section_row = gestion_h3.find_parent('div', class_='row')
            if not section_row:
                return None

            blocs = section_row.find_all('div', class_='bloc-dirigeant')
            if not blocs:
                logger.warning("Aucun bloc dirigeant trouvé")
                return None

            # Extraire les informations du premier bloc
            dirigeant_info = {}
            for bloc in blocs:
                paragraphs = bloc.find_all('p')
                if len(paragraphs) >= 2:
                    label = paragraphs[0].get_text().strip()
                    valeur = paragraphs[1].get_text().strip()
                    dirigeant_info[label] = valeur

            # Extraire le dirigeant
            dirigeant = None
            if 'Dénomination' in dirigeant_info:
                dirigeant = dirigeant_info['Dénomination']
            elif 'Nom' in dirigeant_info and 'Prénom' in dirigeant_info:
                nom = dirigeant_info['Nom']
                prenom = dirigeant_info['Prénom']
                nom_formatted = nom.capitalize() if nom.isupper() else nom
                prenom_formatted = prenom.capitalize() if prenom.isupper() else prenom
                dirigeant = f"{prenom_formatted} {nom_formatted}"
            elif 'Nom' in dirigeant_info:
                nom = dirigeant_info['Nom']
                dirigeant = nom.capitalize() if nom.isupper() else nom

            if dirigeant:
                logger.info(f"Dirigeant trouvé: {dirigeant}")
                return dirigeant

            return None

        except Exception as e:
            logger.error(f"Erreur lors du scraping BeautifulSoup: {str(e)}")
            return None

    def _scrape_inpi_full(self, siren: str) -> Optional[Dict[str, str]]:
        """
        Scrape toutes les informations disponibles depuis data.inpi.fr avec Playwright.

        Note: Cette méthode utilise Playwright pour récupérer les informations complètes
        qui sont chargées dynamiquement via JavaScript sur data.inpi.fr.
        Utilisé uniquement pour un usage légitime et limité.

        Args:
            siren: Numéro SIREN (9 chiffres)

        Returns:
            Dict avec toutes les informations trouvées ou None si erreur
        """
        # Vérifier dynamiquement si Playwright est disponible
        try:
            from playwright.sync_api import sync_playwright
            playwright_available = True
        except ImportError:
            playwright_available = False

        if not playwright_available:
            logger.warning("Playwright non disponible - impossible de scraper les données complètes")
            logger.warning("Installez avec: pip install playwright && playwright install chromium")
            return None

        url = f"https://data.inpi.fr/entreprises/{siren}"

        try:
            logger.info(f"Tentative de scraping INPI complet avec Playwright pour SIREN {siren}")

            result = {}

            with sync_playwright() as p:
                # Lancer le navigateur en mode headless
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()

                # Aller sur la page avec timeout plus long et stratégie de chargement moins stricte
                logger.debug(f"Navigation vers {url}")
                try:
                    # Utiliser "domcontentloaded" au lieu de "networkidle" pour être moins strict
                    page.goto(url, wait_until="domcontentloaded", timeout=60000)
                except Exception as e:
                    logger.warning(f"Timeout lors du chargement complet, mais continuons: {e}")

                # Attendre que le contenu soit chargé
                page.wait_for_timeout(3000)  # 3 secondes pour que le JS s'exécute

                # 1. NOM DE LA SOCIETE - H1
                try:
                    h1_element = page.locator('h1').first
                    if h1_element:
                        nom_societe = h1_element.text_content().strip()
                        # Nettoyer "Entreprise : NAME - SIREN XXX" → "NAME"
                        if " - SIREN" in nom_societe:
                            nom_societe = nom_societe.split(" - SIREN")[0]
                        if nom_societe.startswith("Entreprise : "):
                            nom_societe = nom_societe.replace("Entreprise : ", "")
                        result["NOM DE LA SOCIETE"] = nom_societe.strip()
                        logger.debug(f"Nom société trouvé: {result['NOM DE LA SOCIETE']}")
                except Exception as e:
                    logger.debug(f"Impossible d'extraire le nom: {e}")

                # 2. TYPE DE SOCIETE - Chercher "Forme juridique"
                try:
                    # Chercher le texte contenant "Forme juridique"
                    forme_element = page.locator('text=/Forme juridique/').first
                    if forme_element:
                        # Le sibling suivant contient la valeur
                        sibling = forme_element.locator('xpath=following-sibling::*[1]')
                        forme = sibling.text_content().strip()
                        result["TYPE DE SOCIETE"] = forme
                        logger.debug(f"Type société trouvé: {forme}")
                except Exception as e:
                    logger.debug(f"Impossible d'extraire le type: {e}")

                # 3. CAPITAL SOCIAL
                try:
                    capital_element = page.locator('text=/Capital/').first
                    if capital_element:
                        # Le sibling suivant contient la valeur
                        sibling = capital_element.locator('xpath=following-sibling::*[1]')
                        capital = sibling.text_content().strip()
                        result["CAPITAL SOCIAL"] = capital
                        logger.debug(f"Capital trouvé: {capital}")
                except Exception as e:
                    logger.debug(f"Impossible d'extraire le capital: {e}")

                # 4. ADRESSE DE DOMICILIATION
                try:
                    # Chercher "Adresse du siège"
                    adresse_element = page.locator('text=/Adresse du siège/').first
                    if adresse_element:
                        # Le sibling suivant contient la valeur
                        sibling = adresse_element.locator('xpath=following-sibling::*[1]')
                        adresse = sibling.text_content().strip()
                        result["ADRESSE DE DOMICILIATION"] = adresse
                        logger.debug(f"Adresse trouvée: {adresse}")

                        # 5. LOCALITE RCS - Extraire de l'adresse
                        parts = adresse.split()
                        for i, part in enumerate(parts):
                            if part.isdigit() and len(part) == 5:  # Code postal
                                if i + 1 < len(parts):
                                    ville = ' '.join(parts[i+1:])
                                    # Nettoyer les arrondissements et "FRANCE"
                                    ville_clean = ville.replace(" 1ER ARRONDISSEMENT", "")
                                    ville_clean = ville_clean.replace(" 2E ARRONDISSEMENT", "")
                                    for j in range(3, 21):
                                        ville_clean = ville_clean.replace(f" {j}E ARRONDISSEMENT", "")
                                    ville_clean = ville_clean.replace(" FRANCE", "")
                                    result["LOCALITE RCS"] = ville_clean.strip()
                                    logger.debug(f"Localité RCS trouvée: {ville_clean}")
                                    break
                except Exception as e:
                    logger.debug(f"Impossible d'extraire l'adresse: {e}")

                # 6. PRESIDENT DE LA SOCIETE - Section "Gestion et Direction"
                try:
                    # Attendre que la section dirigeants soit visible
                    page.wait_for_selector('h3#representants', timeout=5000)

                    # Chercher les blocs dirigeant
                    blocs_dirigeant = page.locator('.bloc-dirigeant').all()
                    logger.debug(f"Nombre de blocs dirigeant trouvés: {len(blocs_dirigeant)}")

                    if blocs_dirigeant:
                        # Prendre le premier bloc (généralement le président)
                        premier_bloc = blocs_dirigeant[0]
                        paragraphes = premier_bloc.locator('p').all()

                        dirigeant_info = {}
                        for i in range(0, len(paragraphes), 2):
                            if i + 1 < len(paragraphes):
                                label = paragraphes[i].text_content().strip()
                                valeur = paragraphes[i + 1].text_content().strip()
                                dirigeant_info[label] = valeur
                                logger.debug(f"  {label}: {valeur}")

                        # Extraire le dirigeant
                        dirigeant = None
                        if 'Dénomination' in dirigeant_info:
                            dirigeant = dirigeant_info['Dénomination']
                        elif 'Nom' in dirigeant_info and 'Prénom' in dirigeant_info:
                            nom = dirigeant_info['Nom']
                            prenom = dirigeant_info['Prénom']
                            nom_formatted = nom.capitalize() if nom.isupper() else nom
                            prenom_formatted = prenom.capitalize() if prenom.isupper() else prenom
                            dirigeant = f"{prenom_formatted} {nom_formatted}"
                        elif 'Nom' in dirigeant_info:
                            nom = dirigeant_info['Nom']
                            dirigeant = nom.capitalize() if nom.isupper() else nom

                        if dirigeant:
                            result["PRESIDENT DE LA SOCIETE"] = dirigeant
                            logger.info(f"Dirigeant trouvé: {dirigeant}")

                except Exception as e:
                    logger.debug(f"Impossible d'extraire le dirigeant: {e}")

                browser.close()

            logger.info(f"Scraping Playwright réussi: {len(result)} champs récupérés")
            return result if result else None

        except Exception as e:
            logger.error(f"Erreur lors du scraping Playwright INPI pour SIREN {siren}: {str(e)}")
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
                # Fallback 1: Essayer le scraping complet avec Playwright (si disponible)
                logger.info("API INPI non disponible, tentative de scraping direct...")
                try:
                    scraped_data = self._scrape_inpi_full(siren)
                    if scraped_data and len(scraped_data) > 0:
                        # Copier toutes les données récupérées par scraping
                        for key, value in scraped_data.items():
                            if value:  # Seulement si la valeur n'est pas vide
                                result[key] = value

                        result["enrichment_status"] = "success"  # Données récupérées via scraping
                        result["error_message"] = "Données récupérées via scraping Playwright (API indisponible)"
                        logger.info(f"Scraping complet réussi: {len(scraped_data)} champs récupérés")
                        return result
                except Exception as e:
                    logger.warning(f"Échec du scraping Playwright: {str(e)}")

                # Fallback 2: Essayer au moins de récupérer le dirigeant avec BeautifulSoup
                logger.info("Playwright non disponible, tentative scraping BeautifulSoup (dirigeant seulement)...")
                try:
                    dirigeant = self._scrape_inpi_dirigeant(siren)
                    if dirigeant:
                        result["PRESIDENT DE LA SOCIETE"] = dirigeant
                        result["enrichment_status"] = "partial"
                        result["error_message"] = "Seul le dirigeant a pu être récupéré (API indisponible, environnement limité)"
                        logger.info(f"Dirigeant récupéré via BeautifulSoup: {dirigeant}")
                        return result
                except Exception as e:
                    logger.warning(f"Échec du scraping BeautifulSoup: {str(e)}")

                result["error_message"] = "Entreprise non trouvée dans la base INPI (API et scraping échoués)"
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
            # Essayer d'abord depuis l'API INPI (composition.pouvoirs)
            dirigeant = self._extract_dirigeant_from_api(personne_morale)

            # Fallback: Si pas trouvé dans l'API, essayer le scraping INPI web
            if not dirigeant:
                try:
                    logger.info("Dirigeant non trouvé dans API INPI, tentative de scraping site INPI...")
                    dirigeant = self._scrape_inpi_dirigeant(siren)
                except Exception as e:
                    logger.warning(f"Échec du scraping du dirigeant: {str(e)}")

            result["PRESIDENT DE LA SOCIETE"] = dirigeant if dirigeant else ""

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
