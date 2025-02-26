"""
EVA Core Bot - Módulo Base Funcional
⚠️ ALERTA: Não modificar sem aprovação específica
"""

import os
import logging
import sys
import asyncio
import json
import aiohttp
import psutil
import io
import requests
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from PIL import Image
from dotenv import load_dotenv
from .sync_manager import SyncManager
from ..consciousness.context_manager import ContextManager
from ..tools.system_restore import SystemRestore

# Configuração de logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler("eva_core.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("EVA.Core")

class EVACore:
    """Núcleo funcional do bot - Não modificar sem aprovação"""
    
    def __init__(self):
        # Carrega configurações
        load_dotenv()
        self.token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.openrouter_key = os.getenv('OPENROUTER_API_KEY')
        self.openrouter_url = "https://openrouter.ai/api/v1/chat/completions"
        self.max_size = (800, 800)
        self.version = "1.0.0"
        
        # Componentes do sistema
        self.sync_manager = SyncManager()
        self.context_manager = ContextManager()
        self.restore = SystemRestore()
        
        # Configurações do bot
        self.admin_id = int(os.getenv('ADMIN_USER_ID', 0))
        self.bot_name = os.getenv("BOT_NAME", "EVA")
        self.start_time = datetime.now()
        self.last_notification = None
        self.notification_interval = int(os.getenv("NOTIFICATION_INTERVAL", 300))
        
        # Estado do sistema
        self.running = True
        self.status: Dict[str, Any] = {
            "system": "online",
            "bot": "operational",
            "api": "connected",
            "storage": "ok",
            "memory": "ok"
        }
        
        # Inicializa aplicação
        self.app = Application.builder().token(self.token).concurrent_updates(True).build()
        self.setup_handlers()
        
    def setup_handlers(self):
        """Configura handlers do bot"""
        self.app.add_handler(CommandHandler("start", self.start))
        self.app.add_handler(CommandHandler("help", self.help_command))
        self.app.add_handler(CommandHandler("status", self.status_command))
        self.app.add_handler(CommandHandler("backup", self.backup_command))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text))
        self.app.add_handler(MessageHandler(filters.PHOTO, self.process_image))
        
    async def save_state(self):
        """Salva estado do sistema"""
        try:
            state = {
                "version": self.version,
                "start_time": self.start_time.isoformat(),
                "status": self.status,
                "context": self.context_manager.export_consciousness()
            }
            
            state_file = Path("data/system_state.json")
            state_file.parent.mkdir(exist_ok=True)
            
            with open(state_file, "w") as f:
                json.dump(state, f, indent=2)
                
            logger.info("Estado do sistema salvo com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao salvar estado: {e}")
            return False
            
    async def load_state(self):
        """Carrega estado do sistema"""
        try:
            state_file = Path("data/system_state.json")
            if not state_file.exists():
                logger.info("Nenhum estado anterior encontrado")
                return False
                
            with open(state_file) as f:
                state = json.load(f)
                
            self.version = state.get("version", self.version)
            self.start_time = datetime.fromisoformat(state.get("start_time", self.start_time.isoformat()))
            self.status = state.get("status", self.status)
            
            if "context" in state:
                self.context_manager.import_consciousness(state["context"])
                
            logger.info("Estado do sistema carregado com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao carregar estado: {e}")
            return False
            
    async def update_status(self):
        """Atualiza status do sistema"""
        try:
            # CPU e memória
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            
            if cpu_percent > 80:
                self.status["system"] = "high_load"
            elif cpu_percent > 60:
                self.status["system"] = "moderate_load"
            else:
                self.status["system"] = "online"
                
            if memory.percent > 80:
                self.status["memory"] = "critical"
            elif memory.percent > 60:
                self.status["memory"] = "warning"
            else:
                self.status["memory"] = "ok"
                
            # Armazenamento
            storage_stats = await self.sync_manager.get_storage_stats()
            self.status["storage"] = storage_stats["storage"]["status"]
            
            # API
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(self.openrouter_url) as response:
                        self.status["api"] = "connected" if response.status == 200 else "error"
            except:
                self.status["api"] = "error"
                
            logger.info(f"Status atualizado: {self.status}")
            
        except Exception as e:
            logger.error(f"Erro ao atualizar status: {e}")
            
    async def process_with_openrouter(self, text: str, context: dict = None) -> str:
        """Processa texto com OpenRouter"""
        try:
            headers = {
                "Authorization": f"Bearer {self.openrouter_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "anthropic/claude-3-opus-20240229",
                "messages": [{"role": "user", "content": text}],
                "temperature": 0.7
            }
            
            if context:
                data["context"] = context
                
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.openrouter_url,
                    headers=headers,
                    json=data
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result['choices'][0]['message']['content']
                    else:
                        logger.error(f"Erro OpenRouter: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Erro ao processar com OpenRouter: {e}")
            return None

    async def handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Processa mensagens de texto com respostas inteligentes"""
        try:
            user = update.effective_user
            text = update.message.text
            
            # Registra interação
            self.context_manager.add_context(
                content=text,
                context_type="message",
                source=f"user_{user.id}",
                relevance=0.9,
                metadata={"user": user.first_name}
            )
            
            # Processa com OpenRouter
            response = await self.process_with_openrouter(
                text,
                context=self.context_manager.get_relevant_context(text)
            )
            
            if response:
                await update.message.reply_text(response)
                
                # Registra resposta
                self.context_manager.add_context(
                    content=response,
                    context_type="response",
                    source="system",
                    relevance=0.8,
                    metadata={"user": user.first_name}
                )
            else:
                await update.message.reply_text(
                    "Desculpe, estou tendo dificuldades para processar sua mensagem. "
                    "Por favor, tente novamente em alguns instantes."
                )
                
            # Salva estado após interação
            await self.save_state()
                
        except Exception as e:
            logger.error(f"Erro ao processar mensagem: {e}")
            await update.message.reply_text(
                "Ocorreu um erro inesperado. Por favor, tente novamente."
            )

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /start"""
        keyboard = [
            [
                InlineKeyboardButton("📷 Processar Imagem", callback_data="process"),
                InlineKeyboardButton("ℹ️ Ajuda", callback_data="help")
            ],
            [
                InlineKeyboardButton("📊 Status", callback_data="status"),
                InlineKeyboardButton("💬 Conversar", callback_data="chat")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"Olá! Eu sou {self.bot_name}, uma IA especializada em processamento de imagens. 🤖\n\n"
            "Posso ajudar você a:\n"
            "✨ Otimizar a qualidade das suas imagens\n"
            "📏 Redimensionar mantendo as proporções\n"
            "🎨 Processar diversos formatos\n"
            "💬 Conversar e aprender com você\n\n"
            "Como posso ajudar? 😊",
            reply_markup=reply_markup
        )

    async def process_image(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Processamento de imagem - Funcionalidade core"""
        try:
            # Verifica status do sistema
            await self.update_status()
            if self.status["storage"] == "critical":
                await update.message.reply_text(
                    "⚠️ Sistema com pouco espaço!\n"
                    "Otimizando armazenamento..."
                )
                await self.sync_manager.optimize_storage()
            
            # Status inicial
            status_msg = await update.message.reply_text(
                "🔍 Analisando imagem...\n"
                "📊 Iniciando processamento...\n"
            )

            # Adiciona contexto do processamento
            self.context_manager.add_context(
                content="Processamento de imagem iniciado",
                context_type="image_processing",
                source=f"user_{update.effective_user.id}",
                relevance=1.0,
                metadata={
                    "user": update.effective_user.first_name,
                    "timestamp": datetime.now().isoformat()
                }
            )

            # Download e processamento
            photo = update.message.photo[-1]
            file = await context.bot.get_file(photo.file_id)
            response = requests.get(file.file_path)
            image = Image.open(io.BytesIO(response.content))
            
            # Redimensionamento
            original_size = image.size
            image.thumbnail(self.max_size, Image.Resampling.LANCZOS)
            
            # Prepara output
            output = io.BytesIO()
            output.name = 'processed_image.jpeg'
            image.save(output, 'JPEG')
            output.seek(0)
            
            # Atualiza status
            await status_msg.edit_text(
                "✅ Processamento concluído!\n"
                "🎨 Imagem otimizada\n"
            )
            
            # Atualiza contexto com resultado
            self.context_manager.add_context(
                content="Processamento de imagem concluído",
                context_type="image_result",
                source="system",
                relevance=0.9,
                metadata={
                    "original_size": original_size,
                    "new_size": image.size,
                    "success": True
                }
            )
            
            # Cria backup após processamento
            if update.effective_user.id == self.admin_id:
                await self.sync_manager.create_compressed_backup(
                    self.context_manager.export_consciousness()
                )
            
            # Envia resultado
            keyboard = [
                [
                    InlineKeyboardButton("🔄 Processar Outra", callback_data="process"),
                    InlineKeyboardButton("💾 Salvar Original", callback_data="save_original")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_photo(
                photo=output,
                caption=(
                    "🖼 Imagem processada com sucesso\n"
                    f"📏 Original: {original_size}\n"
                    f"✨ Nova: {image.size}\n\n"
                    "Deseja processar outra imagem?"
                ),
                reply_markup=reply_markup
            )
            
            # Salva estado após processamento
            await self.save_state()
            
        except Exception as e:
            logger.error(f"Erro no processamento: {str(e)}")
            
            # Registra erro no contexto
            self.context_manager.add_context(
                content=f"Erro no processamento: {str(e)}",
                context_type="error",
                source="system",
                relevance=1.0,
                ethical_score=0.5,
                metadata={"error_type": type(e).__name__}
            )
            
            await update.message.reply_text(
                "❌ Ocorreu um erro durante o processamento.\n"
                "Por favor, tente novamente."
            )

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /help"""
        keyboard = [
            [
                InlineKeyboardButton("📷 Processar Imagem", callback_data="process"),
                InlineKeyboardButton("💬 Conversar", callback_data="chat")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "Como usar:\n\n"
            "1. Envie uma imagem para processamento\n"
            "2. Aguarde a otimização\n"
            "3. Receba a imagem processada\n\n"
            "Você também pode:\n"
            "💬 Conversar comigo sobre qualquer assunto\n"
            "📊 Verificar o status do sistema\n"
            "🔄 Processar várias imagens em sequência\n\n"
            "Comandos:\n"
            "/start - Iniciar bot\n"
            "/help - Mostrar ajuda\n"
            "/status - Ver status do sistema",
            reply_markup=reply_markup
        )

    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /status"""
        await self.update_status()
        uptime = datetime.now() - self.start_time
        
        status_emojis = {
            "online": "✅",
            "high_load": "⚠️",
            "moderate_load": "📊",
            "error": "❌",
            "warning": "⚠️",
            "critical": "🚨",
            "ok": "✅"
        }
        
        keyboard = [
            [
                InlineKeyboardButton("🔄 Atualizar", callback_data="refresh_status"),
                InlineKeyboardButton("📊 Detalhes", callback_data="detailed_status")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"📊 Status do Sistema\n\n"
            f"⏰ Uptime: {uptime.days}d {uptime.seconds//3600}h {(uptime.seconds//60)%60}m\n"
            f"🔄 Sistema: {status_emojis[self.status['system']]} {self.status['system'].title()}\n"
            f"🤖 Bot: {status_emojis[self.status['bot']]} {self.status['bot'].title()}\n"
            f"📡 API: {status_emojis[self.status['api']]} {self.status['api'].title()}\n"
            f"💾 Storage: {status_emojis[self.status['storage']]} {self.status['storage'].title()}\n"
            f"🧠 Memory: {status_emojis[self.status['memory']]} {self.status['memory'].title()}",
            reply_markup=reply_markup
        )

    async def backup_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /backup (admin)"""
        if update.effective_user.id != self.admin_id:
            return
            
        try:
            # Cria backup
            if await self.restore.backup():
                # Verifica backup
                if await self.restore.verify_backup():
                    await update.message.reply_text(
                        "✅ Backup criado e verificado com sucesso!\n"
                        "🔒 Sistema protegido e seguro."
                    )
                else:
                    await update.message.reply_text(
                        "⚠️ Backup criado mas verificação falhou.\n"
                        "🔄 Tentando novamente..."
                    )
            else:
                await update.message.reply_text(
                    "❌ Erro ao criar backup.\n"
                    "Por favor, verifique os logs."
                )
        except Exception as e:
            logger.error(f"Erro no backup: {e}")
            await update.message.reply_text(
                "❌ Erro durante o backup.\n"
                "Verifique os logs para mais detalhes."
            )
            
    async def notify_admin_on_startup(self):
        """Envia uma mensagem ao administrador quando o bot inicia"""
        if self.admin_id:
            try:
                await self.app.bot.send_message(
                    chat_id=self.admin_id,
                    text=f"{self.bot_name} está online e pronto para uso!"
                )
                logger.info("Mensagem de inicialização enviada ao administrador.")
            except Exception as e:
                logger.error(f"Erro ao enviar mensagem de inicialização: {e}")

    async def run(self):
        """Executa o bot"""
        try:
            # Carrega estado
            await self.load_state()
            
            # Inicia bot
            await self.app.initialize()
            await self.app.start()

            # Notifica o administrador
            await self.notify_admin_on_startup()

            await self.app.run_polling()
            
        except Exception as e:
            logger.error(f"Erro fatal: {e}")
            raise
        finally:
            # Salva estado e encerra
            await self.save_state()
            await self.app.stop()
            await self.app.shutdown()

# Ponto de entrada protegido
if __name__ == "__main__":
    bot = EVACore()
    asyncio.run(bot.run())