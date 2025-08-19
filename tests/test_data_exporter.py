
import pytest
import pandas as pd
from pathlib import Path
from modules.data_exporter import export_dataframe_to_csv, export_dataframe_to_excel

# Fixture para criar um DataFrame de teste
@pytest.fixture
def sample_dataframe():
    data = {
        "id": [1, 2, 3],
        "col1": ["A", "B", "C"],
        "col2": [10, 20, 30]
    }
    return pd.DataFrame(data)

@pytest.fixture
def sample_dataframe_no_id():
    data = {
        "col1": ["X", "Y", "Z"],
        "col2": [100, 200, 300]
    }
    return pd.DataFrame(data)

# Testes para export_dataframe_to_csv
def test_export_dataframe_to_csv_with_id(tmp_path, sample_dataframe):
    output_file = tmp_path / "output.csv"
    success = export_dataframe_to_csv(sample_dataframe, output_file)

    assert success is True
    assert output_file.exists()

    df_read = pd.read_csv(output_file)
    assert "id" not in df_read.columns # A coluna 'id' deve ser removida
    pd.testing.assert_frame_equal(df_read, sample_dataframe.drop(columns=["id"]))

def test_export_dataframe_to_csv_no_id(tmp_path, sample_dataframe_no_id):
    output_file = tmp_path / "output_no_id.csv"
    success = export_dataframe_to_csv(sample_dataframe_no_id, output_file)

    assert success is True
    assert output_file.exists()

    df_read = pd.read_csv(output_file)
    pd.testing.assert_frame_equal(df_read, sample_dataframe_no_id)

def test_export_dataframe_to_csv_invalid_path(sample_dataframe):
    invalid_path = Path("/non_existent_dir/output.csv")
    success = export_dataframe_to_csv(sample_dataframe, invalid_path)
    assert success is False

# Testes para export_dataframe_to_excel
def test_export_dataframe_to_excel_with_id(tmp_path, sample_dataframe):
    output_file = tmp_path / "output.xlsx"
    success = export_dataframe_to_excel(sample_dataframe, output_file)

    assert success is True
    assert output_file.exists()

    df_read = pd.read_excel(output_file)
    assert "id" not in df_read.columns # A coluna 'id' deve ser removida
    pd.testing.assert_frame_equal(df_read, sample_dataframe.drop(columns=["id"]))

def test_export_dataframe_to_excel_no_id(tmp_path, sample_dataframe_no_id):
    output_file = tmp_path / "output_no_id.xlsx"
    success = export_dataframe_to_excel(sample_dataframe_no_id, output_file)

    assert success is True
    assert output_file.exists()

    df_read = pd.read_excel(output_file)
    pd.testing.assert_frame_equal(df_read, sample_dataframe_no_id)

def test_export_dataframe_to_excel_invalid_path(sample_dataframe):
    invalid_path = Path("/non_existent_dir/output.xlsx")
    success = export_dataframe_to_excel(sample_dataframe, invalid_path)
    assert success is False



