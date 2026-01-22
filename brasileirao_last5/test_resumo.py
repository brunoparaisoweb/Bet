#!/usr/bin/env python3
from sofascore_scraper_ligue1 import scrape_all_teams_sofascore

dados = scrape_all_teams_sofascore()
print('\n=== RESUMO DE JOGOS POR TIME ===')
for time, jogos in sorted(dados.items()):
    print(f'{time}: {len(jogos)} jogos')
    if len(jogos) > 0:
        for jogo in jogos:
            print(f"  - {jogo['data']}: {jogo['mandante']} {jogo['placar_mandante']}x{jogo['placar_visitante']} {jogo['visitante']}")
