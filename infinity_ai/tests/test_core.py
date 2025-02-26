"""
Core System Tests
Testes do sistema de valores fundamentais e indexação neural
"""

import pytest
from pathlib import Path
import tempfile
import shutil
import json
from datetime import datetime

from ..core.core_values import core_values, CodebaseIndex
from ..core.gratitude_logger import gratitude_logger

@pytest.fixture
def core_system():
    """Fixture do sistema principal"""
    return core_values

@pytest.fixture
def progress_mgr():
    """Fixture do gerenciador de progresso"""
    from ..core.progress_manager import progress_manager
    return progress_manager

@pytest.fixture
def codebase_index():
    """Fixture do índice do codebase"""
    return CodebaseIndex(
        file_path="test.py",
        last_modified=datetime.now().timestamp(),
        checksum="abc123",
        dependencies={"import os", "import sys"},
        concepts=["testing", "core"],
        importance=0.8,
        neural_connections={}
    )

def test_core_system_init(core_system):
    """Testa inicialização do sistema"""
    assert core_system is not None
    assert isinstance(core_system.index_dir, Path)
    assert core_system.neural_index == {}

def test_progress_manager_init(progress_mgr):
    """Testa inicialização do gerenciador de progresso"""
    assert progress_mgr is not None

def test_codebase_index_init(codebase_index):
    """Testa inicialização do índice"""
    assert codebase_index.file_path == "test.py"
    assert isinstance(codebase_index.last_modified, float)
    assert codebase_index.checksum == "abc123"
    assert "import os" in codebase_index.dependencies
    assert "testing" in codebase_index.concepts
    assert codebase_index.importance == 0.8
    assert codebase_index.neural_connections == {}

def test_core_system_values(core_system):
    """Testa valores do sistema"""
    # Cria arquivo temporário
    with tempfile.NamedTemporaryFile(suffix=".py") as tf:
        tf.write(b"class TestClass:\n    pass")
        tf.flush()
        
        # Testa análise
        concepts = core_system.analyze_file_concepts(Path(tf.name))
        assert "oop" in concepts
        
        # Testa importância
        importance = core_system.calculate_importance(Path(tf.name), concepts)
        assert 0 <= importance <= 1

def test_progress_manager_styles(progress_mgr):
    """Testa estilos do gerenciador de progresso"""
    # Testa criação de barra de progresso
    with progress_mgr.create_progress("Teste") as progress:
        assert progress is not None
        
    # Testa mensagens
    progress_mgr.show_status("Teste em andamento")
    progress_mgr.show_completion("Teste concluído")

def test_codebase_index_methods(codebase_index):
    """Testa métodos do índice"""
    # Testa conversão para dict
    data = codebase_index.to_dict()
    assert isinstance(data, dict)
    assert data["file_path"] == "test.py"
    
    # Testa criação a partir de dict
    new_index = CodebaseIndex.from_dict(data)
    assert new_index.file_path == codebase_index.file_path
    assert new_index.checksum == codebase_index.checksum

@pytest.mark.asyncio
async def test_core_system_integration(core_system, progress_mgr, codebase_index):
    """Testa integração entre componentes"""
    # Cria diretório temporário
    with tempfile.TemporaryDirectory() as tmpdir:
        # Cria arquivo de teste
        test_file = Path(tmpdir) / "test.py"
        test_file.write_text("class TestClass:\n    pass")
        
        # Indexa arquivo
        await core_system.index_file(test_file)
        
        # Verifica índice
        assert str(test_file) in core_system.neural_index
        
        # Atualiza conexões
        await core_system.update_neural_connections()
        
        # Salva e carrega índice
        core_system.save_neural_index()
        core_system.load_neural_index()

def test_error_handling():
    """Testa tratamento de erros"""
    with pytest.raises(Exception):
        # Tenta indexar arquivo inexistente
        core_values.calculate_file_checksum(Path("nonexistent.py"))
        
    with pytest.raises(Exception):
        # Tenta carregar arquivo inválido
        with tempfile.NamedTemporaryFile(suffix=".json") as tf:
            tf.write(b"invalid json")
            tf.flush()
            core_values.load_neural_index()

def test_file_operations(tmp_path):
    """Testa operações com arquivos"""
    # Cria arquivo de teste
    test_file = tmp_path / "test.py"
    test_file.write_text("""
import os
import sys

class TestClass:
    def test_method(self):
        pass
""")
    
    # Testa checksum
    checksum = core_values.calculate_file_checksum(test_file)
    assert isinstance(checksum, str)
    assert len(checksum) == 64  # SHA-256
    
    # Testa análise de conceitos
    concepts = core_values.analyze_file_concepts(test_file)
    assert "oop" in concepts
    assert "testing" in concepts
    
    # Testa dependências
    deps = core_values.find_dependencies(test_file)
    assert "import os" in deps
    assert "import sys" in deps

def test_performance(benchmark):
    """Testa performance do sistema"""
    def index_operation():
        # Cria arquivo temporário
        with tempfile.NamedTemporaryFile(suffix=".py") as tf:
            tf.write(b"class TestClass:\n    pass")
            tf.flush()
            
            # Executa operações
            core_values.calculate_file_checksum(Path(tf.name))
            core_values.analyze_file_concepts(Path(tf.name))
            core_values.find_dependencies(Path(tf.name))
    
    # Executa benchmark
    result = benchmark(index_operation)
    assert result is not None