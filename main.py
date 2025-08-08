import customtkinter
from app_gui import App

if __name__ == "__main__":
    # Configura o tema e a cor da CustomTkinter
    customtkinter.set_appearance_mode("System")  # Modes: "System" (default), "Dark", "Light"
    customtkinter.set_default_color_theme("green")  # Themes: "blue" (default), "dark-blue", "green"

    # Cria a instância da aplicação
    app = App()
    
    # Inicia o loop principal da aplicação
    app.mainloop()
