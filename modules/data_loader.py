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

def get_available_series(db_path: Path) -> list:
    """
    Retorna uma lista de todos os IDs de série únicos disponíveis no banco de dados.

    Args:
        db_path (Path): Caminho para o banco de dados SQLite.

    Returns:
        list: Uma lista de strings com os IDs das séries disponíveis.
    """
    logger.info(f"Buscando séries disponíveis em: {db_path}")
    sql = "SELECT DISTINCT serie_id FROM dados_bcb ORDER BY serie_id"
    try:
        with SqliteAdapter(str(db_path)) as adapter:
            results = adapter.query(sql)
            series_ids = [row["serie_id"] for row in results]
            logger.info(f"Séries disponíveis encontradas: {series_ids}")
            return series_ids
    except Exception as e:
        logger.error(f"Erro ao buscar séries disponíveis: {e}")
        return []

def infer_frequency(df: pd.DataFrame) -> str:
    """
    Tenta inferir a frequência de uma série temporal a partir de seu índice de data.

    Args:
        df (pd.DataFrame): DataFrame com um índice de data/hora.

    Returns:
        str: A string da frequência inferida (ex: 'D', 'M', 'A') ou None se não puder ser inferida.
    """
    traducao_freq = {
        "D": "diário",
        "M": "mensal (fim do mês)",
        "MS": "mensal (início do mês)",
        "A": "anual",
        "Y": "anual",
        "H": "horário",
        "T": "minutário",
        "min": "minutário",
        "S": "segundos",
        "Q": "trimestral (fim do trimestre)",
        "QS": "trimestral (início do trimestre)"
    }
    
    if not isinstance(df.index, pd.DatetimeIndex):
        df["data"] = pd.to_datetime(df["data"])
        df = df.set_index("data").sort_index()

    freq = pd.infer_freq(df.index)
    if freq in traducao_freq:
        logger.info(f"Frequência inferida {freq} traduzida para: {traducao_freq[freq]}")
        freq = traducao_freq[freq]
        return freq
    else:
        logger.warning(f"Frequência inferida {freq} não reconhecida. Retornando como está.")
        return freq

def load_data_from_csv(file_path: Path) -> pd.DataFrame:
    """
    Carrega dados de um arquivo CSV.

    Args:
        file_path (Path): Caminho para o arquivo CSV.

    Returns:
        pd.DataFrame: DataFrame com os dados do CSV.
    """
    logger.info(f"Carregando dados do CSV: {file_path}")
    try:
        df = pd.read_csv(file_path)
        # Tentar padronizar colunas para 'data' e 'valor'
        if 'data' in df.columns.str.lower() and 'valor' in df.columns.str.lower():
            df.columns = df.columns.str.lower()
            df = df[['data', 'valor']]
        else:
            raise ValueError("O arquivo CSV deve conter colunas 'data' e 'valor'.")
        df['data'] = pd.to_datetime(df['data'])
        df['valor'] = pd.to_numeric(df['valor'])
        logger.info(f"Carregados {len(df)} registros do CSV.")
        return df
    except Exception as e:
        logger.error(f"Erro ao carregar dados do CSV {file_path}: {e}")
        raise

def load_data_from_excel(file_path: Path, sheet_name: str = None) -> pd.DataFrame:
    """
    Carrega dados de um arquivo Excel.

    Args:
        file_path (Path): Caminho para o arquivo Excel.
        sheet_name (str, optional): Nome da planilha a ser carregada. Se None, carrega a primeira planilha.

    Returns:
        pd.DataFrame: DataFrame com os dados do Excel.
    """
    logger.info(f"Carregando dados do Excel: {file_path}, planilha: {sheet_name or 'primeira'}")
    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        # Tentar padronizar colunas para 'data' e 'valor'
        if 'data' in df.columns.str.lower() and 'valor' in df.columns.str.lower():
            df.columns = df.columns.str.lower()
            df = df[['data', 'valor']]
        else:
            raise ValueError("O arquivo Excel deve conter colunas 'data' e 'valor'.")
        df['data'] = pd.to_datetime(df['data'])
        df['valor'] = pd.to_numeric(df['valor'])
        logger.info(f"Carregados {len(df)} registros do Excel.")
        return df
    except Exception as e:
        logger.error(f"Erro ao carregar dados do Excel {file_path}: {e}")
        raise
