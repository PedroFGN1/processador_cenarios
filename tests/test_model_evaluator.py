import pytest
import pandas as pd
import numpy as np
from modules.model_evaluator import calculate_metrics

# Fixture para dados de teste válidos
@pytest.fixture
def valid_data():
    actuals = pd.Series([10, 20, 30, 40, 50])
    predictions = pd.Series([10.1, 20.2, 29.8, 40.3, 49.9])
    return actuals, predictions

# Fixture para dados com NaNs
@pytest.fixture
def data_with_nans():
    actuals = pd.Series([10, 20, np.nan, 40, 50])
    predictions = pd.Series([10.1, np.nan, 29.8, 40.3, 49.9])
    return actuals, predictions

# Fixture para dados com valores zero nos 'actuals' (para testar MAPE)
@pytest.fixture
def data_with_zero_actuals():
    actuals = pd.Series([10, 0, 30, 40, 50])
    predictions = pd.Series([10.1, 0.1, 29.8, 40.3, 49.9])
    return actuals, predictions

# Teste para o cenário de sucesso com dados válidos
def test_calculate_metrics_success(valid_data):
    actuals, predictions = valid_data
    metrics = calculate_metrics(actuals, predictions)

    assert isinstance(metrics, dict)
    assert "rmse" in metrics
    assert "mae" in metrics
    assert "mape" in metrics

    # Valores esperados aproximados (calculados manualmente ou com bibliotecas)
    # RMSE: sqrt(mean((10.1-10)^2 + (20.2-20)^2 + (29.8-30)^2 + (40.3-40)^2 + (49.9-50)^2))
    #     = sqrt(mean(0.01 + 0.04 + 0.04 + 0.09 + 0.01)) = sqrt(0.19/5) = sqrt(0.038) approx 0.1949
    # MAE: mean(|10.1-10| + |20.2-20| + |29.8-30| + |40.3-40| + |49.9-50|)
    #    = (0.1 + 0.2 + 0.2 + 0.3 + 0.1)/5 = 0.9/5 = 0.18
    # MAPE: mean(|(10.1-10)/10| + |(20.2-20)/20| + ...)*100
    #     = (0.01 + 0.01 + 0.0066 + 0.0075 + 0.002)*100 / 5 = 0.0371 * 100 / 5 approx 0.742

    assert metrics["rmse"] == pytest.approx(0.19493588, rel=1e-2)
    assert metrics["mae"] == pytest.approx(0.18, rel=1e-2)
    assert metrics["mape"] == pytest.approx(0.742, rel=1e-2)

# Teste com séries vazias
def test_calculate_metrics_empty_series():
    actuals = pd.Series([])
    predictions = pd.Series([])
    metrics = calculate_metrics(actuals, predictions)

    assert metrics["rmse"] is None
    assert metrics["mae"] is None
    assert metrics["mape"] is None

# Teste com NaNs nos dados
def test_calculate_metrics_with_nans(data_with_nans):
    actuals, predictions = data_with_nans
    metrics = calculate_metrics(actuals, predictions)

    # Após dropar NaNs, os dados válidos são:
    # actuals_clean = [10, 40, 50]
    # predictions_clean = [10.1, 40.3, 49.9]

    # RMSE: sqrt(mean((10.1-10)^2 + (40.3-40)^2 + (49.9-50)^2))
    #     = sqrt(mean(0.01 + 0.09 + 0.01)) = sqrt(0.11/3) = sqrt(0.0366) approx 0.1917
    # MAE: mean(|10.1-10| + |40.3-40| + |49.9-50|)
    #    = (0.1 + 0.3 + 0.1)/3 = 0.5/3 = 0.1666
    # MAPE: mean(|(10.1-10)/10| + |(40.3-40)/40| + |(49.9-50)/50|)*100
    #     = (0.01 + 0.0075 + 0.002)*100 / 3 = 0.0195 * 100 / 3 approx 0.65

    assert metrics["rmse"] == pytest.approx(0.1917, rel=1e-2)
    assert metrics["mae"] == pytest.approx(0.1666, rel=1e-2)
    assert metrics["mape"] == pytest.approx(0.65, rel=1e-2)

# Teste com valores zero nos 'actuals' para MAPE
def test_calculate_metrics_with_zero_actuals(data_with_zero_actuals):
    actuals, predictions = data_with_zero_actuals
    metrics = calculate_metrics(actuals, predictions)

    # O valor com actual=0 deve ser ignorado no cálculo do MAPE
    # actuals_clean para MAPE: [10, 30, 40, 50]
    # predictions_clean para MAPE: [10.1, 29.8, 40.3, 49.9]

    # MAPE: mean(|(10.1-10)/10| + |(29.8-30)/30| + |(40.3-40)/40| + |(49.9-50)/50|)*100
    #     = (0.01 + 0.00666 + 0.0075 + 0.002)*100 / 4 = 0.02616 * 100 / 4 approx 0.654

    assert metrics["rmse"] is not None # RMSE e MAE ainda devem ser calculados
    assert metrics["mae"] is not None
    assert metrics["mape"] == pytest.approx(0.654, rel=1e-2)

# Teste com séries de tamanhos diferentes (pandas alinha automaticamente)
def test_calculate_metrics_mismatched_lengths():
    actuals = pd.Series([10, 20, 30])
    predictions = pd.Series([10.1, 20.2, 29.8, 40.0]) # Uma previsão a mais
    metrics = calculate_metrics(actuals, predictions)

    # Pandas alinha por índice, então o 40.0 será NaN e depois removido
    # actuals_clean = [10, 20, 30]
    # predictions_clean = [10.1, 20.2, 29.8]

    assert metrics["rmse"] == pytest.approx(0.19493588, rel=1e-2)
    assert metrics["mae"] == pytest.approx(0.16666666, rel=1e-2)
    assert metrics["mape"] == pytest.approx(0.742, rel=1e-2)

# Teste com todos os valores de 'actuals' sendo zero (MAPE deve ser None)
def test_calculate_metrics_all_actuals_zero_mape():
    actuals = pd.Series([0, 0, 0])
    predictions = pd.Series([0.1, 0.2, 0.3])
    metrics = calculate_metrics(actuals, predictions)

    assert metrics["rmse"] is not None
    assert metrics["mae"] is not None
    assert metrics["mape"] is None # Não é possível calcular MAPE com todos os actuals zero


