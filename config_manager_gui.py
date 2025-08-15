import customtkinter
import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import yaml
import json
import logging
from pathlib import Path

from modules.scenario_loader import load_scenarios
from modules.data_loader import get_available_series, load_data_from_csv, load_data_from_excel # Importa as novas funções
from utils.get_base_path import get_base_path

logger = logging.getLogger(__name__)

class ConfigManagerFrame(customtkinter.CTkFrame):
    """
    Frame para gerenciar a configuração de cenários.
    """
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self.config_file_path = get_base_path("scenarios_config.yaml")
        self.data_db_path = get_base_path("dados_bcb.db") # Caminho para o DB de dados históricos
        self.scenarios = []

        # Este frame irá conter o título e os botões de ação
        self.header_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 10), sticky="ew")
        self.header_frame.grid_columnconfigure(0, weight=1) # Coluna do título (expansível)
        self.header_frame.grid_columnconfigure(1, weight=0) # Coluna dos botões (não expansível)

        # Título (agora dentro do header_frame)
        self.title_label = customtkinter.CTkLabel(
            self.header_frame, # Mestre alterado para header_frame
            text="Cenários",
            font=customtkinter.CTkFont(size=20, weight="bold")
        )
        self.title_label.grid(row=0, column=0, sticky="w")

        # Frame para os botões de ação (agora dentro do header_frame)
        self.action_buttons_frame = customtkinter.CTkFrame(self.header_frame, fg_color="transparent")
        self.action_buttons_frame.grid(row=0, column=1, sticky="e")

        # Botões (nenhuma alteração aqui, eles usam .pack dentro do seu frame)
        self.add_button = customtkinter.CTkButton(
            self.action_buttons_frame, text="Adicionar Novo", command=self.add_scenario
        )
        self.add_button.pack(side="left", padx=(0, 10))

        self.edit_button = customtkinter.CTkButton(
            self.action_buttons_frame, text="Editar Selecionado", command=self.edit_scenario
        )
        self.edit_button.pack(side="left", padx=(0, 10))

        self.remove_button = customtkinter.CTkButton(
            self.action_buttons_frame, text="Remover Selecionado", command=self.remove_scenario
        )
        self.remove_button.pack(side="left", padx=(0, 10))

        self.import_csv_button = customtkinter.CTkButton(
            self.action_buttons_frame, text="Importar CSV", command=self.import_csv_data
        )
        self.import_csv_button.pack(side="left", padx=(0, 10))

        self.import_excel_button = customtkinter.CTkButton(
            self.action_buttons_frame, text="Importar Excel", command=self.import_excel_data
        )
        self.import_excel_button.pack(side="left")

        # Tabela de cenários
        self.scenario_table = ttk.Treeview(self, columns=("Nome", "Série", "Modelo", "Horizonte"), show="headings")
        self.scenario_table.grid(row=2, column=0, sticky="nsew", padx=20, pady=(10, 0))

        self.scenario_table.heading("Nome", text="Nome do Cenário")
        self.scenario_table.heading("Série", text="ID da Série")
        self.scenario_table.heading("Modelo", text="Modelo")
        self.scenario_table.heading("Horizonte", text="Horizonte")

        self.scenario_table.column("Nome", width=150)
        self.scenario_table.column("Série", width=100)
        self.scenario_table.column("Modelo", width=100)
        self.scenario_table.column("Horizonte", width=80)

        # Scrollbars para a tabela
        vsb = ttk.Scrollbar(self, orient="vertical", command=self.scenario_table.yview)
        vsb.grid(row=2, column=1, sticky="ns")
        self.scenario_table.configure(yscrollcommand=vsb.set)

        hsb = ttk.Scrollbar(self, orient="horizontal", command=self.scenario_table.xview)
        hsb.grid(row=3, column=0, sticky="ew")
        self.scenario_table.configure(xscrollcommand=hsb.set)

        self.load_and_display_scenarios()

    def load_and_display_scenarios(self):
        """
        Carrega os cenários do arquivo e os exibe na tabela.
        """
        for item in self.scenario_table.get_children():
            self.scenario_table.delete(item)

        try:
            self.scenarios = load_scenarios(self.config_file_path)
            if not self.scenarios:
                self.scenario_table.insert("", "end", values=("Nenhum cenário configurado.", "", "", ""))
                return

            for scenario in self.scenarios:
                self.scenario_table.insert(
                    "", "end",
                    values=(
                        scenario.get("nome_cenario"),
                        scenario.get("serie_id"),
                        scenario.get("modelo"),
                        scenario.get("horizonte_previsao")
                    ),
                    tags=(scenario.get("nome_cenario"),) # Tag para fácil identificação
                )

        except (FileNotFoundError, ValueError) as e:
            messagebox.showerror("Erro de Configuração", f"Erro ao carregar cenários: {e}")
            logger.error(f"Erro ao carregar cenários: {e}")
            self.scenarios = []

    def add_scenario(self):
        """
        Abre uma janela para adicionar um novo cenário.
        """
        # Passa o caminho do DB de dados históricos para a janela do formulário
        add_window = ScenarioFormWindow(self, title="Adicionar Cenário", data_db_path=self.data_db_path)
        self.master.wait_window(add_window)
        self.load_and_display_scenarios()

    def edit_scenario(self):
        """
        Abre uma janela para editar o cenário selecionado.
        """
        selected_item = self.scenario_table.focus()
        if not selected_item:
            messagebox.showwarning("Edição de Cenário", "Por favor, selecione um cenário para editar.")
            return

        scenario_name = self.scenario_table.item(selected_item, "values")[0]
        scenario_to_edit = next((s for s in self.scenarios if s["nome_cenario"] == scenario_name), None)

        if scenario_to_edit:
            # Passa o caminho do DB de dados históricos para a janela do formulário
            edit_window = ScenarioFormWindow(self, title="Editar Cenário", scenario_data=scenario_to_edit, data_db_path=self.data_db_path)
            self.master.wait_window(edit_window)
            self.load_and_display_scenarios()
        else:
            messagebox.showerror("Erro", "Cenário selecionado não encontrado.")

    def remove_scenario(self):
        """
        Remove o cenário selecionado.
        """
        selected_item = self.scenario_table.focus()
        if not selected_item:
            messagebox.showwarning("Remoção de Cenário", "Por favor, selecione um cenário para remover.")
            return

        scenario_name = self.scenario_table.item(selected_item, "values")[0]

        if messagebox.askyesno("Confirmar Remoção", f"Tem certeza que deseja remover o cenário \'{scenario_name}\'?"):
            try:
                # Remove o cenário da lista em memória
                self.scenarios = [s for s in self.scenarios if s["nome_cenario"] != scenario_name]

                # Salva a lista atualizada de cenários no arquivo YAML
                with open(self.config_file_path, "w", encoding="utf-8") as f:
                    yaml.dump({"cenarios": self.scenarios}, f, allow_unicode=True, sort_keys=False)

                messagebox.showinfo("Sucesso", f"Cenário \'{scenario_name}\' removido com sucesso!")
                logger.info(f"Cenário \'{scenario_name}\' removido.")
                self.load_and_display_scenarios() # Recarrega a lista na GUI
            except Exception as e:
                messagebox.showerror("Erro ao Remover", f"Não foi possível remover o cenário: {e}")
                logger.error(f"Erro ao remover cenário: {e}")

    def import_csv_data(self):
        """
        Abre uma caixa de diálogo para selecionar um arquivo CSV e importa os dados.
        """
        file_path = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Selecionar arquivo CSV"
        )
        if file_path:
            try:
                df = load_data_from_csv(Path(file_path))
                # Decidir o que fazer com o DataFrame carregado.
                # Por exemplo, salvar no banco de dados de dados históricos ou processar.
                # Por enquanto, apenas exibe uma mensagem de sucesso.
                messagebox.showinfo("Importação CSV", f"Dados do CSV carregados com sucesso! {len(df)} registros.")
                logger.info(f"Dados do CSV {file_path} carregados com sucesso.")
            except Exception as e:
                messagebox.showerror("Erro de Importação CSV", f"Não foi possível carregar o arquivo CSV: {e}")
                logger.error(f"Erro ao importar CSV {file_path}: {e}")

    def import_excel_data(self):
        """
        Abre uma caixa de diálogo para selecionar um arquivo Excel e importa os dados.
        """
        file_path = filedialog.askopenfilename(
            filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")],
            title="Selecionar arquivo Excel"
        )
        if file_path:
            try:
                df = load_data_from_excel(Path(file_path))
                # Decidir o que fazer com o DataFrame carregado.
                # Por exemplo, salvar no banco de dados de dados históricos ou processar.
                # Por enquanto, apenas exibe uma mensagem de sucesso.
                messagebox.showinfo("Importação Excel", f"Dados do Excel carregados com sucesso! {len(df)} registros.")
                logger.info(f"Dados do Excel {file_path} carregados com sucesso.")
            except Exception as e:
                messagebox.showerror("Erro de Importação Excel", f"Não foi possível carregar o arquivo Excel: {e}")
                logger.error(f"Erro ao importar Excel {file_path}: {e}")

