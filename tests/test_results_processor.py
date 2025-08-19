import pytest
import pandas as pd
import json
from datetime import datetime
from modules.results_processor import process_results

# Fixture para cenário de exemplo
@pytest.fixture
def sample_cenario():
    return {
        "nome_cenario": "Cenário Teste",
        "serie_id": "SERIE_A",
        "modelo": "ARIMA",
        "parametros": {"p": 1, "d": 1, "q": 1}
    }

# Fixture para DataFrame de previsão de exemplo
@pytest.fixture
def sample_forecast_df():
    dates = pd.to_datetime(["2023-01-04", "2023-01-05", "2023-01-06"])
    return pd.DataFrame({
        "data_previsao": dates,
        "valor_previsto": [13.0, 14.0, 15.0],
        "limite_inferior": [12.0, 13.0, 14.0],
        "limite_superior": [14.0, 15.0, 16.0]
    })

# Fixture para métricas de exemplo
@pytest.fixture
def sample_metrics():
    return {
        "rmse": 0.5,
        "mae": 0.3,
        "mape": 2.1
    }

# Teste para process_results com todos os parâmetros
def test_process_results_complete(sample_cenario, sample_forecast_df, sample_metrics):
    frequency = "D"
    
    result = process_results(
        cenario=sample_cenario,
        forecast_df=sample_forecast_df,
        metrics=sample_metrics,
        frequency=frequency
    )
    
    assert isinstance(result, list)
    assert len(result) == 3  # Três registros de previsão
    
    # Verificar primeiro registro
    first_record = result[0]
    assert first_record["nome_cenario"] == "Cenário Teste"
    assert first_record["serie_id"] == "SERIE_A"
    assert first_record["modelo_utilizado"] == "ARIMA"
    assert first_record["frequencia_serie"] == "D"
    assert first_record["valor_previsto"] == 13.0
    assert first_record["limite_inferior"] == 12.0
    assert first_record["limite_superior"] == 14.0
    assert first_record["rmse"] == 0.5
    assert first_record["mae"] == 0.3
    assert first_record["mape"] == 2.1
    
    # Verificar se data_execucao está presente e é string
    assert "data_execucao" in first_record
    assert isinstance(first_record["data_execucao"], str)
    
    # Verificar se data_previsao está formatada corretamente
    assert first_record["data_previsao"] == "2023-01-04"
    
    # Verificar se parametros_modelo é JSON válido
    parametros = json.loads(first_record["parametros_modelo"])
    assert parametros == {"p": 1, "d": 1, "q": 1}

# Teste para process_results sem métricas
def test_process_results_no_metrics(sample_cenario, sample_forecast_df):
    result = process_results(
        cenario=sample_cenario,
        forecast_df=sample_forecast_df,
        metrics=None,
        frequency="M"
    )
    
    assert len(result) == 3
    first_record = result[0]
    assert first_record["rmse"] is None
    assert first_record["mae"] is None
    assert first_record["mape"] is None
    assert first_record["frequencia_serie"] == "M"

# Teste para process_results sem frequência
def test_process_results_no_frequency(sample_cenario, sample_forecast_df, sample_metrics):
    result = process_results(
        cenario=sample_cenario,
        forecast_df=sample_forecast_df,
        metrics=sample_metrics,
        frequency=None
    )
    
    assert len(result) == 3
    first_record = result[0]
    assert first_record["frequencia_serie"] is None

# Teste para process_results com valores NaN nos limites
def test_process_results_with_nan_limits(sample_cenario, sample_metrics):
    forecast_df_with_nan = pd.DataFrame({
        "data_previsao": pd.to_datetime(["2023-01-04", "2023-01-05"]),
        "valor_previsto": [13.0, 14.0],
        "limite_inferior": [12.0, pd.NaT],
        "limite_superior": [14.0, pd.NaT]
    })
    
    result = process_results(
        cenario=sample_cenario,
        forecast_df=forecast_df_with_nan,
        metrics=sample_metrics,
        frequency="D"
    )
    
    assert len(result) == 2
    second_record = result[1]
    assert second_record["limite_inferior"] is None
    assert second_record["limite_superior"] is None

# Teste para process_results com cenário sem serie_id
def test_process_results_no_serie_id(sample_forecast_df, sample_metrics):
    cenario_sem_serie = {
        "nome_cenario": "Cenário Sem Série",
        "modelo": "ARIMA",
        "parametros": {"p": 1, "d": 1, "q": 1}
    }
    
    result = process_results(
        cenario=cenario_sem_serie,
        forecast_df=sample_forecast_df,
        metrics=sample_metrics,
        frequency="D"
    )
    
    assert len(result) == 3
    first_record = result[0]
    assert first_record["serie_id"] == "Série Desconhecida"

# Teste para process_results com DataFrame vazio
def test_process_results_empty_dataframe(sample_cenario, sample_metrics):
    empty_df = pd.DataFrame(columns=["data_previsao", "valor_previsto", "limite_inferior", "limite_superior"])
    
    result = process_results(
        cenario=sample_cenario,
        forecast_df=empty_df,
        metrics=sample_metrics,
        frequency="D"
    )
    
    assert isinstance(result, list)
    assert len(result) == 0

