"""
Application unifiée pour génération LOI et BAIL
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

# Initialiser session state pour la navigation
if 'page' not in st.session_state:
    st.session_state.page = 'home'

def show_home():
    """Affiche la page d'accueil"""
    st.title("📄 Générateur de Documents Immobiliers")
    st.markdown("---")

    st.markdown("""
    Bienvenue dans l'outil de génération automatique de documents immobiliers.

    Sélectionnez le type de document que vous souhaitez générer :
    """)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📄 Lettre d'Intention (LOI)")
        st.markdown("""
        - Génération automatique de LOI
        - Enrichissement INPI
        - Export Word
        """)
        if st.button("🚀 Générer une LOI", use_container_width=True, type="primary", key="btn_loi"):
            st.session_state.page = 'loi'
            st.rerun()

    with col2:
        st.markdown("### 📜 Bail Commercial")
        st.markdown("""
        - 16 articles avec logique conditionnelle
        - Variables dérivées automatiques
        - Export Word
        """)
        if st.button("🚀 Générer un BAIL", use_container_width=True, type="primary", key="btn_bail"):
            st.session_state.page = 'bail'
            st.rerun()

    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: gray; padding: 20px;'>
        <p>Générateur automatique de LOI et BAIL v2.0</p>
        <p>Développé par Xavier Kain</p>
    </div>
    """, unsafe_allow_html=True)

def show_loi():
    """Affiche la page LOI"""
    # Bouton retour
    if st.button("← Retour", key="back_from_loi"):
        st.session_state.page = 'home'
        st.rerun()

    st.title("📄 Générateur automatique de Lettres d'Intention (LOI)")
    st.markdown("---")

    # Description
    st.markdown("""
    Cette application génère automatiquement des documents LOI (Lettres d'Intention) avec enrichissement INPI.

    ### Comment ça marche ?
    1. **Uploadez** votre fichier Excel (Fiche de décision)
    2. **Vérifiez** les données extraites
    3. **Générez** le document LOI avec enrichissement INPI automatique
    4. **Téléchargez** le fichier DOCX généré
    """)

    st.markdown("---")

    # Upload du fichier Excel
    st.header("1. Upload du fichier Excel")
    uploaded_file = st.file_uploader(
        "Choisissez votre fichier Excel (Fiche de décision)",
        type=["xlsx", "xls"],
        help="Uploadez le fichier Excel contenant les données",
        key="loi_uploader"
    )

    if uploaded_file is not None:
        try:
            # Sauvegarder temporairement
            temp_path = Path("temp_uploaded.xlsx")
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            st.success(f"✅ Fichier chargé: {uploaded_file.name}")

            # Extraire les données
            with st.spinner("Extraction des données et enrichissement INPI..."):
                parser = ExcelParser(str(temp_path))
                donnees = parser.extract_variables()

            st.success(f"✅ {len(donnees)} variables extraites")

            # Afficher les données extraites
            st.header("2. Données extraites")

            # Informations principales
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Nom Preneur", donnees.get("Nom Preneur", "Non défini"))
                st.metric("Société Bailleur", donnees.get("Société Bailleur", "Non défini"))

            with col2:
                st.metric("Date LOI", donnees.get("Date LOI", "Non défini"))
                st.metric("Loyer annuel HT", str(donnees.get("Loyer annuel HT", "Non défini")))

            with col3:
                st.metric("Surface", str(donnees.get("Surface", "Non défini")))
                st.metric("Durée du Bail", str(donnees.get("Durée du Bail", "Non défini")))

            # Détails complets
            with st.expander("📋 Voir toutes les variables extraites"):
                sorted_donnees = dict(sorted(donnees.items()))

                for key, value in sorted_donnees.items():
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        st.markdown(f"**{key}**")
                    with col2:
                        st.text(str(value))

            st.markdown("---")

            # Génération du document
            st.header("3. Génération du document LOI")

            if st.button("🚀 Générer le document LOI", type="primary", use_container_width=True, key="gen_loi"):
                try:
                    with st.spinner("Génération en cours..."):
                        # Générer la LOI
                        generator = LOIGenerator()

                        # Nom du fichier de sortie
                        nom_preneur = donnees.get("Nom Preneur", "Client")
                        date_loi = donnees.get("Date LOI", "")
                        output_filename = f"{date_loi} - LOI {nom_preneur}.docx"
                        output_filename = output_filename.replace("/", "-").replace("\\", "-")

                        # Générer
                        output_path = Path("output") / output_filename
                        output_path.parent.mkdir(exist_ok=True)

                        generator.generer_document(donnees, str(output_path))

                    st.success("✅ Document LOI généré avec succès!")

                    # Téléchargement
                    st.header("4. Téléchargement")

                    with open(output_path, "rb") as f:
                        st.download_button(
                            label="📥 Télécharger le document LOI",
                            data=f,
                            file_name=output_filename,
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            use_container_width=True,
                            key="download_loi"
                        )

                    st.info(f"📁 Fichier également sauvegardé dans: `{output_path}`")

                except Exception as e:
                    st.error(f"❌ Erreur lors de la génération: {str(e)}")
                    logger.error(f"Erreur génération LOI: {traceback.format_exc()}")

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

def show_bail():
    """Affiche la page BAIL"""
    # Bouton retour
    if st.button("← Retour", key="back_from_bail"):
        st.session_state.page = 'home'
        st.rerun()

    st.title("📜 Générateur automatique de Bail Commercial")
    st.markdown("---")

    # Description
    st.markdown("""
    Cette application génère automatiquement des documents BAIL (Baux Commerciaux) avec logique conditionnelle complexe.

    ### Comment ça marche ?
    1. **Uploadez** votre fichier Excel (Fiche de décision - même format que pour la LOI)
    2. **Vérifiez** les données extraites
    3. **Générez** le document BAIL
    4. **Téléchargez** le fichier DOCX généré
    """)

    st.markdown("---")

    # Vérifier les fichiers nécessaires
    config_path = Path("Redaction BAIL.xlsx")
    template_path = Path("Template BAIL avec placeholder.docx")

    if not config_path.exists():
        st.error(f"❌ Fichier de configuration manquant: {config_path}")
        return

    if not template_path.exists():
        st.error(f"❌ Template manquant: {template_path}")
        return

    # Upload du fichier Excel
    st.header("1. Upload du fichier Excel")
    uploaded_file = st.file_uploader(
        "Choisissez votre fichier Excel (Fiche de décision)",
        type=["xlsx", "xls"],
        help="Uploadez le fichier Excel contenant les données (même format que pour la LOI)",
        key="bail_uploader"
    )

    if uploaded_file is not None:
        try:
            # Sauvegarder temporairement
            temp_path = Path("temp_bail_uploaded.xlsx")
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            st.success(f"✅ Fichier chargé: {uploaded_file.name}")

            # Extraire les données
            with st.spinner("Extraction des données..."):
                parser = ExcelParser(str(temp_path))
                donnees = parser.extract_variables()

                # Générer le nom du fichier de sortie
                nom_preneur = donnees.get("Nom Preneur", "Client")
                date_loi = donnees.get("Date LOI", "")
                output_filename = f"BAIL - {nom_preneur} - {date_loi}.docx"
                output_filename = output_filename.replace("/", "-").replace("\\", "-")

            st.success(f"✅ {len(donnees)} variables extraites")

            # Afficher les données extraites
            st.header("2. Données extraites")

            # Informations principales
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Nom Preneur", donnees.get("Nom Preneur", "Non défini"))
                st.metric("Société Bailleur", donnees.get("Société Bailleur", "Non défini"))

            with col2:
                st.metric("Date LOI", donnees.get("Date LOI", "Non défini"))
                st.metric("Montant du loyer", str(donnees.get("Montant du loyer", "Non défini")))

            with col3:
                st.metric("Durée Bail", str(donnees.get("Durée Bail", "Non défini")) + " ans")
                st.metric("Enseigne", donnees.get("Enseigne", "Non défini"))

            # Détails complets
            with st.expander("📋 Voir toutes les variables extraites"):
                sorted_donnees = dict(sorted(donnees.items()))

                for key, value in sorted_donnees.items():
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        st.markdown(f"**{key}**")
                    with col2:
                        st.text(str(value))

            st.markdown("---")

            # Génération du document
            st.header("3. Génération du document BAIL")

            if st.button("🚀 Générer le document BAIL", type="primary", use_container_width=True, key="gen_bail"):
                try:
                    with st.spinner("Génération en cours..."):
                        # Initialiser le générateur BAIL
                        bail_generator = BailGenerator(str(config_path))

                        # Générer les articles
                        articles_generes = bail_generator.generer_bail(donnees)

                        st.success(f"✅ {len(articles_generes)} articles générés")

                        # Afficher un aperçu des articles
                        with st.expander("📄 Aperçu des articles générés"):
                            for article_name, texte in articles_generes.items():
                                st.markdown(f"**{article_name}**")
                                st.text(texte[:200] + "..." if len(texte) > 200 else texte)
                                st.markdown("---")

                        # Générer le document Word
                        with st.spinner("Création du document Word..."):
                            word_generator = BailWordGenerator(str(template_path))

                            # Générer
                            output_path = Path("output") / output_filename
                            output_path.parent.mkdir(exist_ok=True)

                            # Calculer les données complètes (avec variables dérivées)
                            donnees_complete = bail_generator.calculer_variables_derivees(donnees)

                            word_generator.generer_document(
                                articles_generes,
                                donnees_complete,
                                str(output_path)
                            )

                    st.success(f"✅ Document BAIL généré avec succès!")

                    # Téléchargement
                    st.header("4. Téléchargement")

                    with open(output_path, "rb") as f:
                        st.download_button(
                            label="📥 Télécharger le document BAIL",
                            data=f,
                            file_name=output_filename,
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            use_container_width=True,
                            key="download_bail"
                        )

                    st.info(f"📁 Fichier également sauvegardé dans: `{output_path}`")

                    # Informations
                    with st.expander("ℹ️ Informations importantes"):
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
                    st.error(f"❌ Erreur lors de la génération: {str(e)}")
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

# Router principal
if st.session_state.page == 'home':
    show_home()
elif st.session_state.page == 'loi':
    show_loi()
elif st.session_state.page == 'bail':
    show_bail()
