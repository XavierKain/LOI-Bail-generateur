"""Explorer l'API INPI pour trouver les données de dirigeants."""

from modules.inpi_client import INPIClient
import json

client = INPIClient()
siren = "481283901"  # Fleux

print(f"Exploration pour SIREN: {siren}\n")

# Récupérer les données brutes
company_data = client._search_by_siren(siren)

if company_data:
    # Sauvegarder
    with open('dirigeant_exploration.json', 'w', encoding='utf-8') as f:
        json.dump(company_data, f, indent=2, ensure_ascii=False)

    print("✅ Données sauvegardées dans dirigeant_exploration.json\n")

    # Chercher composition.pouvoirs
    formality = company_data.get("formality", {})
    content = formality.get("content", {})
    personne_morale = content.get("personneMorale", {})
    composition = personne_morale.get("composition", {})
    pouvoirs = composition.get("pouvoirs", [])

    print(f"Nombre de pouvoirs trouvés: {len(pouvoirs)}\n")

    if pouvoirs:
        print("Détails des pouvoirs:\n" + "="*80)
        for i, pouvoir in enumerate(pouvoirs, 1):
            print(f"\n{i}. Pouvoir:")
            role = pouvoir.get("roleEntreprise", "?")
            type_p = pouvoir.get("typeDePersonne", "?")
            actif = pouvoir.get("actif", False)

            print(f"   Role: {role}")
            print(f"   Type: {type_p}")
            print(f"   Actif: {actif}")

            # Si c'est une personne physique
            if type_p == "INDIVIDU" and "individu" in pouvoir:
                individu = pouvoir["individu"]
                desc = individu.get("descriptionPersonne", {})
                nom = desc.get("nom", "?")
                prenoms = desc.get("prenoms", [])

                print(f"   👤 Nom: {nom}")
                print(f"   👤 Prénoms: {' '.join(prenoms)}")

                # Le role 30 correspond souvent au président
                if role in ["30", "71"]:  # 30 = président, 71 = président SAS
                    print(f"   ⭐ PRÉSIDENT/DIRIGEANT POTENTIEL!")
else:
    print("❌ Aucune donnée trouvée")
