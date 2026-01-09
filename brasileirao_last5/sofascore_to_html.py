#!/usr/bin/env python3
"""
Gera um HTML formatado com os últimos 5 jogos do Flamengo no Brasileirão Betano e abre no Firefox.
Requer: sofascore_scraper.py no mesmo diretório.
"""
import subprocess
import webbrowser
from sofascore_scraper import scrape_sofascore_last5

def gerar_html(jogos):
    html = '''<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>Últimos 5 jogos do Flamengo - Brasileirão Betano</title>
    <style>
        body { font-family: Arial, sans-serif; background: #f7f7f7; }
        h1 { color: #d00; }
        table { border-collapse: collapse; margin: 20px auto; background: #fff; box-shadow: 0 2px 8px #0001; }
        th, td { padding: 10px 18px; border: 1px solid #ccc; text-align: center; }
        th { background: #d00; color: #fff; }
        tr:nth-child(even) { background: #f2f2f2; }
    </style>
</head>
<body>
    <h1>Últimos 5 jogos do Flamengo<br><small>Brasileirão Betano</small></h1>
    <table>
        <tr><th>Data</th><th>Mandante</th><th>Visitante</th><th>Placar</th></tr>
'''
    for m in jogos:
        data = m.get("utcDate") or "-"
        home = m.get("homeTeam", {}).get("name", "-")
        away = m.get("awayTeam", {}).get("name", "-")
        full = m.get("score", {}).get("fullTime", {})
        hg = full.get("homeTeam")
        ag = full.get("awayTeam")
        score = f"{hg} x {ag}" if hg is not None and ag is not None else "-"
        html += f"        <tr><td>{data}</td><td>{home}</td><td>{away}</td><td>{score}</td></tr>\n"
    html += "    </table>\n</body>\n</html>"
    return html

def main():
    jogos = scrape_sofascore_last5(debug=False)
    html = gerar_html(jogos)
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
