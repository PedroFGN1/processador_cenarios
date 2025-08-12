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
            if not self.connection:
                raise Exception(f"Não foi possível conectar ao banco de dados {self.db_path}.")
                # Criar banco de dados se não existir
                
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
        Adiciona colunas para métricas de avaliação e frequência da série se não existirem.
        """
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS resultados_previsao (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_cenario TEXT NOT NULL,
            serie_id TEXT NOT NULL,
            data_execucao TIMESTAMP NOT NULL,
            data_previsao DATE NOT NULL,
            frequencia_serie TEXT,
            valor_previsto REAL NOT NULL,
            limite_inferior REAL,
            limite_superior REAL,
            modelo_utilizado TEXT NOT NULL,
            parametros_modelo TEXT,
            rmse REAL,
            mae REAL,
            mape REAL
        )
        """
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(create_table_sql)
            
            # Adicionar colunas se não existirem (para compatibilidade com DBs existentes)
            self._add_column_if_not_exists(cursor, "resultados_previsao", "rmse", "REAL")
            self._add_column_if_not_exists(cursor, "resultados_previsao", "mae", "REAL")
            self._add_column_if_not_exists(cursor, "resultados_previsao", "mape", "REAL")
            self._add_column_if_not_exists(cursor, "resultados_previsao", "frequencia_serie", "TEXT")

            self.connection.commit()
            logging.info("Esquema do banco de dados verificado/criado com sucesso.")
        except Exception as e:
            logging.error(f"Erro ao criar esquema do banco de dados: {e}")
            raise

    def _add_column_if_not_exists(self, cursor, table_name, column_name, column_type):
        """
        Adiciona uma coluna a uma tabela se ela ainda não existir.
        """
        try:
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [info[1] for info in cursor.fetchall()]
            if column_name not in columns:
                cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}")
                logging.info(f"Coluna {column_name} adicionada à tabela {table_name}.")
        except Exception as e:
            logging.error(f"Erro ao adicionar coluna {column_name} à tabela {table_name}: {e}")
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
        placeholders = ", ".join(["?" for _ in columns])
        columns_str = ", ".join(columns)
        
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

    def execute(self, sql, params=None):
        """
        Executa comandos de escrita (INSERT, UPDATE, DELETE).
        Faz commit automático.
        """
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)
            self.connection.commit()
        except Exception as e:
            logging.error(f"Erro ao executar comando de escrita: {e}")
            raise

