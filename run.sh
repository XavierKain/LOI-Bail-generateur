#!/bin/bash

# Script de lancement de l'application Streamlit

echo "🚀 Démarrage du Générateur de LOI..."
echo ""

# Vérifier si les dépendances sont installées
if ! python3 -c "import streamlit" 2>/dev/null; then
    echo "📦 Installation des dépendances..."
    pip3 install -r requirements.txt
    echo ""
fi

# Lancer Streamlit
echo "🌐 L'application sera accessible à l'adresse: http://localhost:8501"
echo ""
streamlit run app.py
