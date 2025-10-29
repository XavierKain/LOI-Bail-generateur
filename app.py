"""
Interface Streamlit pour la génération automatique de documents LOI.
"""

import streamlit as st
import logging
from pathlib import Path
from modules import ExcelParser, LOIGenerator
import traceback

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration de la page
st.set_page_config(
    page_title="Générateur de LOI",
    page_icon="📄",
    layout="wide"
)

# Titre de l'application
st.title("📄 Générateur automatique de Lettres d'Intention (LOI)")
st.markdown("---")

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
    help="Uploadez le fichier Excel contenant les données pour la LOI"
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

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray; padding: 20px;'>
    <p>Générateur automatique de LOI v2.0</p>
    <p>Développé pour Forgeot Property</p>
</div>
""", unsafe_allow_html=True)
