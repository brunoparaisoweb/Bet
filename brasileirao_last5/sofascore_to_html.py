#!/usr/bin/env python3
"""
Gera um HTML formatado com os últimos 5 jogos do Flamengo no Brasileirão Betano e abre no Firefox.
Requer: sofascore_scraper.py no mesmo diretório.
"""
import subprocess
import webbrowser
from sofascore_scraper import scrape_sofascore_last5
from ge_scraper import scrape_primeira_rodada

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

def gerar_html(times_jogos, jogos_rodada, pontos_credito):
    html = '''<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>Últimos 5 jogos - Brasileirão Betano</title>
    <style>
        body { font-family: Arial, sans-serif; background: #f7f7f7; display: flex; }
        .sidebar { width: 250px; padding: 10px; background: #fff; box-shadow: 2px 0 8px #0001; }
        .main-content { flex: 1; padding: 10px; }
        .sidebar-right { width: 250px; padding: 10px; background: #fff; box-shadow: -2px 0 8px #0001; }
        h1 { color: #333; text-align: center; font-size: 1.2em; }
        h2 { color: #d00; text-align: center; margin-top: 20px; font-size: 1em; }
        h3 { color: #333; font-size: 0.9em; margin: 10px 0; }
        table { border-collapse: collapse; margin: 10px auto; background: #fff; box-shadow: 0 2px 8px #0001; font-size: 0.8em; }
        th, td { padding: 5px 9px; border: 1px solid #ccc; text-align: center; }
        th { background: #87CEEB; color: #000; }
        .vitoria { background: #4CAF50 !important; color: #fff; }
        .derrota { background: #f44336 !important; color: #fff; }
        .empate { background: #9e9e9e !important; color: #fff; }
        .jogo-rodada { font-size: 0.75em; padding: 5px; border-bottom: 1px solid #eee; }
        .jogo-rodada:last-child { border-bottom: none; }
        .times-table { width: 100%; font-size: 0.75em; }
        .times-table td { text-align: left; padding: 4px 6px; }
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
    
    html += '''    </div>
    <div class="main-content">
        <h1>Últimos 5 jogos<br><small>Brasileirão Betano</small></h1>
'''
    for time_nome, jogos in times_jogos:
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
    
    # Busca jogos do Flamengo
    print("Buscando jogos do Flamengo...")
    jogos_flamengo = scrape_sofascore_last5(team_id=5981, team_name="flamengo", debug=False)
    
    # Busca jogos do São Paulo
    print("Buscando jogos do São Paulo...")
    jogos_sao_paulo = scrape_sofascore_last5(team_id=1981, team_name="São Paulo", debug=True)
    
    # Gera HTML com ambos os times
    times_jogos = [
        ("Flamengo", jogos_flamengo),
        ("São Paulo", jogos_sao_paulo)
    ]
    
    # Calcula pontos de crédito
    pontos_credito = {
        "Flamengo": calcular_pontos_credito("Flamengo", jogos_flamengo),
        "São Paulo": calcular_pontos_credito("São Paulo", jogos_sao_paulo)
    }
    
    html = gerar_html(times_jogos, jogos_rodada, pontos_credito)
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
