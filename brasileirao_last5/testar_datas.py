abreviacoes_br = {
    'CAM': 'Athletico-PR', 'PAL': 'Palmeiras', 'INT': 'Internacional',
    'CAP': 'Athlético-PR', 'CFC': 'Coritiba', 'RBB': 'RB Bragantino',
    'VIT': 'Vitória', 'REM': 'Remo', 'FLU': 'Fluminense',
    'GRE': 'Grêmio', 'COR': 'Corinthians', 'BAH': 'Bahia',
    'CHA': 'Chapecoense', 'SAN': 'Santos', 'SAO': 'São Paulo',
    'FLA': 'Flamengo', 'MIR': 'Mirassol', 'VAS': 'Vasco',
    'BOT': 'Botafogo', 'CRU': 'Cruzeiro', 'ATL': 'Atlético-MG'
}

jogos = ['CAM x PAL', 'INT x CAP', 'CFC x RBB', 'VIT x REM', 'FLU x GRE', 
         'COR x BAH', 'CHA x SAN', 'SAO x FLA', 'MIR x VAS', 'BOT x CRU']

print("Jogos da rodada expandidos:")
for jogo in jogos:
    times = jogo.split(' x ')
    time1 = abreviacoes_br.get(times[0].strip(), times[0])
    time2 = abreviacoes_br.get(times[1].strip(), times[1])
    confronto_expandido = f"{time1} x {time2}"
    print(f"{jogo} -> {confronto_expandido}")

print("\nBETs esperadas:")
bets_esperadas = [
    "mirassol x vasco",
    "palmeiras x atlético-mg",
    "santos x chapecoense",
    "fluminense x grêmio",
    "vitória x remo",
    "flamengo x são paulo"
]
for bet in bets_esperadas:
    print(bet)
