#!/usr/bin/env python3
"""
Gerador de HTML para Premier League
Baseado no sistema do Brasileirão, adaptado para Premier League 2025/2026
"""
import json
from datetime import datetime
from sofascore_scraper_pl import scrape_sofascore_last5, PREMIER_LEAGUE_TEAM_IDS
from config_pl import PROXIMA_RODADA, CLASSIFICACAO_ATUAL
from ogol_scraper_pl import scrape_h2h_ogol

def calcular_creditos_time(team_name, ultimos_jogos, classificacao, h2h_data=None):
    """
    Calcula os créditos de um time baseado em:
    - Últimos 5 jogos (vitória como mandante = 0.75, visitante = 1.0)
    - Empates (mandante = 0.25, visitante = 0.5)
    - Derrotas (mandante = -1.0, visitante = -0.75)
    - Bônus de classificação normalizado
    - Histórico H2H (se disponível)
    """
    pontos = 0.0
    
    # 1. Pontos dos últimos 5 jogos (sistema normalizado)
    for jogo in ultimos_jogos[:5]:
        home = jogo.get("homeTeam", {}).get("name", "")
        away = jogo.get("awayTeam", {}).get("name", "")
        score = jogo.get("score", {}).get("fullTime", {})
        home_score = score.get("homeTeam", 0)
        away_score = score.get("awayTeam", 0)
        
        # Determina se o time jogou em casa ou fora usando função de correspondência
        e_casa = times_correspondem(team_name, home)
        e_fora = times_correspondem(team_name, away)
        
        if e_casa:
            if home_score > away_score:
                pontos += 0.75  # Vitória como mandante
            elif home_score == away_score:
                pontos += 0.25  # Empate como mandante
            else:
                pontos -= 1.0   # Derrota como mandante
        elif e_fora:
            if away_score > home_score:
                pontos += 1.0   # Vitória como visitante
            elif home_score == away_score:
                pontos += 0.5   # Empate como visitante
            else:
                pontos -= 0.75  # Derrota como visitante
    
    # 2. Bônus de classificação normalizado (escala reduzida)
    # 1º lugar = +2.0, 10º lugar = 0, 20º lugar = -2.0
    for idx, time in enumerate(classificacao, 1):
        if time["time"] == team_name or team_name in time["time"]:
            bonus_classificacao = (11 - idx) * 0.2  # Escala de -1.8 a +2.0
            pontos += bonus_classificacao
            break
    
    # 3. H2H (se disponível) - adiciona pontos baseado no histórico
    if h2h_data:
        pontos += h2h_data.get("bonus_h2h", 0)
    
    return round(pontos, 2)

def normalizar_nome_time(nome):
    """
    Normaliza nomes de times para comparação.
    Retorna conjunto de variações do nome do time.
    """
    apelidos = {
        "Wolverhampton": ["Wolverhampton", "Wolves", "Wolverhampton Wanderers"],
        "Wolves": ["Wolverhampton", "Wolves", "Wolverhampton Wanderers"],
        "Manchester City": ["Manchester City", "Man City", "Man. City"],
        "Man City": ["Manchester City", "Man City", "Man. City"],
        "Manchester United": ["Manchester United", "Man Utd", "Man. United"],
        "Man Utd": ["Manchester United", "Man Utd", "Man. United"],
        "Brighton & Hove Albion": ["Brighton", "Brighton & Hove Albion", "Brighton & Hove"],
        "Brighton": ["Brighton", "Brighton & Hove Albion", "Brighton & Hove"],
        "Leeds United": ["Leeds", "Leeds United"],
        "Leeds": ["Leeds", "Leeds United"],
        "Nottingham Forest": ["Forest", "Nottingham Forest", "Nott'm Forest"],
        "Forest": ["Forest", "Nottingham Forest", "Nott'm Forest"],
    }
    
    return apelidos.get(nome, [nome])

def times_correspondem(team_name, jogo_team_name):
    """
    Verifica se dois nomes de times correspondem, considerando apelidos.
    """
    variacoes_team = normalizar_nome_time(team_name)
    variacoes_jogo = normalizar_nome_time(jogo_team_name)
    
    # Verifica se há interseção entre as variações
    for var1 in variacoes_team:
        for var2 in variacoes_jogo:
            if var1.lower() in var2.lower() or var2.lower() in var1.lower():
                return True
    
    return False

