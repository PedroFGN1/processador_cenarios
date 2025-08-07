import customtkinter
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import logging
import threading

from utils.logger_config import setup_logger, GuiLogHandler
from utils.get_base_path import get_base_path
from config_manager_gui import ConfigManagerFrame
from modules.scenario_loader import load_scenarios
from methods._run_forecasting import run_single_scenario
from persistence.sqlite_adapter import SqliteAdapter

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
        frame.grid_rowconfigure(1, weight=1)
        
        # Título
        title_label = customtkinter.CTkLabel(
            frame,
            text="Resultados das Previsões",
            font=customtkinter.CTkFont(size=20, weight="bold")
        )
        title_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")
        
        # Botão de atualização
        refresh_button = customtkinter.CTkButton(
            frame,
            text="Atualizar Resultados",
            command=self.load_results_to_table
        )
        refresh_button.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="e")
        
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
        execution_thread = threading.Thread(target=self.run_all_scenarios)
        execution_thread.start()
    
    def run_all_scenarios(self):
        """
        Lógica de execução de todos os cenários.
        """
        base_path = get_base_path()
        config_path = base_path / "scenarios_config.yaml"
        data_db_path = base_path / "dados_bcb.db" # Assumindo que o banco de dados está na raiz
        results_db_path = base_path / "previsoes.db"

        try:
            scenarios = load_scenarios(config_path)
            logger.info(f"Iniciando a execução de {len(scenarios)} cenários.")
            for scenario in scenarios:
                run_single_scenario(scenario, data_db_path, results_db_path)
            logger.info("Todos os cenários foram executados com sucesso.")
            messagebox.showinfo("Execução Concluída", "Todos os cenários foram executados com sucesso!")
        except Exception as e:
            logger.error(f"Erro durante a execução dos cenários: {e}")
            messagebox.showerror("Erro na Execução", f"Ocorreu um erro: {e}")
        finally:
            # Reabilita o botão de execução na thread principal
            self.after(0, self.enable_execute_button)

    def enable_execute_button(self):
        """
        Reabilita o botão de execução.
        """
        self.execute_btn.configure(state="normal", text="Iniciar Execução de Todos os Cenários")

    def load_results_to_table(self):
        """
        Carrega os resultados do banco de dados e os exibe na tabela.
        """
        # Limpa a tabela existente
        for item in self.results_table.get_children():
            self.results_table.delete(item)

        try:
            base_path = get_base_path()
            results_db_path = base_path / "previsoes.db"
            
            with SqliteAdapter(str(results_db_path)) as adapter:
                results = adapter.query("SELECT * FROM resultados_previsao ORDER BY data_execucao DESC")

            if not results:
                self.results_table.insert("", "end", text="Nenhum resultado encontrado.")
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


