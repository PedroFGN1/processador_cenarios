import pytest
import pandas as pd
import sqlite3
from pathlib import Path
from modules.data_loader import (
    load_historical_data,
    get_series_tables,
    consolidate_series,
    get_available_series,
    infer_frequency,
    load_data_from_csv,
    load_data_from_excel
)
from persistence.sqlite_adapter import SqliteAdapter

# Fixture para criar um banco de dados SQLite temporário para testes
@pytest.fixture
def temp_data_db(tmp_path):
    db_file = tmp_path / "test_data.db"
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Criar algumas tabelas de exemplo com dados
    cursor.execute("CREATE TABLE serie_a (data TEXT, valor REAL)")
    cursor.execute("INSERT INTO serie_a (data, valor) VALUES ('2023-01-01', 10.0), ('2023-01-02', 11.0), ('2023-01-03', 12.0)")

    cursor.execute("CREATE TABLE serie_b (data TEXT, valor REAL)")
    cursor.execute("INSERT INTO serie_b (data, valor) VALUES ('2023-02-01', 20.0), ('2023-02-02', 21.0)")

    cursor.execute("CREATE TABLE serie_c (data TEXT, valor REAL)")
    cursor.execute("INSERT INTO serie_c (data, valor) VALUES ('2023-03-01', 30.0), ('2023-03-02', 31.0)")

    # Tabela com colunas diferentes para testar get_series_tables
    cursor.execute("CREATE TABLE outra_tabela (id INTEGER, nome TEXT)")

    conn.commit()
    conn.close()
    return str(db_file)

# Fixture para criar um banco de dados vazio
@pytest.fixture
def empty_data_db(tmp_path):
    db_file = tmp_path / "empty_data.db"
    conn = sqlite3.connect(db_file)
    conn.close()
    return str(db_file)

# Fixture para criar um arquivo CSV temporário
@pytest.fixture
def temp_csv_file(tmp_path):
    csv_content = "data,valor\n2024-01-01,100\n2024-01-02,101\n2024-01-03,102"
    file_path = tmp_path / "test_data.csv"
    file_path.write_text(csv_content)
    return file_path

# Fixture para criar um arquivo CSV temporário com colunas diferentes
@pytest.fixture
def temp_csv_file_bad_cols(tmp_path):
    csv_content = "Date,Value\n2024-01-01,100\n2024-01-02,101"
    file_path = tmp_path / "test_data_bad.csv"
    file_path.write_text(csv_content)
    return file_path

# Fixture para criar um arquivo Excel temporário
@pytest.fixture
def temp_excel_file(tmp_path):
    df = pd.DataFrame({"data": pd.to_datetime(["2024-01-01", "2024-01-02"]),
                       "valor": [200, 201]})
    file_path = tmp_path / "test_data.xlsx"
    df.to_excel(file_path, index=False)
    return file_path

# Fixture para criar um arquivo Excel temporário com colunas diferentes
@pytest.fixture
def temp_excel_file_bad_cols(tmp_path):
    df = pd.DataFrame({"Date": pd.to_datetime(["2024-01-01", "2024-01-02"]),
                       "Value": [200, 201]})
    file_path = tmp_path / "test_data_bad.xlsx"
    df.to_excel(file_path, index=False)
    return file_path


# Testes para load_historical_data
def test_load_historical_data_success(temp_data_db):
    # Consolidar antes de carregar dados históricos
    consolidate_series(temp_data_db)
    df = load_historical_data("serie_a", temp_data_db)
    assert not df.empty
    assert len(df) == 3
    assert df["data"].iloc[0] == pd.to_datetime("2023-01-01")
    assert df["valor"].iloc[0] == 10.0
    assert pd.api.types.is_datetime64_any_dtype(df["data"])
    assert pd.api.types.is_float_dtype(df["valor"])

def test_load_historical_data_not_found(temp_data_db):
    consolidate_series(temp_data_db)
    with pytest.raises(ValueError, match="Nenhum dado encontrado para a série inexistente"):
        load_historical_data("serie_inexistente", temp_data_db)

def test_load_historical_data_empty_db(empty_data_db):
    # Não é necessário consolidar se o DB está vazio, pois a função já deve falhar antes
    with pytest.raises(ValueError, match="Nenhum dado encontrado para a série qualquer"):
        load_historical_data("serie_qualquer", empty_data_db)

