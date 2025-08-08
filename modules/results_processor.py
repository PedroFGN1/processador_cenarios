import json
import logging
from datetime import datetime
import pandas as pd

# Configura o logger para este módulo
logger = logging.getLogger(__name__)

def process_results(cenario: dict, forecast_df: pd.DataFrame, metrics: dict = None) -> list:
    """
    Processa os resultados de uma previsão, adicionando metadados do cenário,
    métricas de avaliação e preparando os dados para inserção no banco de dados.
    
    Args:
        cenario (dict): Dicionário contendo as informações do cenário
        forecast_df (pd.DataFrame): DataFrame com os resultados da previsão
        metrics (dict, optional): Dicionário com métricas de avaliação (RMSE, MAE, MAPE).
                                  Padrão para None.
    
    Returns:
        list: Lista de dicionários prontos para inserção no banco de dados
    """
    logger.info(f"Processando resultados para o cenário: {cenario["nome_cenario"]}")
    
    # Obtém a data/hora atual da execução
    data_execucao = datetime.now()
    
    # Converte os parâmetros do modelo para JSON string
    parametros_json = json.dumps(cenario["parametros"])
    
    # Lista para armazenar os registros processados
    processed_records = []
    
    # Processa cada linha do DataFrame de previsão
    for _, row in forecast_df.iterrows():
        record = {
            "nome_cenario": cenario["nome_cenario"],
            "data_execucao": data_execucao.isoformat(),
            "data_previsao": row["data_previsao"].strftime("%Y-%m-%d"),
            "valor_previsto": float(row["valor_previsto"]),
            "limite_inferior": float(row["limite_inferior"]) if pd.notna(row["limite_inferior"]) else None,
            "limite_superior": float(row["limite_superior"]) if pd.notna(row["limite_superior"]) else None,
            "modelo_utilizado": cenario["modelo"],
            "parametros_modelo": parametros_json,
            "rmse": metrics.get("rmse") if metrics else None,
            "mae": metrics.get("mae") if metrics else None,
            "mape": metrics.get("mape") if metrics else None
        }
        processed_records.append(record)
    
    logger.info(f"Processados {len(processed_records)} registros de previsão")
    return processed_records


