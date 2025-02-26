"""
Bot Tests
Testes do bot Telegram

✨ Parte do sistema EVA & GUARANI
🔍 Testes do bot
"""

import pytest
import logging
import asyncio
from pathlib import Path
from unittest.mock import MagicMock, patch
from telegram import Update, Message, Chat, User
from telegram.ext import Application, CommandHandler, MessageHandler
from ..core.progress_manager import ProgressManager
from ..bot.bot_manager import BotManager

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("✨test-bot✨")

@pytest.fixture
def bot_manager():
    """Fixture para o gerenciador do bot"""
    return BotManager()
    
@pytest.fixture
def progress_mgr():
    """Fixture para o gerenciador de progresso"""
    return ProgressManager()
    
@pytest.fixture
def mock_update():
    """Fixture para simular update do Telegram"""
    update = MagicMock(spec=Update)
    message = MagicMock(spec=Message)
    chat = MagicMock(spec=Chat)
    user = MagicMock(spec=User)
    
    # Configura IDs
    chat.id = 123456789
    user.id = 987654321
    user.first_name = "Test"
    
    # Configura mensagem
    message.chat = chat
    message.from_user = user
    message.text = "/start"
    
    # Configura update
    update.message = message
    update.effective_chat = chat
    update.effective_user = user
    
    return update
    
@pytest.mark.asyncio
async def test_bot_init(bot_manager):
    """Testa inicialização do bot"""
    assert bot_manager is not None
    assert isinstance(bot_manager, BotManager)
    
@pytest.mark.asyncio
async def test_start_command(bot_manager, mock_update):
    """Testa comando /start"""
    # Simula comando
    response = await bot_manager.start_command(mock_update, None)
    
    # Verifica resposta
    assert response is not None
    assert "Bem-vindo" in response
    
@pytest.mark.asyncio
async def test_help_command(bot_manager, mock_update):
    """Testa comando /help"""
    # Simula comando
    response = await bot_manager.help_command(mock_update, None)
    
    # Verifica resposta
    assert response is not None
    assert "Comandos disponíveis" in response
    
@pytest.mark.asyncio
async def test_status_command(bot_manager, mock_update):
    """Testa comando /status"""
    # Simula comando
    response = await bot_manager.status_command(mock_update, None)
    
    # Verifica resposta
    assert response is not None
    assert "Status do bot" in response
    
@pytest.mark.asyncio
async def test_resize_image(bot_manager, mock_update):
    """Testa redimensionamento de imagem"""
    # Simula imagem
    with patch("PIL.Image.open") as mock_open:
        # Configura mock
        mock_image = MagicMock()
        mock_image.size = (1000, 1000)
        mock_open.return_value = mock_image
        
        # Testa redimensionamento
        result = await bot_manager.resize_image("test.jpg", 500)
        
        # Verifica resultado
        assert result is not None
        assert mock_image.resize.called
        
@pytest.mark.asyncio
async def test_error_handling(bot_manager, mock_update):
    """Testa tratamento de erros"""
    # Simula erro
    error = Exception("Test error")
    
    # Testa handler
    await bot_manager.error_handler(mock_update, error)
    
    # Verifica se enviou mensagem de erro
    assert mock_update.message.reply_text.called
    
def test_command_registration(bot_manager):
    """Testa registro de comandos"""
    # Verifica handlers
    handlers = bot_manager.get_handlers()
    
    # Verifica tipos
    assert any(isinstance(h, CommandHandler) for h in handlers)
    assert any(isinstance(h, MessageHandler) for h in handlers)
    
def test_bot_configuration(bot_manager):
    """Testa configuração do bot"""
    # Verifica configurações
    config = bot_manager.get_config()
    
    assert "token" in config
    assert "allowed_types" in config
    assert "max_size" in config
    
@pytest.mark.asyncio
async def test_message_processing(bot_manager, mock_update):
    """Testa processamento de mensagens"""
    # Simula mensagem
    mock_update.message.text = "Teste de mensagem"
    
    # Processa mensagem
    response = await bot_manager.process_message(mock_update)
    
    # Verifica resposta
    assert response is not None
    
def test_performance(bot_manager, benchmark):
    """Testa performance"""
    def bot_operation():
        # Simula operações do bot
        bot_manager.get_handlers()
        bot_manager.get_config()
        return True
        
    # Executa benchmark
    result = benchmark(bot_operation)
    assert result is True 