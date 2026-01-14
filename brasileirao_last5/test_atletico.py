from sofascore_scraper_laliga import scrape_sofascore_last5

jogos = scrape_sofascore_last5(2836, 'Atletico Madrid', debug=True)

print('\n=== ÚLTIMOS 5 JOGOS DO ATLÉTICO MADRID ===')
for i, jogo in enumerate(jogos[:5], 1):
    home = jogo.get("homeTeam", {}).get("name", "")
    away = jogo.get("awayTeam", {}).get("name", "")
    score = jogo.get("score", {}).get("fullTime", {})
    home_score = score.get("homeTeam", 0)
    away_score = score.get("awayTeam", 0)
    date = jogo.get("startDate", "")
    
    print(f'{i}. {home} {home_score}-{away_score} {away} | {date}')
