"""
Interface Streamlit pour la génération automatique de documents LOI et BAIL.
"""

import streamlit as st
import logging
from pathlib import Path
from modules import ExcelParser, LOIGenerator, BailGenerator, BailWordGenerator
import traceback
import pandas as pd

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration de la page
st.set_page_config(
    page_title="Générateur de LOI et BAIL",
    page_icon="📄",
    layout="wide"
)

# Titre de l'application
st.title("📄 Générateur automatique de documents LOI et BAIL")
st.markdown("---")

# Tabs pour sélectionner le type de document
tab_loi, tab_bail = st.tabs(["📄 Lettre d'Intention (LOI)", "📜 Bail Commercial"])

# ============================================================================
# TAB LOI
# ============================================================================
with tab_loi:
        # Description
        st.markdown("""
        Cette application génère automatiquement des documents LOI (Lettres d'Intention) pour des baux commerciaux.

        ### Comment ça marche ?
        1. **Uploadez** votre fichier Excel (Fiche de décision)
        2. **Vérifiez** les données extraites
        3. **Générez** le document LOI
        4. **Téléchargez** le fichier DOCX généré
        """)

        st.markdown("---")

        # Vérifier que les fichiers nécessaires existent
        config_path = Path("Rédaction LOI.xlsx")
        template_path = Path("Template LOI avec placeholder.docx")

        if not config_path.exists():
            st.error(f"❌ Fichier de configuration manquant: {config_path}")
            st.stop()

        if not template_path.exists():
            st.error(f"❌ Template manquant: {template_path}")
            st.stop()

        # Upload du fichier Excel
        st.header("1. Upload du fichier Excel")
        uploaded_file = st.file_uploader(
            "Choisissez votre fichier Excel (Fiche de décision)",
            type=["xlsx", "xls"],
            help="Uploadez le fichier Excel contenant les données pour la LOI",
            key="loi_uploader"
        )

    if uploaded_file is not None:
        try:
            # Sauvegarder temporairement le fichier
            temp_path = Path("temp_uploaded.xlsx")
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            st.success(f"✅ Fichier chargé: {uploaded_file.name}")

            # Extraire les données
            with st.spinner("Extraction des données..."):
                parser = ExcelParser(str(temp_path), str(config_path))
                variables = parser.extract_variables()
                societes_info = parser.extract_societe_info()
                output_filename = parser.get_output_filename(variables)

            st.success(f"✅ {len(variables)} variables extraites")

            # Afficher les données extraites
            st.header("2. Données extraites")

            # Informations principales
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Nom Preneur", variables.get("Nom Preneur", "Non défini"))
                st.metric("Société Bailleur", variables.get("Société Bailleur", "Non défini"))

            with col2:
                st.metric("Date LOI", variables.get("Date LOI", "Non défini"))
                st.metric("Montant du loyer", variables.get("Montant du loyer", "Non défini") + " €")

            with col3:
                st.metric("Durée Bail", variables.get("Durée Bail", "Non défini") + " ans")
                st.metric("Enseigne", variables.get("Enseigne", "Non défini"))

            # Section INPI (si données enrichies)
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

            # Génération du document
            st.header("3. Génération du document LOI")

            if st.button("🚀 Générer le document LOI", type="primary", use_container_width=True):
                try:
                    with st.spinner("Génération en cours..."):
                        # Créer le générateur
                        generator = LOIGenerator(variables, societes_info, str(template_path))

                        # Générer le document
                        output_path = Path("output") / output_filename
                        generated_path = generator.generate(str(output_path))

                    st.success(f"✅ Document généré avec succès!")

                    # Téléchargement
                    st.header("4. Téléchargement")

                    with open(generated_path, "rb") as f:
                        st.download_button(
                            label="📥 Télécharger le document LOI",
                            data=f,
                            file_name=output_filename,
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            use_container_width=True
                        )

                    st.info(f"📁 Fichier également sauvegardé dans: `{generated_path}`")

                    # Informations sur les placeholders
                    with st.expander("ℹ️ Informations importantes"):
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
                    st.error(f"❌ Erreur lors de la génération: {str(e)}")
                    logger.error(f"Erreur génération: {traceback.format_exc()}")

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



# ============================================================================
# TAB BAIL
# ============================================================================
with tab_bail:
    # Description
    st.markdown("""
    Cette application génère automatiquement des documents BAIL (Baux Commerciaux).

    ### Comment ça marche ?
    1. **Uploadez** votre fichier Excel (Données BAIL)
    2. **Vérifiez** les données extraites
    3. **Générez** le document BAIL
    4. **Téléchargez** le fichier DOCX généré
    """)

    st.markdown("---")

    # Vérifier que les fichiers nécessaires existent
    bail_config_path = Path("Redaction BAIL.xlsx")
    bail_template_path = Path("Template BAIL avec placeholder.docx")

    if not bail_config_path.exists():
        st.error(f"❌ Fichier de configuration manquant: {bail_config_path}")
        st.stop()

    if not bail_template_path.exists():
        st.error(f"❌ Template manquant: {bail_template_path}")
        st.stop()

    # Upload du fichier Excel
    st.header("1. Upload du fichier Excel")
    bail_uploaded_file = st.file_uploader(
        "Choisissez votre fichier Excel (Données BAIL)",
        type=["xlsx", "xls"],
        help="Uploadez le fichier Excel contenant les données pour le BAIL",
        key="bail_uploader"
    )

    if bail_uploaded_file is not None:
        try:
            # Sauvegarder temporairement
            bail_temp_path = Path("temp_bail_uploaded.xlsx")
            with open(bail_temp_path, "wb") as f:
                f.write(bail_uploaded_file.getbuffer())

            st.success(f"✅ Fichier chargé: {bail_uploaded_file.name}")

            # Lire le fichier Excel pour extraire les données
            with st.spinner("Extraction des données..."):
                # Lire l'onglet "Liste" ou le premier onglet disponible
                try:
                    df = pd.read_excel(bail_temp_path, sheet_name="Liste")
                except:
                    df = pd.read_excel(bail_temp_path, sheet_name=0)

                # Convertir en dictionnaire (première colonne = clés, deuxième = valeurs)
                if len(df.columns) >= 2:
                    donnees = dict(zip(df.iloc[:, 0], df.iloc[:, 1]))
                    # Nettoyer les NaN
                    donnees = {k: v for k, v in donnees.items() if pd.notna(k) and pd.notna(v)}
                else:
                    st.error("Le fichier Excel doit avoir au moins 2 colonnes (Variable, Valeur)")
                    st.stop()

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

            if st.button("🚀 Générer le document BAIL", type="primary", use_container_width=True, key="generate_bail"):
                try:
                    with st.spinner("Génération en cours..."):
                        # Initialiser le générateur BAIL
                        bail_generator = BailGenerator(str(bail_config_path))

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
                            word_generator = BailWordGenerator(str(bail_template_path))

                            # Définir le nom de sortie
                            nom_preneur = donnees.get("Nom Preneur", "Client")
                            date_loi = donnees.get("Date LOI", "")
                            output_filename = f"BAIL - {nom_preneur} - {date_loi}.docx".replace("/", "-")

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
            if bail_temp_path.exists():
                bail_temp_path.unlink()

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
