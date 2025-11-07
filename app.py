"""
Application unifiée pour génération LOI et BAIL
Interface unique avec upload unique et deux boutons de génération
"""

import streamlit as st
import logging
from pathlib import Path
from modules import ExcelParser, LOIGenerator, BailGenerator, BailWordGenerator
import traceback

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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
template_bail_path = Path("Template BAIL avec placeholder.docx")

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
        # Sauvegarder temporairement le fichier
        temp_path = Path("temp_uploaded.xlsx")
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        st.success(f"✅ Fichier chargé: {uploaded_file.name}")

        # Extraire les données avec le parser ORIGINAL (fonctionnel pour LOI)
        with st.spinner("Extraction des données et enrichissement INPI..."):
            parser = ExcelParser(str(temp_path), str(config_loi_path))
            variables = parser.extract_variables()
            societes_info = parser.extract_societe_info()
            output_filename_loi = parser.get_output_filename(variables)

        st.success(f"✅ {len(variables)} variables extraites et enrichies")

        # Afficher les données extraites
        st.header("2. Données extraites")

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

        # Détails complets
        with st.expander("📋 Voir toutes les variables extraites"):
            # Filtrer les variables spéciales (formules, descriptions)
            display_vars = {
                k: v for k, v in variables.items()
                if not k.startswith("_")
            }

            # Trier par ordre alphabétique
            sorted_vars = dict(sorted(display_vars.items()))

            # Afficher dans un tableau
            for key, value in sorted_vars.items():
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.markdown(f"**{key}**")
                with col2:
                    if value:
                        st.text(value)
                    else:
                        st.markdown("*Non défini*")

        st.markdown("---")

        # Génération des documents (DEUX BOUTONS CÔTE À CÔTE)
        st.header("3. Génération des documents")

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
                    with st.spinner("Génération du document LOI..."):
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

                    # Téléchargement
                    with open(generated_path, "rb") as f:
                        st.download_button(
                            label="📥 Télécharger le document LOI",
                            data=f,
                            file_name=output_filename_loi,
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            use_container_width=True,
                            key="download_loi"
                        )

                    st.info(f"📁 Fichier sauvegardé: `{generated_path}`")

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
                    with st.spinner("Génération du document BAIL..."):
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

                        # Calculer les données complètes (avec variables dérivées)
                        donnees_complete = bail_generator.calculer_variables_derivees(variables)

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

                    # Téléchargement
                    with open(output_path, "rb") as f:
                        st.download_button(
                            label="📥 Télécharger le document BAIL",
                            data=f,
                            file_name=output_filename_bail,
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            use_container_width=True,
                            key="download_bail"
                        )

                    st.info(f"📁 Fichier sauvegardé: `{output_path}`")

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

        # Nettoyage
        if temp_path.exists():
            temp_path.unlink()

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
