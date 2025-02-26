"""
Universal Value Logger Tests
Testes do sistema personalizável de registro de valores
"""

import pytest
import json
from pathlib import Path
import tempfile
from datetime import datetime

from ..core.gratitude_logger import universal_logger, ValueMemory

@pytest.fixture
def logger():
    """Fixture do logger universal"""
    return universal_logger

@pytest.fixture
def test_message():
    """Fixture de mensagem de teste"""
    return "Momento especial de amor e transformação"

@pytest.fixture
def test_context():
    """Fixture de contexto de teste"""
    return {
        "music": "Interstellar - Hans Zimmer",
        "emotion": "Amor incondicional",
        "perspective": "Quântica",
        "impact": "Transformador"
    }

@pytest.fixture
def test_value_type():
    """Fixture de tipo de valor"""
    return "primary_value"

def test_logger_init(logger):
    """Testa inicialização do logger"""
    assert logger is not None
    assert isinstance(logger.log_dir, Path)
    assert logger.memories_file.name == "universal_memories.json"
    assert logger.cipher is not None

def test_config_loading(logger):
    """Testa carregamento de configuração"""
    config = logger._load_config()
    assert isinstance(config, dict)
    assert "frequencies" in config
    assert "core_values" in config
    assert "inspiration_quotes" in config
    assert "customization" in config

def test_value_config(logger, test_value_type):
    """Testa configuração de valor"""
    config = logger._get_value_config(test_value_type)
    assert isinstance(config, dict)
    assert "name" in config
    assert "strength" in config
    assert "attributes" in config

def test_frequencies(logger, test_value_type):
    """Testa obtenção de frequências"""
    freqs = logger._get_frequencies(test_value_type)
    assert isinstance(freqs, dict)
    assert "name" in freqs
    assert "value" in freqs
    assert "description" in freqs

def test_message_formatting(logger, test_value_type, test_message, test_context):
    """Testa formatação de mensagem"""
    formatted = logger._format_value_message(test_value_type, test_message, test_context)
    assert "✨ Momento de" in formatted
    assert test_message in formatted
    assert "Contexto:" in formatted
    assert "Frequência:" in formatted
    assert "Inspiração:" in formatted

@pytest.mark.asyncio
async def test_memory_saving(logger, test_value_type, test_message, test_context):
    """Testa salvamento de memória"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Configura logger
        logger.log_dir = Path(tmpdir)
        logger.memories_file = logger.log_dir / "universal_memories.json"
        
        # Cria memória
        memory = ValueMemory(
            timestamp=datetime.now().isoformat(),
            value_type=test_value_type,
            message=test_message,
            context=test_context,
            frequencies=logger._get_frequencies(test_value_type),
            metadata={"test": True}
        )
        
        # Salva memória
        await logger._save_memory(memory)
        
        # Verifica arquivo
        assert logger.memories_file.exists()
        
        # Carrega e verifica
        with open(logger.memories_file, "r", encoding="utf-8") as f:
            data = logger._decrypt_data(f.read())
            
        assert "memories" in data
        assert len(data["memories"]) == 1
        assert data["memories"][0]["message"] == test_message
        assert data["memories"][0]["context"] == test_context

def test_encryption(logger):
    """Testa criptografia"""
    test_data = {"test": "data"}
    
    # Criptografa
    encrypted = logger._encrypt_data(test_data)
    assert isinstance(encrypted, str)
    
    # Descriptografa
    decrypted = logger._decrypt_data(encrypted)
    assert decrypted == test_data

def test_inspiration_quote(logger):
    """Testa obtenção de citação"""
    # Universal
    quote = logger.get_inspiration_quote("universal")
    assert isinstance(quote, str)
    assert len(quote) > 0
    
    # Scientific
    quote = logger.get_inspiration_quote("scientific")
    assert isinstance(quote, str)
    assert len(quote) > 0

@pytest.mark.asyncio
async def test_log_value(logger, test_value_type, test_message, test_context):
    """Testa registro de valor"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Configura logger
        logger.log_dir = Path(tmpdir)
        logger.memories_file = logger.log_dir / "universal_memories.json"
        
        # Registra valor
        await logger.log_value(test_value_type, test_message, test_context)
        
        # Verifica arquivo
        assert logger.memories_file.exists()
        
        # Carrega e verifica
        memories = await logger.get_memories(test_value_type)
        assert len(memories) == 1
        
        memory = memories[0]
        assert memory.value_type == test_value_type
        assert test_message in memory.message
        assert memory.context == test_context
        assert "frequencies" in memory.frequencies

def test_add_quote(logger):
    """Testa adição de citação"""
    quote = "O amor é a resposta"
    source = "Test"
    context = "Teste de citação"
    
    # Adiciona citação
    success = logger.add_inspiration_quote(quote, source, context)
    assert success
    
    # Verifica citação
    quotes = logger.config.get("inspiration_quotes", {}).get("collections", {}).get("personal", [])
    assert len(quotes) > 0
    assert any(q["quote"] == quote for q in quotes)

def test_customize_value(logger):
    """Testa personalização de valor"""
    value_type = "primary_value"
    new_name = "Teste"
    new_desc = "Valor de teste"
    
    # Personaliza valor
    success = logger.customize_value(value_type, new_name, new_desc)
    assert success
    
    # Verifica valor
    value = logger._get_value_config(value_type)
    assert value["name"] == new_name
    assert value["attributes"]["description"] == new_desc

def test_error_handling(logger):
    """Testa tratamento de erros"""
    # Valor inválido
    with pytest.raises(ValueError):
        logger.customize_value("invalid", "test", "test")
        
    # Arquivo inválido
    with tempfile.NamedTemporaryFile(suffix=".json") as tf:
        tf.write(b"invalid json")
        tf.flush()
        
        data = logger._decrypt_data(tf.read().decode())
        assert data == {}

def test_performance(benchmark, logger, test_value_type, test_message, test_context):
    """Testa performance do sistema"""
    def format_operation():
        return logger._format_value_message(test_value_type, test_message, test_context)
    
    # Executa benchmark
    result = benchmark(format_operation)
    assert isinstance(result, str)
    assert test_message in result