def extrair_resultados_ultimos5(team_name, ultimos_jogos):
    """
    Extrai os resultados dos últimos 5 jogos de um time.
    Retorna lista de resultados: 'V' (vitória), 'E' (empate), 'D' (derrota)
    """
    resultados = []
    
    for jogo in ultimos_jogos[:5]:
        home = jogo.get("homeTeam", {}).get("name", "")
        away = jogo.get("awayTeam", {}).get("name", "")
        score = jogo.get("score", {}).get("fullTime", {})
        home_score = score.get("homeTeam", 0)
        away_score = score.get("awayTeam", 0)
        
        # Determina se o time jogou em casa ou fora usando função de correspondência
        e_casa = times_correspondem(team_name, home)
        e_fora = times_correspondem(team_name, away)
        
        if e_casa:
            if home_score > away_score:
                resultados.append('V')
            elif home_score == away_score:
                resultados.append('E')
            else:
                resultados.append('D')
        elif e_fora:
            if away_score > home_score:
                resultados.append('V')
            elif home_score == away_score:
                resultados.append('E')
            else:
                resultados.append('D')
    
    # Preenche com '-' se não tiver 5 jogos
    while len(resultados) < 5:
        resultados.append('-')
    
    return resultados[:5]

def calcular_pontos_h2h(resultados):
    """
    Calcula pontos H2H baseado nos últimos 5 jogos.
    Fórmula: (V*3 + E*1) / 5 jogos - 1.5 (média)
    Normaliza para ter valores entre -1.5 e +1.5
    """
    pontos = 0
    jogos_validos = 0
    
    for res in resultados:
        if res == 'V':
            pontos += 3
            jogos_validos += 1
        elif res == 'E':
            pontos += 1
            jogos_validos += 1
        elif res == 'D':
            pontos += 0
            jogos_validos += 1
    
    if jogos_validos == 0:
        return 0.0
    
    # Média de pontos por jogo
    media = pontos / 5  # Divide por 5 sempre para normalizar
    # Subtrai 1.5 (que seria a média teórica de 50% vitórias)
    return round(media - 1.5, 1)

def extrair_h2h_confronto_direto(time_mandante, time_visitante, debug=False):
    """
    Extrai os últimos 5 jogos entre dois times específicos (confronto direto).
    Retorna lista de resultados do ponto de vista do time mandante:
    'V' (vitória), 'E' (empate), 'D' (derrota)
    """
    resultados = []
    
    # Busca confrontos diretos no ogol.com.br
    jogos_h2h = scrape_h2h_ogol(time_mandante, time_visitante, debug=debug)
    
    if debug:
        print(f"  Confronto {time_mandante} vs {time_visitante}: {len(jogos_h2h)} jogos encontrados")
    
    for jogo in jogos_h2h[:5]:  # Até 5 jogos
        resultado = jogo.get("resultado", "").strip().upper()
        
        # Resultado já vem do ponto de vista do time_mandante (primeiro parâmetro da busca)
        if resultado == 'V':
            resultados.append('V')
        elif resultado == 'E':
            resultados.append('E')
        elif resultado == 'D':
            resultados.append('D')
        else:
            # Se não conseguir determinar, marca como '-'
            resultados.append('-')
    
    # Preenche com '-' se não tiver 5 jogos
    while len(resultados) < 5:
        resultados.append('-')
    
    return resultados[:5]

