"""
Application unifiée pour génération LOI et BAIL
Interface unique avec upload unique et deux boutons de génération
"""

import streamlit as st
import logging
from pathlib import Path
from modules import ExcelParser, LOIGenerator, BailGenerator, BailWordGenerator
from modules.placeholder_extractor import extract_all_placeholders, categorize_placeholders
import traceback
import hashlib

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Fonction cachée pour parser le fichier Excel (évite de recharger à chaque clic)
@st.cache_data(show_spinner=False)
def parse_excel_cached(file_content: bytes, file_name: str, config_path: str):
    """Parse le fichier Excel et cache le résultat pour éviter les rechargements."""
    # Créer un hash du contenu pour identifier le fichier de manière unique
    file_hash = hashlib.md5(file_content).hexdigest()

    # Sauvegarder temporairement
    temp_path = Path(f"temp_{file_hash}.xlsx")
    with open(temp_path, "wb") as f:
        f.write(file_content)

    try:
        # Parser le fichier
        parser = ExcelParser(str(temp_path), config_path)
        variables = parser.extract_variables()
        societes_info = parser.extract_societe_info()
        output_filename_loi = parser.get_output_filename(variables)

        return variables, societes_info, output_filename_loi
    finally:
        # Nettoyer le fichier temporaire
        if temp_path.exists():
            temp_path.unlink()

# Configuration de la page
st.set_page_config(
    page_title="Générateur LOI & BAIL",
    page_icon="📄",
    layout="wide"
)

# Titre de l'application
st.title("📄 Générateur de Documents Immobiliers")
st.markdown("Génération automatique de LOI et BAIL à partir d'une Fiche de décision")

st.markdown("---")

# Description
st.markdown("""
Cette application génère automatiquement des documents LOI (Lettres d'Intention) et BAIL (Baux Commerciaux).

### Comment ça marche ?
1. **Uploadez** votre fichier Excel (Fiche de décision)
2. **Vérifiez** les données extraites et enrichies (INPI)
3. **Choisissez** : Générer LOI ou Générer BAIL (ou les deux !)
4. **Téléchargez** les fichiers DOCX générés
""")

st.markdown("---")

# Vérifier que les fichiers nécessaires existent
config_loi_path = Path("Rédaction LOI.xlsx")
template_loi_path = Path("Template LOI avec placeholder.docx")
config_bail_path = Path("Redaction BAIL.xlsx")
template_bail_path = Path("2025 - Template BAIL.docx")

missing_files = []
if not config_loi_path.exists():
    missing_files.append(str(config_loi_path))
if not template_loi_path.exists():
    missing_files.append(str(template_loi_path))
if not config_bail_path.exists():
    missing_files.append(str(config_bail_path))
if not template_bail_path.exists():
    missing_files.append(str(template_bail_path))

if missing_files:
    st.error(f"❌ Fichiers manquants: {', '.join(missing_files)}")
    st.stop()

# Upload du fichier Excel (UNIQUE)
st.header("1. Upload du fichier Excel")
uploaded_file = st.file_uploader(
    "Choisissez votre fichier Excel (Fiche de décision)",
    type=["xlsx", "xls"],
    help="Uploadez le fichier Excel contenant les données pour LOI et BAIL"
)

