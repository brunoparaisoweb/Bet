"""Script para analisar o card Matches linha por linha"""
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto('https://www.sofascore.com/team/football/atletico-madrid/2836', timeout=30000)
    page.wait_for_timeout(3000)
    
    cards = page.query_selector_all('.card-component')
    for card in cards:
        text = card.inner_text()
        first_line = text.split('\n')[0] if text else ''
        if first_line in ['Matches', 'Partidas']:
            print('=== Card Matches ===')
            lines = text.split('\n')
            for i, line in enumerate(lines):
                print(f'{i:3d}: {repr(line)}')
            break
    
    browser.close()
