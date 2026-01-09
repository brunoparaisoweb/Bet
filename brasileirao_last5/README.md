# Brasileirão - últimos 5 jogos por time

Projeto Python simples que apresenta os últimos 5 jogos (resultados) de cada time
do Campeonato Brasileiro Série A.

Requisitos
- Python 3.8+
- Dependências: `requests` (veja `requirements.txt`)

Instalação

```bash
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
\.venv\Scripts\activate   # Windows PowerShell
pip install -r requirements.txt
```

Uso

1. Registre-se em https://www.football-data.org/ e obtenha uma API key (gratuito com limites).
2. Exporte a variável de ambiente `FOOTBALL_DATA_API_KEY` com a chave obtida.

Windows PowerShell:

```powershell
$env:FOOTBALL_DATA_API_KEY='f259f5faf95d420e9df7388e91d487c6'
python main.py
```

Linux/macOS:

```bash
export FOOTBALL_DATA_API_KEY='f259f5faf95d420e9df7388e91d487c6'
python main.py
```

Se você não fornecer uma chave, o script usará um `sample_data.json` de demonstração
e imprimirá dados simulados.

Observações
- O projeto usa o endpoint de competições de `football-data.org` com o código
  `BSA` (Campeonato Brasileiro Série A). Se a API mudar ou você preferir outra
  fonte (RapidAPI, API-Football, etc.), ajuste `main.py`.
