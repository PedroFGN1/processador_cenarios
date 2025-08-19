
import pytest
import logging
import sys
from unittest.mock import MagicMock, patch
from utils.logger_config import setup_logger, GuiLogHandler

# Fixture para limpar os handlers do logger após cada teste
@pytest.fixture(autouse=True)
def clear_loggers():
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    for handler in logging.getLogger("processador_cenarios").handlers[:]:
        logging.getLogger("processador_cenarios").removeHandler(handler)
    yield
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    for handler in logging.getLogger("processador_cenarios").handlers[:]:
        logging.getLogger("processador_cenarios").removeHandler(handler)

# Testes para setup_logger
def test_setup_logger_returns_logger():
    logger = setup_logger()
    assert isinstance(logger, logging.Logger)
    assert logger.name == "processador_cenarios"

def test_setup_logger_sets_level():
    logger = setup_logger(level=logging.DEBUG)
    assert logger.level == logging.DEBUG

def test_setup_logger_adds_console_handler():
    logger = setup_logger()
    assert any(isinstance(h, logging.StreamHandler) for h in logger.handlers)

def test_setup_logger_prevents_duplicate_handlers():
    logger1 = setup_logger()
    initial_handler_count = len(logger1.handlers)
    logger2 = setup_logger() # Chama novamente
    assert len(logger2.handlers) == initial_handler_count # Não deve adicionar novos handlers

def test_setup_logger_applies_formatter():
    logger = setup_logger()
    console_handler = next(h for h in logger.handlers if isinstance(h, logging.StreamHandler))
    formatter = console_handler.formatter
    assert isinstance(formatter, logging.Formatter)
    # Testar um formato simples para garantir que o formatter está lá
    log_record = logging.LogRecord("test", logging.INFO, __file__, 1, "Test message", [], None)
    formatted_message = formatter.format(log_record)
    assert "Test message" in formatted_message
    assert " - INFO - " in formatted_message # Verifica parte do formato padrão

# Testes para GuiLogHandler
def test_gui_log_handler_inserts_text():
    mock_text_widget = MagicMock()
    handler = GuiLogHandler(mock_text_widget)
    logger = logging.getLogger("test_gui_log")
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)

    logger.info("Mensagem de teste")

    mock_text_widget.insert.assert_called_once()
    # Verifica que a mensagem formatada foi inserida
    # O formato padrão do logger inclui timestamp, nome, nível, etc.
    inserted_text = mock_text_widget.insert.call_args[0][1]
    assert "Mensagem de teste" in inserted_text
    assert " - INFO - " in inserted_text
    assert inserted_text.endswith("\n")

def test_gui_log_handler_scrolls_to_end():
    mock_text_widget = MagicMock()
    handler = GuiLogHandler(mock_text_widget)
    logger = logging.getLogger("test_gui_log_scroll")
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)

    logger.info("Outra mensagem")

    mock_text_widget.see.assert_called_once_with("end")

def test_gui_log_handler_handles_no_widget():
    handler = GuiLogHandler(None)
    logger = logging.getLogger("test_gui_log_no_widget")
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)

    # Não deve levantar exceção mesmo sem widget
    try:
        logger.info("Mensagem sem widget")
    except Exception as e:
        pytest.fail(f"GuiLogHandler levantou exceção sem widget: {e}")

def test_gui_log_handler_handles_widget_exception():
    mock_text_widget = MagicMock()
    mock_text_widget.insert.side_effect = Exception("Erro de widget simulado")
    handler = GuiLogHandler(mock_text_widget)
    logger = logging.getLogger("test_gui_log_widget_exception")
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)

    # Não deve levantar exceção, apenas logar internamente (ou ignorar)
    try:
        logger.info("Mensagem com erro de widget")
    except Exception as e:
        pytest.fail(f"GuiLogHandler levantou exceção do widget: {e}")

    mock_text_widget.insert.assert_called_once()



