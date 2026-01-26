#!/usr/bin/env python3
"""
Gera um HTML formatado com os últimos 5 jogos do Flamengo no Brasileirão Betano e abre no Firefox.
Requer: sofascore_scraper.py no mesmo diretório.
"""
import subprocess
import webbrowser
import json
import os
from sofascore_scraper import scrape_sofascore_last5
# from ge_scraper import scrape_primeira_rodada, scrape_classificacao
from ogol_scraper import scrape_h2h_ogol
from sofascore_team_ids import get_team_logo_html

# Horários fixos da rodada 1 do Brasileirão 2026
HORARIOS_RODADA_1 = {
    "Atlético-MG x Palmeiras": "19:00",
    "Internacional x Athletico-PR": "19:00",
    "Coritiba x RB Bragantino": "19:00",
    "Vitória x Remo": "19:00",
    "Fluminense x Grêmio": "19:30",
    "Corinthians x Bahia": "20:00",
    "Chapecoense x Santos": "20:00",
    "São Paulo x Flamengo": "21:30",
    "Mirassol x Vasco": "20:00",
    "Botafogo x Cruzeiro": "21:30"
}

def scrape_primeira_rodada():
    """Retorna os jogos da 1ª rodada do Brasileirão com horários"""
    jogos = [
        {"data": "28/01", "hora": "19:00", "time1": "Atlético-MG", "time2": "Palmeiras"},
        {"data": "28/01", "hora": "19:00", "time1": "Internacional", "time2": "Athletico-PR"},
        {"data": "28/01", "hora": "19:00", "time1": "Coritiba", "time2": "RB Bragantino"},
        {"data": "28/01", "hora": "19:00", "time1": "Vitória", "time2": "Remo"},
        {"data": "28/01", "hora": "19:30", "time1": "Fluminense", "time2": "Grêmio"},
        {"data": "28/01", "hora": "20:00", "time1": "Corinthians", "time2": "Bahia"},
        {"data": "28/01", "hora": "20:00", "time1": "Chapecoense", "time2": "Santos"},
        {"data": "28/01", "hora": "21:30", "time1": "São Paulo", "time2": "Flamengo"},
        {"data": "29/01", "hora": "20:00", "time1": "Mirassol", "time2": "Vasco"},
        {"data": "29/01", "hora": "21:30", "time1": "Botafogo", "time2": "Cruzeiro"}
    ]
    return jogos

def scrape_classificacao():
    """Retorna a classificação atual do Brasileirão"""
    times_brasileirao = [
        "Flamengo", "Palmeiras", "São Paulo", "Corinthians", "Fluminense",
        "Grêmio", "Botafogo", "Atlético-MG", "Internacional", "Cruzeiro",
        "Athletico-PR", "Bahia", "Vasco", "Bragantino", "Vitória",
        "Mirassol", "Santos", "Remo", "Chapecoense", "Coritiba"
    ]
    
    classificacao = []
    for i, time in enumerate(times_brasileirao, 1):
        classificacao.append({
            "posicao": str(i),
            "time": time,
            "pontos": "0",
            "jogos": "0"
        })
    
    return classificacao

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

def normalizar_nome_brasileiro(nome):
    """
    Normaliza nomes de times brasileiros para formato padrão (corrige encoding)
    Mapeia diretamente nomes com encoding problemático para os nomes corretos
    """
    # Mapeamento direto de todos os possíveis nomes problemáticos
    mapeamento_direto = {
        # Atlético-MG variações
        "AtlÚtico-MG": "Atlético-MG",
        "Atl‚tico-MG": "Atlético-MG",
        "Atletico-MG": "Atlético-MG",
        # São Paulo variações
        "SÒo Paulo": "São Paulo",
        "S®o Paulo": "São Paulo",
        "Sao Paulo": "São Paulo",
        # Grêmio variações
        "GrÛmio": "Grêmio",
        "Gr‰mio": "Grêmio",
        "Gremio": "Grêmio",
        # Vitória variações
        "Vit¾ria": "Vitória",
        "Vit¢ria": "Vitória",
        "Vitoria": "Vitória"
    }
    
    return mapeamento_direto.get(nome, nome)

