import pandas as pd
import logging
from pathlib import Path

# Configura o logger para este módulo
logger = logging.getLogger(__name__)

def export_to_csv(data: list, filepath: Path) -> None:
    """
    Exporta uma lista de dicionários para um arquivo CSV.
    
    Args:
        data (list): Lista de dicionários com os dados a serem exportados
        filepath (Path): Caminho completo para o arquivo CSV de destino
    
    Raises:
        ValueError: Se a lista de dados estiver vazia
        Exception: Para outros erros durante a exportação
    """
    if not data:
        logger.warning("Nenhum dado fornecido para exportação")
        raise ValueError("Nenhum dado fornecido para exportação")
    
    try:
        # Converte a lista de dicionários para DataFrame
        df = pd.DataFrame(data)
        
        # Garante que o diretório de destino existe
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        # Exporta para CSV
        df.to_csv(filepath, index=False, encoding='utf-8')
        
        logger.info(f"Dados exportados com sucesso para: {filepath}")
        logger.info(f"Total de registros exportados: {len(data)}")
        
    except Exception as e:
        logger.error(f"Erro ao exportar dados para CSV: {e}")
        raise

