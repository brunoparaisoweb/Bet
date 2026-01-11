#!/usr/bin/env python3
"""Teste da tabela H2H com pontuação"""

import json

# Carrega dados H2H
with open("h2h_data.json", "r", encoding="utf-8") as f:
    dados_h2h = json.load(f)

# Processa resultados com pontuação
resultados_h2h = {}

for confronto in dados_h2h:
    time1 = confronto["time1"]
    time2 = confronto["time2"]
    h2h_list = confronto["h2h"]
    
    if time1 not in resultados_h2h:
        resultados_h2h[time1] = {"resultados": [], "pontos": 0.0}
    if time2 not in resultados_h2h:
        resultados_h2h[time2] = {"resultados": [], "pontos": 0.0}
    
    for jogo in h2h_list:
        texto = jogo["texto"]
        resultado_time1 = texto[0]
        
        # Identifica mandante
        partes = texto.split()
        placar_idx = -1
        for i, parte in enumerate(partes):
            if '-' in parte and any(c.isdigit() for c in parte):
                placar_idx = i
                break
        
        if placar_idx > 0:
            mandante_palavras = []
            for i in range(2, placar_idx):
                mandante_palavras.append(partes[i])
            mandante_texto = " ".join(mandante_palavras)
            
            time1_mandante = time1.lower() in mandante_texto.lower() or mandante_texto.lower() in time1.lower()
            
            # Calcula pontos
            if resultado_time1 == "V":
                if time1_mandante:
                    resultados_h2h[time1]["resultados"].append("V")
                    resultados_h2h[time1]["pontos"] += 0.1
                    resultados_h2h[time2]["resultados"].append("D")
                    resultados_h2h[time2]["pontos"] -= 0.1
                else:
                    resultados_h2h[time1]["resultados"].append("V")
                    resultados_h2h[time1]["pontos"] += 0.2
                    resultados_h2h[time2]["resultados"].append("D")
                    resultados_h2h[time2]["pontos"] -= 0.2
            
            elif resultado_time1 == "E":
                if time1_mandante:
                    resultados_h2h[time1]["resultados"].append("E")
                    resultados_h2h[time1]["pontos"] += 0.0
                    resultados_h2h[time2]["resultados"].append("E")
                    resultados_h2h[time2]["pontos"] += 0.1
                else:
                    resultados_h2h[time1]["resultados"].append("E")
                    resultados_h2h[time1]["pontos"] += 0.1
                    resultados_h2h[time2]["resultados"].append("E")
                    resultados_h2h[time2]["pontos"] += 0.0
            
            elif resultado_time1 == "D":
                if time1_mandante:
                    resultados_h2h[time1]["resultados"].append("D")
                    resultados_h2h[time1]["pontos"] -= 0.2
                    resultados_h2h[time2]["resultados"].append("V")
                    resultados_h2h[time2]["pontos"] += 0.2
                else:
                    resultados_h2h[time1]["resultados"].append("D")
                    resultados_h2h[time1]["pontos"] -= 0.1
                    resultados_h2h[time2]["resultados"].append("V")
                    resultados_h2h[time2]["pontos"] += 0.1

# Gera HTML
html = """<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Créditos Confronto Direto</title>
<style>
body { font-family: Arial; padding: 20px; background: #f5f5f5; }
.container { max-width: 600px; margin: 0 auto; background: white; padding: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
h2 { color: #333; text-align: center; }
table { width: 100%; border-collapse: collapse; margin-top: 20px; }
th, td { border: 1px solid #ddd; padding: 8px; text-align: center; }
th { background: #87CEEB; color: #000; font-weight: bold; }
td:first-child { text-align: left; font-weight: bold; }
.h2h-vitoria { background: #4CAF50; color: white; font-weight: bold; }
.h2h-empate { background: #9e9e9e; color: white; font-weight: bold; }
.h2h-derrota { background: #f44336; color: white; font-weight: bold; }
</style>
</head>
<body>
<div class="container">
<h2>Créditos confronto direto</h2>
<p style="text-align: center; color: #666; font-size: 0.9em;">Últimos 5 confrontos diretos de cada time + Pontuação</p>
<table>
<tr><th>Time</th><th>1º</th><th>2º</th><th>3º</th><th>4º</th><th>5º</th><th>Pts</th></tr>
"""

# Ordena alfabeticamente
for time in sorted(resultados_h2h.keys()):
    dados_time = resultados_h2h[time]
    resultados = dados_time["resultados"]
    pontos = dados_time["pontos"]
    html += f"<tr><td>{time}</td>"
    
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

html += """
</table>
<div style="margin-top: 20px; padding: 10px; background: #f9f9f9; border-left: 4px solid #87CEEB;">
<p style="margin: 5px 0; font-size: 0.9em;"><strong>Legenda:</strong></p>
<p style="margin: 5px 0; font-size: 0.85em;"><span style="background: #4CAF50; color: white; padding: 2px 8px; border-radius: 3px;">V</span> = Vitória</p>
<p style="margin: 5px 0; font-size: 0.85em;"><span style="background: #9e9e9e; color: white; padding: 2px 8px; border-radius: 3px;">E</span> = Empate</p>
<p style="margin: 5px 0; font-size: 0.85em;"><span style="background: #f44336; color: white; padding: 2px 8px; border-radius: 3px;">D</span> = Derrota</p>
</div>
</div>
</body>
</html>
"""

with open("teste_h2h_creditos.html", "w", encoding="utf-8") as f:
    f.write(html)

print("[OK] Teste gerado: teste_h2h_creditos.html")
print(f"Total de times: {len(resultados_h2h)}")
for time, dados in sorted(resultados_h2h.items()):
    print(f"{time}: {dados['resultados'][:5]} - Pontos: {dados['pontos']:.1f}")