def gerar_html_premier_league():
    """
    Gera o HTML principal com análise da Premier League
    """
    print("=== GERANDO HTML PREMIER LEAGUE ===\n")
    
    # 1. Buscar últimos jogos de cada time
    print("1. Buscando últimos jogos do SofaScore...")
    dados_times = {}
    
    for team_name, team_id in PREMIER_LEAGUE_TEAM_IDS.items():
        # Evita duplicatas (usa nome completo, não abreviações)
        if team_name in ["Man City", "Man Utd", "Leeds", "Forest", "Wolves", "Brighton"]:
            continue
            
        print(f"   - {team_name}...")
        jogos = scrape_sofascore_last5(team_id, team_name, debug=False)
        
        # Filtra apenas jogos de 2026 (formato da data: DD/MM/YY)
        jogos_2026 = [j for j in jogos if j.get("startDate", "").endswith("/26")]
        
        dados_times[team_name] = {
            "ultimos_jogos": jogos_2026,
            "team_id": team_id
        }
    
    print(f"\nDados coletados de {len(dados_times)} times")
    
    # 2. Calcular créditos para cada time
    print("Calculando créditos...")
    for team_name in dados_times:
        creditos = calcular_creditos_time(
            team_name,
            dados_times[team_name]["ultimos_jogos"],
            CLASSIFICACAO_ATUAL
        )
        dados_times[team_name]["creditos"] = creditos
    
    # 3. Calcular dados H2H (confrontos diretos da próxima rodada)
    print("Calculando H2H dos confrontos diretos...")
    h2h_dados = {}
    
    for jogo in PROXIMA_RODADA:
        home = jogo["time1"]
        away = jogo["time2"]
        
        # Busca confrontos diretos entre os dois times
        resultados_home = extrair_h2h_confronto_direto(home, away, debug=False)
        pontos_h2h_home = calcular_pontos_h2h(resultados_home)
        
        # Para o time visitante, inverte os resultados (V vira D, D vira V)
        resultados_away = []
        for res in resultados_home:
            if res == 'V':
                resultados_away.append('D')
            elif res == 'D':
                resultados_away.append('V')
            else:
                resultados_away.append(res)  # 'E' ou '-' permanece igual
        
        pontos_h2h_away = calcular_pontos_h2h(resultados_away)
        
        # Armazena os dados H2H
        h2h_dados[home] = {
            "resultados": resultados_home,
            "pontos": pontos_h2h_home,
            "adversario": away
        }
        
        h2h_dados[away] = {
            "resultados": resultados_away,
            "pontos": pontos_h2h_away,
            "adversario": home
        }
    
    # 3.5. Atualizar créditos totais com pontos H2H
    for team_name in h2h_dados:
        if team_name in dados_times:
            creditos_gerais = dados_times[team_name]["creditos"]
            pontos_h2h = h2h_dados[team_name]["pontos"]
            creditos_totais = creditos_gerais + pontos_h2h
            dados_times[team_name]["creditos_totais"] = creditos_totais
    
    # 4. Analisar próxima rodada
    analises_rodada = []
    
    for jogo in PROXIMA_RODADA:
        home = jogo["time1"]
        away = jogo["time2"]
        
        # Usa créditos totais (gerais + H2H) se disponível, senão usa só os gerais
        creditos_home = dados_times.get(home, {}).get("creditos_totais", dados_times.get(home, {}).get("creditos", 0))
        creditos_away = dados_times.get(away, {}).get("creditos_totais", dados_times.get(away, {}).get("creditos", 0))
        diferenca = abs(creditos_home - creditos_away)
        
        analises_rodada.append({
            "mandante": home,
            "visitante": away,
            "data": jogo["data"],
            "creditos_mandante": creditos_home,
            "creditos_visitante": creditos_away,
            "diferenca": diferenca,
            "favorito": home if creditos_home > creditos_away else away
        })
    
    # 5. Identificar BETs (diferença >= 2.0 E favorito com pontuação > 0)
    bets = [a for a in analises_rodada if a["diferenca"] >= 2.0 and 
            (a["creditos_mandante"] > 0 if a["favorito"] == a["mandante"] else a["creditos_visitante"] > 0)]
    bets.sort(key=lambda x: x["diferenca"], reverse=True)
    
    # 6. Gerar HTML
    html = gerar_html_template(CLASSIFICACAO_ATUAL, analises_rodada, dados_times, bets, h2h_dados)
    
    # Salvar arquivo
    with open("premier_league_analysis.html", "w", encoding="utf-8") as f:
        f.write(html)
    
    return html

