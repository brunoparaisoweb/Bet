#!/usr/bin/env python3
"""
Teste do SofaScore scraper para Premier League
Verifica se conseguimos buscar os últimos 5 jogos de alguns times
"""
from sofascore_scraper_pl import scrape_sofascore_last5, PREMIER_LEAGUE_TEAM_IDS

print("=== TESTANDO SOFASCORE - PREMIER LEAGUE ===\n")

# Testa com 3 times principais
times_teste = [
    ("Arsenal", 42),
    ("Manchester City", 17),
    ("Liverpool", 44)
]

total_sucesso = 0
total_falhas = 0

for nome, team_id in times_teste:
    print(f"\n--- {nome} (ID: {team_id}) ---")
    try:
        jogos = scrape_sofascore_last5(team_id, nome, debug=False)
        
        if jogos and len(jogos) > 0:
            print(f"✓ Encontrados {len(jogos)} jogos da Premier League")
            total_sucesso += 1
            
            # Mostra os jogos encontrados
            for i, jogo in enumerate(jogos, 1):
                home = jogo.get("homeTeam", {}).get("name", "?")
                away = jogo.get("awayTeam", {}).get("name", "?")
                score = jogo.get("score", {}).get("fullTime", {})
                hs = score.get("homeTeam", "?")
                aws = score.get("awayTeam", "?")
                data = jogo.get("startDate", "")
                print(f"  {i}. {data} - {home} {hs} x {aws} {away}")
        else:
            print(f"✗ Nenhum jogo encontrado")
            total_falhas += 1
            
    except Exception as e:
        print(f"✗ Erro: {e}")
        total_falhas += 1

print(f"\n{'='*50}")
print(f"RESULTADO: {total_sucesso} sucessos, {total_falhas} falhas")

if total_sucesso == len(times_teste):
    print("✓ Todos os testes passaram! SofaScore funcionando.")
elif total_sucesso > 0:
    print("⚠ Alguns testes falharam. Pode precisar de ajustes.")
else:
    print("✗ Todos os testes falharam. Scraper precisa ser revisado.")
