"""
Neural Index Tests
Testes do sistema de indexação neural

✨ Parte do sistema EVA & GUARANI
🔍 Testes de indexação neural
"""

import pytest
import logging
import tempfile
from pathlib import Path
from ..core.core_values import CodebaseIndex
from ..core.neural_index import NeuralIndexer

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("✨test-neural✨")

@pytest.fixture
def neural_indexer():
    """Fixture para o indexador neural"""
    return NeuralIndexer()
    
@pytest.fixture
def test_files(tmp_path):
    """Fixture para arquivos de teste"""
    # Cria arquivos temporários
    files = {
        "main.py": "def main():\n    print('Hello')\n",
        "utils.py": "def helper():\n    return True\n",
        "test.py": "def test_main():\n    assert True\n"
    }
    
    for name, content in files.items():
        (tmp_path / name).write_text(content)
        
    return tmp_path
    
def test_indexer_init(neural_indexer):
    """Testa inicialização do indexador"""
    assert neural_indexer is not None
    assert isinstance(neural_indexer, NeuralIndexer)
    
def test_file_indexing(neural_indexer, test_files):
    """Testa indexação de arquivos"""
    # Indexa arquivos
    for file in test_files.glob("*.py"):
        neural_indexer.index_file(file)
        
    # Verifica se foram indexados
    indexed = neural_indexer.get_indexed_files()
    assert len(indexed) == 3
    assert "main.py" in [f.name for f in indexed]
    
def test_concept_extraction(neural_indexer, test_files):
    """Testa extração de conceitos"""
    # Indexa arquivo
    main_file = test_files / "main.py"
    concepts = neural_indexer.extract_concepts(main_file)
    
    # Verifica conceitos
    assert isinstance(concepts, list)
    assert len(concepts) > 0
    assert "function" in concepts
    
def test_dependency_analysis(neural_indexer, test_files):
    """Testa análise de dependências"""
    # Indexa arquivos
    for file in test_files.glob("*.py"):
        neural_indexer.index_file(file)
        
    # Analisa dependências
    deps = neural_indexer.analyze_dependencies(test_files / "test.py")
    assert isinstance(deps, list)
    
def test_neural_connections(neural_indexer, test_files):
    """Testa conexões neurais"""
    # Indexa arquivos
    for file in test_files.glob("*.py"):
        neural_indexer.index_file(file)
        
    # Busca conexões
    main_file = test_files / "main.py"
    connections = neural_indexer.get_connections(main_file)
    
    assert isinstance(connections, list)
    assert len(connections) > 0
    
def test_importance_calculation(neural_indexer, test_files):
    """Testa cálculo de importância"""
    # Indexa arquivo
    main_file = test_files / "main.py"
    importance = neural_indexer.calculate_importance(main_file)
    
    assert isinstance(importance, float)
    assert importance >= 0
    
def test_index_persistence(neural_indexer, test_files, tmp_path):
    """Testa persistência do índice"""
    # Indexa arquivos
    for file in test_files.glob("*.py"):
        neural_indexer.index_file(file)
        
    # Salva índice
    index_file = tmp_path / "index.json"
    neural_indexer.save_index(index_file)
    
    # Carrega índice
    new_indexer = NeuralIndexer()
    new_indexer.load_index(index_file)
    
    # Verifica se manteve os dados
    assert len(new_indexer.get_indexed_files()) == 3
    
def test_search_functionality(neural_indexer, test_files):
    """Testa funcionalidade de busca"""
    # Indexa arquivos
    for file in test_files.glob("*.py"):
        neural_indexer.index_file(file)
        
    # Busca por conceito
    results = neural_indexer.search_by_concept("function")
    assert isinstance(results, list)
    assert len(results) > 0
    
    # Busca por similaridade
    results = neural_indexer.search_similar(test_files / "main.py")
    assert isinstance(results, list)
    
def test_error_handling(neural_indexer):
    """Testa tratamento de erros"""
    with pytest.raises(FileNotFoundError):
        neural_indexer.index_file("nonexistent.py")
        
    with pytest.raises(ValueError):
        neural_indexer.calculate_importance(None)
        
def test_performance(neural_indexer, test_files, benchmark):
    """Testa performance"""
    def index_operation():
        for file in test_files.glob("*.py"):
            neural_indexer.index_file(file)
        return True
        
    # Executa benchmark
    result = benchmark(index_operation)
    assert result is True 