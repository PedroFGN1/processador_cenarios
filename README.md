# Processador de Cenários de Previsão de Séries Temporais

Esta é uma aplicação desktop desenvolvida em Python com CustomTkinter para gerenciar, executar e visualizar cenários de previsão de séries temporais. Ela suporta modelos como ARIMA, Prophet e RandomForest, permitindo a configuração de parâmetros e a persistência dos resultados em um banco de dados SQLite.

## Estrutura do Projeto

```
processador_cenarios/
├── main.py                          # Ponto de entrada da aplicação GUI
├── app_gui.py                       # Lógica da janela principal e navegação
├── config_manager_gui.py            # Lógica para gerenciamento de cenários (adicionar/editar/remover)
├── scenarios_config.yaml           # Arquivo de configuração dos cenários (editável via GUI)
├── requirements.txt                 # Lista de dependências Python
├── previsoes.db                     # Banco de dados SQLite para resultados das previsões
├── dados_bcb.db                     # Banco de dados SQLite de exemplo com dados históricos
├── create_dummy_db.py               # Script para gerar dados de exemplo para dados_bcb.db
├── methods/                         # Módulos de orquestração de execução
│   └── _run_forecasting.py          # Orquestrador de um único cenário
├── modules/                         # Módulos de lógica de negócio (carregamento, modelos, processamento, gráfico)
│   ├── chart_generator.py
│   ├── data_loader.py
│   ├── data_exporter.py
│   ├── forecasting_model.py
│   ├── results_processor.py
│   └── scenario_loader.py
├── persistence/                     # Módulos de persistência (adaptadores de banco de dados)
│   ├── base_adapter.py
│   └── sqlite_adapter.py
└── utils/                           # Módulos utilitários (caminho base, logger)
    ├── get_base_path.py
    └── logger_config.py
```

## Pré-requisitos

Certifique-se de ter o Python 3.11+ instalado em seu sistema.

## Instalação e Configuração

Siga os passos abaixo para configurar e executar a aplicação:

1.  **Descompacte o Projeto:**
    Se você recebeu um arquivo `.zip`, descompacte-o em um diretório de sua escolha.

2.  **Navegue até o Diretório do Projeto:**
    Abra um terminal ou prompt de comando e navegue até o diretório `processador_cenarios`:
    ```bash
    cd /caminho/para/processador_cenarios
    ```

3.  **Crie e Ative o Ambiente Virtual:**
    É altamente recomendável usar um ambiente virtual para isolar as dependências do projeto:
    ```bash
    python3.11 -m venv venv
    # No Windows:
    # .\venv\Scripts\activate
    # No Linux/macOS:
    source venv/bin/activate
    ```

4.  **Instale as Dependências:**
    Com o ambiente virtual ativado, instale todas as bibliotecas necessárias:
    ```bash
    pip install -r requirements.txt
    ```

5.  **Gere o Banco de Dados de Dados Históricos de Exemplo:**
    A aplicação precisa de dados históricos para realizar as previsões. Um script foi fornecido para criar um banco de dados de exemplo (`dados_bcb.db`):
    ```bash
    python create_dummy_db.py
    ```
    Este script criará o arquivo `dados_bcb.db` no diretório raiz do projeto com dados fictícios para as séries IPCA, SELIC e VENDAS_MENSAIS.

6. **Criação de Executável .exe**

    Para criar um executável `.exe`, execute este comando no terminal python no diretório raiz da aplicação.

    ```bash
    pyinstaller --noconsole --onefile --icon="assets/icon.ico" --add-data="scenarios_config.yaml;." --name="Scenario" main.py
    ```

    - `--noconsole`: este comando impede que a janela preta de terminal apareça por trás da janela da aplicação.
    - `--onefile`: Cria um único arquivo `.exe`.
    - `--icon="assets/icon.ico"`: Associa o ícone ao executável.
    - `--add-data="frontend;frontend"`: Comando para aplicações Eel, inclui arquivos HTML, CSS e JS no diretório raiz do executável. 
    - `--add-data="{}_config.yaml;."`: Inclui os arquivos de configuração `scenarios_config.yaml` no diretório raiz do executável.
    - `--name="Scenario"`: Define o nome do arquivo de saída.

## Como Executar a Aplicação

Após a instalação e configuração, execute a aplicação com o seguinte comando (certifique-se de que o ambiente virtual está ativado):

```bash
python main.py
```

## Instruções de Uso da GUI

Ao iniciar a aplicação, você verá uma janela com um menu de navegação à esquerda:

### 1. Gerenciar Cenários

Nesta aba, você pode configurar seus cenários de previsão:

-   **Visualizar Cenários:** Os cenários existentes no `scenarios_config.yaml` serão listados.
-   **Adicionar Novo:** Clique no botão "Adicionar Novo" para abrir um formulário. Preencha os detalhes do cenário (Nome, ID da Série, Modelo, Horizonte, Intervalo de Confiança e Parâmetros JSON) e clique em "Salvar".
    *   **Observação sobre Parâmetros JSON:** Para modelos como ARIMA, Prophet e RandomForest, os parâmetros específicos devem ser fornecidos em formato JSON válido (ex: `{"p": 5, "d": 1, "q": 0}` para ARIMA).
-   **Editar Selecionado:** (Funcionalidade em desenvolvimento para seleção na lista).
-   **Remover Selecionado:** (Funcionalidade em desenvolvimento para seleção na lista).

### 2. Executar Previsões

Nesta aba, você pode iniciar o processo de previsão:

-   **Iniciar Execução de Todos os Cenários:** Clique neste botão para que a aplicação execute todos os cenários configurados no `scenarios_config.yaml`.
-   **Logs de Execução:** A caixa de texto abaixo do botão exibirá logs em tempo real sobre o progresso de cada cenário (carregamento de dados, execução do modelo, salvamento de resultados).
    *   **Observação:** A execução ocorre em uma thread separada para evitar que a interface congele. Mensagens de sucesso ou erro serão exibidas em pop-ups ao final da execução.

### 3. Visualizar Resultados

Nesta aba, você pode consultar os resultados das previsões salvas:

-   **Atualizar Resultados:** Clique neste botão para carregar e exibir os resultados mais recentes do banco de dados `previsoes.db` em uma tabela.
-   **Tabela de Resultados:** Os resultados serão exibidos em formato tabular, incluindo o nome do cenário, data da execução, data da previsão, valor previsto, limites de confiança e modelo utilizado.

## Observações Importantes para Testes

-   **Dados Históricos:** O script `create_dummy_db.py` gera dados fictícios. Para testes mais realistas, você pode substituir o `dados_bcb.db` por um banco de dados real com suas séries temporais, garantindo que a tabela seja `dados_bcb` e contenha as colunas `serie_id`, `data` e `valor`.
-   **Parâmetros dos Modelos:** Certifique-se de que os parâmetros JSON fornecidos para cada modelo (`ARIMA`, `Prophet`, `RandomForest`) estejam corretos e correspondam ao esperado pelo modelo.
-   **Logs:** Monitore a saída do terminal onde você iniciou a aplicação e a caixa de logs na GUI para identificar quaisquer erros ou avisos durante a execução.
-   **Empacotamento:** A fase final do projeto incluirá o empacotamento da aplicação em um executável único usando PyInstaller, o que facilitará a distribuição para usuários finais sem a necessidade de instalar Python ou dependências. (Esta etapa ainda não foi realizada).

## Licença e Suporte

Este projeto foi desenvolvido como uma ferramenta de código aberto para facilitar o controle de cenários de previsão de séries temporais.
## 👨‍💻 Autor: Pedro Ferreira Galvão Neto

---