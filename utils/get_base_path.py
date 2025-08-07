import os
from pathlib import Path

def get_base_path():
    """
    Retorna o caminho absoluto para o diretório raiz do projeto.
    Isso é útil para localizar arquivos de configuração, bancos de dados, etc.,
    independentemente de onde o script é executado.
    """
    # Obtém o caminho do arquivo atual
    current_file_path = Path(__file__).resolve()

    # Navega para o diretório raiz do projeto (assumindo que este script está em utils/)
    # Pode ser necessário ajustar se a estrutura de pastas mudar
    base_path = current_file_path.parent.parent

    return base_path

