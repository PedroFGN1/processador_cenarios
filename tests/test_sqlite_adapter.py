import pytest
import sqlite3
from pathlib import Path
from persistence.sqlite_adapter import SqliteAdapter

# Fixture para criar um banco de dados SQLite temporário para cada teste
@pytest.fixture
def temp_db_path(tmp_path):
    db_file = tmp_path / "test_db.db"
    return str(db_file)

# Teste de conexão e criação de esquema
def test_create_schema_if_not_exists(temp_db_path):
    with SqliteAdapter(temp_db_path) as adapter:
        adapter.create_schema_if_not_exists()

    # Verificar se a tabela foi criada e as colunas existem
    conn = sqlite3.connect(temp_db_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(resultados_previsao)")
    columns = [info[1] for info in cursor.fetchall()]
    conn.close()

    expected_columns = [
        "id", "nome_cenario", "serie_id", "data_execucao", "data_previsao",
        "frequencia_serie", "valor_previsto", "limite_inferior", "limite_superior",
        "modelo_utilizado", "parametros_modelo", "rmse", "mae", "mape"
    ]
    for col in expected_columns:
        assert col in columns

# Teste de inserção de múltiplos registros
def test_insert_many(temp_db_path):
    with SqliteAdapter(temp_db_path) as adapter:
        adapter.create_schema_if_not_exists()
        data_to_insert = [
            {
                "nome_cenario": "Cenario A",
                "serie_id": "SERIE001",
                "data_execucao": "2023-01-01 10:00:00",
                "data_previsao": "2023-01-02",
                "frequencia_serie": "D",
                "valor_previsto": 100.5,
                "limite_inferior": 90.0,
                "limite_superior": 110.0,
                "modelo_utilizado": "ARIMA",
                "parametros_modelo": "{}",
                "rmse": 5.0,
                "mae": 4.0,
                "mape": 0.05
            },
            {
                "nome_cenario": "Cenario B",
                "serie_id": "SERIE002",
                "data_execucao": "2023-01-01 11:00:00",
                "data_previsao": "2023-01-03",
                "frequencia_serie": "M",
                "valor_previsto": 200.0,
                "limite_inferior": 180.0,
                "limite_superior": 220.0,
                "modelo_utilizado": "Prophet",
                "parametros_modelo": "{}",
                "rmse": 10.0,
                "mae": 8.0,
                "mape": 0.04
            }
        ]
        adapter.insert_many("resultados_previsao", data_to_insert)

        # Verificar se os dados foram inseridos corretamente
        conn = sqlite3.connect(temp_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM resultados_previsao")
        rows = cursor.fetchall()
        conn.close()

        assert len(rows) == 2
        assert rows[0][1] == "Cenario A" # nome_cenario
        assert rows[1][2] == "SERIE002" # serie_id

# Teste de consulta (query)
def test_query(temp_db_path):
    with SqliteAdapter(temp_db_path) as adapter:
        adapter.create_schema_if_not_exists()
        data_to_insert = [
            {
                "nome_cenario": "Cenario X",
                "serie_id": "SERIE_QUERY",
                "data_execucao": "2023-02-01 12:00:00",
                "data_previsao": "2023-02-02",
                "frequencia_serie": "D",
                "valor_previsto": 50.0,
                "limite_inferior": 45.0,
                "limite_superior": 55.0,
                "modelo_utilizado": "ARIMA",
                "parametros_modelo": "{}",
                "rmse": 2.0,
                "mae": 1.5,
                "mape": 0.03
            }
        ]
        adapter.insert_many("resultados_previsao", data_to_insert)

        results = adapter.query("SELECT nome_cenario, valor_previsto FROM resultados_previsao WHERE serie_id = ?", ("SERIE_QUERY",))
        assert len(results) == 1
        assert results[0]["nome_cenario"] == "Cenario X"
        assert results[0]["valor_previsto"] == 50.0

# Teste de execução de comando (execute)
def test_execute(temp_db_path):
    with SqliteAdapter(temp_db_path) as adapter:
        adapter.create_schema_if_not_exists()
        data_to_insert = [
            {
                "nome_cenario": "Cenario Update",
                "serie_id": "SERIE_UPDATE",
                "data_execucao": "2023-03-01 09:00:00",
                "data_previsao": "2023-03-02",
                "frequencia_serie": "D",
                "valor_previsto": 75.0,
                "limite_inferior": 70.0,
                "limite_superior": 80.0,
                "modelo_utilizado": "Prophet",
                "parametros_modelo": "{}",
                "rmse": 3.0,
                "mae": 2.5,
                "mape": 0.02
            }
        ]
        adapter.insert_many("resultados_previsao", data_to_insert)

        adapter.execute("UPDATE resultados_previsao SET valor_previsto = ? WHERE serie_id = ?", (85.0, "SERIE_UPDATE"))

        results = adapter.query("SELECT valor_previsto FROM resultados_previsao WHERE serie_id = ?", ("SERIE_UPDATE",))
        assert results[0]["valor_previsto"] == 85.0

# Teste de tratamento de erro na conexão
def test_connection_error():
    # Tentar conectar a um caminho inválido ou com permissões negadas
    with pytest.raises(Exception, match="unable to open database file"):
        with SqliteAdapter("/non/existent/path/invalid.db"):
            pass

# Teste de tratamento de erro na inserção
def test_insert_many_error(temp_db_path):
    with SqliteAdapter(temp_db_path) as adapter:
        adapter.create_schema_if_not_exists()
        # Dados com coluna inexistente para forçar erro
        data_to_insert = [
            {
                "nome_cenario": "Cenario Erro",
                "coluna_inexistente": "valor"
            }
        ]
        with pytest.raises(sqlite3.OperationalError):
            adapter.insert_many("resultados_previsao", data_to_insert)

# Teste de tratamento de erro na query
def test_query_error(temp_db_path):
    with SqliteAdapter(temp_db_path) as adapter:
        adapter.create_schema_if_not_exists()
        with pytest.raises(sqlite3.OperationalError):
            adapter.query("SELECT * FROM tabela_inexistente")

# Teste de tratamento de erro na execução
def test_execute_error(temp_db_path):
    with SqliteAdapter(temp_db_path) as adapter:
        adapter.create_schema_if_not_exists()
        with pytest.raises(sqlite3.OperationalError):
            adapter.execute("INSERT INTO tabela_inexistente (col) VALUES (?) ", ("valor",))


