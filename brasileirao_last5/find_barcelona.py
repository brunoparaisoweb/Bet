"""Script para encontrar o jogo Barcelona 3x1 na página do Atlético Madrid"""
from playwright.sync_api import sync_playwright
import re

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto('https://www.sofascore.com/team/football/atletico-madrid/2836', timeout=30000)
    page.wait_for_timeout(3000)
    
    print("=== Navegando para jogos anteriores no Card Matches ===")
    
    # Pega todos os cards
    cards = page.query_selector_all('.card-component')
    
    # Card 2 é o "Matches"
    if len(cards) > 2:
        for click in range(15):
            cards = page.query_selector_all('.card-component')
            card2 = cards[2]
            card_text = card2.inner_text()
            
            # Verificar se Barcelona aparece
            if 'Barcelona' in card_text and '3' in card_text:
                print(f"\n=== ENCONTROU BARCELONA no clique {click}! ===")
                # Mostrar contexto do jogo
                lines = card_text.split('\n')
                for i, line in enumerate(lines):
                    if 'Barcelona' in line:
                        context = lines[max(0,i-5):i+10]
                        print('\n'.join(context))
                        break
                break
            else:
                # Mostrar progresso
                # Encontrar ultimo jogo visível
                all_dates = re.findall(r'(\d{2}/\d{2}/\d{2})', card_text)
                last_date = all_dates[-1] if all_dates else "???"
                print(f"Clique {click}: último jogo = {last_date}")
            
            # Clicar no botão 0 (seta esquerda - jogos anteriores)
            nav_buttons = card2.query_selector_all('button')
            if len(nav_buttons) >= 1:
                nav_buttons[0].click()
                page.wait_for_timeout(1500)
    
    browser.close()
