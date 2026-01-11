#!/usr/bin/env python3
"""
Inspeciona a estrutura da página do ogol.com.br
"""

from playwright.sync_api import sync_playwright
import time

url = "https://www.ogol.com.br/equipe/fluminense/historico-vs-equipes?fk_adv=2243"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    
    print(f"Acessando: {url}\n")
    page.goto(url, timeout=30000)
    time.sleep(5)
    
    # Extrai o HTML da página
    html = page.content()
    
    # Salva em arquivo para análise
    with open("ogol_page.html", "w", encoding="utf-8") as f:
        f.write(html)
    
    print("HTML salvo em ogol_page.html")
    
    # Procura por diferentes seletores
    print("\nProcurando elementos...")
    
    # Tabelas
    tabelas = page.query_selector_all('table')
    print(f"Tabelas encontradas: {len(tabelas)}")
    
    # Divs com class contendo "jogo", "partida", "match", "game"
    for termo in ["jogo", "partida", "match", "game", "resultado", "historico"]:
        elementos = page.query_selector_all(f'[class*="{termo}"]')
        print(f"Elementos com '{termo}' no class: {len(elementos)}")
    
    # Lista todos os elementos visíveis com texto
    print("\nPrimeiros 10 elementos com texto visível:")
    elementos_texto = page.query_selector_all('div, tr, li')
    count = 0
    for elem in elementos_texto:
        texto = elem.inner_text()
        if texto and len(texto) > 20 and len(texto) < 200:
            print(f"\n{count+1}. {texto[:100]}")
            count += 1
            if count >= 10:
                break
    
    print("\n\nMantendo navegador aberto por 30 segundos para inspeção manual...")
    time.sleep(30)
    
    browser.close()
