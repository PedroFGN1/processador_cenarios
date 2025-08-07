import logging
import sys
from datetime import datetime

def setup_logger(name="processador_cenarios", level=logging.INFO):
    """
    Configura e retorna um logger para a aplicação.
    
    Args:
        name (str): Nome do logger
        level: Nível de logging (default: INFO)
    
    Returns:
        logging.Logger: Logger configurado
    """
    # Cria o logger
    logger = logging.getLogger(name)
    
    # Evita duplicação de handlers se a função for chamada múltiplas vezes
    if logger.handlers:
        return logger
    
    logger.setLevel(level)
    
    # Cria um handler para o console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    # Define o formato das mensagens
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    
    # Adiciona o handler ao logger
    logger.addHandler(console_handler)
    
    return logger

class GuiLogHandler(logging.Handler):
    """
    Handler customizado para enviar logs para um widget de texto da GUI.
    """
    def __init__(self, text_widget=None):
        super().__init__()
        self.text_widget = text_widget
    
    def emit(self, record):
        """
        Emite uma mensagem de log para o widget de texto.
        """
        if self.text_widget:
            try:
                msg = self.format(record)
                # Adiciona a mensagem ao widget de texto
                self.text_widget.insert("end", msg + "\n")
                # Faz scroll automático para a última linha
                self.text_widget.see("end")
            except Exception:
                # Se houver erro, não faz nada para evitar quebrar a aplicação
                pass

