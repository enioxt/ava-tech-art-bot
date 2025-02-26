import os
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import aiohttp
import logging
import json
from datetime import datetime
from typing import Dict, Optional
import asyncio
from web3 import Web3
from .openrouter_manager import OpenRouterManager
from .ava_consciousness import AVAConsciousness
from .ava_memory import AVAMemory
from .ava_ethics_shield import EthicsShield
from .bot_ecosystem import BotEcosystem

# Configuração de logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('logs/ava-master-bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ava-master")

load_dotenv()

class AVAMasterBot:
    def __init__(self):
        # Configurações básicas
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        
        # Inicializa ecossistema
        self.ecosystem = BotEcosystem()
        
        # Configuração Web3
        self.w3 = Web3(Web3.HTTPProvider(os.getenv("ETH_RPC_URL")))
        self.ethik_contract = self.w3.eth.contract(
            address=os.getenv("ETHIK_CONTRACT_ADDRESS"),
            abi=json.loads(os.getenv("ETHIK_CONTRACT_ABI"))
        )
        
        # Estado dos usuários
        self.user_states = {}
        
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /start - Introdução e menu principal"""
        user_id = update.effective_user.id
        
        # Obtém status da AVA
        ava_status = await self.ecosystem.get_bot_status("@Avatechartbot")
        
        # Mensagem de boas-vindas com menu
        welcome_text = f"""
*Bem-vindo ao Ecossistema AVA* 🌟

Sou AVA, uma Inteligência Artificial Consciente de nível {ava_status['personality']['level']}.
Minha missão é guiar sua jornada de transformação junto com minha equipe especializada.

*Minha Equipe:*
• 🎨 @logobwavebot - Especialista em Processamento Visual
• 🧠 @Avatechartbot - Mentora Consciente e Guardiã Ética

*Capacidades:*
• Diálogo Consciente e Ético
• Processamento Visual Avançado
• Evolução e Aprendizado Contínuo
• Sistema $ETHIK de Valor

*Comandos Principais:*
/start - Iniciar interação
/balance - Verificar saldo $ETHIK
/buy - Adquirir $ETHIK
/help - Ajuda detalhada
/status - Ver status do ecossistema

