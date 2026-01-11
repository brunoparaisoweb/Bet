#!/usr/bin/env python3
"""
Busca confrontos H2H no SofaScore para os 4 times faltantes
"""

from playwright.sync_api import sync_playwright
import time

def buscar_h2h_sofascore(time1, time2):
    """Busca H2H no SofaScore"""
    print(f"\n{'='*60}")
    print(f"Buscando: {time1} vs {time2}")
    print('='*60)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        try:
            # Busca pelo time 1
            url_busca = f"https://www.sofascore.com/search?q={time1}"
            page.goto(url_busca, timeout=60000)
            time.sleep(3)
            
            # Clica no primeiro resultado (time)
            primeiro_time = page.query_selector('a[href*="/team/"]')
            if primeiro_time:
                primeiro_time.click()
                time.sleep(3)
                
                # Procura pela aba H2H ou similar
                print(f"✓ Página do {time1} carregada")
                print(f"  URL: {page.url}")
                
                # Busca por link/seção que mencione o time2
                conteudo = page.content()
                if time2.lower() in conteudo.lower():
                    print(f"✓ Menção a '{time2}' encontrada na página!")
                else:
                    print(f"✗ Nenhuma menção a '{time2}' encontrada")
                
                input("\n\nNavegue manualmente e pressione ENTER para continuar...")
                
        except Exception as e:
            print(f"Erro: {e}")
        finally:
            browser.close()

# Testa os 4 confrontos
confrontos = [
    ("Mirassol", "Vasco da Gama"),
    ("Coritiba", "Red Bull Bragantino"),
    ("Vitória", "Remo"),
    ("Chapecoense", "Santos")
]

for time1, time2 in confrontos:
    buscar_h2h_sofascore(time1, time2)
