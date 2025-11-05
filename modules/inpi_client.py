"""
Client pour l'API INPI (Institut National de la Propriété Industrielle).
Permet de récupérer les informations des entreprises françaises via le RNE.
"""

import logging
import requests
import time
from typing import Optional, Dict
from ratelimit import limits, sleep_and_retry
from functools import lru_cache

from .config import Config

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
        self.username = username or Config.INPI_USERNAME
        self.password = password or Config.INPI_PASSWORD
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

            result["NOM DE LA SOCIETE"] = (
                desc_etab.get("nomCommercial") or
                desc_etab.get("enseigne") or
                personne_morale.get("denomination") or
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

            # Capital social - chercher dans personneMorale.capital
            capital = personne_morale.get("capital", {})
            if isinstance(capital, dict):
                montant = capital.get("montant") or capital.get("capitalSocial")
                if montant:
                    if isinstance(montant, (int, float)):
                        result["CAPITAL SOCIAL"] = f"{int(montant):,}".replace(",", " ") + " €"
                    else:
                        result["CAPITAL SOCIAL"] = str(montant)
            elif isinstance(capital, (int, float)):
                result["CAPITAL SOCIAL"] = f"{int(capital):,}".replace(",", " ") + " €"

            # Localité RCS (greffe) - chercher dans les identifiants
            identifiants = personne_morale.get("identifiant", {})
            if isinstance(identifiants, list):
                for ident in identifiants:
                    if ident.get("typeIdentifiant") == "RCS":
                        result["LOCALITE RCS"] = ident.get("registre", "")
                        break

            # Adresse de domiciliation (siège social)
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

            # Président/gérant (représentant légal)
            # Les représentants sont souvent dans une section séparée de l'API
            # Pour l'instant on laisse vide, nécessiterait un appel API supplémentaire
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