def gerar_html_template(classificacao, analises, dados_times, bets, h2h_dados):
    """
    Template HTML para exibição
    """
    html = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Premier League 2025/2026 - Análise</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0 0 20px 0;
            background: #f7f7f7;
            display: flex;
        }
        .sidebar {
            width: 220px;
            padding: 10px;
            background: #fff;
            box-shadow: 2px 0 8px #0001;
            font-size: 0.75em;
        }
        .main-content {
            flex: 1;
            padding: 8px;
            display: flex;
            flex-wrap: wrap;
            justify-content: space-around;
        }
        .sidebar-right {
            width: 250px;
            padding: 15px;
            background: #fff;
            box-shadow: -2px 0 8px #0001;
            font-size: 0.9em;
        }
        footer {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: #37003c;
            color: #fff;
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 4px 15px;
            font-size: 9px;
            z-index: 1000;
        }
        .time-section {
            width: 18%;
            min-width: 180px;
            margin: 5px;
        }
        h1 {
            color: #333;
            text-align: center;
            font-size: 0.9em;
            margin: 5px 0;
            width: 100%;
        }
        h2 {
            color: #d00;
            text-align: center;
            margin: 8px 0 5px 0;
            font-size: 0.75em;
        }
        h3 {
            color: #333;
            font-size: 0.9em;
            margin: 8px 0 4px 0;
        }
        table {
            border-collapse: collapse;
            margin: 5px auto;
            background: #fff;
            box-shadow: 0 1px 4px #0001;
            font-size: 0.65em;
            width: 100%;
        }
        th, td {
            padding: 3px 5px;
            border: 1px solid #ccc;
            text-align: center;
            font-size: 0.85em;
        }
        th {
            background: #37003c;
            color: #fff;
        }
        .vitoria {
            background: #4CAF50 !important;
            color: #fff;
        }
        .derrota {
            background: #f44336 !important;
            color: #fff;
        }
        .empate {
            background: #9e9e9e !important;
            color: #fff;
        }
        .jogo-rodada {
            font-size: 0.75em;
            padding: 3px 2px;
            border-bottom: 1px solid #eee;
            line-height: 1.3;
        }
        .jogo-rodada:last-child {
            border-bottom: none;
        }
        .match-card {
            background: white;
            border: 1px solid #ddd;
            border-radius: 6px;
            padding: 12px;
            margin-bottom: 12px;
            width: 18%;
            min-width: 180px;
            margin: 5px;
        }
        .match-header {
            display: flex;
            justify-content: space-between;
            font-size: 9px;
            color: #666;
            margin-bottom: 8px;
        }
        .match-teams {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin: 8px 0;
            font-size: 11px;
        }
        .team {
            flex: 1;
            font-weight: 600;
        }
        .team.away {
            text-align: right;
        }
        .vs {
            padding: 0 10px;
            color: #999;
            font-size: 9px;
        }
        .credits {
            display: flex;
            justify-content: space-between;
            font-size: 9px;
            color: #666;
            margin-top: 6px;
        }
        .favorito {
            background: #e7f3ff;
            border-left: 3px solid #2196F3;
        }
        .bet-high {
            background: #fff3cd;
            border-left: 3px solid #ff9800;
        }
        .bet-item {
            padding: 4px 6px;
            margin-bottom: 4px;
            background: #f8f9fa;
            border-radius: 3px;
            border-left: 2px solid #28a745;
        }
        .bet-time {
            font-weight: 600;
            color: #28a745;
            font-size: 10px;
        }
        .bet-diff {
            font-size: 9px;
            color: #666;
            margin-top: 1px;
        }
        .bet-matchup {
            font-size: 8px;
            color: #888;
            margin-top: 1px;
        }
        .pos {
            display: inline-block;
            width: 22px;
            text-align: center;
            font-weight: 600;
        }
        .h2h-table {
            width: 100%;
            font-size: 0.68em;
            margin-top: 5px;
        }
        .h2h-table th {
            background: #37003c;
            color: #fff;
            padding: 2px 1px;
            font-size: 0.8em;
        }
        .h2h-table td {
            padding: 2px 1px;
            text-align: center;
        }
        .h2h-table td:first-child {
            text-align: left;
            padding-left: 5px;
        }
        .h2h-vitoria {
            background: #4CAF50 !important;
            color: #fff;
            font-weight: bold;
        }
        .h2h-empate {
            background: #9e9e9e !important;
            color: #fff;
            font-weight: bold;
        }
        .h2h-derrota {
            background: #f44336 !important;
            color: #fff;
            font-weight: bold;
        }
        .times-table {
            width: 100%;
            font-size: 0.85em;
        }
        .times-table td {
            text-align: left;
            padding: 5px 8px;
        }
        .times-table td:last-child {
            text-align: center;
            font-weight: bold;
        }
        .top3 {
            background: #FFD700 !important;
        }
        .negativo {
            background: #ff6b6b !important;
            color: #fff;
        }
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
            color: #37003c;
            display: block;
            margin-bottom: 5px;
            font-size: 12px;
        }
    </style>
