#!/usr/bin/env python3
"""
Gera um HTML formatado com os últimos 5 jogos do Flamengo no Brasileirão Betano e abre no Firefox.
Requer: sofascore_scraper.py no mesmo diretório.
"""
import subprocess
import webbrowser
from sofascore_scraper import scrape_sofascore_last5
from ge_scraper import scrape_primeira_rodada, scrape_classificacao

def calcular_pontos_credito(time_nome, jogos):
    """Calcula pontos de crédito baseado nos últimos jogos.
    Vitória como mandante = 0.75 pontos
    Vitória como visitante = 1.0 pontos
    Empate como mandante = 0.25 pontos
    Empate como visitante = 0.5 pontos
    Derrota como mandante = -1.0 pontos
    Derrota como visitante = -0.75 pontos
    """
    pontos = 0.0
    
    for jogo in jogos:
        home = jogo.get("homeTeam", {}).get("name", "")
        away = jogo.get("awayTeam", {}).get("name", "")
        full = jogo.get("score", {}).get("fullTime", {})
        hg = full.get("homeTeam")
        ag = full.get("awayTeam")
        
        if hg is not None and ag is not None:
            # Verifica se o time é mandante ou visitante
            time_mandante = time_nome.lower() in home.lower()
            
            if time_mandante:
                if hg > ag:
                    # Vitória como mandante
                    pontos += 0.75
                elif hg == ag:
                    # Empate como mandante
                    pontos += 0.25
                else:
                    # Derrota como mandante
                    pontos -= 1.0
            else:
                if ag > hg:
                    # Vitória como visitante
                    pontos += 1.0
                elif hg == ag:
                    # Empate como visitante
                    pontos += 0.5
                else:
                    # Derrota como visitante
                    pontos -= 0.75
    
    return pontos

def calcular_bonus_mandante(jogos_rodada):
    """Adiciona 0.5 pontos para times que jogam como mandante na próxima rodada."""
    # Mapeamento de abreviações para nomes completos
    abreviacoes = {
        "FLU": "Fluminense", "Fluminense": "Fluminense",
        "GRE": "Grêmio", "Grêmio": "Grêmio", "Gremio": "Grêmio",
        "BOT": "Botafogo", "Botafogo": "Botafogo",
        "CRU": "Cruzeiro", "Cruzeiro": "Cruzeiro",
        "SAO": "São Paulo", "São Paulo": "São Paulo", "Sao Paulo": "São Paulo",
        "FLA": "Flamengo", "Flamengo": "Flamengo",
        "COR": "Corinthians", "Corinthians": "Corinthians",
        "BAH": "Bahia", "Bahia": "Bahia",
        "MIR": "Mirassol", "Mirassol": "Mirassol",
        "VAS": "Vasco", "Vasco": "Vasco",
        "CAM": "Atlético-MG", "ATL": "Atlético-MG", "Atlético-MG": "Atlético-MG", 
        "Atletico-MG": "Atlético-MG", "Atlético MG": "Atlético-MG",
        "PAL": "Palmeiras", "Palmeiras": "Palmeiras",
        "INT": "Internacional", "Internacional": "Internacional",
        "CAP": "Athletico-PR", "Athletico-PR": "Athletico-PR", "Athletico PR": "Athletico-PR",
        "CFC": "Coritiba", "Coritiba": "Coritiba",
        "RBB": "Bragantino", "BRA": "Bragantino", "Bragantino": "Bragantino",
        "VIT": "Vitória", "Vitória": "Vitória", "Vitoria": "Vitória",
        "REM": "Remo", "Remo": "Remo",
        "CHA": "Chapecoense", "Chapecoense": "Chapecoense",
        "SAN": "Santos", "Santos": "Santos"
    }
    
    bonus = {}
    for jogo in jogos_rodada:
        time_mandante = jogo.get("time1", "").strip()
        if time_mandante:
            # Converte abreviação para nome completo
            nome_completo = abreviacoes.get(time_mandante, time_mandante)
            # Se ainda não encontrou, tenta normalizar
            if nome_completo == time_mandante:
                # Procura por match parcial (case-insensitive)
                for abrev, nome in abreviacoes.items():
                    if abrev.lower() in time_mandante.lower() or time_mandante.lower() in abrev.lower():
                        nome_completo = nome
                        break
            bonus[nome_completo] = bonus.get(nome_completo, 0) + 0.5
    return bonus

