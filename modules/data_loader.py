import pandas as pd
import logging
from pathlib import Path
from persistence.sqlite_adapter import SqliteAdapter

# Configura o logger para este módulo
logger = logging.getLogger(__name__)

def load_historical_data(serie_id: str, db_path: Path) -> pd.DataFrame:
    """
    Carrega dados históricos de uma série temporal do banco de dados.

    Args:
        serie_id (str): Identificador da série temporal.
        db_path (Path): Caminho para o banco de dados SQLite.

    Returns:
        pd.DataFrame: DataFrame com colunas "data" (datetime) e "valor" (float).

    Raises:
        ValueError: Se nenhum dado for encontrado para a série especificada.
        Exception: Para outros erros de banco de dados.
    """
    logger.info(f"Carregando dados históricos para a série: {serie_id}")

    # SQL para buscar os dados da série
    sql = """
    SELECT data, valor 
    FROM dados_bcb 
    WHERE serie_id = ? 
    ORDER BY data
    """

    try:
        with SqliteAdapter(str(db_path)) as adapter:
            results = adapter.query(sql, (serie_id,))

            if not results:
                logger.error(f"Nenhum dado encontrado para a série {serie_id}")
                raise ValueError(f"Nenhum dado encontrado para a série {serie_id}")

            # Converte os resultados para DataFrame
            data = []
            for row in results:
                data.append({
                    "data": row["data"],
                    "valor": row["valor"]
                })

            df = pd.DataFrame(data)

            # Converte os tipos de dados
            df["data"] = pd.to_datetime(df["data"])
            df["valor"] = df["valor"].astype(float)

            logger.info(f"Carregados {len(df)} registros para a série {serie_id}")
            return df

    except Exception as e:
        logger.error(f"Erro ao carregar dados para a série {serie_id}: {e}")
        raise

