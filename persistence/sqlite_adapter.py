import sqlite3
import logging
from .base_adapter import BaseAdapter

class SqliteAdapter(BaseAdapter):
    """
    Implementação concreta do adaptador para bancos de dados SQLite.
    """
    
    def __enter__(self):
        """
        Estabelece a conexão com o banco de dados SQLite.
        """
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row  # Permite acesso por nome de coluna
            return self
        except Exception as e:
            logging.error(f"Erro ao conectar com o banco de dados {self.db_path}: {e}")
            raise
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Fecha a conexão com o banco de dados.
        """
        if self.connection:
            self.connection.close()
    
    def create_schema_if_not_exists(self):
        """
        Cria a tabela de resultados de previsão se ela não existir.
        """
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS resultados_previsao (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_cenario TEXT NOT NULL,
            data_execucao TIMESTAMP NOT NULL,
            data_previsao DATE NOT NULL,
            valor_previsto REAL NOT NULL,
            limite_inferior REAL,
            limite_superior REAL,
            modelo_utilizado TEXT NOT NULL,
            parametros_modelo TEXT
        )
        """
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(create_table_sql)
            self.connection.commit()
            logging.info("Esquema do banco de dados verificado/criado com sucesso.")
        except Exception as e:
            logging.error(f"Erro ao criar esquema do banco de dados: {e}")
            raise
    
    def insert_many(self, table_name, data):
        """
        Insere múltiplos registros na tabela especificada.
        
        Args:
            table_name (str): Nome da tabela
            data (list): Lista de dicionários com os dados
        """
        if not data:
            logging.warning("Nenhum dado fornecido para inserção.")
            return
        
        # Obtém as colunas do primeiro registro
        columns = list(data[0].keys())
        placeholders = ', '.join(['?' for _ in columns])
        columns_str = ', '.join(columns)
        
        sql = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
        
        try:
            cursor = self.connection.cursor()
            # Converte os dicionários em tuplas na ordem correta das colunas
            values = [tuple(record[col] for col in columns) for record in data]
            cursor.executemany(sql, values)
            self.connection.commit()
            logging.info(f"Inseridos {len(data)} registros na tabela {table_name}.")
        except Exception as e:
            logging.error(f"Erro ao inserir dados na tabela {table_name}: {e}")
            raise
    
    def query(self, sql, params=None):
        """
        Executa uma consulta SQL e retorna os resultados.
        
        Args:
            sql (str): Comando SQL
            params (tuple, optional): Parâmetros para a consulta
        
        Returns:
            list: Lista de sqlite3.Row objects
        """
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)
            return cursor.fetchall()
        except Exception as e:
            logging.error(f"Erro ao executar consulta SQL: {e}")
            raise

