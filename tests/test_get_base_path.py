import pytest
import os
import sys
from unittest.mock import patch
from utils.get_base_path import get_config_path, get_database_path

# Mock para simular o ambiente de aplicação "frozen" (empacotada)
@pytest.fixture
def mock_frozen_environment():
    with patch.object(sys, 'frozen', True):
        with patch.object(sys, 'executable', '/path/to/dist/app_executable'):
            yield

# Mock para simular o ambiente de aplicação "não frozen" (desenvolvimento)
@pytest.fixture
def mock_unfrozen_environment():
    with patch.object(sys, 'frozen', False):
        with patch.object(sys, 'argv', ['/path/to/script/main.py']):
            yield
'''
# Teste para get_app_base_path em ambiente frozen
def test_get_app_base_path_frozen(mock_frozen_environment):
    base_path = get_app_base_path()
    assert base_path == os.path.dirname('/path/to/dist/app_executable')

# Teste para get_app_base_path em ambiente unfrozen
def test_get_app_base_path_unfrozen(mock_unfrozen_environment):
    base_path = get_app_base_path()
    assert base_path == os.path.dirname(os.path.abspath('/path/to/script/main.py'))
'''
# Teste para get_config_path em ambiente frozen
def test_get_config_path_frozen(mock_frozen_environment):
    config_path = get_config_path()
    assert config_path == os.path.join(os.path.dirname('/path/to/dist/app_executable'), 'config.yaml')

# Teste para get_config_path em ambiente unfrozen
def test_get_config_path_unfrozen(mock_unfrozen_environment):
    config_path = get_config_path()
    assert config_path == os.path.join(os.path.dirname(os.path.abspath('/path/to/script/main.py')), 'config.yaml')

# Teste para get_database_path em ambiente frozen
def test_get_database_path_frozen(mock_frozen_environment):
    db_path = get_database_path()
    assert db_path == os.path.join(os.path.dirname('/path/to/dist/app_executable'), 'data.db')

# Teste para get_database_path em ambiente unfrozen
def test_get_database_path_unfrozen(mock_unfrozen_environment):
    db_path = get_database_path()
    assert db_path == os.path.join(os.path.dirname(os.path.abspath('/path/to/script/main.py')), 'data.db')


