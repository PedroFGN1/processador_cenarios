import os
import sys

def get_config_path(path):
    """
    Retorna o caminho base para encontrar os arquivos de recurso.
    Args:
        path (str): O caminho relativo do arquivo a ser buscado.
    Returns:
        str: O caminho completo para o arquivo.
    """
    if getattr(sys, "frozen", False):
        # Se o programa estiver "congelado" (rodando como .exe)
        # o caminho base é o diretório temporário _MEIPASS
        return os.path.join(sys._MEIPASS, path)
    else:
        # Se estiver rodando como script .py normal
        # O caminho base é o diretório do script principal
        base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        return os.path.join(base_dir, path)
    return base_path
def get_database_path(path):
    """
    Retorna o caminho base para encontrar os arquivos de recurso.
    Args:
        path (str): O caminho relativo do arquivo a ser buscado.
    Returns:
        str: O caminho completo para o arquivo.
    """
    if getattr(sys, "frozen", False):
        # Se o programa estiver "congelado" (rodando como .exe)
        # o caminho base é o diretório temporário _MEIPASS
        return os.path.join(os.path.dirname(sys.executable), path)
    else:
        # Se estiver rodando como script .py normal
        # O caminho base é o diretório do script principal
        base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        return os.path.join(base_dir, path)