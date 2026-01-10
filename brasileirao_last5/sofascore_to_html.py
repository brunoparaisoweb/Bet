#!/usr/bin/env python3
"""
Gera um HTML formatado com os últimos 5 jogos do Flamengo no Brasileirão Betano e abre no Firefox.
Requer: sofascore_scraper.py no mesmo diretório.
"""
import subprocess
import webbrowser
from sofascore_scraper import scrape_sofascore_last5
from ge_scraper import scrape_primeira_rodada

def gerar_html(times_jogos, jogos_rodada):
    html = '''<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>Últimos 5 jogos - Brasileirão Betano</title>
    <style>
        body { font-family: Arial, sans-serif; background: #f7f7f7; display: flex; }
        .sidebar { width: 250px; padding: 10px; background: #fff; box-shadow: 2px 0 8px #0001; }
        .main-content { flex: 1; padding: 10px; }
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
    
    html += "    </div>\n</body>\n</html>"
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
    html = gerar_html(times_jogos, jogos_rodada)
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
