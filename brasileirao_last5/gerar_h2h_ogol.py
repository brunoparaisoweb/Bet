#!/usr/bin/env python3
"""Gera HTML com histórico H2H usando ogol.com.br"""

import json
from ge_scraper import scrape_primeira_rodada
from ogol_scraper import scrape_h2h_ogol

# Mapeamento de abreviações do GE para nomes completos
ABREVIACOES_TIMES = {
    "FLU": "Fluminense",
    "GRE": "Grêmio",
    "BOT": "Botafogo",
    "CRU": "Cruzeiro",
    "SAO": "São Paulo",
    "FLA": "Flamengo",
    "COR": "Corinthians",
    "BAH": "Bahia",
    "MIR": "Mirassol",
    "VAS": "Vasco",
    "CAM": "Atlético-MG",
    "PAL": "Palmeiras",
    "INT": "Internacional",
    "CAP": "Athletico-PR",
    "CFC": "Coritiba",
    "RBB": "Bragantino",
    "VIT": "Vitória",
    "REM": "Remo",
    "CHA": "Chapecoense",
    "SAN": "Santos"
}

def normalizar_nome_time(abrev):
    """Converte abreviação do GE para nome completo"""
    return ABREVIACOES_TIMES.get(abrev, abrev)

def gerar_html_h2h_ogol():
    """Gera HTML com H2H de todos os confrontos da rodada usando ogol.com.br"""
    
    print("Buscando jogos da 1ª rodada...")
    jogos_rodada = scrape_primeira_rodada()
    
    print(f"\nEncontrados {len(jogos_rodada)} jogos na rodada")
    
    # Para cada confronto, busca o H2H
    print("\n" + "="*80)
    print("Buscando histórico H2H de cada confronto no ogol.com.br...")
    print("="*80)
    
    confrontos_h2h = []
    
    for jogo in jogos_rodada:
        time1_abrev = jogo['time1']
        time2_abrev = jogo['time2']
        
        # Normaliza nomes
        time1 = normalizar_nome_time(time1_abrev)
        time2 = normalizar_nome_time(time2_abrev)
        
        print(f"\n--- {time1} vs {time2} ---")
        
        # Busca H2H no ogol
        h2h = scrape_h2h_ogol(time1, time2, debug=True)
        
        if h2h:
            print(f"[OK] Encontrados {len(h2h)} confrontos H2H")
            confrontos_h2h.append({
                "time1": time1,
                "time2": time2,
                "h2h": h2h
            })
        else:
            print("[X] Nenhum confronto H2H encontrado")
            confrontos_h2h.append({
                "time1": time1,
                "time2": time2,
                "h2h": []
            })
    
    # Gera HTML
    print("\n" + "="*80)
    print("Gerando HTML...")
    print("="*80)
    
    html = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Histórico H2H - 1ª Rodada Brasileirão (Ogol)</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }
        h1 {
            text-align: center;
            color: #333;
        }
        .confronto {
            background: white;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .confronto h2 {
            margin-top: 0;
            color: #2c5aa0;
            border-bottom: 2px solid #2c5aa0;
            padding-bottom: 10px;
        }
        .h2h-jogo {
            background: #f9f9f9;
            border-left: 4px solid #2c5aa0;
            padding: 10px;
            margin: 10px 0;
            font-family: 'Courier New', monospace;
            font-size: 14px;
        }
        .sem-dados {
            color: #999;
            font-style: italic;
            text-align: center;
            padding: 20px;
        }
        .rodada-info {
            text-align: center;
            background: #2c5aa0;
            color: white;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 30px;
        }
        .fonte {
            text-align: center;
            color: #666;
            font-size: 12px;
            margin-top: 10px;
        }
    </style>
</head>
<body>
    <div class="rodada-info">
        <h1>Histórico de Confrontos (H2H)</h1>
        <p>1ª Rodada do Brasileirão Série A - 28/01</p>
        <p class="fonte">Fonte: ogol.com.br</p>
    </div>
"""
    
    for confronto in confrontos_h2h:
        html += f"""
    <div class="confronto">
        <h2>{confronto['time1']} vs {confronto['time2']}</h2>
"""
        
        if confronto['h2h']:
            html += f"""
        <p><strong>Últimos {len(confronto['h2h'])} confrontos:</strong></p>
"""
            for i, jogo in enumerate(confronto['h2h'], 1):
                html += f"""
        <div class="h2h-jogo">
            {jogo['texto']}
        </div>
"""
        else:
            html += """
        <div class="sem-dados">
            Dados de H2H não disponíveis para este confronto
        </div>
"""
        
        html += """
    </div>
"""
    
    html += """
</body>
</html>
"""
    
    # Salva o HTML
    with open("h2h_rodada_ogol.html", "w", encoding="utf-8") as f:
        f.write(html)
    
    # Salva os dados em JSON para uso posterior
    with open("h2h_data.json", "w", encoding="utf-8") as f:
        json.dump(confrontos_h2h, f, ensure_ascii=False, indent=2)
    
    print(f"\n[OK] HTML gerado: h2h_rodada_ogol.html")
    print(f"[OK] Dados JSON salvos: h2h_data.json")
    print(f"  Total de confrontos: {len(confrontos_h2h)}")
    print(f"  Confrontos com H2H: {sum(1 for c in confrontos_h2h if c['h2h'])}")
    print(f"  Confrontos sem H2H: {sum(1 for c in confrontos_h2h if not c['h2h'])}")


if __name__ == "__main__":
    gerar_html_h2h_ogol()
