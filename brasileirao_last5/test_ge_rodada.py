#!/usr/bin/env python3
from ge_scraper import scrape_primeira_rodada

jogos = scrape_primeira_rodada()
print(f'Total de jogos encontrados: {len(jogos)}')
for j in jogos:
    print(f"{j['data']} - {j['time1']} x {j['time2']}")
