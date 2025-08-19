
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
import pandas as pd
from methods._run_forecasting import run_single_scenario

# Fixture para um cenário de teste básico
@pytest.fixture
def sample_scenario():
    return {
        "nome_cenario": "Cenario Teste",
        "serie_id": "SERIE_TESTE",
        "modelo": "ARIMA",
        "horizonte_previsao": 3,
        "parametros": {"p": 1, "d": 1, "q": 1}
    }

# Fixture para dados históricos de exemplo
@pytest.fixture
def sample_historical_data():
    dates = pd.to_datetime(["2023-01-01", "2023-01-02", "2023-01-03", "2023-01-04", "2023-01-05", "2023-01-06"])
    values = [10.0, 11.0, 12.0, 13.0, 14.0, 15.0]
    return pd.DataFrame({"data": dates, "valor": values})

# Teste de sucesso para run_single_scenario
@patch("methods._run_forecasting.load_historical_data")
@patch("methods._run_forecasting.infer_frequency")
@patch("methods._run_forecasting.forecast_factory")
@patch("methods._run_forecasting.calculate_metrics")
@patch("methods._run_forecasting.process_results")
@patch("methods._run_forecasting.SqliteAdapter")
def test_run_single_scenario_success(
    mock_sqlite_adapter,
    mock_process_results,
    mock_calculate_metrics,
    mock_forecast_factory,
    mock_infer_frequency,
    mock_load_historical_data,
    sample_scenario,
    sample_historical_data
):
    # Configurar mocks
    mock_load_historical_data.return_value = sample_historical_data
    mock_infer_frequency.return_value = "diário"

    mock_model_instance = MagicMock()
    mock_forecast_factory.return_value = mock_model_instance

    # Mockar o retorno de predict para o conjunto de teste
    mock_model_instance.predict.side_effect = [
        pd.DataFrame({
            "data_previsao": pd.to_datetime(["2023-01-04", "2023-01-05", "2023-01-06"]),
            "valor_previsto": [13.1, 14.1, 15.1],
            "limite_inferior": [12.0, 13.0, 14.0],
            "limite_superior": [14.0, 15.0, 16.0]
        }),
        # Mockar o retorno de predict para a previsão final
        pd.DataFrame({
            "data_previsao": pd.to_datetime(["2023-01-07", "2023-01-08", "2023-01-09"]),
            "valor_previsto": [16.0, 17.0, 18.0],
            "limite_inferior": [15.0, 16.0, 17.0],
            "limite_superior": [17.0, 18.0, 19.0]
        })
    ]

    mock_calculate_metrics.return_value = {"rmse": 0.5, "mae": 0.4, "mape": 0.03}
    mock_process_results.return_value = [{"record": 1}, {"record": 2}, {"record": 3}]

    mock_adapter_instance = MagicMock()
    mock_sqlite_adapter.return_value.__enter__.return_value = mock_adapter_instance

    # Executar a função
    run_single_scenario(sample_scenario, Path("data.db"), Path("results.db"))

    # Verificar se as funções foram chamadas corretamente
    mock_load_historical_data.assert_called_once_with("SERIE_TESTE", Path("data.db"))
    mock_infer_frequency.assert_called_once()
    mock_forecast_factory.assert_called_once_with("ARIMA")
    assert mock_model_instance.predict.call_count == 2
    mock_calculate_metrics.assert_called_once()
    mock_process_results.assert_called_once_with(
        sample_scenario,
        mock_model_instance.predict.call_args_list[1].return_value, # A segunda chamada de predict
        {"rmse": 0.5, "mae": 0.4, "mape": 0.03},
        "diário"
    )
    mock_sqlite_adapter.assert_called_once_with("results.db")
    mock_adapter_instance.create_schema_if_not_exists.assert_called_once()
    mock_adapter_instance.insert_many.assert_called_once_with("resultados_previsao", [{"record": 1}, {"record": 2}, {"record": 3}])