def extrair_h2h_confronto_direto(time_mandante, time_visitante, debug=False):
    """
    Extrai os últimos 5 jogos entre dois times específicos (confronto direto).
    Retorna lista de resultados do ponto de vista do time mandante:
    'V' (vitória), 'E' (empate), 'D' (derrota)
    """
    resultados = []
    
    # Busca confrontos diretos no ogol.com.br
    jogos_h2h = scrape_h2h_ogol(time_mandante, time_visitante, debug=debug)
    
    for jogo in jogos_h2h[:5]:  # Até 5 jogos
        # O resultado vem no campo "texto", exemplo: "V 2025-11-05 São Paulo 2-2 Flamengo..."
        texto = jogo.get("texto", "").strip()
        
        # O primeiro caractere do texto é o resultado (V, E ou D)
        if len(texto) > 0:
            resultado = texto[0].upper()
            
            if resultado in ['V', 'E', 'D']:
                resultados.append(resultado)
            else:
                resultados.append('-')
        else:
            resultados.append('-')
    
    # Preenche com '-' se não tiver 5 jogos
    while len(resultados) < 5:
        resultados.append('-')
    
    return resultados[:5]

def calcular_pontos_h2h(resultados):
    """
    Calcula pontos H2H baseado nos últimos 5 jogos.
    V = +0.2 (casa) ou +0.1 (fora)
    E = 0.0 (casa) ou +0.1 (fora)
    D = -0.2 (casa) ou -0.1 (fora)
    """
    pontos = 0.0
    jogos_validos = 0
    
    for res in resultados:
        if res == 'V':
            pontos += 0.2  # Vitória (simplificado, sem distinguir casa/fora)
            jogos_validos += 1
        elif res == 'E':
            pontos += 0.05  # Empate (média entre casa e fora)
            jogos_validos += 1
        elif res == 'D':
            pontos -= 0.15  # Derrota (média entre casa e fora)
            jogos_validos += 1
    
    return round(pontos, 1)

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

def analisar_apostas(jogos_rodada, pontos_credito):
    """Analisa os confrontos da rodada e retorna apostas sugeridas.
    Retorna lista de times recomendados quando a diferença de créditos é >= 2.
    """
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
    
    apostas = []
    
    for jogo in jogos_rodada:
        time1_orig = jogo.get("time1", "").strip()
        time2_orig = jogo.get("time2", "").strip()
        
        if not time1_orig or not time2_orig:
            continue
        
        # Normaliza nomes dos times
        time1 = abreviacoes.get(time1_orig, time1_orig)
        time2 = abreviacoes.get(time2_orig, time2_orig)
        
        # Se ainda não encontrou, tenta normalizar
        if time1 == time1_orig:
            for abrev, nome in abreviacoes.items():
                if abrev.lower() in time1_orig.lower() or time1_orig.lower() in abrev.lower():
                    time1 = nome
                    break
        
        if time2 == time2_orig:
            for abrev, nome in abreviacoes.items():
                if abrev.lower() in time2_orig.lower() or time2_orig.lower() in abrev.lower():
                    time2 = nome
                    break
        
        # Pega os pontos de crédito
        pontos_time1 = pontos_credito.get(time1, 0.0)
        pontos_time2 = pontos_credito.get(time2, 0.0)
        
        # Calcula a diferença
        diferenca = abs(pontos_time1 - pontos_time2)
        
        # Se a diferença for >= 2 e o favorito tiver pontuação > 0, adiciona o time com maior pontuação
        if diferenca >= 2.0:
            if pontos_time1 > pontos_time2 and pontos_time1 > 0:
                apostas.append({
                    "time": time1,
                    "adversario": time2,
                    "pontos": pontos_time1,
                    "pontos_adv": pontos_time2,
                    "diferenca": diferenca
                })
            elif pontos_time2 > pontos_time1 and pontos_time2 > 0:
                apostas.append({
                    "time": time2,
                    "adversario": time1,
                    "pontos": pontos_time2,
                    "pontos_adv": pontos_time1,
                    "diferenca": diferenca
                })
    
    # Ordena por diferença (maior primeiro)
    apostas.sort(key=lambda x: x["diferenca"], reverse=True)
    
    return apostas

