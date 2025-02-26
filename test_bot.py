import logging
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackContext, Filters

# Carrega as variáveis de ambiente
load_dotenv()

# Configuração de logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler("bot.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def start(update: Update, context: CallbackContext):
    logger.info(f"Usuário {update.effective_user.id} iniciou o bot")
    update.message.reply_text(
        'Olá! Envie uma foto e eu vou redimensioná-la para você.'
    )

def handle_photo(update: Update, context: CallbackContext):
    logger.info(f"Recebendo foto do usuário {update.effective_user.id}")
    update.message.reply_text('Recebi sua foto! Processando...')
    # Aqui vai o código de processamento da imagem
    # Por enquanto só confirmamos o recebimento

def handle_text(update: Update, context: CallbackContext):
    logger.info(f"Mensagem de texto recebida do usuário {update.effective_user.id}")
    update.message.reply_text('Por favor, envie uma foto para que eu possa redimensioná-la.')

def error_handler(update: object, context: CallbackContext):
    logger.error(f"Erro: {context.error}")
    if update and hasattr(update, 'effective_message'):
        update.effective_message.reply_text(
            'Desculpe, ocorreu um erro. Por favor, tente novamente.'
        )

def main():
    try:
        # Obtém o token do arquivo .env
        token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not token:
            logger.error("Token não encontrado no arquivo .env")
            return

        logger.info("Iniciando o bot...")
        
        # Cria o Updater e passa o token do bot
        updater = Updater(token)

        # Obtém o dispatcher para registrar os handlers
        dp = updater.dispatcher

        # Adiciona os handlers
        dp.add_handler(CommandHandler("start", start))
        dp.add_handler(MessageHandler(Filters.photo, handle_photo))
        dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_text))
        
        # Registra o handler de erros
        dp.add_error_handler(error_handler)

        # Inicia o bot
        logger.info("Bot iniciado e aguardando mensagens...")
        updater.start_polling()

        # Mantém o bot rodando até que seja pressionado Ctrl+C
        updater.idle()

    except Exception as e:
        logger.error(f"Erro ao iniciar o bot: {e}")
        raise e

if __name__ == '__main__':
    main()