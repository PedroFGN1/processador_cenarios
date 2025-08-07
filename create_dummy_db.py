import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path

def create_dummy_data_db(db_path: Path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS dados_bcb")
    cursor.execute("""
        CREATE TABLE dados_bcb (
            serie_id TEXT NOT NULL,
            data TEXT NOT NULL,
            valor REAL NOT NULL,
            PRIMARY KEY (serie_id, data)
        )
    """)

    # Dados para IPCA (exemplo de série mensal, mas vamos simular diário para simplificar)
    ipca_data = []
    start_date = datetime(2020, 1, 1)
    for i in range(100):
        date = start_date + timedelta(days=i)
        value = 0.5 + (i * 0.01) + (i % 10) * 0.05 # Simula um crescimento com alguma sazonalidade
        ipca_data.append(("IPCA", date.strftime("%Y-%m-%d"), round(value, 2)))

    # Dados para SELIC (exemplo de série diária)
    selic_data = []
    start_date = datetime(2020, 1, 1)
    for i in range(100):
        date = start_date + timedelta(days=i)
        value = 2.0 + (i * 0.005) + (i % 5) * 0.02 # Simula um crescimento
        selic_data.append(("SELIC", date.strftime("%Y-%m-%d"), round(value, 2)))

    # Dados para VENDAS_MENSAIS (exemplo de série com mais ruído)
    vendas_data = []
    start_date = datetime(2020, 1, 1)
    for i in range(100):
        date = start_date + timedelta(days=i)
        value = 100.0 + (i * 0.5) + (i % 7) * 2.0 + (i % 3) * -1.0 # Crescimento com ruído e sazonalidade
        vendas_data.append(("VENDAS_MENSAIS", date.strftime("%Y-%m-%d"), round(value, 2)))

    cursor.executemany("INSERT INTO dados_bcb (serie_id, data, valor) VALUES (?, ?, ?)", ipca_data)
    cursor.executemany("INSERT INTO dados_bcb (serie_id, data, valor) VALUES (?, ?, ?)", selic_data)
    cursor.executemany("INSERT INTO dados_bcb (serie_id, data, valor) VALUES (?, ?, ?)", vendas_data)

    conn.commit()
    conn.close()
    print(f"Banco de dados de dados históricos criado em {db_path} com dados de exemplo.")

if __name__ == "__main__":
    base_path = Path(__file__).parent
    db_file = base_path / "dados_bcb.db"
    create_dummy_data_db(db_file)