</head>
<body>
    <!-- Sidebar Esquerda: Próxima Rodada -->
    <div class="sidebar">
        <h3>Próxima Rodada - Premier League</h3>
"""
    
    # Próxima rodada na sidebar
    for jogo in PROXIMA_RODADA:
        # Simplifica os nomes
        home_short = jogo["time1"][:3].upper() if len(jogo["time1"]) > 10 else jogo["time1"]
        away_short = jogo["time2"][:3].upper() if len(jogo["time2"]) > 10 else jogo["time2"]
        data_short = jogo["data"][:5]  # Pega só DD/MM
        
        html += f'        <div class="jogo-rodada">{data_short} - {home_short} x {away_short}</div>\n'
    
    html += """
        <h3 style="margin-top: 12px;">Classificação</h3>
        <table style="width: 100%; font-size: 0.7em;">
            <tr><th style="padding: 2px;">Pos</th><th>Time</th><th>Pts</th><th>J</th></tr>
"""
    
    # Classificação
    for time in classificacao:
        html += f"""            <tr><td style="text-align: center; padding: 1px 2px;">{time['posicao']}</td><td style="text-align: left; padding: 1px 2px;">{time['time']}</td><td style="text-align: center; padding: 1px 2px;">{time['pontos']}</td><td style="text-align: center; padding: 1px 2px;">{time['jogos']}</td></tr>
"""
    
    html += """        </table>

        <h3 style="margin-top: 10px;">Créditos confronto direto</h3>
        <table class="h2h-table">
            <tr><th>Time</th><th>vs</th><th>1</th><th>2</th><th>3</th><th>4</th><th>5</th><th>Pts</th></tr>
"""
    
    # Tabela H2H - ordena por nome do time
    times_ordenados = sorted(h2h_dados.keys())
    for team_name in times_ordenados:
        dados_h2h = h2h_dados[team_name]
        resultados = dados_h2h["resultados"]
        pontos = dados_h2h["pontos"]
        adversario = dados_h2h.get("adversario", "")
        
        # Nome do time (encurtado se necessário)
        nome_display = team_name if len(team_name) <= 12 else team_name[:10] + "."
        adversario_display = adversario[:3].upper() if len(adversario) > 3 else adversario
        
        html += f'            <tr><td>{nome_display}</td><td style="font-size: 9px; color: #666;">{adversario_display}</td>'
        
        # 5 resultados
        for res in resultados:
            if res == 'V':
                html += '<td class="h2h-vitoria">V</td>'
            elif res == 'E':
                html += '<td class="h2h-empate">E</td>'
            elif res == 'D':
                html += '<td class="h2h-derrota">D</td>'
            else:
                html += '<td>-</td>'
        
        # Pontos H2H
        html += f'<td style="font-weight: bold; background: #FFE4B5;">{pontos}</td></tr>\n'
    
    html += """        </table>
    </div>
    
    <!-- Conteúdo Principal: Últimos 5 Jogos de Cada Time -->
    <div class="main-content">
        <h1>Premier League 2025/2026</h1>
"""
    
    # Ordena times alfabeticamente para exibição
    times_ordenados = sorted(dados_times.keys())
    
    for team_name in times_ordenados:
        html += f"""    <div class="time-section">
    <h2>{team_name}</h2>
    <table>
        <tr><th>Data</th><th>Mandante</th><th>Visitante</th><th>Placar</th></tr>
