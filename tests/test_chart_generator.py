
import pytest
import pandas as pd
from unittest.mock import MagicMock, patch
import matplotlib.pyplot as plt

# Fixture para dados históricos de exemplo
@pytest.fixture
def sample_historical_data():
    dates = pd.to_datetime(["2023-01-01", "2023-01-02", "2023-01-03"])
    values = [10.0, 11.0, 12.0]
    return pd.DataFrame({"data": dates, "valor": values})

# Fixture para dados de previsão de exemplo
@pytest.fixture
def sample_forecast_data():
    dates = pd.to_datetime(["2023-01-04", "2023-01-05", "2023-01-06"])
    values = [13.0, 14.0, 15.0]
    lower = [12.0, 13.0, 14.0]
    upper = [14.0, 15.0, 16.0]
    scenario_name = ["Cenario A", "Cenario A", "Cenario A"]
    return pd.DataFrame({
        "data_previsao": dates,
        "valor_previsto": values,
        "limite_inferior": lower,
        "limite_superior": upper,
        "nome_cenario": scenario_name
    })

# Fixture para um master_frame mockado
@pytest.fixture
def mock_master_frame():
    mock_frame = MagicMock()
    mock_frame.winfo_children.return_value = []
    return mock_frame

# Teste principal para verificar chamadas a matplotlib e limpeza do frame
@patch("modules.chart_generator.Figure")
@patch("modules.chart_generator.FigureCanvasTkAgg")
@patch("modules.chart_generator.NavigationToolbar2Tk")
@patch("modules.chart_generator.customtkinter.get_appearance_mode")
def test_create_forecast_chart_calls_matplotlib_functions(
    mock_get_appearance_mode,
    mock_navigation_toolbar2tk,
    mock_figure_canvas_tkagg,
    mock_figure,
    sample_historical_data,
    sample_forecast_data,
    mock_master_frame
):
    # Configurar mocks
    mock_get_appearance_mode.return_value = "Dark"

    mock_fig_instance = MagicMock()
    mock_figure.return_value = mock_fig_instance
    mock_ax_instance = MagicMock()
    mock_fig_instance.add_subplot.return_value = mock_ax_instance

    mock_canvas_instance = MagicMock()
    mock_figure_canvas_tkagg.return_value = mock_canvas_instance
    mock_canvas_instance.get_tk_widget.return_value = MagicMock()

    # Importar a função após os mocks estarem configurados
    from modules.chart_generator import create_forecast_chart
    create_forecast_chart(
        sample_historical_data,
        [sample_forecast_data],
        "Título do Gráfico",
        mock_master_frame
    )

    # Verificar se Figure e add_subplot foram chamados
    mock_figure.assert_called_once()
    mock_fig_instance.add_subplot.assert_called_once_with(111)

# Teste para o caso de dados históricos vazios
@patch("modules.chart_generator.Figure")
@patch("modules.chart_generator.FigureCanvasTkAgg")
@patch("modules.chart_generator.NavigationToolbar2Tk")
@patch("modules.chart_generator.customtkinter.get_appearance_mode")
def test_create_forecast_chart_empty_historical_data(
    mock_get_appearance_mode,
    mock_navigation_toolbar2tk,
    mock_figure_canvas_tkagg,
    mock_figure,
    sample_forecast_data,
    mock_master_frame
):
    mock_get_appearance_mode.return_value = "Light"
    mock_fig_instance = MagicMock()
    mock_figure.return_value = mock_fig_instance
    mock_ax_instance = MagicMock()
    mock_fig_instance.add_subplot.return_value = mock_ax_instance

    from modules.chart_generator import create_forecast_chart
    create_forecast_chart(
        pd.DataFrame({"data": [], "valor": []}),
        [sample_forecast_data],
        "Título do Gráfico",
        mock_master_frame
    )

    mock_figure.assert_called_once()

# Teste para o caso de lista de previsões vazia
@patch("modules.chart_generator.Figure")
@patch("modules.chart_generator.FigureCanvasTkAgg")
@patch("modules.chart_generator.NavigationToolbar2Tk")
@patch("modules.chart_generator.customtkinter.get_appearance_mode")
def test_create_forecast_chart_empty_forecast_list(
    mock_get_appearance_mode,
    mock_navigation_toolbar2tk,
    mock_figure_canvas_tkagg,
    mock_figure,
    sample_historical_data,
    mock_master_frame
):
    mock_get_appearance_mode.return_value = "Dark"
    mock_fig_instance = MagicMock()
    mock_figure.return_value = mock_fig_instance
    mock_ax_instance = MagicMock()
    mock_fig_instance.add_subplot.return_value = mock_ax_instance

    from modules.chart_generator import create_forecast_chart
    create_forecast_chart(
        sample_historical_data,
        [],
        "Título do Gráfico",
        mock_master_frame
    )

    mock_figure.assert_called_once()


