import yaml
import logging
from pathlib import Path

# Configura o logger para este módulo
logger = logging.getLogger(__name__)

def load_scenarios(config_path) -> list:
    """
    Carrega os cenários de previsão de um arquivo YAML.

    Args:
        config_path (Path): Caminho para o arquivo de configuração YAML.

    Returns:
        list: Uma lista de dicionários, onde cada dicionário representa um cenário.

    Raises:
        FileNotFoundError: Se o arquivo de configuração não for encontrado.
        ValueError: Se o arquivo YAML estiver malformado ou não contiver a chave 'cenarios'.
    """
    if not config_path:
        logger.error(f"Arquivo de configuração não encontrado: {config_path}")
        raise FileNotFoundError(f"Arquivo de configuração não encontrado: {config_path}")

    try:
        with open(config_path, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
    except yaml.YAMLError as e:
        logger.error(f"Erro ao parsear o arquivo YAML {config_path}: {e}")
        raise ValueError(f"Arquivo YAML malformado: {e}")

    if not isinstance(config, dict) or 'cenarios' not in config or not isinstance(config['cenarios'], list):
        logger.error(f"Estrutura inválida no arquivo de configuração. Esperado uma chave 'cenarios' como lista.")
        raise ValueError("Estrutura inválida no arquivo de configuração. Esperado uma chave 'cenarios' como lista.")

    logger.info(f"Cenários carregados com sucesso de {config_path}.")
    return config['cenarios']

