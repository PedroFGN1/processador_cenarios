import customtkinter
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

def create_forecast_chart(historical_data: pd.DataFrame, list_of_forecast_dfs: list[pd.DataFrame], title: str, master_frame: any) -> FigureCanvasTkAgg:
    """
    Cria um gráfico interativo mostrando dados históricos e previsões de múltiplos cenários.

    Args:
        historical_data (pd.DataFrame): DataFrame com dados históricos (colunas 'data', 'valor').
        list_of_forecast_dfs (list[pd.DataFrame]): Lista de DataFrames, onde cada um contém dados de previsão
                                                  (colunas 'data_previsao', 'valor_previsto', 'limite_inferior',
                                                  'limite_superior', 'nome_cenario').
        title (str): Título do gráfico.
        master_frame (any): O frame CustomTkinter onde o gráfico será incorporado.

    Returns:
        FigureCanvasTkAgg: O objeto canvas do Matplotlib para ser empacotado na GUI.
    """
    logger.info(f"Gerando gráfico para: {title}")
    appearance_mode = customtkinter.get_appearance_mode()
    mode_index = 1 if appearance_mode == "Light" else 0
    if appearance_mode == "Dark":
        bg_color = "#2B2B2B"  # Fundo para o modo escuro (gray17)
        grid_color = "#474747" # Grid para o modo escuro (gray28)
    else: # "Light"
        bg_color = "#EBEBEB"  # Fundo para o modo claro (ex: gray92)
        grid_color = "#D9D9D9" # Grid para o modo claro (ex: gray85)
    text_color = customtkinter.ThemeManager.theme["CTkLabel"]["text_color"][mode_index]
    print(f"Background color: {bg_color}, Text color: {text_color}, Grid color: {grid_color}")
    # Aplica as cores ao criar a figura
    fig, ax = plt.subplots(figsize=(10, 6), facecolor=bg_color)
    ax.set_facecolor(bg_color)

    # Configura a cor dos eixos, ticks e labels
    ax.tick_params(axis='x', colors=text_color, labelsize=9)
    ax.tick_params(axis='y', colors=text_color, labelsize=9)
    for spine in ax.spines.values():
        spine.set_edgecolor(text_color)

    # Plotar dados históricos
    if not historical_data.empty:
        # Se houver múltiplos serie_id nos dados históricos (para comparação de séries diferentes)
        if 'serie_id' in historical_data.columns and historical_data['serie_id'].nunique() > 1:
            for serie_id in historical_data['serie_id'].unique():
                subset = historical_data[historical_data['serie_id'] == serie_id]
                ax.plot(subset['data'], subset['valor'], label=f'Histórico ({serie_id})', marker='o', markersize=4)
        else:
            ax.plot(historical_data['data'], historical_data['valor'], label='Dados Históricos', color='blue', marker='o', markersize=4)

    # Cores para os cenários
    colors = plt.cm.get_cmap('viridis', len(list_of_forecast_dfs))

    # Plotar cada previsão
    for i, forecast_df in enumerate(list_of_forecast_dfs):
        if not forecast_df.empty:
            scenario_name = forecast_df['nome_cenario'].iloc[0] if 'nome_cenario' in forecast_df.columns else f'Previsão {i+1}'
            color = colors(i)
            ax.plot(forecast_df['data_previsao'], forecast_df['valor_previsto'], label=f'Previsão ({scenario_name})', color=color, linestyle='--', marker='x')

            # Plotar intervalo de confiança, se disponível
            if 'limite_inferior' in forecast_df.columns and 'limite_superior' in forecast_df.columns:
                ax.fill_between(
                    forecast_df['data_previsao'],
                    forecast_df['limite_inferior'],
                    forecast_df['limite_superior'],
                    color=color, alpha=0.2
                )

    ax.set_title(title, color=text_color)
    ax.set_xlabel('Data', color=text_color)
    ax.set_ylabel('Valor', color=text_color)
    legend = ax.legend()
    for text in legend.get_texts():
        text.set_color(text_color)
        
    ax.grid(True, color=grid_color, linestyle='--', alpha=0.5)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    canvas = FigureCanvasTkAgg(fig, master=master_frame)
    return canvas
