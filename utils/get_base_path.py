import os
import sys
from pathlib import Path

def get_base_path(path):
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

# Função Alternativa não utilizada    
def get_base_path2():
    """
    Versão robusta com múltiplas estratégias de detecção.

    Returns:
        Path: Caminho absoluto para o diretório raiz do projeto
    """
    if getattr(sys, 'frozen', False):
        # Executando como executável PyInstaller
        if hasattr(sys, '_MEIPASS'):
            # Diretório temporário do PyInstaller existe
            # Usar diretório do executável em vez do temporário
            base_path = Path(sys.executable).parent
        else:
            # Fallback para sys.argv[0]
            base_path = Path(os.path.dirname(sys.argv[0]))
    else:
        # Executando como script Python normal
        current_file_path = Path(__file__).resolve()
        base_path = current_file_path.parent.parent

    return base_path