class ScenarioFormWindow(customtkinter.CTkToplevel):
    """
    Janela de formulário para adicionar ou editar um cenário.
    """
    def __init__(self, master, title="Cenário", scenario_data=None, data_db_path=None):
        super().__init__(master)
        self.title(title)
        self.geometry("500x600")
        self.transient(master)
        self.grab_set()

        self.scenario_data = scenario_data if scenario_data else {}
        self.master_frame = master
        self.data_db_path = data_db_path # Recebe o caminho do DB de dados históricos

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.create_form_widgets()

        if self.scenario_data:
            self.fill_form_with_data()

    def create_form_widgets(self):
        """
        Cria os campos do formulário para o cenário.
        """
        row = 0

        # Nome do Cenário
        customtkinter.CTkLabel(self, text="Nome do Cenário:").grid(row=row, column=0, padx=10, pady=5, sticky="w")
        self.name_entry = customtkinter.CTkEntry(self)
        self.name_entry.grid(row=row, column=1, padx=10, pady=5, sticky="ew")
        row += 1

        # ID da Série (agora um CTkComboBox)
        customtkinter.CTkLabel(self, text="ID da Série:").grid(row=row, column=0, padx=10, pady=5, sticky="w")
        
        # Carrega as séries disponíveis
        available_series = get_available_series(self.data_db_path)
        if not available_series:
            available_series = ["Nenhuma série disponível"] # Opção padrão se não houver séries
            messagebox.showwarning("Aviso", "Nenhuma série histórica encontrada no banco de dados. Por favor, crie o banco de dados de exemplo ou importe dados.")

        self.serie_id_menu = customtkinter.CTkOptionMenu(self, values=available_series)
        self.serie_id_menu.grid(row=row, column=1, padx=10, pady=5, sticky="ew")
        self.serie_id_menu.set(available_series[0]) # Define o primeiro como padrão
        row += 1

        # Modelo
        customtkinter.CTkLabel(self, text="Modelo:").grid(row=row, column=0, padx=10, pady=5, sticky="w")
        self.model_options = ["ARIMA", "Prophet", "RandomForest"]
        self.model_menu = customtkinter.CTkOptionMenu(self, values=self.model_options)
        self.model_menu.grid(row=row, column=1, padx=10, pady=5, sticky="ew")
        self.model_menu.set(self.model_options[0])
        row += 1

        # Horizonte de Previsão
        customtkinter.CTkLabel(self, text="Horizonte de Previsão:").grid(row=row, column=0, padx=10, pady=5, sticky="w")
        self.horizon_entry = customtkinter.CTkEntry(self)
        self.horizon_entry.grid(row=row, column=1, padx=10, pady=5, sticky="ew")
        row += 1

        # Intervalo de Confiança
        customtkinter.CTkLabel(self, text="Intervalo de Confiança (0.0-1.0):").grid(row=row, column=0, padx=10, pady=5, sticky="w")
        self.confidence_entry = customtkinter.CTkEntry(self)
        self.confidence_entry.grid(row=row, column=1, padx=10, pady=5, sticky="ew")
        row += 1

        # Parâmetros do Modelo (JSON)
        customtkinter.CTkLabel(self, text="Parâmetros do Modelo (JSON):").grid(row=row, column=0, padx=10, pady=5, sticky="w")
        self.params_textbox = customtkinter.CTkTextbox(self, height=100)
        self.params_textbox.grid(row=row, column=1, padx=10, pady=5, sticky="ew")
        row += 1

        # Botões Salvar e Cancelar
        self.save_button = customtkinter.CTkButton(self, text="Salvar", command=self.save_scenario)
        self.save_button.grid(row=row, column=0, padx=10, pady=20, sticky="ew")

        self.cancel_button = customtkinter.CTkButton(self, text="Cancelar", command=self.destroy)
        self.cancel_button.grid(row=row, column=1, padx=10, pady=20, sticky="ew")

    def fill_form_with_data(self):
        """
        Preenche o formulário com os dados do cenário para edição.
        """
        self.name_entry.insert(0, self.scenario_data.get("nome_cenario", ""))
        # Define o valor da ComboBox para a série ID
        self.serie_id_menu.set(self.scenario_data.get("serie_id", self.serie_id_menu.cget("values")[0]))
        self.model_menu.set(self.scenario_data.get("modelo", self.model_options[0]))
        self.horizon_entry.insert(0, str(self.scenario_data.get("horizonte_previsao", "")))
        self.confidence_entry.insert(0, str(self.scenario_data.get("intervalo_confianca", "")))
        
        params = self.scenario_data.get("parametros", {})
        self.params_textbox.insert("1.0", json.dumps(params, indent=2))

    def save_scenario(self):
        """
        Salva o cenário (novo ou editado) no arquivo YAML.
        """
        new_scenario = {
            "nome_cenario": self.name_entry.get(),
            "serie_id": self.serie_id_menu.get(), # Pega o valor da ComboBox
            "modelo": self.model_menu.get(),
            "horizonte_previsao": int(self.horizon_entry.get()),
            "intervalo_confianca": float(self.confidence_entry.get())
        }
        
        try:
            params_str = self.params_textbox.get("1.0", "end-1c")
            new_scenario["parametros"] = json.loads(params_str) if params_str.strip() else {}
        except json.JSONDecodeError:
            messagebox.showerror("Erro de Parâmetros", "Parâmetros do Modelo não são um JSON válido.")
            return

        # Validação básica
        if not new_scenario["nome_cenario"] or not new_scenario["serie_id"]:
            messagebox.showerror("Erro de Validação", "Nome do Cenário e ID da Série são obrigatórios.")
            return

        try:
            all_scenarios = load_scenarios(self.master_frame.config_file_path)
        except (FileNotFoundError, ValueError):
            all_scenarios = []

        if self.scenario_data: # Edição
            # Encontra e substitui o cenário antigo
            found = False
            for i, scenario in enumerate(all_scenarios):
                if scenario.get("nome_cenario") == self.scenario_data.get("nome_cenario"):
                    all_scenarios[i] = new_scenario
                    found = True
                    break
            if not found:
                # Se o nome do cenário foi alterado, remove o antigo e adiciona o novo
                all_scenarios = [s for s in all_scenarios if s["nome_cenario"] != self.scenario_data.get("nome_cenario")]
                all_scenarios.append(new_scenario)
        else: # Novo cenário
            if any(s.get("nome_cenario") == new_scenario["nome_cenario"] for s in all_scenarios):
                messagebox.showerror("Erro", "Já existe um cenário com este nome.")
                return
            all_scenarios.append(new_scenario)

        try:
            with open(self.master_frame.config_file_path, "w", encoding="utf-8") as f:
                yaml.dump({"cenarios": all_scenarios}, f, allow_unicode=True, sort_keys=False)
            messagebox.showinfo("Sucesso", "Cenário salvo com sucesso!")
            logger.info(f"Cenário \'{new_scenario["nome_cenario"]}\' salvo/atualizado.")
            self.destroy()
        except Exception as e:
            messagebox.showerror("Erro ao Salvar", f"Não foi possível salvar o cenário: {e}")
            logger.error(f"Erro ao salvar cenário: {e}")

# --- Funções auxiliares para a App principal (app_gui.py) --- #

def create_config_frame(master_frame, app_instance):
    """
    Cria e retorna o frame de gerenciamento de cenários para a janela principal.
    """
    frame = ConfigManagerFrame(master_frame)
    frame.grid(row=0, column=0, sticky="nsew")
    return frame
