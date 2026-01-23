# 🏆 BestBet - Sistema de Atualização Automática

## Como Usar

### 1. Iniciar o Servidor

Execute o arquivo `iniciar_servidor.bat` ou rode o comando:

```bash
python server_bestbet.py
```

O servidor será iniciado em: **http://localhost:5000**

### 2. Acessar a Página BestBet

Abra seu navegador e acesse: **http://localhost:5000**

### 3. Atualizar Campeonatos

Cada seção de campeonato agora possui:

- **📅 Data de Atualização**: Mostra quando o arquivo foi gerado pela última vez
- **🔄 Botão de Atualização**: Clique para atualizar os dados do campeonato
- **📊 Barra de Progresso**: Mostra o andamento da atualização em tempo real
- **ℹ️ Botão de Detalhes**: Link para ver a análise completa

### 4. Como Funciona a Atualização

Quando você clica no botão de atualização (🔄):

1. O sistema executa o script Python correspondente ao campeonato
2. Uma barra de progresso mostra o andamento
3. Os dados são atualizados automaticamente
4. A data de modificação é atualizada
5. A página é recarregada automaticamente

### Scripts por Campeonato

| Campeonato | Script | Arquivo Gerado |
|------------|--------|----------------|
| 🇧🇷 Brasileirão | `sofascore_to_html.py` | `sofascore_result.html` |
| 🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League | `gerar_html_pl.py` | `premier_league_analysis.html` |
| 🇪🇸 La Liga | `gerar_html_laliga.py` | `laliga_analysis.html` |
| 🇮🇹 Serie A | `gerar_html_seria.py` | `seria_analysis.html` |
| 🇫🇷 Ligue 1 | `gerar_html_ligue1.py` | `LIGUE1_analysis.html` |

### Requisitos

- Python 3.x
- Flask
- Flask-CORS
- BeautifulSoup4
- Outras dependências dos scripts de scraping

### Instalação de Dependências

```bash
pip install flask flask-cors beautifulsoup4
```

### Solução de Problemas

**Erro: "Servidor não está rodando"**
- Certifique-se de que o servidor foi iniciado corretamente
- Verifique se a porta 5000 não está sendo usada por outro programa

**Erro: "Atualização falhou"**
- Verifique os logs do servidor no terminal
- Certifique-se de que todos os scripts Python estão funcionando corretamente

**Barra de progresso não aparece**
- Limpe o cache do navegador
- Recarregue a página com Ctrl+F5

## Tecnologias Utilizadas

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript
- **API**: REST API com endpoints para atualização e progresso
- **Threading**: Execução assíncrona para não bloquear a interface