if uploaded_file is not None:
    try:
        st.success(f"✅ Fichier chargé: {uploaded_file.name}")

        # Extraire les données avec le parser CACHÉ (évite rechargement à chaque clic)
        file_content = uploaded_file.getbuffer().tobytes()

        with st.spinner("Extraction des données et enrichissement INPI..."):
            variables, societes_info, output_filename_loi = parse_excel_cached(
                file_content,
                uploaded_file.name,
                str(config_loi_path)
            )

        # IMPORTANT: Toujours mettre à jour la date d'aujourd'hui (ne pas utiliser celle du cache)
        from datetime import datetime
        variables["Date d'aujourd'hui"] = datetime.now().strftime("%d/%m/%Y")

        st.success(f"✅ {len(variables)} variables extraites et enrichies (données en cache)")

        # Afficher les données extraites
        st.header("2. Données extraites et enrichies")

        # Informations principales
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Nom Preneur", variables.get("Nom Preneur", "Non défini"))
            st.metric("Société Bailleur", variables.get("Société Bailleur", "Non défini"))

        with col2:
            st.metric("Date LOI", variables.get("Date LOI", "Non défini"))
            montant_loyer = variables.get("Montant du loyer", "Non défini")
            st.metric("Montant du loyer", f"{montant_loyer} €" if montant_loyer != "Non défini" else "Non défini")

        with col3:
            duree_bail = variables.get("Durée Bail", "Non défini")
            st.metric("Durée Bail", f"{duree_bail} ans" if duree_bail != "Non défini" else "Non défini")
            st.metric("Enseigne", variables.get("Enseigne", "Non défini"))

        # Section INPI (si données enrichies via SIRET)
        siret = variables.get("N° DE SIRET", "")
        if siret:
            st.markdown("---")
            inpi_enriched = variables.get("_inpi_enriched", "false") == "true"

            if inpi_enriched:
                st.success("🏢 Données INPI enrichies automatiquement ✅")
            else:
                error_msg = variables.get("_inpi_error", "Erreur inconnue")
                st.warning(f"⚠️ Enrichissement INPI échoué: {error_msg}")

            # Afficher les données INPI
            with st.expander("📊 Informations INPI", expanded=inpi_enriched):
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("**SIRET**")
                    st.text(siret)

                    st.markdown("**Nom de la société**")
                    st.text(variables.get("NOM DE LA SOCIETE", "Non disponible"))

                    st.markdown("**Type de société**")
                    st.text(variables.get("TYPE DE SOCIETE", "Non disponible"))

                with col2:
                    st.markdown("**Capital social**")
                    st.text(variables.get("CAPITAL SOCIAL", "Non disponible"))

                    st.markdown("**Localité RCS**")
                    st.text(variables.get("LOCALITE RCS", "Non disponible"))

                st.markdown("**Adresse de domiciliation**")
                st.text(variables.get("ADRESSE DE DOMICILIATION", "Non disponible"))

                st.markdown("**Président / Gérant**")
                st.text(variables.get("PRESIDENT DE LA SOCIETE", "Non disponible"))

        # Détails complets
        with st.expander("📋 Voir toutes les variables extraites", expanded=False):
            # Filtrer les variables spéciales (formules, descriptions)
            display_vars = {
                k: v for k, v in variables.items()
                if not k.startswith("_")
            }

            # Trier par ordre alphabétique
            sorted_vars = dict(sorted(display_vars.items()))

            # Compter les variables manquantes
            missing_count = sum(1 for v in display_vars.values() if not v or str(v).strip() == "")
            total_count = len(display_vars)

            if missing_count > 0:
                st.warning(f"⚠️ {missing_count}/{total_count} variables manquantes")
            else:
                st.success(f"✅ Toutes les {total_count} variables sont renseignées")

            # Afficher dans un tableau avec codes couleur
            for key, value in sorted_vars.items():
                col1, col2, col3 = st.columns([2, 3, 1])
                with col1:
                    st.markdown(f"**{key}**")
                with col2:
                    if value and str(value).strip():
                        st.text(str(value))
                    else:
                        st.markdown("*Non défini*")
                with col3:
                    if value and str(value).strip():
                        st.markdown("✅")
                    else:
                        st.markdown("⚠️")

        st.markdown("---")

        # Génération des documents (DEUX BOUTONS CÔTE À CÔTE)
        st.header("3. Génération des documents")

        st.info("💡 **Info**: Grâce au cache, après la première génération, les suivantes seront quasi-instantanées ! La barre de chargement indique la progression.")

        col_loi, col_bail = st.columns(2)

        # BOUTON LOI
        with col_loi:
            st.markdown("### 📄 Lettre d'Intention")
            st.markdown("""
            - Enrichissement INPI automatique
            - Sections optionnelles
            - Headers/Footers personnalisés
            """)

            if st.button("🚀 Générer LOI", type="primary", use_container_width=True, key="btn_gen_loi"):
                try:
                    with st.spinner("⏳ Génération en cours... (Enrichissement INPI, création du document)"):
                        # Créer le générateur LOI avec l'API ORIGINALE
                        generator = LOIGenerator(
                            variables,
                            societes_info,
                            str(template_loi_path)
                        )

                        # Générer le document
                        output_path = Path("output") / output_filename_loi
                        output_path.parent.mkdir(exist_ok=True)
                        generated_path = generator.generate(str(output_path))

                    st.success("✅ Document LOI généré avec succès!")
                    st.info("👇 Cliquez sur le bouton ci-dessous pour télécharger le document")

                    # Téléchargement direct
                    with open(generated_path, "rb") as f:
                        file_data = f.read()

                        st.download_button(
                            label="📥 Télécharger le document LOI",
                            data=file_data,
                            file_name=output_filename_loi,
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            use_container_width=True,
                            key="download_loi",
                            type="primary"
                        )

                    st.caption(f"📁 Fichier sauvegardé: `{generated_path}`")

                    # Informations sur les placeholders
                    with st.expander("ℹ️ Informations LOI"):
                        st.markdown("""
                        ### Finalisation du document

                        Le document généré peut contenir des placeholders en **rouge** qui indiquent des données manquantes.
                        Ces placeholders doivent être complétés manuellement dans le document Word.

                        ### Sections optionnelles

                        Les sections optionnelles (ex: paliers années 4-6) sont automatiquement supprimées si elles n'ont pas de données.

                        ### Prochaines étapes

                        1. Ouvrez le document DOCX généré
                        2. Vérifiez que toutes les données sont correctes
                        3. Complétez les placeholders en rouge (si présents)
                        4. Exportez en PDF si nécessaire
                        """)

                except Exception as e:
                    st.error(f"❌ Erreur lors de la génération LOI: {str(e)}")
                    logger.error(f"Erreur génération LOI: {traceback.format_exc()}")

                    with st.expander("Détails de l'erreur"):
                        st.code(traceback.format_exc())

        # BOUTON BAIL
        with col_bail:
            st.markdown("### 📜 Bail Commercial")
            st.markdown("""
            - 16 articles conditionnels
            - Variables dérivées automatiques
            - Logique complexe
            """)

            if st.button("🚀 Générer BAIL", type="primary", use_container_width=True, key="btn_gen_bail"):
                try:
                    with st.spinner("⏳ Génération en cours... (Analyse des conditions, création des articles)"):
                        # Générer le nom du fichier BAIL
                        nom_preneur = variables.get("Nom Preneur", "Client")
                        date_loi = variables.get("Date LOI", "")
                        output_filename_bail = f"BAIL - {nom_preneur} - {date_loi}.docx"
                        output_filename_bail = output_filename_bail.replace("/", "-").replace("\\", "-")

                        # Initialiser le générateur BAIL
                        bail_generator = BailGenerator(str(config_bail_path))

                        # Générer les articles
                        articles_generes = bail_generator.generer_bail(variables)

                    st.success(f"✅ {len(articles_generes)} articles générés")

                    with st.spinner("⏳ Finalisation du document Word..."):
                        # Calculer les données complètes (avec variables dérivées)
                        donnees_complete = bail_generator.calculer_variables_derivees(variables)

                        # Afficher les variables dérivées calculées
                        with st.expander("🔍 Variables dérivées calculées"):
                            # Identifier les nouvelles variables (dérivées)
                            derived_vars = {k: v for k, v in donnees_complete.items() if k not in variables}

                            if derived_vars:
                                st.info(f"✨ {len(derived_vars)} variables calculées automatiquement")

                                for key, value in sorted(derived_vars.items()):
                                    col1, col2, col3 = st.columns([2, 3, 1])
                                    with col1:
                                        st.markdown(f"**{key}**")
                                    with col2:
                                        if value and str(value).strip():
                                            st.text(str(value))
                                        else:
                                            st.markdown("*Non calculé*")
                                    with col3:
                                        if value and str(value).strip():
                                            st.markdown("✅")
                                        else:
                                            st.markdown("⚠️")
                            else:
                                st.warning("Aucune variable dérivée calculée")

                        # Générer le document Word
                        word_generator = BailWordGenerator(str(template_bail_path))

                        output_path = Path("output") / output_filename_bail
                        output_path.parent.mkdir(exist_ok=True)

                        word_generator.generer_document(
                            articles_generes,
                            donnees_complete,
                            str(output_path)
                        )

                    st.success("✅ Document BAIL généré avec succès!")
                    st.info("👇 Cliquez sur le bouton ci-dessous pour télécharger le document")

                    # Téléchargement direct
                    with open(output_path, "rb") as f:
                        file_data = f.read()

                        st.download_button(
                            label="📥 Télécharger le document BAIL",
                            data=file_data,
                            file_name=output_filename_bail,
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            use_container_width=True,
                            key="download_bail",
                            type="primary"
                        )

                    st.caption(f"📁 Fichier sauvegardé: `{output_path}`")

                    # Afficher tous les placeholders du template avec leur statut
                    with st.expander("📝 Statut des placeholders du template"):
                        # Extraire tous les placeholders du template
                        all_placeholders = extract_all_placeholders(str(template_bail_path))
                        categorized = categorize_placeholders(all_placeholders)

                        # Compter les placeholders par statut
                        filled_count = 0
                        missing_count = 0

                        st.markdown("### Variables normales")
                        for placeholder in categorized["variables_normales"]:
                            # Normaliser et chercher la valeur
                            value = donnees_complete.get(placeholder)
                            if not value:
                                # Essayer avec normalisation
                                from modules.bail_word_generator import BailWordGenerator
                                wg = BailWordGenerator()
                                normalized = wg._normalize_variable_name(placeholder, donnees_complete)
                                value = donnees_complete.get(normalized)

                            col1, col2, col3 = st.columns([2, 3, 1])
                            with col1:
                                st.markdown(f"**[{placeholder}]**")
                            with col2:
                                if value and str(value).strip():
                                    st.text(str(value)[:50] + ("..." if len(str(value)) > 50 else ""))
                                    filled_count += 1
                                else:
                                    st.markdown("*Non trouvé*")
                                    missing_count += 1
                            with col3:
                                if value and str(value).strip():
                                    st.markdown("✅")
                                else:
                                    st.markdown("❌")

                        if categorized["variables_lettres"]:
                            st.markdown("### Variables 'en lettres'")
                            for placeholder in categorized["variables_lettres"]:
                                base_var = placeholder.replace(" en lettres", "")
                                value = donnees_complete.get(base_var)

                                col1, col2, col3 = st.columns([2, 3, 1])
                                with col1:
                                    st.markdown(f"**[{placeholder}]**")
                                with col2:
                                    if value:
                                        st.text(f"Basé sur: {base_var} = {value}")
                                        filled_count += 1
                                    else:
                                        st.markdown(f"*Variable de base '{base_var}' non trouvée*")
                                        missing_count += 1
                                with col3:
                                    if value:
                                        st.markdown("✅")
                                    else:
                                        st.markdown("❌")

                        st.markdown("---")
                        if missing_count > 0:
                            st.warning(f"⚠️ {missing_count} placeholders non remplacés sur {filled_count + missing_count} total")
                        else:
                            st.success(f"✅ Tous les {filled_count} placeholders seront remplacés")

                    # Informations
                    with st.expander("ℹ️ Informations BAIL"):
                        st.markdown("""
                        ### Finalisation du document

                        Le document généré peut contenir des placeholders qui indiquent des données manquantes.
                        Ces placeholders doivent être complétés manuellement dans le document Word.

                        ### Articles conditionnels

                        Certains articles sont générés uniquement si les conditions sont remplies:
                        - Article préliminaire: Si conditions suspensives
                        - Article 5.3: Selon option d'accession
                        - Article 7.6: Si droit d'entrée présent
                        - Article 26.1: Si paliers de loyer
                        - Article 26.2: Si franchise de loyer

                        ### Prochaines étapes

                        1. Ouvrez le document DOCX généré
                        2. Vérifiez que toutes les données sont correctes
                        3. Complétez les placeholders si présents
                        4. Exportez en PDF si nécessaire
                        """)

                except Exception as e:
                    st.error(f"❌ Erreur lors de la génération BAIL: {str(e)}")
                    logger.error(f"Erreur génération BAIL: {traceback.format_exc()}")

                    with st.expander("Détails de l'erreur"):
                        st.code(traceback.format_exc())

    except Exception as e:
        st.error(f"❌ Erreur lors du traitement du fichier: {str(e)}")
        logger.error(f"Erreur traitement: {traceback.format_exc()}")

        with st.expander("Détails de l'erreur"):
            st.code(traceback.format_exc())

else:
    st.info("👆 Uploadez un fichier Excel pour commencer")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray; padding: 20px;'>
    <p>Générateur automatique de LOI et BAIL v2.0</p>
    <p>Développé par Xavier Kain</p>
</div>
""", unsafe_allow_html=True)
