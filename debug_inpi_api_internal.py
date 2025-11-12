"""Analyser les requêtes réseau de data.inpi.fr pour trouver l'API interne"""

from playwright.sync_api import sync_playwright
import json

siren = "532321916"
url = f"https://data.inpi.fr/entreprises/{siren}"

print("=" * 80)
print("ANALYSE DES REQUÊTES RÉSEAU")
print("=" * 80)

api_calls = []

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    # Intercepter toutes les requêtes réseau
    def handle_request(request):
        if 'api' in request.url.lower() or 'json' in request.url.lower():
            api_calls.append({
                'url': request.url,
                'method': request.method,
                'headers': dict(request.headers)
            })
            print(f"\n📡 API Call: {request.method} {request.url}")

    def handle_response(response):
        if 'api' in response.url.lower() or 'json' in response.url.lower():
            print(f"   ✅ Status: {response.status}")
            if response.status == 200:
                try:
                    # Essayer de lire le JSON
                    content_type = response.headers.get('content-type', '')
                    if 'json' in content_type:
                        data = response.json()
                        print(f"   📦 JSON Keys: {list(data.keys()) if isinstance(data, dict) else 'array'}")
                except:
                    pass

    page.on('request', handle_request)
    page.on('response', handle_response)

    print(f"\n🌐 Navigation vers {url}...")
    page.goto(url, wait_until="networkidle", timeout=60000)

    print("\n\n" + "=" * 80)
    print("RÉSUMÉ DES APPELS API")
    print("=" * 80)

    for idx, call in enumerate(api_calls):
        print(f"\n{idx + 1}. {call['method']} {call['url']}")

    browser.close()

print("\n" + "=" * 80)
