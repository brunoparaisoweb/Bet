#!/usr/bin/env python3
"""
Debug - salva HTML da página do GE Premier League
"""
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    
    print("Acessando página...")
    page.goto("https://ge.globo.com/futebol/futebol-internacional/futebol-ingles/", wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(5000)
    
    print("Salvando HTML...")
    with open("ge_pl_debug.html", "w", encoding="utf-8") as f:
        f.write(page.content())
    
    print("✓ HTML salvo em ge_pl_debug.html")
    print("\nProcurando elementos...")
    
    # Tenta encontrar diferentes seletores
    selectors = [
        ".proximos-jogos__lista",
        ".proximos-jogos__item",
        ".tabela-times",
        "[class*='proximos']",
        "[class*='tabela']",
        ".jogo",
        ".partida"
    ]
    
    for selector in selectors:
        elems = page.query_selector_all(selector)
        if elems:
            print(f"✓ Encontrado {len(elems)} elementos com seletor: {selector}")
        else:
            print(f"✗ Nenhum elemento encontrado com seletor: {selector}")
    
    input("\nPressione Enter para fechar o navegador...")
    browser.close()
