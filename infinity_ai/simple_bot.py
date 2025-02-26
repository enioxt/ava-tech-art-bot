import logging
import os
import sys
from pathlib import Path

# Adiciona o diretório src ao PYTHONPATH
src_path = str(Path(__file__).parent.parent)
if src_path not in sys.path:
    sys.path.append(src_path)

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from infinity_ai.config import BOT_TOKEN, BOT_NAME, validate_config

# Configuração de logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /start."""
    user = update.effective_user
    await update.message.reply_text(
        f"👋 Olá {user.first_name}! Eu sou {BOT_NAME}.\n"
        "🎨 Envie-me uma imagem e eu a redimensionarei para você!"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /help."""
    await update.message.reply_text(
        "🤖 Como usar o bot:\n\n"
        "1. Envie uma imagem\n"
        "2. Eu a redimensionarei automaticamente\n"
        "3. Enviarei a imagem otimizada de volta\n\n"
        "Comandos disponíveis:\n"
        "/start - Inicia o bot\n"
        "/help - Mostra esta mensagem de ajuda"
    )

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processa fotos enviadas."""
    try:
        # Por enquanto, apenas confirma o recebimento
        await update.message.reply_text(
            "🖼️ Recebi sua imagem! Em breve implementarei o redimensionamento."
        )
    except Exception as e:
        logger.error(f"Erro ao processar foto: {str(e)}")
        await update.message.reply_text(
            "❌ Desculpe, ocorreu um erro ao processar sua imagem."
        )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processa mensagens de texto."""
    await update.message.reply_text(
        "🖼️ Por favor, envie uma imagem para que eu possa redimensioná-la."
    )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Trata erros do bot."""
    logger.error(f"Erro: {context.error}")
    try:
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "❌ Desculpe, ocorreu um erro inesperado."
            )
    except:
        pass

def main():
    """Função principal."""
    try:
        # Valida configurações
        validate_config()
        
        # Cria a aplicação
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Adiciona handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
        
        # Adiciona handler de erro
        application.add_error_handler(error_handler)
        
        # Inicia o bot
        logger.info("🤖 Bot iniciado!")
        application.run_polling()
        
    except Exception as e:
        logger.error(f"❌ Erro fatal: {str(e)}")
        raise

if __name__ == '__main__':
    main() 