# Teste para dados históricos insuficientes
@patch("methods._run_forecasting.load_historical_data")
@patch("methods._run_forecasting.logger") # Mockar o logger para verificar warnings
def test_run_single_scenario_insufficient_data(
    mock_logger,
    mock_load_historical_data,
    sample_scenario
):
    # Dados históricos com menos registros que o horizonte + 1
    insufficient_data = pd.DataFrame({
        "data": pd.to_datetime(["2023-01-01", "2023-01-02", "2023-01-03"]),
        "valor": [10.0, 11.0, 12.0]
    })
    mock_load_historical_data.return_value = insufficient_data

    run_single_scenario(sample_scenario, Path("data.db"), Path("results.db"))

    mock_logger.warning.assert_called_once_with(
        "Dados insuficientes para o cenário Cenário Teste. Mínimo de 4 pontos necessários."
    )
    # Nenhuma outra função de processamento deve ser chamada
    mock_logger.info.assert_called_once_with("Iniciando execução do cenário: Cenário Teste (Série: SERIE_TESTE, Modelo: ARIMA)")

# Teste para erro ao carregar dados históricos
@patch("methods._run_forecasting.load_historical_data")
@patch("methods._run_forecasting.logger")
def test_run_single_scenario_load_data_error(
    mock_logger,
    mock_load_historical_data,
    sample_scenario
):
    mock_load_historical_data.side_effect = ValueError("Erro ao carregar dados")

    run_single_scenario(sample_scenario, Path("data.db"), Path("results.db"))

    mock_logger.error.assert_called_once_with(
        "Erro de validação no cenário Cenário Teste: Erro ao carregar dados"
    )

# Teste para erro na criação/previsão do modelo
@patch("methods._run_forecasting.load_historical_data")
@patch("methods._run_forecasting.infer_frequency")
@patch("methods._run_forecasting.forecast_factory")
@patch("methods._run_forecasting.logger")
def test_run_single_scenario_model_error(
    mock_logger,
    mock_forecast_factory,
    mock_infer_frequency,
    mock_load_historical_data,
    sample_scenario,
    sample_historical_data
):
    mock_load_historical_data.return_value = sample_historical_data
    mock_infer_frequency.return_value = "diário"
    mock_forecast_factory.side_effect = Exception("Erro no modelo")

    run_single_scenario(sample_scenario, Path("data.db"), Path("results.db"))

    mock_logger.error.assert_called_once()
    assert "Erro inesperado ao executar o cenário Cenário Teste: Erro no modelo" in mock_logger.error.call_args[0][0]

# Teste para erro ao salvar resultados
@patch("methods._run_forecasting.load_historical_data")
@patch("methods._run_forecasting.infer_frequency")
@patch("methods._run_forecasting.forecast_factory")
@patch("methods._run_forecasting.calculate_metrics")
@patch("methods._run_forecasting.process_results")
@patch("methods._run_forecasting.SqliteAdapter")
@patch("methods._run_forecasting.logger")
def test_run_single_scenario_save_results_error(
    mock_logger,
    mock_sqlite_adapter,
    mock_process_results,
    mock_calculate_metrics,
    mock_forecast_factory,
    mock_infer_frequency,
    mock_load_historical_data,
    sample_scenario,
    sample_historical_data
):
    mock_load_historical_data.return_value = sample_historical_data
    mock_infer_frequency.return_value = "diário"

    mock_model_instance = MagicMock()
    mock_forecast_factory.return_value = mock_model_instance
    mock_model_instance.predict.side_effect = [
        pd.DataFrame({"data_previsao": [], "valor_previsto": [], "limite_inferior": [], "limite_superior": []}),
        pd.DataFrame({"data_previsao": [], "valor_previsto": [], "limite_inferior": [], "limite_superior": []})
    ]

    mock_calculate_metrics.return_value = {"rmse": 0.5, "mae": 0.4, "mape": 0.03}
    mock_process_results.return_value = [{"record": 1}]

    mock_adapter_instance = MagicMock()
    mock_sqlite_adapter.return_value.__enter__.return_value = mock_adapter_instance
    mock_adapter_instance.insert_many.side_effect = Exception("Erro ao salvar no DB")

    run_single_scenario(sample_scenario, Path("data.db"), Path("results.db"))

    mock_logger.error.assert_called_once()
    assert "Erro inesperado ao executar o cenário Cenário Teste: Erro ao salvar no DB" in mock_logger.error.call_args[0][0]



