#!/usr/bin/env python3
"""
Descobre IDs dos times no ogol.com.br
"""

from playwright.sync_api import sync_playwright
import time
import re

times_slugs = {
    "Bahia": "bahia",
    "Mirassol": "mirassol",
    "Bragantino": "red-bull-bragantino",
    "Remo": "clube-do-remo"
}

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context(
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    )
    page = context.new_page()
    
    ids_encontrados = {}
    
    for time, slug in times_slugs.items():
        url = f"https://www.ogol.com.br/equipe/{slug}/"
        print(f"\n{time}: Acessando {url}")
        
        try:
            page.goto(url, timeout=60000, wait_until="domcontentloaded")
            time.sleep(3)
            
            # Procura por links que contenham "historico-vs-equipes?fk_adv="
            # O link de algum adversário terá esse padrão
            links = page.query_selector_all('a[href*="historico-vs-equipes"]')
            
            if links:
                # Pega o primeiro link e extrai o padrão da URL
                primeiro_link = links[0].get_attribute('href')
                print(f"  Link exemplo: {primeiro_link}")
                
                # A URL do próprio time deve estar em algum lugar
                # Vamos procurar pela URL da página atual
                url_atual = page.url
                print(f"  URL atual: {url_atual}")
                
                # Procura por IDs na URL ou no HTML
                # O ID pode estar em algo como: /equipe/bahia/XXXX
                match = re.search(r'/equipe/[^/]+/(\d+)', url_atual)
                if match:
                    id_encontrado = match.group(1)
                    print(f"  ✓ ID encontrado: {id_encontrado}")
                    ids_encontrados[time] = id_encontrado
                else:
                    # Tenta encontrar em meta tags ou dados da página
                    html = page.content()
                    # Procura por padrões como "fk_eq=XXXX" ou similares
                    matches = re.findall(r'fk_eq[=:](\d+)', html)
                    if matches:
                        id_encontrado = matches[0]
                        print(f"  ✓ ID encontrado no HTML: {id_encontrado}")
                        ids_encontrados[time] = id_encontrado
                    else:
                        print(f"  ✗ ID não encontrado")
            else:
                print(f"  ✗ Links não encontrados")
                
        except Exception as e:
            print(f"  ✗ Erro: {e}")
    
    print("\n" + "="*80)
    print("IDs ENCONTRADOS:")
    print("="*80)
    for time, id_time in ids_encontrados.items():
        print(f'    "{time}": {id_time},')
    
    time.sleep(5)
    browser.close()
