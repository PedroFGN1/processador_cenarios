
import pytest
import yaml
from pathlib import Path
from modules.scenario_loader import load_scenarios

# Fixture para criar um arquivo YAML de configuração temporário
@pytest.fixture
def temp_config_file(tmp_path):
    config_data = {
        "cenarios": [
            {
                "nome_cenario": "Cenario Teste 1",
                "serie_id": "123",
                "modelo": "ARIMA",
                "horizonte_previsao": 12,
                "parametros_modelo": {"p": 1, "d": 1, "q": 1}
            },
            {
                "nome_cenario": "Cenario Teste 2",
                "serie_id": "456",
                "modelo": "Prophet",
                "horizonte_previsao": 6,
                "parametros_modelo": {"growth": "linear"}
            }
        ]
    }
    file_path = tmp_path / "test_config.yaml"
    with open(file_path, "w", encoding="utf-8") as f:
        yaml.dump(config_data, f)
    return file_path

# Fixture para criar um arquivo YAML vazio
@pytest.fixture
def empty_config_file(tmp_path):
    file_path = tmp_path / "empty_config.yaml"
    file_path.touch()
    return file_path

# Fixture para criar um arquivo YAML malformado
@pytest.fixture
def malformed_config_file(tmp_path):
    file_path = tmp_path / "malformed_config.yaml"
    file_path.write_text("cenarios: - item1\n  - item2: [}") # YAML inválido
    return file_path

# Fixture para criar um arquivo YAML sem a chave 'cenarios'
@pytest.fixture
def no_scenarios_key_config_file(tmp_path):
    config_data = {
        "outras_configuracoes": {
            "chave": "valor"
        }
    }
    file_path = tmp_path / "no_scenarios_config.yaml"
    with open(file_path, "w", encoding="utf-8") as f:
        yaml.dump(config_data, f)
    return file_path

def test_load_scenarios_success(temp_config_file):
    scenarios = load_scenarios(temp_config_file)
    assert len(scenarios) == 2
    assert scenarios[0]["nome_cenario"] == "Cenario Teste 1"
    assert scenarios[1]["modelo"] == "Prophet"

def test_load_scenarios_file_not_found():
    with pytest.raises(FileNotFoundError, match="Arquivo de configuração não encontrado"):
        load_scenarios(Path("non_existent_file.yaml"))

def test_load_scenarios_empty_file(empty_config_file):
    scenarios = load_scenarios(empty_config_file)
    assert scenarios == []

def test_load_scenarios_malformed_yaml(malformed_config_file):
    with pytest.raises(ValueError, match="Arquivo YAML malformado"):
        load_scenarios(malformed_config_file)

def test_load_scenarios_no_scenarios_key(no_scenarios_key_config_file):
    with pytest.raises(ValueError, match="Estrutura inválida no arquivo de configuração"):
        load_scenarios(no_scenarios_key_config_file)

def test_load_scenarios_config_path_none():
    with pytest.raises(FileNotFoundError, match="Arquivo de configuração não encontrado"):
        load_scenarios(None)



