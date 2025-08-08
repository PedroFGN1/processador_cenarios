import pandas as pd
from sklearn.metrics import mean_squared_error, mean_absolute_error
import numpy as np
import logging

logger = logging.getLogger(__name__)

def calculate_metrics(actuals: pd.Series, predictions: pd.Series) -> dict:
    """
    Calcula métricas de avaliação para previsões de séries temporais.

    Args:
        actuals (pd.Series): Série de valores reais.
        predictions (pd.Series): Série de valores previstos.

    Returns:
        dict: Dicionário contendo as métricas RMSE, MAE e MAPE.
    """
    metrics = {}
    
    # Remove NaNs que podem surgir de alinhamento de séries
    combined = pd.DataFrame({"actual": actuals, "prediction": predictions}).dropna()
    if combined.empty:
        logger.warning("Não há dados suficientes para calcular métricas após remover NaNs.")
        return {"rmse": None, "mae": None, "mape": None}

    actuals_clean = combined["actual"]
    predictions_clean = combined["prediction"]

    try:
        metrics["rmse"] = np.sqrt(mean_squared_error(actuals_clean, predictions_clean))
    except Exception as e:
        logger.error(f"Erro ao calcular RMSE: {e}")
        metrics["rmse"] = None

    try:
        metrics["mae"] = mean_absolute_error(actuals_clean, predictions_clean)
    except Exception as e:
        logger.error(f"Erro ao calcular MAE: {e}")
        metrics["mae"] = None

    try:
        # MAPE: Evitar divisão por zero
        mape_values = np.abs((actuals_clean - predictions_clean) / actuals_clean)
        mape_values = mape_values[np.isfinite(mape_values)] # Remove inf ou NaN
        if not mape_values.empty:
            metrics["mape"] = np.mean(mape_values) * 100
        else:
            metrics["mape"] = None
    except Exception as e:
        logger.error(f"Erro ao calcular MAPE: {e}")
        metrics["mape"] = None

    logger.info(f"Métricas calculadas: {metrics}")
    return metrics



