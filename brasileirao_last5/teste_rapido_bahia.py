#!/usr/bin/env python3
"""Testa rapidamente vários IDs para Bahia"""

from playwright.sync_api import sync_playwright
import time

# IDs para testar
ids_teste = [2249, 2250, 2253, 2259, 2260]

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(user_agent='Mozilla/5.0...')
    page = context.new_page()
    
    for id_teste in ids_teste:
        url = f"https://www.ogol.com.br/equipe/corinthians/historico-vs-equipes?fk_adv={id_teste}"
        print(f"\nTestando ID {id_teste}:")
        
        try:
            page.goto(url, timeout=15000, wait_until="domcontentloaded")
            time.sleep(2)
            
            # Extrai os primeiros jogos
            js = """
            () => {
                const linhas = document.querySelectorAll('tr');
                for (const linha of linhas) {
                    const texto = linha.innerText || '';
                    if (texto.match(/\\d{4}-\\d{2}-\\d{2}/)) {
                        return texto.substring(0, 100);
                    }
                }
                return '';
            }
            """
            primeiro_jogo = page.evaluate(js)
            
            if "Bahia" in primeiro_jogo:
                print(f"  ✓✓✓ BAHIA ENCONTRADO! ID = {id_teste}")
                print(f"  Jogo: {primeiro_jogo}")
                break
            elif primeiro_jogo:
                # Extrai o nome do time do jogo
                partes = primeiro_jogo.split()
                if len(partes) > 3:
                    print(f"  Time: {partes[2] if partes[2] != 'Corinthians' else partes[3]}")
            else:
                print(f"  Sem jogos")
        except Exception as e:
            print(f"  Erro: {e}")
    
    browser.close()
