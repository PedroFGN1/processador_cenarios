import logging
from pathlib import Path
from datetime import datetime
import pandas as pd

from modules.data_loader import load_historical_data, infer_frequency # Importa infer_frequency
from modules.forecasting_model import forecast_factory
from modules.results_processor import process_results
from modules.model_evaluator import calculate_metrics
from persistence.sqlite_adapter import SqliteAdapter

# Configura o logger para este módulo
logger = logging.getLogger(__name__)

def run_single_scenario(
    cenario: dict,
    data_db_path: Path,
    results_db_path: Path
) -> None:
    """
    Executa um único cenário de previsão de ponta a ponta.

    Args:
        cenario (dict): Dicionário contendo as informações do cenário.
        data_db_path (Path): Caminho para o banco de dados de dados históricos (dados_bcb.db).
        results_db_path (Path): Caminho para o banco de dados de resultados (previsoes.db).
    """
    nome_cenario = cenario.get("nome_cenario", "Cenário Desconhecido")
    serie_id = cenario.get("serie_id")
    modelo_nome = cenario.get("modelo")
    horizonte = cenario.get("horizonte_previsao")
    parametros = cenario.get("parametros", {})

    logger.info(f"Iniciando execução do cenário: {nome_cenario} (Série: {serie_id}, Modelo: {modelo_nome})")

    try:
        # 1. Carregar dados históricos
        historical_data = load_historical_data(serie_id, data_db_path)
        logger.info(f"Dados históricos carregados para {serie_id}. Total de {len(historical_data)} registros.")

        if historical_data.empty or len(historical_data) < horizonte + 1: # +1 para ter pelo menos um ponto de treino
            logger.warning(f"Dados insuficientes para o cenário {nome_cenario}. Mínimo de {horizonte + 1} pontos necessários.")
            return

        # Inferir frequência da série temporal
        frequency = infer_frequency(historical_data)
        logger.info(f"Frequência inferida para a série {serie_id}: {frequency}")

        # Dividir dados em treino e teste para avaliação
        train_data = historical_data.iloc[:-horizonte]
        test_data = historical_data.iloc[-horizonte:]

        # 2. Instanciar e executar o modelo de previsão
        model = forecast_factory(modelo_nome)
        
        # Previsão no conjunto de teste para avaliação
        forecast_test_df = model.predict(train_data, horizonte, **parametros)
        logger.info(f"Previsão no conjunto de teste concluída para o cenário {nome_cenario}.")

        # Calcular métricas de avaliação
        metrics = calculate_metrics(test_data["valor"].reset_index(drop=True), forecast_test_df["valor_previsto"].reset_index(drop=True))
        logger.info(f"Métricas de avaliação para {nome_cenario}: {metrics}")

        # Previsão final usando todos os dados históricos para o horizonte real
        final_forecast_df = model.predict(historical_data, horizonte, **parametros)
        logger.info(f"Previsão final concluída para o cenário {nome_cenario}.")

        # 3. Processar resultados para inserção no banco de dados
        # Passa as métricas e a frequência para o processador de resultados
        processed_records = process_results(cenario, final_forecast_df, metrics, frequency) # Passa a frequência
        logger.info(f"Resultados processados para o cenário {nome_cenario}. Total de {len(processed_records)} registros de previsão.")

        # 4. Salvar resultados no banco de dados
        with SqliteAdapter(str(results_db_path)) as adapter:
            adapter.create_schema_if_not_exists()
            adapter.insert_many("resultados_previsao", processed_records)
        logger.info(f"Resultados do cenário {nome_cenario} salvos no banco de dados.")

    except ValueError as ve:
        logger.error(f"Erro de validação no cenário {nome_cenario}: {ve}")
    except Exception as e:
        logger.error(f"Erro inesperado ao executar o cenário {nome_cenario}: {e}", exc_info=True)

    logger.info(f"Execução do cenário {nome_cenario} finalizada.")


