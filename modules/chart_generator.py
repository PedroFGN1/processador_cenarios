import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

def create_forecast_chart(historical_data: pd.DataFrame, forecast_data: pd.DataFrame, scenario_name: str, master_frame: any) -> FigureCanvasTkAgg:
    """
    Cria um gráfico interativo mostrando dados históricos, previsão e intervalo de confiança.

    Args:
        historical_data (pd.DataFrame): DataFrame com dados históricos (colunas 'data', 'valor').
        forecast_data (pd.DataFrame): DataFrame com dados de previsão (colunas 'data_previsao', 'valor_previsto', 'limite_inferior', 'limite_superior').
        scenario_name (str): Nome do cenário para o título do gráfico.
        master_frame (any): O frame CustomTkinter onde o gráfico será incorporado.

    Returns:
        FigureCanvasTkAgg: O objeto canvas do Matplotlib para ser empacotado na GUI.
    """
    logger.info(f"Gerando gráfico para o cenário: {scenario_name}")

    fig, ax = plt.subplots(figsize=(10, 6))

    # Plotar dados históricos
    if not historical_data.empty:
        ax.plot(historical_data['data'], historical_data['valor'], label='Dados Históricos', color='blue', marker='o', markersize=4)

    # Plotar previsão
    if not forecast_data.empty:
        ax.plot(forecast_data['data_previsao'], forecast_data['valor_previsto'], label='Previsão', color='red', linestyle='--', marker='x')

        # Plotar intervalo de confiança
        ax.fill_between(
            forecast_data['data_previsao'],
            forecast_data['limite_inferior'],
            forecast_data['limite_superior'],
            color='red', alpha=0.2, label='Intervalo de Confiança'
        )

    ax.set_title(f'Previsão para o Cenário: {scenario_name}')
    ax.set_xlabel('Data')
    ax.set_ylabel('Valor')
    ax.legend()
    ax.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()

    canvas = FigureCanvasTkAgg(fig, master=master_frame)
    return canvas



