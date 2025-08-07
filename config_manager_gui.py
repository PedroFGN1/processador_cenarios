import customtkinter
import tkinter as tk
from tkinter import messagebox
import yaml
import json
import logging
from pathlib import Path

from modules.scenario_loader import load_scenarios
from utils.get_base_path import get_base_path

logger = logging.getLogger(__name__)

class ConfigManagerFrame(customtkinter.CTkFrame):
    """
    Frame para gerenciar a configuração de cenários.
    """
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.base_path = get_base_path()
        self.config_file_path = self.base_path / "scenarios_config.yaml"
        self.scenarios = []

        # Título
        self.title_label = customtkinter.CTkLabel(
            self,
            text="Gerenciamento de Cenários",
            font=customtkinter.CTkFont(size=20, weight="bold")
        )
        self.title_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        # Frame para os botões de ação
        self.action_buttons_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.action_buttons_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="e")

        self.add_button = customtkinter.CTkButton(
            self.action_buttons_frame,
            text="Adicionar Novo",
            command=self.add_scenario
        )
        self.add_button.pack(side="left", padx=(0, 10))

        self.edit_button = customtkinter.CTkButton(
            self.action_buttons_frame,
            text="Editar Selecionado",
            command=self.edit_scenario
        )
        self.edit_button.pack(side="left", padx=(0, 10))

        self.remove_button = customtkinter.CTkButton(
            self.action_buttons_frame,
            text="Remover Selecionado",
            command=self.remove_scenario
        )
        self.remove_button.pack(side="left")

        # Frame para a lista de cenários
        self.scenario_list_frame = customtkinter.CTkScrollableFrame(self)
        self.scenario_list_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(10, 20))
        self.scenario_list_frame.grid_columnconfigure(0, weight=1)

        self.load_and_display_scenarios()

    def load_and_display_scenarios(self):
        """
        Carrega os cenários do arquivo e os exibe na interface.
        """
        # Limpa os widgets existentes na lista
        for widget in self.scenario_list_frame.winfo_children():
            widget.destroy()

        try:
            self.scenarios = load_scenarios(self.config_file_path)
            if not self.scenarios:
                customtkinter.CTkLabel(self.scenario_list_frame, text="Nenhum cenário configurado.").pack(pady=10)
                return

            for i, scenario in enumerate(self.scenarios):
                scenario_name = scenario.get("nome_cenario", f"Cenário {i+1}")
                scenario_label = customtkinter.CTkLabel(
                    self.scenario_list_frame,
                    text=f"- {scenario_name} ({scenario.get("modelo")})",
                    anchor="w",
                    font=customtkinter.CTkFont(size=14)
                )
                scenario_label.pack(fill="x", pady=2, padx=5)

        except (FileNotFoundError, ValueError) as e:
            messagebox.showerror("Erro de Configuração", f"Erro ao carregar cenários: {e}")
            logger.error(f"Erro ao carregar cenários: {e}")
            self.scenarios = [] # Garante que a lista esteja vazia em caso de erro

    def add_scenario(self):
        """
        Abre uma janela para adicionar um novo cenário.
        """
        add_window = ScenarioFormWindow(self, title="Adicionar Cenário")
        self.master.wait_window(add_window) # Espera a janela fechar
        self.load_and_display_scenarios() # Recarrega a lista após fechar

    def edit_scenario(self):
        """
        Abre uma janela para editar o cenário selecionado.
        """
        # Lógica para selecionar o cenário (ainda não implementada)
        messagebox.showinfo("Funcionalidade", "Selecione um cenário para editar (funcionalidade em desenvolvimento).")

    def remove_scenario(self):
        """
        Remove o cenário selecionado.
        """
        # Lógica para selecionar e remover o cenário (ainda não implementada)
        messagebox.showinfo("Funcionalidade", "Selecione um cenário para remover (funcionalidade em desenvolvimento).")

class ScenarioFormWindow(customtkinter.CTkToplevel):
    """
    Janela de formulário para adicionar ou editar um cenário.
    """
    def __init__(self, master, title="Cenário", scenario_data=None):
        super().__init__(master)
        self.title(title)
        self.geometry("500x600")
        self.transient(master) # Faz com que a janela seja modal
        self.grab_set() # Bloqueia interação com a janela principal

        self.scenario_data = scenario_data if scenario_data else {}
        self.master_frame = master

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Widgets do formulário
        self.create_form_widgets()

        # Preenche com dados existentes se for edição
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

        # ID da Série
        customtkinter.CTkLabel(self, text="ID da Série:").grid(row=row, column=0, padx=10, pady=5, sticky="w")
        self.serie_id_entry = customtkinter.CTkEntry(self)
        self.serie_id_entry.grid(row=row, column=1, padx=10, pady=5, sticky="ew")
        row += 1

        # Modelo
        customtkinter.CTkLabel(self, text="Modelo:").grid(row=row, column=0, padx=10, pady=5, sticky="w")
        self.model_options = ["ARIMA", "Prophet", "RandomForest"]
        self.model_menu = customtkinter.CTkOptionMenu(self, values=self.model_options)
        self.model_menu.grid(row=row, column=1, padx=10, pady=5, sticky="ew")
        self.model_menu.set(self.model_options[0]) # Valor padrão
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
        self.serie_id_entry.insert(0, self.scenario_data.get("serie_id", ""))
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
            "serie_id": self.serie_id_entry.get(),
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
            # Carrega todos os cenários existentes
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
                all_scenarios.append(new_scenario) # Caso não encontre (nome mudou, etc.)
        else: # Novo cenário
            # Verifica se o nome do cenário já existe
            if any(s.get("nome_cenario") == new_scenario["nome_cenario"] for s in all_scenarios):
                messagebox.showerror("Erro", "Já existe um cenário com este nome.")
                return
            all_scenarios.append(new_scenario)

        # Salva de volta no arquivo YAML
        try:
            with open(self.master_frame.config_file_path, "w", encoding="utf-8") as f:
                yaml.dump({"cenarios": all_scenarios}, f, allow_unicode=True, sort_keys=False)
            messagebox.showinfo("Sucesso", "Cenário salvo com sucesso!")
            logger.info(f"Cenário \{new_scenario["nome_cenario"]}\ salvo/atualizado.")
            self.destroy() # Fecha a janela após salvar
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


