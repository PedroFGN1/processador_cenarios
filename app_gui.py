import customtkinter
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
import logging
import threading
import pandas as pd

from utils.logger_config import setup_logger, GuiLogHandler
from utils.get_base_path import get_database_path, get_config_path
from config_manager_gui import ConfigManagerFrame
from modules.scenario_loader import load_scenarios
from methods._run_forecasting import run_single_scenario
from persistence.sqlite_adapter import SqliteAdapter
from modules.chart_generator import create_forecast_chart # Importa a função de gráfico
from modules.data_exporter import export_dataframe_to_csv, export_dataframe_to_excel # Importa as funções de exportação
from modules.data_loader import load_historical_data, consolidate_series # Importa para carregar dados históricos para comparação

# Configura o logger
logger = setup_logger()

class App(customtkinter.CTk):
    """
    Classe principal da aplicação GUI.
    """
    
    def __init__(self):
        super().__init__()
        
        # Configurações da janela principal
        self.title("Processador de Cenários de Previsão")
        self.geometry("1200x800")
        self.minsize(800, 600)
        
        # Configura o grid da janela principal
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Cria o frame de navegação (lateral esquerda)
        self.navigation_frame = customtkinter.CTkFrame(self, width=200, corner_radius=0)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.navigation_frame.grid_rowconfigure(4, weight=1)
        
        # Título da aplicação no frame de navegação
        self.navigation_label = customtkinter.CTkLabel(
            self.navigation_frame, 
            text="Processador\nde Cenários",
            font=customtkinter.CTkFont(size=15, weight="bold")
        )
        self.navigation_label.grid(row=0, column=0, padx=20, pady=20)
        
        # Botões de navegação
        self.config_button = customtkinter.CTkButton(
            self.navigation_frame,
            corner_radius=0,
            height=40,
            border_spacing=10,
            text="Gerenciar Cenários",
            fg_color="transparent",
            text_color=("gray10", "gray90"),
            hover_color=("gray70", "gray30"),
            anchor="w",
            command=self.show_config_frame
        )
        self.config_button.grid(row=1, column=0, sticky="ew")
        
        self.execute_button = customtkinter.CTkButton(
            self.navigation_frame,
            corner_radius=0,
            height=40,
            border_spacing=10,
            text="Executar Previsões",
            fg_color="transparent",
            text_color=("gray10", "gray90"),
            hover_color=("gray70", "gray30"),
            anchor="w",
            command=self.show_execute_frame
        )
        self.execute_button.grid(row=2, column=0, sticky="ew")
        
        self.results_button = customtkinter.CTkButton(
            self.navigation_frame,
            corner_radius=0,
            height=40,
            border_spacing=10,
            text="Visualizar Resultados",
            fg_color="transparent",
            text_color=("gray10", "gray90"),
            hover_color=("gray70", "gray30"),
            anchor="w",
            command=self.show_results_frame
        )
        self.results_button.grid(row=3, column=0, sticky="ew")
        
        # Frame principal (área de conteúdo)
        self.main_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)
        
        # Dicionário para armazenar os frames das diferentes telas
        self.frames = {}
        
        # Cria os frames das diferentes telas
        self.create_frames()
        
        # Mostra a tela inicial (Gerenciar Cenários)
        self.show_config_frame()

        # Configura o handler de log para a caixa de texto de execução
        self.log_handler = GuiLogHandler(self.frames["execute"].log_textbox)
        logger.addHandler(self.log_handler)

        # Inicializa o banco de dados de resultados
        self.initialize_results_database()

        # Atualiza a lista de séries disponíveis
        status = consolidate_series(get_database_path("dados_bcb.db"))
        if not status[0]:
            logger.warning(status[1])
        else:
            logger.info(status[1])
    
    def initialize_results_database(self):
        """
        Inicializa o banco de dados de resultados se não existir.
        Garante que a aplicação pode funcionar mesmo sem execuções prévias.
        """
        try:
            result_path = get_database_path("previsoes.db")
            
            with SqliteAdapter(str(result_path)) as adapter:
                adapter.create_schema_if_not_exists()
                
            logger.info("Banco de dados de resultados inicializado com sucesso.")
        except Exception as e:
            logger.error(f"Erro ao inicializar banco de resultados: {e}")

    def create_frames(self):
        """
        Cria os frames para cada tela da aplicação.
        """
        # Frame de configuração de cenários
        self.frames["config"] = ConfigManagerFrame(self.main_frame)
        
        # Frame de execução
        self.frames["execute"] = self.create_execute_frame()
        
        # Frame de resultados
        self.frames["results"] = self.create_results_frame()
    
    def create_execute_frame(self):
        """
        Cria o frame de execução de previsões.
        """
        frame = customtkinter.CTkFrame(self.main_frame)
        frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)
        
        # Título
        title_label = customtkinter.CTkLabel(
            frame,
            text="Execução de Previsões",
            font=customtkinter.CTkFont(size=20, weight="bold")
        )
        title_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")
        
        # Área de conteúdo
        content_frame = customtkinter.CTkFrame(frame)
        content_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(10, 20))
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_rowconfigure(1, weight=1)
        
        # Botão de execução
        self.execute_btn = customtkinter.CTkButton(
            content_frame,
            text="Iniciar Execução de Todos os Cenários",
            height=40,
            font=customtkinter.CTkFont(size=14, weight="bold"),
            command=self.start_execution_thread
        )
        self.execute_btn.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        
        # Barra de progresso
        self.progress_bar = customtkinter.CTkProgressBar(content_frame)
        self.progress_bar.grid(row=3, column=0, padx=20, pady=(10, 5), sticky="ew")
        self.progress_bar.set(0) # Inicializa com 0

        # Label de status
        self.status_label = customtkinter.CTkLabel(content_frame, text="Aguardando execução...")
        self.status_label.grid(row=4, column=0, padx=20, pady=(0, 10), sticky="w")

        # Área de logs
        log_label = customtkinter.CTkLabel(
            content_frame,
            text="Logs de Execução:",
            font=customtkinter.CTkFont(size=14, weight="bold")
        )
        log_label.grid(row=1, column=0, padx=20, pady=(10, 5), sticky="w")
        
        frame.log_textbox = customtkinter.CTkTextbox(content_frame, height=400)
        frame.log_textbox.grid(row=2, column=0, sticky="nsew", padx=20, pady=(5, 20))
        
        return frame
    
    def create_results_frame(self):
        """
        Cria o frame de visualização de resultados.
        """
        frame = customtkinter.CTkFrame(self.main_frame)
        frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(2, weight=1) # Ajustado para acomodar o gráfico
        
        # Frame de cabeçalho com título e botões
        header_frame = customtkinter.CTkFrame(frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=20, pady=(20, 10))
        header_frame.grid_columnconfigure(0, weight=1)

        # Título
        title_label = customtkinter.CTkLabel(
            header_frame,
            text="Resultados das Previsões",
            font=customtkinter.CTkFont(size=20, weight="bold")
        )
        title_label.grid(row=0, column=0, sticky="w")
        
        # Frame para botões de ação
        buttons_frame = customtkinter.CTkFrame(header_frame, fg_color="transparent")
        buttons_frame.grid(row=0, column=1, sticky="e")

        # Botão de atualização
        refresh_button = customtkinter.CTkButton(
            buttons_frame,
            text="Atualizar",
            command=self.load_results_to_table
        )
        refresh_button.pack(side="left", padx=(0, 10))

        # Botão de exportação para CSV
        export_csv_button = customtkinter.CTkButton(
            buttons_frame,
            text="Exportar CSV",
            command=self.export_results_to_csv
        )
        export_csv_button.pack(side="left", padx=(0, 10))

        # Botão de exportação para Excel
        export_excel_button = customtkinter.CTkButton(
            buttons_frame,
            text="Exportar Excel",
            command= self.export_results_to_excel
        )
        export_excel_button.pack(side="left")
        
        # Tabela de resultados
        self.results_table = ttk.Treeview(frame)
        self.results_table.grid(row=1, column=0, sticky="nsew", padx=20, pady=(10, 20))
        
        # Scrollbars para a tabela
        vsb = ttk.Scrollbar(frame, orient="vertical", command=self.results_table.yview)
        vsb.grid(row=1, column=1, sticky="ns")
        self.results_table.configure(yscrollcommand=vsb.set)
        
        hsb = ttk.Scrollbar(frame, orient="horizontal", command=self.results_table.xview)
        hsb.grid(row=2, column=0, sticky="ew")
        self.results_table.configure(xscrollcommand=hsb.set)

        # Frame para o gráfico
        self.chart_frame = customtkinter.CTkFrame(frame)
        self.chart_frame.grid(row=3, column=0, columnspan=2, sticky="nsew", padx=20, pady=(10, 20))
        self.chart_frame.grid_columnconfigure(0, weight=1)
        self.chart_frame.grid_rowconfigure(0, weight=1)

        # Adiciona um evento de seleção à tabela para exibir o gráfico
        self.results_table.bind("<<TreeviewSelect>>", self.on_scenario_select)
        
        return frame
    
    def show_config_frame(self):
        """
        Mostra o frame de configuração de cenários.
        """
        self.select_frame_by_name("config")
        self.frames["config"].load_and_display_scenarios()
    
    def show_execute_frame(self):
        """
        Mostra o frame de execução.
        """
        self.select_frame_by_name("execute")
    
    def show_results_frame(self):
        """
        Mostra o frame de resultados.
        """
        self.select_frame_by_name("results")
        self.load_results_to_table()
    
    def select_frame_by_name(self, name):
        """
        Seleciona um frame por nome, escondendo os outros.
        """
        for frame_name, frame in self.frames.items():
            frame.grid_remove()
        
        if name in self.frames:
            self.frames[name].grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        
        self.update_navigation_buttons(name)
    
    def update_navigation_buttons(self, selected_name):
        """
        Atualiza a aparência dos botões de navegação.
        """
        buttons = {
            "config": self.config_button,
            "execute": self.execute_button,
            "results": self.results_button
        }
        
        for name, button in buttons.items():
            if name == selected_name:
                button.configure(fg_color=("gray75", "gray25"))
            else:
                button.configure(fg_color="transparent")
    
    def start_execution_thread(self):
        """
        Inicia a execução dos cenários em uma thread separada para não bloquear a GUI.
        """
        self.execute_btn.configure(state="disabled", text="Executando...")
        self.progress_bar.set(0)
        self.status_label.configure(text="Iniciando execução...")
        execution_thread = threading.Thread(target=self.run_all_scenarios)
        execution_thread.start()
    
    def run_all_scenarios(self):
        """
        Lógica de execução de todos os cenários.
        """
        config_path = get_config_path("scenarios_config.yaml")
        data_db_path = get_database_path("dados_bcb.db") # Assumindo que o banco de dados está na raiz
        results_db_path = get_database_path("previsoes.db")

        try:
            scenarios = load_scenarios(config_path)
            total_scenarios = len(scenarios)
            logger.info(f"Iniciando a execução de {total_scenarios} cenários.")
            
            for i, scenario in enumerate(scenarios):
                scenario_name = scenario.get("nome_cenario", "Cenário Desconhecido")
                self.after(0, self.status_label.configure, f"Executando cenário: {scenario_name} ({i+1}/{total_scenarios})")
                self.after(0, self.progress_bar.set, (i + 1) / total_scenarios)
                run_single_scenario(scenario, data_db_path, results_db_path)

            logger.info("Todos os cenários foram executados com sucesso.")
            self.after(0, messagebox.showinfo, "Execução Concluída", "Todos os cenários foram executados com sucesso!")
        except Exception as e:
            logger.error(f"Erro durante a execução dos cenários: {e}")
            self.after(0, messagebox.showerror, "Erro na Execução", f"Ocorreu um erro: {e}")
        finally:
            self.after(0, self.enable_execute_button)
            self.after(0, self.status_label.configure, "Execução finalizada.")
            self.after(0, self.progress_bar.set, 1.0)

    def enable_execute_button(self):
        """
        Reabilita o botão de execução.
        """
        self.execute_btn.configure(state="normal", text="Iniciar Execução de Todos os Cenários")

    def load_results_to_table(self):
        """
        Carrega os resultados do banco de dados e os exibe na tabela.
        """
        for item in self.results_table.get_children():
            self.results_table.delete(item)

        try:
            results_db_path = get_database_path("previsoes.db")
            
            with SqliteAdapter(str(results_db_path)) as adapter:
                # Inclui as métricas de avaliação na consulta
                results = adapter.query("SELECT nome_cenario, serie_id, data_execucao, data_previsao, frequencia_serie, valor_previsto, limite_inferior, limite_superior, modelo_utilizado, parametros_modelo, rmse, mae, mape FROM resultados_previsao ORDER BY data_execucao DESC")

            if not results:
                self.results_table.insert("", "end", values=("Nenhum resultado encontrado.", "", "", "", "", "", "", "", "", "", "", "", "", ""))
                return

            # Define as colunas da tabela
            columns = list(results[0].keys())
            self.results_table["columns"] = columns
            self.results_table.column("#0", width=0, stretch=tk.NO) # Coluna fantasma
            
            for col in columns:
                self.results_table.heading(col, text=col, anchor=tk.W)
                self.results_table.column(col, anchor=tk.W, width=100)

            # Insere os dados na tabela
            for row in results:
                self.results_table.insert("", "end", values=list(row))

        except Exception as e:
            messagebox.showerror("Erro ao Carregar Resultados", f"Não foi possível carregar os resultados: {e}")
            logger.error(f"Erro ao carregar resultados: {e}")

    def export_results_to_csv(self):
        """
        Exporta os resultados da tabela para um arquivo CSV.
        """
        try:
            # Solicita ao usuário o local para salvar o arquivo
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                title="Salvar resultados como CSV"
            )
            
            if not file_path:
                return  # Usuário cancelou

            # Carrega os dados do banco de dados
            results_db_path = get_database_path("previsoes.db")
            
            with SqliteAdapter(str(results_db_path)) as adapter:
                results = adapter.query("SELECT * FROM resultados_previsao ORDER BY data_execucao DESC")

            if not results:
                messagebox.showwarning("Aviso", "Nenhum resultado encontrado para exportar.")
                return

            # Converte para DataFrame
            df = pd.DataFrame(results)
            if df.empty:
                messagebox.showwarning("Aviso", "Nenhum resultado encontrado para exportar.")
                return

            # Exporta usando a função utilitária
            export_dataframe_to_csv(df, file_path)
            messagebox.showinfo("Exportação Concluída", f"Resultados exportados com sucesso para:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Erro na Exportação", f"Erro ao exportar resultados: {e}")
            logger.error(f"Erro ao exportar resultados para CSV: {e}")

    def export_results_to_excel(self):
        """
        Exporta os resultados da tabela para um arquivo Excel.
        """
        try:
            # Solicita ao usuário o local para salvar o arquivo
            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                title="Salvar resultados como Excel"
            )
            
            if not file_path:
                return  # Usuário cancelou

            # Carrega os dados do banco de dados
            results_db_path = get_database_path("previsoes.db")
            
            with SqliteAdapter(str(results_db_path)) as adapter:
                results = adapter.query("SELECT * FROM resultados_previsao ORDER BY data_execucao DESC")

            if not results:
                messagebox.showwarning("Aviso", "Nenhum resultado encontrado para exportar.")
                return

            # Converte para DataFrame
            df = pd.DataFrame(results)
            if df.empty:
                messagebox.showwarning("Aviso", "Nenhum resultado encontrado para exportar.")
                return

            # Exporta usando a função utilitária
            export_dataframe_to_excel(df, file_path)
            messagebox.showinfo("Exportação Concluída", f"Resultados exportados com sucesso para:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Erro na Exportação", f"Erro ao exportar resultados: {e}")
            logger.error(f"Erro ao exportar resultados para Excel: {e}")

    def on_scenario_select(self, event):
        """
        Lida com a seleção de um cenário na tabela de resultados para exibir o gráfico.
        """
        selected_item = self.results_table.focus()
        if not selected_item:
            return

        # Limpa o frame do gráfico antes de adicionar um novo
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        values = self.results_table.item(selected_item, "values")
        if not values or values[0] == "Nenhum resultado encontrado.":
            return

        # Extrai os dados necessários para o gráfico
        scenario_name = values[0]
        serie_id = values[1]

        # Reconstruir o DataFrame de previsão a partir dos valores da tabela
        # É mais robusto carregar os dados do DB novamente para garantir tipos corretos
        results_db_path = get_database_path("previsoes.db")
        data_db_path = get_database_path("dados_bcb.db")

        try:
            with SqliteAdapter(str(results_db_path)) as adapter:
                # Busca os resultados específicos para o cenário selecionado
                # Pode ser necessário ajustar a query para pegar apenas a última execução do cenário
                forecast_records = adapter.query(
                    "SELECT data_previsao, valor_previsto, limite_inferior, limite_superior FROM resultados_previsao WHERE nome_cenario = ? ORDER BY data_execucao DESC, data_previsao ASC LIMIT ?",
                    (scenario_name, 100) # Limita para evitar gráficos muito grandes, ajustar conforme necessário
                )
            if not forecast_records:
                logger.warning(f"Nenhum dado de previsão encontrado para o cenário {scenario_name} para plotagem.")
                return

            forecast_df = pd.DataFrame(forecast_records) 
            # Seta o index para refletir os da query
            forecast_df.columns = ["data_previsao", "valor_previsto", "limite_inferior", "limite_superior"]

            forecast_df["data_previsao"] = pd.to_datetime(forecast_df["data_previsao"])
            forecast_df["valor_previsto"] = pd.to_numeric(forecast_df["valor_previsto"])
            forecast_df["limite_inferior"] = pd.to_numeric(forecast_df["limite_inferior"])
            forecast_df["limite_superior"] = pd.to_numeric(forecast_df["limite_superior"])

            # Carregar dados históricos correspondentes
            historical_df = load_historical_data(serie_id, data_db_path)

            # Cria e exibe o gráfico
            create_forecast_chart(historical_df, [forecast_df], scenario_name, self.chart_frame)

        except Exception as e:
            logger.error(f"Erro ao gerar gráfico para o cenário {scenario_name}: {e}", exc_info=True)
            messagebox.showerror("Erro no Gráfico", f"Não foi possível gerar o gráfico: {e}")


