"""
Progress Manager Tests
Testes do gerenciador de progresso

✨ Parte do sistema EVA & GUARANI
🔍 Testes de progresso visual
"""

import pytest
import logging
from pathlib import Path
from ..core.progress_manager import ProgressManager

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("✨test-progress✨")

@pytest.fixture
def progress_mgr():
    """Fixture para o gerenciador de progresso"""
    return ProgressManager()
    
def test_manager_init(progress_mgr):
    """Testa inicialização do gerenciador"""
    assert progress_mgr is not None
    assert isinstance(progress_mgr, ProgressManager)
    
def test_style_configuration(progress_mgr):
    """Testa configuração de estilos"""
    styles = progress_mgr.get_styles()
    
    # Verifica estilos básicos
    assert "info" in styles
    assert "success" in styles
    assert "error" in styles
    assert "warning" in styles
    
    # Verifica propriedades
    for style in styles.values():
        assert "color" in style
        assert "prefix" in style
        
def test_status_display(progress_mgr, capsys):
    """Testa exibição de status"""
    # Testa mensagem info
    progress_mgr.show_status("Test info", "info")
    captured = capsys.readouterr()
    assert "Test info" in captured.out
    
    # Testa mensagem success
    progress_mgr.show_status("Test success", "success")
    captured = capsys.readouterr()
    assert "Test success" in captured.out
    
    # Testa mensagem error
    progress_mgr.show_status("Test error", "error")
    captured = capsys.readouterr()
    assert "Test error" in captured.out
    
def test_progress_bar(progress_mgr, capsys):
    """Testa barra de progresso"""
    # Cria barra
    bar = progress_mgr.create_progress_bar("Test Progress")
    assert bar is not None
    
    # Atualiza progresso
    bar.update(50)
    captured = capsys.readouterr()
    assert "50%" in captured.out
    
    # Completa barra
    bar.update(100)
    captured = capsys.readouterr()
    assert "100%" in captured.out
    
def test_completion_message(progress_mgr, capsys):
    """Testa mensagem de conclusão"""
    progress_mgr.show_completion("Test complete")
    captured = capsys.readouterr()
    assert "Test complete" in captured.out
    assert "✨" in captured.out
    
def test_error_handling(progress_mgr):
    """Testa tratamento de erros"""
    with pytest.raises(ValueError):
        progress_mgr.show_status("Test", "invalid_style")
        
    with pytest.raises(ValueError):
        progress_mgr.create_progress_bar("")
        
def test_style_customization(progress_mgr):
    """Testa customização de estilos"""
    # Adiciona estilo customizado
    custom_style = {
        "color": "magenta",
        "prefix": "🎨"
    }
    progress_mgr.add_style("custom", custom_style)
    
    # Verifica se foi adicionado
    styles = progress_mgr.get_styles()
    assert "custom" in styles
    assert styles["custom"] == custom_style
    
def test_progress_formatting(progress_mgr):
    """Testa formatação do progresso"""
    # Testa diferentes formatos
    formats = [
        (25, "[██--------]"),
        (50, "[█████-----]"),
        (75, "[███████---]"),
        (100, "[██████████]")
    ]
    
    for progress, expected in formats:
        bar = progress_mgr.format_progress(progress)
        assert expected in bar
        
def test_async_progress(progress_mgr):
    """Testa progresso assíncrono"""
    async def async_task():
        # Simula tarefa assíncrona
        bar = progress_mgr.create_progress_bar("Async Task")
        for i in range(0, 101, 25):
            await bar.update_async(i)
        return True
        
    # Executa tarefa
    result = pytest.mark.asyncio(async_task())
    assert result is True
    
def test_performance(progress_mgr, benchmark):
    """Testa performance"""
    def progress_operation():
        for i in range(100):
            progress_mgr.show_status(f"Step {i}", "info")
        return True
        
    # Executa benchmark
    result = benchmark(progress_operation)
    assert result is True 