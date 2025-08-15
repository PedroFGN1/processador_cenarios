import customtkinter
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
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
    # Limpa o frame mestre de widgets antigos antes de desenhar o novo gráfico
    for widget in master_frame.winfo_children():
        widget.destroy()

    logger.info(f"Gerando gráfico para: {title}")
    
    # --- Lógica de Cores (permanece a mesma) ---
    appearance_mode = customtkinter.get_appearance_mode()
    if appearance_mode == "Dark":
        bg_color = "#2B2B2B"
        grid_color = "#474747"
        text_color = "white"
    else: # "Light"
        bg_color = "#EBEBEB"
        grid_color = "#D9D9D9"
        text_color = "black"

    # --- Criação do Gráfico (Estilo Orientado a Objetos) ---
    # ALTERADO: Usamos Figure() em vez de plt.subplots() para melhor integração
    fig = Figure(figsize=(10, 6), facecolor=bg_color)
    ax = fig.add_subplot(111)
    ax.set_facecolor(bg_color)

    # --- Configuração e Plotagem dos Dados (seu código, com pequenas adaptações) ---
    ax.tick_params(axis='x', colors=text_color, labelsize=9)
    ax.tick_params(axis='y', colors=text_color, labelsize=9)
    for spine in ax.spines.values():
        spine.set_edgecolor(text_color)

    if not historical_data.empty:
        if 'serie_id' in historical_data.columns and historical_data['serie_id'].nunique() > 1:
            for serie_id in historical_data['serie_id'].unique():
                subset = historical_data[historical_data['serie_id'] == serie_id]
                ax.plot(subset['data'], subset['valor'], label=f'Histórico ({serie_id})', marker='o', markersize=4)
        else:
            ax.plot(historical_data['data'], historical_data['valor'], label='Dados Históricos', color='blue', marker='o', markersize=4)

    # Cores para os cenários (usando um colormap mais moderno)
    colors = plt.cm.get_cmap('plasma', len(list_of_forecast_dfs))

    for i, forecast_df in enumerate(list_of_forecast_dfs):
        if not forecast_df.empty:
            scenario_name = forecast_df['nome_cenario'].iloc[0] if 'nome_cenario' in forecast_df.columns else f'Previsão {i+1}'
            color = colors(i)
            ax.plot(forecast_df['data_previsao'], forecast_df['valor_previsto'], label=f'Previsão ({scenario_name})', color=color, linestyle='--', marker='x')
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
    legend.get_frame().set_facecolor(bg_color) # Adiciona cor de fundo à legenda
    for text in legend.get_texts():
        text.set_color(text_color)
        
    ax.grid(True, color=grid_color, linestyle='--', alpha=0.5)
    # ALTERADO: fig.autofmt_xdate() é melhor para rotacionar datas
    fig.autofmt_xdate(rotation=45) 
    fig.tight_layout()

    # --- NOVO: Integração da Barra de Ferramentas e do Canvas ---
    
    # Cria o canvas que desenhará o gráfico
    canvas = FigureCanvasTkAgg(fig, master=master_frame)
    canvas_widget = canvas.get_tk_widget()
    
    # Cria a barra de ferramentas
    toolbar = NavigationToolbar2Tk(canvas, master_frame, pack_toolbar=False)
    toolbar.update()
    
    # Estiliza a barra de ferramentas para combinar com o tema
    toolbar.config(background=bg_color)
    for button in toolbar.winfo_children():
        button.config(background=bg_color)

    # Posiciona os widgets na tela
    toolbar.pack(side="top", fill="x", padx=5)
    canvas_widget.pack(side="top", fill="both", expand=True)