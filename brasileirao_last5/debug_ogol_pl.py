#!/usr/bin/env python3
"""
Debug do ogol.com.br para verificar estrutura HTML
"""
from playwright.sync_api import sync_playwright

url = "https://www.ogol.com.br/equipe/arsenal/75/historico-vs-equipes?fk_adv=85"

print(f"Abrindo: {url}")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)  # Visível
    page = browser.new_page()
    
    page.goto(url, wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(5000)
    
    # Salva HTML
    with open("ogol_pl_debug.html", "w", encoding="utf-8") as f:
        f.write(page.content())
    print("HTML salvo em: ogol_pl_debug.html")
    
    # Verifica diferentes seletores de tabela
    seletores = [
        "table.jogos tbody tr",
        "table tbody tr",
        ".jogos tbody tr",
        "tbody tr",
        "table tr"
    ]
    
    for seletor in seletores:
        elementos = page.query_selector_all(seletor)
        print(f"{seletor}: {len(elementos)} elementos")
    
    # Aguarda para inspeção manual
    print("\nPágina aberta. Pressione Enter para fechar...")
    input()
    
    browser.close()