def calcular_bonus_classificacao(classificacao):
    """Adiciona pontos de crédito baseado na posição na classificação do campeonato."""
    bonus = {}
    
    for item in classificacao:
        time = item.get("time", "").strip()
        try:
            posicao = int(item.get("posicao", "0"))
        except ValueError:
            posicao = 0
        
        # Define pontos baseado na posição
        if posicao == 1:
            bonus[time] = 0.5
        elif posicao in [2, 3]:
            bonus[time] = 0.4
        elif posicao in [4, 5]:
            bonus[time] = 0.3
        elif posicao in [6, 7]:
            bonus[time] = 0.2
        elif posicao in [8, 9]:
            bonus[time] = 0.1
        elif posicao in [10, 11]:
            bonus[time] = 0.0
        elif posicao in [12, 13]:
            bonus[time] = -0.1
        elif posicao in [14, 15]:
            bonus[time] = -0.2
        elif posicao in [16, 17]:
            bonus[time] = -0.3
        elif posicao in [18, 19]:
            bonus[time] = -0.4
        elif posicao == 20:
            bonus[time] = -0.5
        else:
            bonus[time] = 0.0
    
    return bonus

def gerar_html(times_jogos, jogos_rodada, classificacao, pontos_credito):
    html = '''<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>Últimos 5 jogos - Brasileirão Betano</title>
    <style>
        body { font-family: Arial, sans-serif; background: #f7f7f7; display: flex; }
        .sidebar { width: 250px; padding: 15px; background: #fff; box-shadow: 2px 0 8px #0001; font-size: 0.9em; }
        .main-content { flex: 1; padding: 8px; display: flex; flex-wrap: wrap; justify-content: space-around; }
        .sidebar-right { width: 250px; padding: 15px; background: #fff; box-shadow: -2px 0 8px #0001; font-size: 0.9em; }
        .time-section { width: 18%; min-width: 180px; margin: 5px; }
        h1 { color: #333; text-align: center; font-size: 0.9em; margin: 5px 0; width: 100%; }
        h2 { color: #d00; text-align: center; margin: 8px 0 5px 0; font-size: 0.75em; }
        h3 { color: #333; font-size: 1.0em; margin: 12px 0; }
        table { border-collapse: collapse; margin: 5px auto; background: #fff; box-shadow: 0 1px 4px #0001; font-size: 0.65em; width: 100%; }
        th, td { padding: 3px 5px; border: 1px solid #ccc; text-align: center; font-size: 0.85em; }
        th { background: #87CEEB; color: #000; }
        .vitoria { background: #4CAF50 !important; color: #fff; }
        .derrota { background: #f44336 !important; color: #fff; }
        .empate { background: #9e9e9e !important; color: #fff; }
        .jogo-rodada { font-size: 0.85em; padding: 5px; border-bottom: 1px solid #eee; }
        .jogo-rodada:last-child { border-bottom: none; }
        .times-table { width: 100%; font-size: 0.85em; }
        .times-table td { text-align: left; padding: 5px 8px; }
        .times-table td:last-child { text-align: center; font-weight: bold; }
        .top3 { background: #FFD700 !important; }
        .negativo { background: #ff6b6b !important; color: #fff; }
    </style>
</head>
<body>
    <div class="sidebar">
        <h3>1ª Rodada - Brasileirão</h3>
'''
    
    for jogo in jogos_rodada:
        html += f'        <div class="jogo-rodada">{jogo["data"]} - {jogo["time1"]} x {jogo["time2"]}</div>\n'
    
    html += '''
        <h3 style="margin-top: 20px;">Classificação</h3>
        <table style="width: 100%; font-size: 0.75em;">
            <tr><th style="padding: 3px;">Pos</th><th>Time</th><th>Pts</th><th>J</th></tr>
'''
    
    for item in classificacao:
        pos = item.get("posicao", "")
        time = item.get("time", "")
        pts = item.get("pontos", "0")
        jogos = item.get("jogos", "0")
        html += f'            <tr><td style="text-align: center; padding: 2px;">{pos}</td><td style="text-align: left; padding: 2px;">{time}</td><td style="text-align: center; padding: 2px;">{pts}</td><td style="text-align: center; padding: 2px;">{jogos}</td></tr>\n'
    
    html += '''        </table>
    </div>
    <div class="main-content">
        <h1>Últimos 5 jogos<br><small>Brasileirão Betano</small></h1>
'''
    for time_nome, jogos in times_jogos:
        html += f'    <div class="time-section">\n'
        html += f'    <h2>{time_nome}</h2>\n'
        html += '    <table>\n'
        html += '        <tr><th>Data</th><th>Mandante</th><th>Visitante</th><th>Placar</th></tr>\n'
        
        for m in jogos:
            data = m.get("utcDate") or "-"
            home = m.get("homeTeam", {}).get("name", "-")
            away = m.get("awayTeam", {}).get("name", "-")
            full = m.get("score", {}).get("fullTime", {})
            hg = full.get("homeTeam")
            ag = full.get("awayTeam")
            score = f"{hg} x {ag}" if hg is not None and ag is not None else "-"
            
            # Determina o resultado do time
            classe = ""
            if hg is not None and ag is not None:
                # Verifica se o time é mandante ou visitante
                time_mandante = time_nome.lower() in home.lower()
                if time_mandante:
                    if hg > ag:
                        classe = "vitoria"
                    elif hg < ag:
                        classe = "derrota"
                    else:
                        classe = "empate"
                else:
                    if ag > hg:
                        classe = "vitoria"
                    elif ag < hg:
                        classe = "derrota"
                    else:
                        classe = "empate"
            
            html += f'        <tr class="{classe}"><td>{data}</td><td>{home}</td><td>{away}</td><td>{score}</td></tr>\n'
        html += "    </table>\n"
        html += "    </div>\n"
    
    html += '''    </div>
    <div class="sidebar-right">
        <h3>Times do Brasileirão</h3>
        <table class="times-table">
            <tr><th>Time</th><th>Pontos de Crédito</th></tr>
'''
    
    # Lista de todos os times
    todos_times = [
        "Flamengo", "Palmeiras", "São Paulo", "Corinthians", "Fluminense",
        "Grêmio", "Botafogo", "Atlético-MG", "Internacional", "Cruzeiro",
        "Athletico-PR", "Bahia", "Vasco", "Bragantino", "Vitória",
        "Mirassol", "Santos", "Remo", "Chapecoense", "Coritiba"
    ]
    
    # Cria lista de tuplas (time, pontos) e ordena por pontos (decrescente)
    times_com_pontos = [(time, pontos_credito.get(time, 0.0)) for time in todos_times]
    times_com_pontos.sort(key=lambda x: x[1], reverse=True)  # Ordem decrescente
    
    for i, (time, pontos) in enumerate(times_com_pontos):
        # Define classe CSS baseado na posição e pontuação
        classe = ""
        if i < 3:  # Top 3
            classe = "top3"
        elif pontos < 0:  # Pontuação negativa
            classe = "negativo"
        
        html += f'            <tr class="{classe}"><td>{time}</td><td>{pontos:.2f}</td></tr>\n'
    
    html += '''        </table>
    </div>
</body>
</html>
'''
    return html

