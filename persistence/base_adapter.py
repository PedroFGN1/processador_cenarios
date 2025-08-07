from abc import ABC, abstractmethod

class BaseAdapter(ABC):
    """
    Classe base abstrata para adaptadores de banco de dados.
    Define a interface que todos os adaptadores concretos devem implementar.
    """
    
    def __init__(self, db_path):
        """
        Inicializa o adaptador com o caminho do banco de dados.
        
        Args:
            db_path (str): Caminho para o arquivo do banco de dados
        """
        self.db_path = db_path
        self.connection = None
    
    @abstractmethod
    def __enter__(self):
        """
        Método para usar o adaptador com a sintaxe 'with'.
        Deve estabelecer a conexão com o banco de dados.
        """
        pass
    
    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Método para usar o adaptador com a sintaxe 'with'.
        Deve fechar a conexão com o banco de dados.
        """
        pass
    
    @abstractmethod
    def create_schema_if_not_exists(self):
        """
        Cria o esquema do banco de dados (tabelas) se elas não existirem.
        """
        pass
    
    @abstractmethod
    def insert_many(self, table_name, data):
        """
        Insere múltiplos registros em uma tabela.
        
        Args:
            table_name (str): Nome da tabela
            data (list): Lista de dicionários com os dados a serem inseridos
        """
        pass
    
    @abstractmethod
    def query(self, sql, params=None):
        """
        Executa uma consulta SQL e retorna os resultados.
        
        Args:
            sql (str): Comando SQL a ser executado
            params (tuple, optional): Parâmetros para a consulta
        
        Returns:
            list: Lista de tuplas com os resultados da consulta
        """
        pass

