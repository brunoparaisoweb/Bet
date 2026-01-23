"""
Servidor Flask para atualizar análises dos campeonatos
"""
from flask import Flask, jsonify, send_file, request
from flask_cors import CORS
import subprocess
import os
import threading
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Status de progresso para cada campeonato
progresso = {
    'brasileirao': {'status': 'idle', 'progresso': 0, 'mensagem': ''},
    'premier': {'status': 'idle', 'progresso': 0, 'mensagem': ''},
    'laliga': {'status': 'idle', 'progresso': 0, 'mensagem': ''},
    'seria': {'status': 'idle', 'progresso': 0, 'mensagem': ''},
    'ligue1': {'status': 'idle', 'progresso': 0, 'mensagem': ''}
}

def executar_script(campeonato, script, arquivo_html):
    """Executa o script Python e atualiza o progresso"""
    global progresso
    
    try:
        progresso[campeonato]['status'] = 'running'
        progresso[campeonato]['progresso'] = 10
        progresso[campeonato]['mensagem'] = 'Iniciando...'
        
        # Executa o script
        progresso[campeonato]['progresso'] = 30
        progresso[campeonato]['mensagem'] = 'Executando script...'
        
        result = subprocess.run(
            ['python', script],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        
        progresso[campeonato]['progresso'] = 80
        
        if result.returncode == 0:
            progresso[campeonato]['progresso'] = 90
            progresso[campeonato]['mensagem'] = 'Atualizando BestBet...'
            
            # Regenera o bestbet.html
            subprocess.run(
                ['python', 'gerar_bestbet.py'],
                capture_output=True,
                text=True,
                cwd=os.path.dirname(os.path.abspath(__file__))
            )
            
            progresso[campeonato]['progresso'] = 100
            progresso[campeonato]['status'] = 'success'
            progresso[campeonato]['mensagem'] = 'Concluído!'
            
            # Obtém a data de modificação do arquivo
            if os.path.exists(arquivo_html):
                mtime = os.path.getmtime(arquivo_html)
                data_modificacao = datetime.fromtimestamp(mtime).strftime('%d/%m/%Y %H:%M')
                progresso[campeonato]['data_modificacao'] = data_modificacao
        else:
            progresso[campeonato]['progresso'] = 100
            progresso[campeonato]['status'] = 'error'
            progresso[campeonato]['mensagem'] = f'Erro: {result.stderr}'
            
    except Exception as e:
        progresso[campeonato]['progresso'] = 100
        progresso[campeonato]['status'] = 'error'
        progresso[campeonato]['mensagem'] = f'Erro: {str(e)}'

@app.route('/')
def index():
    """Serve a página bestbet.html"""
    return send_file('bestbet.html')

@app.route('/<path:filename>')
def servir_arquivo(filename):
    """Serve arquivos HTML estáticos"""
    try:
        return send_file(filename)
    except FileNotFoundError:
        return jsonify({'error': 'Arquivo não encontrado'}), 404

@app.route('/atualizar/<campeonato>', methods=['POST'])
def atualizar(campeonato):
    """Inicia a atualização de um campeonato"""
    
    scripts = {
        'brasileirao': ('sofascore_to_html.py', 'sofascore_result.html'),
        'premier': ('gerar_html_pl.py', 'premier_league_analysis.html'),
        'laliga': ('gerar_html_laliga.py', 'laliga_analysis.html'),
        'seria': ('gerar_html_seria.py', 'seria_analysis.html'),
        'ligue1': ('gerar_html_ligue1.py', 'LIGUE1_analysis.html')
    }
    
    if campeonato not in scripts:
        return jsonify({'error': 'Campeonato inválido'}), 400
    
    if progresso[campeonato]['status'] == 'running':
        return jsonify({'error': 'Atualização já em andamento'}), 400
    
    # Reseta o progresso
    progresso[campeonato] = {'status': 'idle', 'progresso': 0, 'mensagem': ''}
    
    # Executa em thread separada para não bloquear
    script, arquivo = scripts[campeonato]
    thread = threading.Thread(target=executar_script, args=(campeonato, script, arquivo))
    thread.start()
    
    return jsonify({'success': True})

@app.route('/progresso/<campeonato>')
def obter_progresso(campeonato):
    """Retorna o progresso da atualização"""
    if campeonato not in progresso:
        return jsonify({'error': 'Campeonato inválido'}), 400
    
    return jsonify(progresso[campeonato])

@app.route('/data_modificacao/<campeonato>')
def obter_data_modificacao(campeonato):
    """Retorna a data de modificação do arquivo HTML"""
    arquivos = {
        'brasileirao': 'sofascore_result.html',
        'premier': 'premier_league_analysis.html',
        'laliga': 'laliga_analysis.html',
        'seria': 'seria_analysis.html',
        'ligue1': 'LIGUE1_analysis.html'
    }
    
    if campeonato not in arquivos:
        return jsonify({'error': 'Campeonato inválido'}), 400
    
    arquivo = arquivos[campeonato]
    if os.path.exists(arquivo):
        mtime = os.path.getmtime(arquivo)
        data_modificacao = datetime.fromtimestamp(mtime).strftime('%d/%m/%Y %H:%M')
        return jsonify({'data': data_modificacao})
    
    return jsonify({'data': 'N/A'})

if __name__ == '__main__':
    print("Servidor BestBet iniciado em http://localhost:5000")
    app.run(debug=True, port=5000)