# Testes para get_series_tables
def test_get_series_tables_success(temp_data_db):
    tables = get_series_tables(temp_data_db)
    assert sorted(tables) == sorted(["serie_a", "serie_b", "serie_c"])

def test_get_series_tables_empty_db(empty_data_db):
    tables = get_series_tables(empty_data_db)
    assert tables == []

# Testes para consolidate_series
def test_consolidate_series_success(temp_data_db):
    status, message = consolidate_series(temp_data_db)
    assert status is True
    assert "Consolidação concluída com sucesso." in message

    # Verificar se a tabela consolidada foi criada e preenchida
    with SqliteAdapter(temp_data_db) as adapter:
        results = adapter.query("SELECT serie_id, data, valor FROM series_consolidada ORDER BY serie_id, data")
        assert len(results) == 7 # 3 de serie_a + 2 de serie_b + 2 de serie_c
        assert results[0]["serie_id"] == "serie_a"
        assert results[5]["serie_id"] == "serie_c"

def test_consolidate_series_empty_db(empty_data_db):
    status, message = consolidate_series(empty_data_db)
    assert status is False
    assert "Nenhuma tabela de série encontrada para consolidação." in message

# Testes para get_available_series
def test_get_available_series_success(temp_data_db):
    # Primeiro consolida para garantir que a tabela series_consolidada existe
    consolidate_series(temp_data_db)
    series_ids = get_available_series(temp_data_db)
    assert sorted(series_ids) == sorted(["serie_a", "serie_b", "serie_c"])

def test_get_available_series_no_consolidated_table(empty_data_db):
    # Não consolida, então a tabela series_consolidada não existe
    series_ids = get_available_series(empty_data_db)
    assert series_ids == []

# Testes para infer_frequency
def test_infer_frequency_daily():
    df = pd.DataFrame({"data": pd.to_datetime(["2023-01-01", "2023-01-02", "2023-01-03"]),
                       "valor": [1, 2, 3]})
    freq = infer_frequency(df)
    assert freq == "D"

def test_infer_frequency_monthly():
    df = pd.DataFrame({"data": pd.to_datetime(["2023-01-31", "2023-02-28", "2023-03-31"]),
                       "valor": [1, 2, 3]})
    freq = infer_frequency(df)
    assert freq == "M"

def test_infer_frequency_unknown():
    df = pd.DataFrame({"data": pd.to_datetime(["2023-01-01", "2023-01-03", "2023-01-07"]),
                       "valor": [1, 2, 3]})
    freq = infer_frequency(df)
    assert freq is None

# Testes para load_data_from_csv
def test_load_data_from_csv_success(temp_csv_file):
    df = load_data_from_csv(temp_csv_file)
    assert not df.empty
    assert len(df) == 3
    assert df["data"].iloc[0] == pd.to_datetime("2024-01-01")
    assert df["valor"].iloc[0] == 100
    assert pd.api.types.is_datetime64_any_dtype(df["data"])
    assert pd.api.types.is_numeric_dtype(df["valor"])

def test_load_data_from_csv_missing_cols(temp_csv_file_bad_cols):
    with pytest.raises(ValueError, match="O arquivo CSV deve conter colunas 'data' e 'valor'."):
        load_data_from_csv(temp_csv_file_bad_cols)

def test_load_data_from_csv_non_existent_file(tmp_path):
    with pytest.raises(Exception):
        load_data_from_csv(tmp_path / "non_existent.csv")

# Testes para load_data_from_excel
def test_load_data_from_excel_success(temp_excel_file):
    df = load_data_from_excel(temp_excel_file)
    assert not df.empty
    assert len(df) == 2
    assert df["data"].iloc[0] == pd.to_datetime("2024-01-01")
    assert df["valor"].iloc[0] == 200
    assert pd.api.types.is_datetime64_any_dtype(df["data"])
    assert pd.api.types.is_numeric_dtype(df["valor"])

def test_load_data_from_excel_missing_cols(temp_excel_file_bad_cols):
    with pytest.raises(ValueError, match="O arquivo Excel deve conter colunas 'data' e 'valor'."):
        load_data_from_excel(temp_excel_file_bad_cols)

def test_load_data_from_excel_non_existent_file(tmp_path):
    with pytest.raises(Exception):
        load_data_from_excel(tmp_path / "non_existent.xlsx")


