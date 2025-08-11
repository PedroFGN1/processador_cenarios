# Análise do Projeto: Processador de Cenários de Previsão de Séries Temporais

## 1. Visão Geral do Projeto

O projeto "Processador de Cenários de Previsão de Séries Temporais" é uma aplicação desktop desenvolvida em Python, utilizando a biblioteca CustomTkinter para a interface gráfica. Seu objetivo principal é permitir que o usuário gerencie, execute e visualize cenários de previsão para séries temporais. A aplicação suporta a integração de diferentes modelos de previsão (ARIMA, Prophet, RandomForest) e persiste os resultados em um banco de dados SQLite.

## 2. Estrutura do Projeto

A estrutura do repositório é bem organizada e modular, facilitando a compreensão e manutenção. Os principais diretórios e arquivos são:

-   `main.py`: Ponto de entrada da aplicação, responsável por inicializar a interface gráfica.
-   `app_gui.py`: Contém a lógica principal da interface do usuário, incluindo a navegação entre as diferentes seções (Gerenciar Cenários, Executar Previsões, Visualizar Resultados).
-   `config_manager_gui.py`: Lida com a interface e a lógica para adicionar, editar e remover cenários de previsão.
-   `scenarios_config.yaml`: Arquivo YAML que armazena as configurações dos cenários de previsão, carregado e manipulado pela GUI.
-   `requirements.txt`: Lista as dependências Python necessárias para o projeto.
-   `create_dummy_db.py`: Script para gerar um banco de dados SQLite de exemplo (`dados_bcb.db`) com dados históricos fictícios.
-   `methods/`: Contém módulos de orquestração de execução, como `_run_forecasting.py`, que coordena a execução de um único cenário.
-   `modules/`: Agrupa a lógica de negócio principal, incluindo:
    -   `data_loader.py`: Responsável por carregar dados históricos do banco de dados.
    -   `data_exporter.py`: (Não analisado em detalhes, mas presumivelmente para exportação de dados).
    -   `forecasting_model.py`: Implementa a fábrica de modelos e as classes para ARIMA, Prophet e RandomForest.
    -   `results_processor.py`: Processa os resultados das previsões para serem salvos no banco de dados.
    -   `scenario_loader.py`: Carrega as configurações dos cenários do arquivo YAML.
-   `persistence/`: Contém adaptadores para persistência de dados, como `sqlite_adapter.py` para interação com o SQLite.
-   `utils/`: Módulos utilitários, como `get_base_path.py` e `logger_config.py`.

## 3. Funcionalidades Principais

A aplicação oferece as seguintes funcionalidades através de sua interface gráfica:

### 3.1. Gerenciamento de Cenários

*   **Criação e Edição:** Permite adicionar novos cenários de previsão e editar os existentes através de uma interface gráfica.
*   **Remoção:** Possibilita a exclusão de cenários configurados.
*   **Seleção de Séries:** Permite associar cenários a diferentes séries temporais disponíveis no banco de dados.
*   **Configuração de Modelos:** Suporte para diferentes modelos de previsão (ARIMA, Prophet, RandomForest) com configuração de parâmetros.
*   **Importação de Dados:** Capacidade de importar dados históricos de séries temporais a partir de arquivos CSV e Excel, servindo como base para futuras integrações de dados.

Permite ao usuário definir e armazenar diferentes cenários de previsão. Cada cenário inclui:
-   Nome do cenário
-   ID da série temporal a ser prevista
-   Modelo de previsão (ARIMA, Prophet, RandomForest)
-   Parâmetros específicos do modelo (em formato JSON)
-   Horizonte de previsão
-   Intervalo de confiança

Os cenários são salvos no arquivo `scenarios_config.yaml`.

### 3.2. Execução de Previsões

O usuário pode iniciar a execução de todos os cenários configurados. A execução ocorre em uma thread separada para não bloquear a GUI, e os logs de progresso são exibidos em tempo real na interface. Após a execução, os resultados são salvos em um banco de dados SQLite (`previsoes.db`).

*   **Execução em Lote:** Permite executar previsões para todos os cenários configurados de uma só vez.
*   **Feedback de Progresso:** Exibe uma barra de progresso e mensagens de status durante a execução.
*   **Registro de Logs:** Detalhes da execução são registrados em tempo real em uma área de logs na interface.

### 3.3. Visualização de Resultados

*   **Tabela de Resultados:** Exibe os resultados de todas as previsões realizadas em uma tabela organizada.
*   **Gráficos Interativos:** Permite visualizar graficamente os dados históricos e as previsões para cenários selecionados.
*   **Seleção Múltipla:** Suporte para selecionar múltiplos cenários na tabela e visualizá-los simultaneamente no gráfico para comparação.
*   **Comparação de Cenários:** Facilita a análise comparativa entre diferentes modelos ou configurações de cenários através da sobreposição de gráficos.
*   **Métricas de Avaliação:** Exibe métricas de desempenho do modelo (RMSE, MAE, MAPE) para cada previsão, permitindo uma análise quantitativa.
*   **Frequência da Série:** A frequência inferida da série temporal é armazenada e exibida, auxiliando na compreensão dos dados.

### 3.4. Exportação de Resultados

*   **Exportação para CSV:** Permite exportar todos os resultados da previsão para um arquivo CSV.
*   **Exportação para Excel:** Permite exportar todos os resultados da previsão para um arquivo Excel.

## 4. Arquitetura e Fluxo de Dados

A arquitetura do projeto é baseada em módulos bem definidos, seguindo um fluxo lógico:

1.  **Configuração:** Cenários são definidos via GUI e salvos em `scenarios_config.yaml`.
2.  **Carregamento de Dados:** Quando um cenário é executado, `data_loader.py` carrega os dados históricos da série especificada de `dados_bcb.db`.
3.  **Modelagem e Previsão:** `forecasting_model.py` instancia o modelo de previsão apropriado (ARIMA, Prophet, RandomForest) com base na configuração do cenário e executa a previsão.
4.  **Processamento de Resultados:** `results_processor.py` formata os resultados da previsão, adicionando metadados do cenário e a data de execução.
5.  **Persistência:** `sqlite_adapter.py` é utilizado para salvar os resultados processados no banco de dados `previsoes.db`.

## 5. Pontos Fortes e Boas Práticas

-   **Modularidade:** O código é bem dividido em módulos com responsabilidades claras (GUI, lógica de negócio, persistência, utilitários).
-   **Separação de Preocupações:** A lógica da interface (CustomTkinter) está separada da lógica de negócio e persistência.
-   **Extensibilidade de Modelos:** A arquitetura com `BaseModel` e `forecast_factory` facilita a adição de novos modelos de previsão no futuro.
-   **Persistência de Dados:** Utilização de SQLite para armazenar dados históricos e resultados de previsão, garantindo que os dados sejam mantidos entre as sessões.
-   **Configuração Flexível:** O uso de um arquivo YAML para cenários permite fácil configuração e modificação.
-   **GUI Responsiva:** A execução de previsões em uma thread separada evita que a interface congele, proporcionando uma melhor experiência ao usuário.
-   **Logging:** A presença de um sistema de logging (`logger_config.py`) ajuda no rastreamento de eventos e depuração.

