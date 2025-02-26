import os
import sys
import logging
import asyncio
import platform
from datetime import datetime
from dotenv import load_dotenv
from telegram import Bot

# Configuração avançada de logging
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.DEBUG,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(f'bot_test_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    ]
)
logger = logging.getLogger(__name__)

async def test_connection():
    """Testa a conexão com a API do Telegram com logs detalhados"""
    try:
        # Log do ambiente
        logger.info("="*50)
        logger.info("INICIANDO TESTE DE CONEXÃO DO BOT")
        logger.info("="*50)
        logger.info(f"Sistema Operacional: {platform.system()} {platform.version()}")
        logger.info(f"Python Version: {sys.version}")
        logger.info(f"Diretório atual: {os.getcwd()}")
        
        # Verifica se o arquivo .env existe
        env_path = os.path.join(os.getcwd(), '.env')
        if os.path.exists(env_path):
            logger.info(f"Arquivo .env encontrado em: {env_path}")
        else:
            logger.error(f"Arquivo .env NÃO encontrado em: {env_path}")
            return False
        
        # Carrega variáveis de ambiente
        logger.info("Tentando carregar variáveis de ambiente...")
        load_dotenv()
        logger.info("Variáveis de ambiente carregadas")
        
        # Verifica o token
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not token:
            logger.error("❌ Token não encontrado no arquivo .env")
            return False
        
        token_preview = f"{token[:10]}...{token[-10:]}"
        logger.info(f"✓ Token encontrado: {token_preview}")
        
        # Tenta criar uma instância do bot
        logger.info("Tentando criar instância do bot...")
        bot = Bot(token=token)
        logger.info("✓ Instância do bot criada com sucesso")
        
        # Tenta fazer uma requisição de teste
        logger.info("Testando conexão com a API do Telegram...")
        me = await bot.get_me()
        logger.info("✓ Conexão estabelecida com sucesso!")
        logger.info("-"*50)
        logger.info("INFORMAÇÕES DO BOT:")
        logger.info(f"Nome: {me.first_name}")
        logger.info(f"Username: @{me.username}")
        logger.info(f"ID: {me.id}")
        logger.info(f"É bot? {me.is_bot}")
        logger.info("-"*50)
        
        # Testa outras funcionalidades básicas
        logger.info("Testando funcionalidades básicas...")
        
        try:
            updates = await bot.get_updates(limit=1, timeout=1)
            logger.info(f"✓ get_updates funcionando (recebidos: {len(updates)} updates)")
        except Exception as e:
            logger.warning(f"⚠️ Erro ao testar get_updates: {str(e)}")
        
        try:
            commands = await bot.get_my_commands()
            logger.info(f"✓ get_my_commands funcionando (comandos: {len(commands)})")
        except Exception as e:
            logger.warning(f"⚠️ Erro ao testar get_my_commands: {str(e)}")
        
        logger.info("="*50)
        logger.info("TESTE CONCLUÍDO COM SUCESSO!")
        logger.info("="*50)
        
        return True
        
    except Exception as e:
        logger.error("="*50)
        logger.error("ERRO FATAL DURANTE O TESTE")
        logger.error(f"Tipo do erro: {type(e).__name__}")
        logger.error(f"Mensagem de erro: {str(e)}")
        logger.error("Traceback completo:", exc_info=True)
        logger.error("="*50)
        return False

async def main():
    print("\n🤖 Iniciando teste do bot Telegram...\n")
    success = await test_connection()
    
    if success:
        print("\n✅ Teste concluído com sucesso! Verifique os logs para mais detalhes.")
    else:
        print("\n❌ Teste falhou! Verifique os logs para identificar o problema.")
    
    print("\nℹ️ Um arquivo de log foi criado com informações detalhadas.")

if __name__ == '__main__':
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main()) 