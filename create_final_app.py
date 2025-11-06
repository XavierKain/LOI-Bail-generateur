"""Create final app.py with proper structure using Python string manipulation."""

# Read the working LOI app
with open('app_loi_working.py', 'r', encoding='utf-8') as f:
    loi_lines = f.readlines()

# Read the working BAIL app
with open('app_bail.py', 'r', encoding='utf-8') as f:
    bail_lines = f.readlines()

# Build the new app.py
output = []

# Header
output.append('"""\n')
output.append('Interface Streamlit pour la génération automatique de documents LOI et BAIL.\n')
output.append('"""\n\n')
output.append('import streamlit as st\n')
output.append('import logging\n')
output.append('from pathlib import Path\n')
output.append('from modules import ExcelParser, LOIGenerator, BailGenerator, BailWordGenerator\n')
output.append('import traceback\n')
output.append('import pandas as pd\n\n')

output.append('# Configuration du logging\n')
output.append('logging.basicConfig(\n')
output.append('    level=logging.INFO,\n')
output.append('    format=\'%(asctime)s - %(name)s - %(levelname)s - %(message)s\'\n')
output.append(')\n')
output.append('logger = logging.getLogger(__name__)\n\n')

output.append('# Configuration de la page\n')
output.append('st.set_page_config(\n')
output.append('    page_title="Générateur de LOI et BAIL",\n')
output.append('    page_icon="📄",\n')
output.append('    layout="wide"\n')
output.append(')\n\n')

output.append('# Titre de l\'application\n')
output.append('st.title("📄 Générateur automatique de documents LOI et BAIL")\n')
output.append('st.markdown("---")\n\n')

output.append('# Tabs pour sélectionner le type de document\n')
output.append('tab_loi, tab_bail = st.tabs(["📄 Lettre d\'Intention (LOI)", "📜 Bail Commercial"])\n\n')

output.append('# ============================================================================\n')
output.append('# TAB LOI\n')
output.append('# ============================================================================\n')
output.append('with tab_loi:\n')

# Extract LOI content (skip imports, just take the main logic starting from "Cette application")
in_content = False
for line in loi_lines:
    if 'Cette application génère automatiquement des documents LOI' in line:
        in_content = True
    if in_content and '# Footer' in line:
        break
    if in_content:
        # Indent by 4 spaces
        if line.strip():
            output.append('    ' + line)
        else:
            output.append('\n')

# Add BAIL tab
output.append('\n# ============================================================================\n')
output.append('# TAB BAIL\n')
output.append('# ============================================================================\n')
output.append('with tab_bail:\n')

# Extract BAIL content
in_bail_content = False
for line in bail_lines:
    if 'Cette application génère automatiquement des documents BAIL' in line:
        in_bail_content = True
    if in_bail_content and '# Footer' in line:
        break
    if in_bail_content:
        # Indent by 4 spaces
        if line.strip():
            output.append('    ' + line)
        else:
            output.append('\n')

# Footer
output.append('\n# Footer\n')
output.append('st.markdown("---")\n')
output.append('st.markdown("""\n')
output.append('<div style=\'text-align: center; color: gray; padding: 20px;\'>\n')
output.append('    <p>Générateur automatique de LOI et BAIL v2.0</p>\n')
output.append('    <p>Développé par Xavier Kain</p>\n')
output.append('</div>\n')
output.append('""", unsafe_allow_html=True)\n')

# Write the file
with open('app.py', 'w', encoding='utf-8') as f:
    f.writelines(output)

print("✅ app.py créé avec succès")
print(f"   Total lignes: {len(output)}")
