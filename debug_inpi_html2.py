"""Debug détaillé de la structure INPI"""

import requests
from bs4 import BeautifulSoup

siren = "532321916"
url = f"https://data.inpi.fr/entreprises/{siren}"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

response = requests.get(url, headers=headers, timeout=30)

if response.status_code == 200:
    soup = BeautifulSoup(response.content, 'html.parser')

    # Regarder le contenu de notice-description
    print("=" * 80)
    print("CONTENU DE notice-description")
    print("=" * 80)

    notice = soup.find('div', id='notice-description')
    if notice:
        # Trouver tous les dl (definition lists)
        dls = notice.find_all('dl')
        print(f"\nNombre de <dl> trouvés: {len(dls)}\n")

        for idx, dl in enumerate(dls):
            print(f"\n--- DL #{idx} ---")
            # dt = terme, dd = définition
            dts = dl.find_all('dt')
            dds = dl.find_all('dd')

            for dt, dd in zip(dts, dds):
                label = dt.get_text().strip()
                value = dd.get_text().strip()
                print(f"{label}: {value}")

    # Regarder aussi les tableaux
    print("\n" + "=" * 80)
    print("TABLEAUX SUR LA PAGE")
    print("=" * 80)

    tables = soup.find_all('table')
    print(f"\nNombre de tableaux: {len(tables)}\n")

    for idx, table in enumerate(tables[:5]):
        print(f"\n--- TABLE #{idx} ---")
        rows = table.find_all('tr')
        for row in rows[:5]:
            cells = [cell.get_text().strip() for cell in row.find_all(['th', 'td'])]
            print(f"  {' | '.join(cells)}")

else:
    print(f"Erreur HTTP {response.status_code}")
