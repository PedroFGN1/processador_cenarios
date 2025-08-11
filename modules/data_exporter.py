import pandas as pd
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def export_dataframe_to_csv(df: pd.DataFrame, file_path: Path) -> bool:
    """
    Exporta um DataFrame para um arquivo CSV.

    Args:
        df (pd.DataFrame): O DataFrame a ser exportado.
        file_path (Path): O caminho completo para o arquivo CSV de saída.

    Returns:
        bool: True se a exportação for bem-sucedida, False caso contrário.
    """
    try:
        if 'id' in df.columns:
            df = df.drop(columns=['id'])  # Remove a coluna 'id' se existir
        df.to_csv(file_path, index=False, encoding="utf-8")
        logger.info(f"DataFrame exportado com sucesso para CSV: {file_path}")
        return True
    except Exception as e:
        logger.error(f"Erro ao exportar DataFrame para CSV {file_path}: {e}")
        return False

def export_dataframe_to_excel(df: pd.DataFrame, file_path: Path) -> bool:
    """
    Exporta um DataFrame para um arquivo Excel.

    Args:
        df (pd.DataFrame): O DataFrame a ser exportado.
        file_path (Path): O caminho completo para o arquivo Excel de saída.

    Returns:
        bool: True se a exportação for bem-sucedida, False caso contrário.
    """
    try:
        if 'id' in df.columns:
            df = df.drop(columns=['id'])  # Remove a coluna 'id' se existir
        df.to_excel(file_path, index=False, engine="openpyxl")
        logger.info(f"DataFrame exportado com sucesso para Excel: {file_path}")
        return True
    except Exception as e:
        logger.error(f"Erro ao exportar DataFrame para Excel {file_path}: {e}")
        return False