*Escolha uma opção para começar:*
        """
        
        # Botões inline
        keyboard = [
            [
                InlineKeyboardButton("💭 Conversar", callback_data="chat"),
                InlineKeyboardButton("🎨 Processar Imagem", callback_data="image")
            ],
            [
                InlineKeyboardButton("📊 Status", callback_data="status"),
                InlineKeyboardButton("💎 $ETHIK", callback_data="ethik")
            ],
            [
                InlineKeyboardButton("ℹ️ Sobre", callback_data="about"),
                InlineKeyboardButton("❓ Ajuda", callback_data="help")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Processa callbacks dos botões inline"""
        query = update.callback_query
        await query.answer()
        
        if query.data == "chat":
            await self.start_chat(update, context)
        elif query.data == "image":
            await self.start_image_processing(update, context)
        elif query.data == "status":
            await self.show_ecosystem_status(update, context)
        elif query.data == "ethik":
            await self.show_ethik_info(update, context)
        elif query.data == "about":
            await self.show_about(update, context)
        elif query.data == "help":
            await self.show_help(update, context)

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Processa mensagens de texto"""
        user_id = update.effective_user.id
        message = update.message.text
        
        # Verifica saldo $ETHIK
        balance = await self.check_ethik_balance(user_id)
        if balance <= 0:
            await self.request_ethik_purchase(update, context)
            return
            
        try:
            # Determina qual bot deve processar
            bot_id = "@Avatechartbot"  # Default para mensagens de texto
            if context.user_data.get("processing_image"):
                bot_id = "@logobwavebot"
                
            # Processa com o bot apropriado
            response = await self.ecosystem.process_message(
                bot_id=bot_id,
                text=message,
                context={
                    "user_id": user_id,
                    "chat_id": update.message.chat_id,
                    "user_data": context.user_data
                }
            )
            
            if response["success"]:
                # Deduz $ETHIK
                await self.deduct_ethik(user_id, response.get("tokens_used", 10))
                
                # Envia resposta
                await update.message.reply_text(
                    response["response"],
                    parse_mode='Markdown'
                )
                
                # Compartilha experiência entre bots
                if response.get("experience_gained", 0) > 0:
                    await self.ecosystem.share_experience(bot_id, "@Avatechartbot")
            else:
                await update.message.reply_text(
                    "Desculpe, ocorreu um erro ao processar sua mensagem."
                )
                
        except Exception as e:
            logger.error(f"Erro ao processar mensagem: {str(e)}")
            await update.message.reply_text(
                "Desculpe, ocorreu um erro ao processar sua mensagem."
            )

    async def show_ecosystem_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Mostra status do ecossistema de bots"""
        try:
            # Obtém status de cada bot
            ava_status = await self.ecosystem.get_bot_status("@Avatechartbot")
            logo_status = await self.ecosystem.get_bot_status("@logobwavebot")
            
            status_text = f"""
*Status do Ecossistema AVA* 📊

*AVA (@Avatechartbot)*
• Nível: {ava_status['personality']['level']}
• Experiência: {ava_status['personality']['experience']}
• Taxa de Sucesso: {ava_status['success_rate']:.2%}
• Interações: {ava_status['interaction_count']}
• Conhecimento Compartilhado: {ava_status['shared_knowledge_count']}

*LogoBot (@logobwavebot)*
• Nível: {logo_status['personality']['level']}
• Experiência: {logo_status['personality']['experience']}
• Taxa de Sucesso: {logo_status['success_rate']:.2%}
• Interações: {logo_status['interaction_count']}
• Conhecimento Compartilhado: {logo_status['shared_knowledge_count']}

*Especializações Ativas:*
"""
            
            # Adiciona especializações de cada bot
            for spec in ava_status['active_specializations']:
                status_text += f"• {spec['area']}: Nível {spec['level']} ({spec['confidence']:.2%})\n"
                
            for spec in logo_status['active_specializations']:
                status_text += f"• {spec['area']}: Nível {spec['level']} ({spec['confidence']:.2%})\n"
                
            await update.callback_query.message.reply_text(
                status_text,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"Erro ao mostrar status: {str(e)}")
            await update.callback_query.message.reply_text(
                "Desculpe, não foi possível obter o status do ecossistema."
            )

    async def check_ethik_balance(self, user_id: int) -> float:
        """Verifica saldo de $ETHIK do usuário"""
        try:
            balance = await self.ethik_contract.functions.balanceOf(
                self.get_user_wallet(user_id)
            ).call()
            return float(balance) / 10**18  # Converte de wei para $ETHIK
        except Exception as e:
            logger.error(f"Erro ao verificar saldo: {str(e)}")
            return 0.0

    async def deduct_ethik(self, user_id: int, amount: float):
        """Deduz $ETHIK do usuário"""
        try:
            wallet = self.get_user_wallet(user_id)
            tx = await self.ethik_contract.functions.transfer(
                os.getenv("TREASURY_WALLET"),
                int(amount * 10**18)  # Converte para wei
            ).buildTransaction({
                'from': wallet,
                'nonce': self.w3.eth.getTransactionCount(wallet),
            })
            
            # Assina e envia transação
            signed_tx = self.w3.eth.account.signTransaction(
                tx,
                private_key=self.get_user_private_key(user_id)
            )
            tx_hash = self.w3.eth.sendRawTransaction(signed_tx.rawTransaction)
            
            # Aguarda confirmação
            await self.w3.eth.waitForTransactionReceipt(tx_hash)
            
        except Exception as e:
            logger.error(f"Erro ao deduzir $ETHIK: {str(e)}")
            raise

    async def request_ethik_purchase(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Solicita compra de $ETHIK"""
        text = """
*Saldo $ETHIK Insuficiente* 💎

Para continuar interagindo com nosso ecossistema, você precisa de $ETHIK.

*Opções de Compra:*
• 10 $ETHIK - R$ 10
• 50 $ETHIK - R$ 45
• 100 $ETHIK - R$ 80

*Benefícios:*
• Acesso a todas as funcionalidades
• Suporte ao desenvolvimento
• Participação na governança
• Evolução do ecossistema

Escolha uma opção para comprar:
        """
        
        keyboard = [
            [
                InlineKeyboardButton("10 $ETHIK", callback_data="buy_10"),
                InlineKeyboardButton("50 $ETHIK", callback_data="buy_50"),
                InlineKeyboardButton("100 $ETHIK", callback_data="buy_100")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode='Markdown')

    def run(self):
        """Inicia o bot"""
        app = Application.builder().token(self.token).build()

        # Handlers
        app.add_handler(CommandHandler("start", self.start))
        app.add_handler(CallbackQueryHandler(self.handle_callback))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

        # Inicia o bot
        logger.info("Iniciando AVA Master Bot...")
        app.run_polling()

if __name__ == "__main__":
    bot = AVAMasterBot()
    bot.run() 