"""
        
        # Últimos 5 jogos do time
        jogos = dados_times[team_name]["ultimos_jogos"][:5]
        
        for jogo in jogos:
            # Extrai informações do jogo
            home_team = jogo.get("homeTeam", {}).get("name", "")
            away_team = jogo.get("awayTeam", {}).get("name", "")
            score = jogo.get("score", {}).get("fullTime", {})
            home_score = score.get("homeTeam", 0)
            away_score = score.get("awayTeam", 0)
            
            # Data do jogo (formato já vem como DD/MM/YY do scraper)
            date_str = jogo.get("startDate", "")
            if date_str:
                date_formatted = date_str
            else:
                date_formatted = "N/A"
            
            # Determina a classe CSS (vitória, empate, derrota)
            # Usa função de correspondência para aceitar apelidos (Wolves/Wolverhampton, etc)
            e_casa = times_correspondem(team_name, home_team)
            e_fora = times_correspondem(team_name, away_team)
            
            css_class = ""
            if e_casa:
                if home_score > away_score:
                    css_class = "vitoria"
                elif home_score == away_score:
                    css_class = "empate"
                else:
                    css_class = "derrota"
            elif e_fora:
                if away_score > home_score:
                    css_class = "vitoria"
                elif home_score == away_score:
                    css_class = "empate"
                else:
                    css_class = "derrota"
            
            html += f'        <tr class="{css_class}"><td>{date_formatted}</td><td>{home_team}</td><td>{away_team}</td><td>{home_score} x {away_score}</td></tr>\n'
        
        html += """    </table>
    </div>
"""
    
    html += """    </div>
    
    <!-- Sidebar Direita: Pontos de Crédito e BETs -->
    <div class="sidebar-right">
        <h3>Times da Premier League</h3>
        <table class="times-table">
            <tr><th>Time</th><th>Créditos Totais</th></tr>
"""
    
    # Cria lista única com todos os times e seus créditos (totais se tiver H2H, senão gerais)
    times_ordenados = []
    for team_name, dados in dados_times.items():
        # Usa creditos_totais se disponível (times da próxima rodada), senão usa creditos gerais
        creditos = dados.get("creditos_totais", dados.get("creditos", 0))
        times_ordenados.append((team_name, creditos))
    
    # Ordena todos os times por créditos (do maior para o menor)
    times_ordenados.sort(key=lambda x: x[1], reverse=True)
    
    for idx, (team_name, creditos) in enumerate(times_ordenados):
        # Define a classe CSS: top3 para os 3 primeiros, negativo para negativos
        if idx < 3:
            css_class = "top3"
        elif creditos < 0:
            css_class = "negativo"
        else:
            css_class = ""
        
        html += f'            <tr class="{css_class}"><td>{team_name}</td><td>{creditos:.2f}</td></tr>\n'
    
    html += """        </table>

        <h3 style="margin-top: 12px; color: #d00; font-size: 0.85em;">BETs Recomendadas</h3>
"""
    
    if bets:
        for bet in bets:
            # Encurta os nomes dos times se forem muito longos
            mandante_short = bet['mandante'][:12] + "." if len(bet['mandante']) > 12 else bet['mandante']
            visitante_short = bet['visitante'][:12] + "." if len(bet['visitante']) > 12 else bet['visitante']
            favorito_short = bet['favorito'][:15] + "." if len(bet['favorito']) > 15 else bet['favorito']
            
            html += f"""        <div class="bet-item">
            <div class="bet-time">{favorito_short}</div>
            <div class="bet-matchup">{mandante_short} vs {visitante_short}</div>
            <div class="bet-diff">Dif: {bet['diferenca']:.1f}</div>
        </div>
"""
    else:
        html += """        <p style="font-size: 10px; color: #999; margin: 8px 0;">
            Nenhuma BET ≥ 2.0 pts
        </p>
"""
    
    html += """    </div>
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
"""
    
    return html

if __name__ == "__main__":
    gerar_html_premier_league()
