"""
Page d'accueil - Sélection LOI ou BAIL
Version avec pages sans emojis pour compatibilité Streamlit Cloud
"""

import streamlit as st

st.set_page_config(
    page_title="Générateur LOI & BAIL",
    page_icon="📄",
    layout="wide"
)

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
    if st.button("🚀 Générer une LOI", use_container_width=True, type="primary"):
        st.switch_page("pages/1_LOI.py")

with col2:
    st.markdown("### 📜 Bail Commercial")
    st.markdown("""
    - 16 articles avec logique conditionnelle
    - Variables dérivées automatiques
    - Export Word
    """)
    if st.button("🚀 Générer un BAIL", use_container_width=True, type="primary"):
        st.switch_page("pages/2_BAIL.py")

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray; padding: 20px;'>
    <p>Générateur automatique de LOI et BAIL v2.0</p>
    <p>Développé par Xavier Kain</p>
</div>
""", unsafe_allow_html=True)