def main():
    # Busca jogos da 1ª rodada
    print("Buscando jogos da 1ª rodada...")
    jogos_rodada = scrape_primeira_rodada()
    
    # Busca classificação atual
    print("Buscando classificação atual...")
    classificacao = scrape_classificacao()
    
    # Busca jogos do Flamengo
    print("Buscando jogos do Flamengo...")
    jogos_flamengo = scrape_sofascore_last5(team_id=5981, team_name="flamengo", debug=False)
    
    # Busca jogos do São Paulo
    print("Buscando jogos do São Paulo...")
    jogos_sao_paulo = scrape_sofascore_last5(team_id=1981, team_name="São Paulo", debug=False)
    
    # Busca jogos do Fluminense
    print("Buscando jogos do Fluminense...")
    jogos_fluminense = scrape_sofascore_last5(team_id=1961, team_name="Fluminense", debug=False, click_navigation=False)
    
    # Busca jogos do Grêmio
    print("Buscando jogos do Grêmio...")
    jogos_gremio = scrape_sofascore_last5(team_id=5926, team_name="Grêmio", debug=False)
    
    # Busca jogos do Botafogo
    print("Buscando jogos do Botafogo...")
    jogos_botafogo = scrape_sofascore_last5(team_id=1958, team_name="Botafogo", debug=False)
    
    # Busca jogos do Cruzeiro
    print("Buscando jogos do Cruzeiro...")
    jogos_cruzeiro = scrape_sofascore_last5(team_id=1954, team_name="Cruzeiro", debug=False)
    
    # Busca jogos do Corinthians
    print("Buscando jogos do Corinthians...")
    jogos_corinthians = scrape_sofascore_last5(team_id=1957, team_name="Corinthians", debug=False, click_navigation=True)
    
    # Busca jogos do Bahia
    print("Buscando jogos do Bahia...")
    jogos_bahia = scrape_sofascore_last5(team_id=1955, team_name="Bahia", debug=False)
    
    # Busca jogos do Vasco
    print("Buscando jogos do Vasco...")
    jogos_vasco = scrape_sofascore_last5(team_id=1974, team_name="Vasco", debug=False)
    
    # Busca jogos do Mirassol
    print("Buscando jogos do Mirassol...")
    jogos_mirassol = scrape_sofascore_last5(team_id=21982, team_name="Mirassol", debug=False)
    
    # Busca jogos do Palmeiras
    print("Buscando jogos do Palmeiras...")
    jogos_palmeiras = scrape_sofascore_last5(team_id=1963, team_name="Palmeiras", debug=False)
    
    # Busca jogos do Atlético-MG
    print("Buscando jogos do Atlético-MG...")
    jogos_atletico_mg = scrape_sofascore_last5(team_id=1977, team_name="Atlético-MG", debug=False)
    
    # Gera HTML com ambos os times
    times_jogos = [
        ("Flamengo", jogos_flamengo),
        ("São Paulo", jogos_sao_paulo),
        ("Fluminense", jogos_fluminense),
        ("Grêmio", jogos_gremio),
        ("Botafogo", jogos_botafogo),
        ("Cruzeiro", jogos_cruzeiro),
        ("Corinthians", jogos_corinthians),
        ("Bahia", jogos_bahia),
        ("Vasco", jogos_vasco),
        ("Mirassol", jogos_mirassol),
        ("Palmeiras", jogos_palmeiras),
        ("Atlético-MG", jogos_atletico_mg)
    ]
    
    # Calcula pontos de crédito
    pontos_credito = {
        "Flamengo": calcular_pontos_credito("Flamengo", jogos_flamengo),
        "São Paulo": calcular_pontos_credito("São Paulo", jogos_sao_paulo),
        "Fluminense": calcular_pontos_credito("Fluminense", jogos_fluminense),
        "Grêmio": calcular_pontos_credito("Grêmio", jogos_gremio),
        "Botafogo": calcular_pontos_credito("Botafogo", jogos_botafogo),
        "Cruzeiro": calcular_pontos_credito("Cruzeiro", jogos_cruzeiro),
        "Corinthians": calcular_pontos_credito("Corinthians", jogos_corinthians),
        "Bahia": calcular_pontos_credito("Bahia", jogos_bahia),
        "Vasco": calcular_pontos_credito("Vasco", jogos_vasco),
        "Mirassol": calcular_pontos_credito("Mirassol", jogos_mirassol),
        "Palmeiras": calcular_pontos_credito("Palmeiras", jogos_palmeiras),
        "Atlético-MG": calcular_pontos_credito("Atlético-MG", jogos_atletico_mg)
    }
    
    # Adiciona bônus de 0.5 pontos para times mandantes na próxima rodada
    bonus_mandante = calcular_bonus_mandante(jogos_rodada)
    for time, bonus in bonus_mandante.items():
        if time in pontos_credito:
            pontos_credito[time] += bonus
        else:
            pontos_credito[time] = bonus
    
    # Adiciona bônus/penalidade baseado na posição na classificação
    bonus_classificacao = calcular_bonus_classificacao(classificacao)
    for time, bonus in bonus_classificacao.items():
        if time in pontos_credito:
            pontos_credito[time] += bonus
        else:
            pontos_credito[time] = bonus
    
    html = gerar_html(times_jogos, jogos_rodada, classificacao, pontos_credito)
    fname = "sofascore_result.html"
    with open(fname, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Arquivo gerado: {fname}")
    # Tenta abrir no Firefox
    try:
        subprocess.Popen(["firefox", fname])
    except Exception:
        webbrowser.open_new_tab(fname)

if __name__ == "__main__":
    main()
