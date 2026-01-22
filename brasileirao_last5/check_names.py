#!/usr/bin/env python3
from sofascore_scraper_ligue1 import scrape_sofascore_last5

jogos = scrape_sofascore_last5(1659, 'Strasbourg')
print('Nomes dos times nos jogos do Strasbourg:')
for j in jogos:
    print(f"  Mandante: '{j['mandante']}', Visitante: '{j['visitante']}'")
