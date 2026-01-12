#!/usr/bin/env python3
"""
Teste com debug ativado
"""
from sofascore_scraper_pl import scrape_sofascore_last5

print("=== TESTE COM DEBUG - Arsenal ===\n")

jogos = scrape_sofascore_last5(team_id=42, team_name="Arsenal", debug=True)

print(f"\n{'='*50}")
print(f"Total de jogos encontrados: {len(jogos)}")

if jogos:
    for i, jogo in enumerate(jogos, 1):
        home = jogo.get("homeTeam", {}).get("name", "?")
        away = jogo.get("awayTeam", {}).get("name", "?")
        score = jogo.get("score", {}).get("fullTime", {})
        hs = score.get("homeTeam", "?")
        aws = score.get("awayTeam", "?")
        print(f"{i}. {home} {hs} x {aws} {away}")
else:
    print("Nenhum jogo encontrado")
    print("\nVerifique o arquivo sofascore_pl_debug.html para ver o HTML da página")
