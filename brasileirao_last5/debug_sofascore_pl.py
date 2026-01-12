#!/usr/bin/env python3
"""
Debug do SofaScore - verifica estrutura da página
"""
from playwright.sync_api import sync_playwright

team_id = 42
team_name = "Arsenal"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context(
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    )
    page = context.new_page()
    
    url = f"https://www.sofascore.com/pt/time/futebol/{team_name.lower()}/{team_id}"
    print(f"Acessando: {url}")
    
    page.goto(url, wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(5000)
    
    print("\nSalvando HTML...")
    with open("sofascore_pl_debug.html", "w", encoding="utf-8") as f:
        f.write(page.content())
    print("✓ HTML salvo em sofascore_pl_debug.html")
    
    print("\nProcurando por texto 'Premier League'...")
    if "Premier League" in page.content():
        print("✓ Encontrado 'Premier League' no HTML")
    else:
        print("✗ 'Premier League' não encontrado")
    
    print("\nProcurando elementos...")
    selectors = [
        '[class*="event"]',
        '[class*="match"]',
        '[class*="game"]',
        '[class*="fixture"]',
        'a[href*="/jogo/"]',
    ]
    
    for selector in selectors:
        elems = page.query_selector_all(selector)
        print(f"  {selector}: {len(elems)} elementos")
        if elems and len(elems) > 0:
            try:
                texto = elems[0].inner_text()
                print(f"    Primeiro elemento: {texto[:100] if texto else 'vazio'}")
            except:
                print(f"    Primeiro elemento: [erro ao pegar texto]")
    
    input("\nPressione Enter para fechar...")
    browser.close()
