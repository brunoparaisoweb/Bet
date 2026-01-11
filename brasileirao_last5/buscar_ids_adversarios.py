#!/usr/bin/env python3
"""
Busca os IDs dos times adversários na página de histórico
"""

from playwright.sync_api import sync_playwright
import time
import re

def buscar_id_adversario(slug_time1, nome_time2):
    """Busca o ID de um time adversário na lista"""
    url = f"https://www.ogol.com.br/equipe/{slug_time1}/historico-vs-equipes"
    print(f"\n{'='*80}")
    print(f"Buscando {nome_time2} na página de {slug_time1}")
    print(f"URL: {url}")
    print('='*80)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        page = context.new_page()
        
        try:
            page.goto(url, timeout=60000, wait_until="domcontentloaded")
            time.sleep(5)
            
            # Extrai todos os links da página
            links = page.evaluate("""
                () => {
                    const allLinks = Array.from(document.querySelectorAll('a'));
                    return allLinks.map(link => ({
                        href: link.href,
                        text: link.innerText.trim()
                    })).filter(l => l.href && l.href.includes('fk_adv'));
                }
            """)
            
            print(f"\nLinks com fk_adv encontrados: {len(links)}")
            
            # Procura pelo time específico
            nome_lower = nome_time2.lower()
            for link in links:
                if nome_lower in link['text'].lower():
                    match = re.search(r'fk_adv=(\d+)', link['href'])
                    if match:
                        id_encontrado = match.group(1)
                        print(f"\n✓✓✓ {nome_time2} ENCONTRADO ✓✓✓")
                        print(f"  Texto: {link['text']}")
                        print(f"  ID: {id_encontrado}")
                        print(f"  URL: {link['href']}")
                        return id_encontrado
            
            print(f"\n❌ {nome_time2} NÃO encontrado")
            print("\nPrimeiros 10 times disponíveis:")
            for link in links[:10]:
                match = re.search(r'fk_adv=(\d+)', link['href'])
                if match:
                    print(f"  - {link['text']}: {match.group(1)}")
            
        except Exception as e:
            print(f"❌ Erro: {e}")
        finally:
            browser.close()
    
    return None

# Busca cada par de times
print("\n" + "="*80)
print("BUSCANDO IDS DOS ADVERSÁRIOS")
print("="*80)

resultados = {}

# Mirassol vs Vasco
id_vasco = buscar_id_adversario("mirassol", "Vasco")
if id_vasco:
    resultados["Vasco (vs Mirassol)"] = id_vasco

# Coritiba vs Bragantino
id_bragantino = buscar_id_adversario("coritiba", "Bragantino")
if id_bragantino:
    resultados["Bragantino (vs Coritiba)"] = id_bragantino

# Vitória vs Remo  
id_remo = buscar_id_adversario("vitoria", "Remo")
if id_remo:
    resultados["Remo (vs Vitória)"] = id_remo

# Chapecoense vs Santos
id_santos = buscar_id_adversario("chapecoense", "Santos")
if id_santos:
    resultados["Santos (vs Chapecoense)"] = id_santos

print("\n" + "="*80)
print("RESUMO DOS IDS ENCONTRADOS")
print("="*80)
for time, id_time in resultados.items():
    print(f"{time}: {id_time}")