def gerar_html(times_jogos, jogos_rodada, classificacao, pontos_credito, resultados_h2h=None, apostas=None):
    html = '''<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>Brasileirão Betano</title>
    <style>
        body { font-family: Arial, sans-serif; background: #f7f7f7; display: flex; margin: 0; padding: 0 0 20px 0; }
        .sidebar { width: 220px; padding: 10px; background: #fff; box-shadow: 2px 0 8px #0001; font-size: 0.75em; }
        .main-content { flex: 1; padding: 8px; display: flex; flex-wrap: wrap; justify-content: space-around; }
        .sidebar-right { width: 250px; padding: 15px; background: #fff; box-shadow: -2px 0 8px #0001; font-size: 0.9em; }
        .time-section { width: 18%; min-width: 180px; margin: 5px; }
        h1 { color: #333; text-align: center; font-size: 0.9em; margin: 5px 0; width: 100%; }
        h2 { color: #d00; text-align: center; margin: 8px 0 5px 0; font-size: 0.75em; }
        h3 { color: #333; font-size: 0.9em; margin: 8px 0 4px 0; }
        table { border-collapse: collapse; margin: 5px auto; background: #fff; box-shadow: 0 1px 4px #0001; font-size: 0.65em; width: 100%; }
        th, td { padding: 3px 5px; border: 1px solid #ccc; text-align: center; font-size: 0.85em; }
        th { background: #87CEEB; color: #000; }
        .vitoria { background: #4CAF50 !important; color: #fff; }
        .derrota { background: #f44336 !important; color: #fff; }
        .empate { background: #9e9e9e !important; color: #fff; }
        .jogo-rodada { font-size: 0.75em; padding: 3px 2px; border-bottom: 1px solid #eee; line-height: 1.3; }
        .jogo-rodada:last-child { border-bottom: none; }
        .times-table { width: 100%; font-size: 0.85em; }
        .times-table td { text-align: left; padding: 5px 8px; }
        .times-table td:last-child { text-align: center; font-weight: bold; }
        .top3 { background: #FFD700 !important; }
        .negativo { background: #ff6b6b !important; color: #fff; }
        .h2h-table { width: 100%; font-size: 0.68em; margin-top: 5px; }
        .h2h-table th { background: #87CEEB; color: #000; padding: 2px 1px; font-size: 0.8em; }
        .h2h-table td { padding: 2px 1px; text-align: center; }
        .h2h-table td:first-child { text-align: left; padding-left: 5px; }
        .h2h-vitoria { background: #4CAF50 !important; color: #fff; font-weight: bold; }
        .h2h-empate { background: #9e9e9e !important; color: #fff; font-weight: bold; }
        .h2h-derrota { background: #f44336 !important; color: #fff; font-weight: bold; }
        .bets-table { width: 100%; font-size: 0.85em; margin-top: 15px; border-collapse: collapse; }
        .bets-table th { background: #FFD700; color: #000; padding: 8px 5px; font-size: 0.9em; font-weight: bold; }
        .bets-table td { padding: 6px 5px; text-align: left; border-bottom: 1px solid #eee; }
        .bets-table tr:hover { background: #f9f9f9; }
        .bet-time { font-weight: bold; color: #d00; }
        .bet-diferenca { color: #666; font-size: 0.85em; }
        .aviso-box {
            position: fixed;
            bottom: 30px;
            left: 50%;
            transform: translateX(-50%);
            background: #fff3cd;
            border: 2px solid #ff9800;
            border-radius: 5px;
            padding: 10px 20px;
            font-size: 11px;
            color: #856404;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
            z-index: 999;
            max-width: 600px;
            text-align: center;
        }
        .aviso-box strong {
            color: #00703c;
            display: block;
            margin-bottom: 5px;
            font-size: 12px;
        }
        footer {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: #87CEEB;
            color: #000;
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 4px 15px;
            font-size: 9px;
            z-index: 1000;
        }
    </style>
</head>
<body>
    <div class="sidebar">
        <h3>Próxima Rodada - Brasileirão</h3>
'''
    
    for jogo in jogos_rodada:
        hora_display = f" {jogo['hora']}" if jogo.get('hora') else ""
        html += f'        <div class="jogo-rodada">{jogo["data"]}{hora_display} - {jogo["time1"]} x {jogo["time2"]}</div>\n'
    
    html += '''
        <h3 style="margin-top: 12px;">Classificação</h3>
        <table style="width: 100%; font-size: 0.7em;">
            <tr><th style="padding: 2px;">Pos</th><th>Time</th><th>Pts</th><th>J</th></tr>
'''
    
    for item in classificacao:
        pos = item.get("posicao", "")
        time = item.get("time", "")
        pts = item.get("pontos", "0")
        jogos = item.get("jogos", "0")
        html += f'            <tr><td style="text-align: center; padding: 1px 2px;">{pos}</td><td style="text-align: left; padding: 1px 2px;">{time}</td><td style="text-align: center; padding: 1px 2px;">{pts}</td><td style="text-align: center; padding: 1px 2px;">{jogos}</td></tr>\n'
    
    html += '''        </table>
'''
    
    # Adiciona tabela de Créditos Confronto Direto
    if resultados_h2h:
        html += '''
        <h3 style="margin-top: 10px;">Créditos confronto direto</h3>
        <table class="h2h-table">
            <tr><th>Time</th><th>1</th><th>2</th><th>3</th><th>4</th><th>5</th><th>Pts</th></tr>
'''
        
        # Ordena times alfabeticamente
        times_ordenados = sorted(resultados_h2h.keys())
        
        for time in times_ordenados:
            dados_time = resultados_h2h[time]
            resultados = dados_time["resultados"]
            pontos = dados_time["pontos"]
            html += f'            <tr><td>{time}</td>'
            
            # Adiciona até 5 resultados (preenche com "-" se não houver)
            for i in range(5):
                if i < len(resultados):
                    resultado = resultados[i]
                    classe = ""
                    if resultado == "V":
                        classe = "h2h-vitoria"
                    elif resultado == "E":
                        classe = "h2h-empate"
                    elif resultado == "D":
                        classe = "h2h-derrota"
                    html += f'<td class="{classe}">{resultado}</td>'
                else:
                    html += '<td>-</td>'
            
            # Adiciona coluna de pontos
            html += f'<td style="font-weight: bold; background: #FFE4B5;">{pontos:.1f}</td>'
            html += '</tr>\n'
        
        html += '''        </table>
'''
    
    html += '''
    </div>
    <div class="main-content">
        <h1>Brasileirão Betano</h1>
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
            
            # Adiciona escudos dos times
            home_logo = get_team_logo_html(home, "18px")
            away_logo = get_team_logo_html(away, "18px")
            html += f'        <tr class="{classe}"><td>{data}</td><td>{home_logo}{home}</td><td>{away_logo}{away}</td><td>{score}</td></tr>\n'
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
'''
    
    # Adiciona tabela de BETs se houver apostas sugeridas
    if apostas:
        html += '''
        <h3 style="margin-top: 20px; color: #d00;">BETs</h3>
        <table class="bets-table">
            <tr><th colspan="2">Apostas Recomendadas</th></tr>
'''
        
        for aposta in apostas:
            time = aposta["time"]
            adversario = aposta["adversario"]
            pontos = aposta["pontos"]
            pontos_adv = aposta["pontos_adv"]
            diferenca = aposta["diferenca"]
            
            html += f'''            <tr>
                <td colspan="2">
                    <span class="bet-time">{time}</span> vs {adversario}<br>
                    <span class="bet-diferenca">Créditos: {pontos:.2f} x {pontos_adv:.2f} (Δ {diferenca:.2f})</span>
                </td>
            </tr>
'''
        
        html += '''        </table>
'''
    
    html += '''    </div>
    <div class="aviso-box">
        <strong>⚠️ ATENÇÃO</strong>
        Atentar ao encerramento da temporada. Atualizar: - ID e NOME dos novos times; - Atualizar as TABELAS
    </div>
    <footer>
        <span>Development for Bruno Paraiso - 2026 | Todos os direitos reservados</span>
        <span id="data-criacao"></span>
    </footer>
    <script>
        const dataCriacao = new Date(document.lastModified);
        document.getElementById('data-criacao').textContent = 
            'Criado em: ' + dataCriacao.toLocaleString('pt-BR', {day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit'});
    </script>
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
    
    # Busca jogos do Internacional
    print("Buscando jogos do Internacional...")
    jogos_internacional = scrape_sofascore_last5(team_id=1966, team_name="Internacional", debug=False)
    
    # Busca jogos do Red Bull Bragantino
    print("Buscando jogos do Red Bull Bragantino...")
    jogos_bragantino = scrape_sofascore_last5(team_id=1999, team_name="Bragantino", debug=False)
    
    # Busca jogos do Vitória
    print("Buscando jogos do Vitória...")
    jogos_vitoria = scrape_sofascore_last5(team_id=1962, team_name="Vitória", debug=False)
    
    # Busca jogos do Santos
    print("Buscando jogos do Santos...")
    jogos_santos = scrape_sofascore_last5(team_id=1968, team_name="Santos", debug=False)
    
    # Busca jogos do Remo
    print("Buscando jogos do Remo...")
    jogos_remo = scrape_sofascore_last5(team_id=2012, team_name="Remo", debug=False)
    
    # Busca jogos do Chapecoense
    print("Buscando jogos do Chapecoense...")
    jogos_chapecoense = scrape_sofascore_last5(team_id=21845, team_name="Chapecoense", debug=False)
    
    # Busca jogos do Coritiba
    print("Buscando jogos do Coritiba...")
    jogos_coritiba = scrape_sofascore_last5(team_id=1982, team_name="Coritiba", debug=False)
    
    # Busca jogos do Athletico-PR
    print("Buscando jogos do Athletico-PR...")
    jogos_athletico_pr = scrape_sofascore_last5(team_id=1967, team_name="Athletico-PR", debug=False)
    
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
        ("Atlético-MG", jogos_atletico_mg),
        ("Internacional", jogos_internacional),
        ("Bragantino", jogos_bragantino),
        ("Vitória", jogos_vitoria),
        ("Santos", jogos_santos),
        ("Remo", jogos_remo),
        ("Chapecoense", jogos_chapecoense),
        ("Coritiba", jogos_coritiba),
        ("Athletico-PR", jogos_athletico_pr)
    ]
    
    # Ordena times alfabeticamente
    times_jogos = sorted(times_jogos, key=lambda x: x[0])
    
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
        "Atlético-MG": calcular_pontos_credito("Atlético-MG", jogos_atletico_mg),
        "Internacional": calcular_pontos_credito("Internacional", jogos_internacional),
        "Bragantino": calcular_pontos_credito("Bragantino", jogos_bragantino),
        "Vitória": calcular_pontos_credito("Vitória", jogos_vitoria),
        "Santos": calcular_pontos_credito("Santos", jogos_santos),
        "Remo": calcular_pontos_credito("Remo", jogos_remo),
        "Chapecoense": calcular_pontos_credito("Chapecoense", jogos_chapecoense),
        "Coritiba": calcular_pontos_credito("Coritiba", jogos_coritiba),
        "Athletico-PR": calcular_pontos_credito("Athletico-PR", jogos_athletico_pr)
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
    
    # Busca e processa dados H2H dos confrontos diretos da próxima rodada
    print("\nBuscando dados de confrontos diretos (H2H)...")
    resultados_h2h = {}
    
    # Mapeamento de abreviações para nomes completos (inclui variações com encoding problemático)
    abreviacoes = {
        "FLU": "Fluminense", "Fluminense": "Fluminense",
        "GRE": "Grêmio", "Grêmio": "Grêmio",
        "BOT": "Botafogo", "Botafogo": "Botafogo",
        "CRU": "Cruzeiro", "Cruzeiro": "Cruzeiro",
        "SAO": "São Paulo", "São Paulo": "São Paulo",
        "FLA": "Flamengo", "Flamengo": "Flamengo",
        "COR": "Corinthians", "Corinthians": "Corinthians",
        "BAH": "Bahia", "Bahia": "Bahia",
        "MIR": "Mirassol", "Mirassol": "Mirassol",
        "VAS": "Vasco", "Vasco": "Vasco",
        "CAM": "Atlético-MG", "ATL": "Atlético-MG", "Atlético-MG": "Atlético-MG",
        "PAL": "Palmeiras", "Palmeiras": "Palmeiras",
        "INT": "Internacional", "Internacional": "Internacional",
        "CAP": "Athletico-PR", "Athletico-PR": "Athletico-PR",
        "CFC": "Coritiba", "Coritiba": "Coritiba",
        "RBB": "Bragantino", "BRA": "Bragantino", "Bragantino": "Bragantino",
        "VIT": "Vitória", "Vitória": "Vitória",
        "REM": "Remo", "Remo": "Remo",
        "CHA": "Chapecoense", "Chapecoense": "Chapecoense",
        "SAN": "Santos", "Santos": "Santos"
    }
    
    for jogo in jogos_rodada:
        time1_abrev = jogo.get("time1", "").strip()
        time2_abrev = jogo.get("time2", "").strip()
        
        # Converte abreviações para nomes completos
        time1 = abreviacoes.get(time1_abrev, time1_abrev)
        time2 = abreviacoes.get(time2_abrev, time2_abrev)
        
        # Normaliza nomes (corrige encoding)
        time1 = normalizar_nome_brasileiro(time1)
        time2 = normalizar_nome_brasileiro(time2)
        
        # Busca confrontos diretos entre os dois times
        resultados_time1 = extrair_h2h_confronto_direto(time1, time2, debug=False)
        pontos_h2h_time1 = calcular_pontos_h2h(resultados_time1)
        
        # Para o time2, inverte os resultados (V vira D, D vira V)
        resultados_time2 = []
        for res in resultados_time1:
            if res == 'V':
                resultados_time2.append('D')
            elif res == 'D':
                resultados_time2.append('V')
            else:
                resultados_time2.append(res)  # 'E' ou '-' permanece igual
        
        pontos_h2h_time2 = calcular_pontos_h2h(resultados_time2)
        
        # Armazena os dados H2H
        resultados_h2h[time1] = {
            "resultados": resultados_time1,
            "pontos": pontos_h2h_time1
        }
        
        resultados_h2h[time2] = {
            "resultados": resultados_time2,
            "pontos": pontos_h2h_time2
        }
        
        # Adiciona pontos H2H aos pontos de crédito totais
        if time1 in pontos_credito:
            pontos_credito[time1] += pontos_h2h_time1
        if time2 in pontos_credito:
            pontos_credito[time2] += pontos_h2h_time2
    
    # Analisa apostas baseado nos créditos
    apostas = analisar_apostas(jogos_rodada, pontos_credito)
    
    html = gerar_html(times_jogos, jogos_rodada, classificacao, pontos_credito, resultados_h2h, apostas)
    fname = "sofascore_result.html"
    with open(fname, "w", encoding="utf-8") as f:
        f.write(html)
    # Tenta abrir no Firefox
    try:
        subprocess.Popen(["firefox", fname])
    except Exception:
        webbrowser.open_new_tab(fname)

if __name__ == "__main__":
    main()
