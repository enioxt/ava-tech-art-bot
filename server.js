import TelegramBot from 'node-telegram-bot-api';
import sharp from 'sharp';
import fs from 'fs';
import path from 'path';
import Redis from 'ioredis';

// Configurações
const token = '7642662485:AAHqu2VIY2sCLKMNvqO5o8thbjhyr1aimiw';
const RATE_LIMIT = 1000; // 1 segundo entre mensagens
const SYNC_INTERVAL = 2000; // 2 segundos entre sincronizações
const INSTANCE_TIMEOUT = 5000; // 5 segundos para timeout de instância

// Redis para sincronização
const redis = new Redis({
  host: process.env.REDIS_HOST || 'localhost',
  port: process.env.REDIS_PORT || 6379,
  password: process.env.REDIS_PASSWORD,
  retryStrategy: (times) => {
    const delay = Math.min(times * 50, 2000);
    return delay;
  }
});

// Criar diretórios necessários
const dirs = ['temp', 'logs', 'backups'];
dirs.forEach(dir => {
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir);
    console.log(`✓ Diretório ${dir} criado`);
  }
});

// Gerenciador de instâncias
class InstanceManager {
  constructor() {
    this.instanceId = Math.random().toString(36).substring(7);
    this.lastHeartbeat = Date.now();
    this.isActive = false;
  }

  async register() {
    try {
      await redis.set(`instance:${this.instanceId}`, JSON.stringify({
        startTime: Date.now(),
        lastHeartbeat: this.lastHeartbeat
      }), 'EX', 30);
      this.isActive = true;
      this.startHeartbeat();
    } catch (error) {
      console.error('Erro ao registrar instância:', error);
    }
  }

  async startHeartbeat() {
    setInterval(async () => {
      try {
        this.lastHeartbeat = Date.now();
        await redis.set(`instance:${this.instanceId}`, JSON.stringify({
          startTime: Date.now(),
          lastHeartbeat: this.lastHeartbeat
        }), 'EX', 30);
      } catch (error) {
        console.error('Erro no heartbeat:', error);
      }
    }, 10000);
  }

  async checkActiveInstances() {
    try {
      const instances = await redis.keys('instance:*');
      return instances.length;
    } catch (error) {
      console.error('Erro ao verificar instâncias:', error);
      return 0;
    }
  }
}

// Gerenciador de mensagens
class MessageManager {
  constructor() {
    this.processingMessages = new Map();
  }

  async lockMessage(chatId, messageId) {
    const lockKey = `lock:${chatId}:${messageId}`;
    const acquired = await redis.set(lockKey, '1', 'NX', 'EX', 30);
    return acquired === 'OK';
  }

  async unlockMessage(chatId, messageId) {
    const lockKey = `lock:${chatId}:${messageId}`;
    await redis.del(lockKey);
  }

  isProcessing(chatId, messageId) {
    return this.processingMessages.has(`${chatId}:${messageId}`);
  }

  startProcessing(chatId, messageId) {
    this.processingMessages.set(`${chatId}:${messageId}`, Date.now());
  }

  endProcessing(chatId, messageId) {
    this.processingMessages.delete(`${chatId}:${messageId}`);
  }
}

// Inicializar gerenciadores
const instanceManager = new InstanceManager();
const messageManager = new MessageManager();

// Inicializar bot com retry em caso de erro
const initBot = async () => {
  await instanceManager.register();
  
  const bot = new TelegramBot(token, { 
    polling: true,
    request: {
      timeout: 30000,
      forever: true,
      keepAlive: true
    }
  });

  // Handler de erros de polling
  bot.on('polling_error', async (error) => {
    console.error('Erro de polling:', error);
    await new Promise(resolve => setTimeout(resolve, 5000));
    initBot();
  });

  // Handler de mensagens
  bot.on('message', async (msg) => {
    try {
      const chatId = msg.chat.id;
      const messageId = msg.message_id;

      // Verificar se mensagem já está sendo processada
      if (messageManager.isProcessing(chatId, messageId)) {
        return;
      }

      // Tentar obter lock para processar mensagem
      const hasLock = await messageManager.lockMessage(chatId, messageId);
      if (!hasLock) {
        return;
      }

      messageManager.startProcessing(chatId, messageId);

      console.log(`Nova mensagem de ${msg.from.username || msg.from.id}: ${msg.text || '[mídia]'}`);

      // Comando /start
      if (msg.text === '/start') {
        await bot.sendMessage(chatId, `Olá! 👋 
Eu sou a Ava, uma assistente que ajuda a redimensionar imagens.

*Como me usar:*
1. Envie uma imagem
2. Digite as dimensões desejadas (exemplo: 800x600)
3. Receba sua imagem redimensionada!

*Comandos disponíveis:*
/start - Exibe esta mensagem
/help - Exibe ajuda detalhada
/status - Verifica status do sistema`, { parse_mode: 'Markdown' });
        return;
      }

      // Comando /help
      if (msg.text === '/help') {
        await bot.sendMessage(chatId, `*Ajuda Detalhada* 🔍

*Redimensionamento de Imagens:*
• Envie qualquer imagem
• Responda com as dimensões no formato LARGURAxALTURA
• Exemplo: 800x600, 1024x768, etc
• A qualidade é mantida em 85%
• Formatos suportados: JPG, PNG

*Dicas:*
• Mantenha as proporções para melhor resultado
• Tamanho máximo: 5000x5000
• Aguarde alguns segundos entre os comandos

*Precisa de ajuda?*
Entre em contato com @admin`, { parse_mode: 'Markdown' });
        return;
      }

      // Comando /status
      if (msg.text === '/status') {
        const activeInstances = await instanceManager.checkActiveInstances();
        const status = {
          uptime: process.uptime(),
          memory: process.memoryUsage(),
          instances: activeInstances,
          dirs: dirs.map(dir => ({
            name: dir,
            exists: fs.existsSync(dir)
          }))
        };
        
        await bot.sendMessage(chatId, `*Status do Sistema* 📊

*Uptime:* ${Math.floor(status.uptime / 3600)}h ${Math.floor((status.uptime % 3600) / 60)}m
*Memória:* ${Math.round(status.memory.heapUsed / 1024 / 1024)}MB / ${Math.round(status.memory.heapTotal / 1024 / 1024)}MB
*Instâncias Ativas:* ${status.instances}
*Diretórios:* ${status.dirs.map(d => `\n• ${d.name}: ${d.exists ? '✅' : '❌'}`).join('')}`, { parse_mode: 'Markdown' });
        return;
      }

      // Processar imagem
      if (msg.photo) {
        await bot.sendMessage(chatId, 'Digite as dimensões desejadas (exemplo: 800x600):');
        return;
      }

      // Processar dimensões
      if (msg.text && msg.reply_to_message?.photo) {
        const dimensions = msg.text.split('x').map(Number);
        if (dimensions.length !== 2 || isNaN(dimensions[0]) || isNaN(dimensions[1])) {
          await bot.sendMessage(chatId, '❌ Formato inválido! Use: larguraxaltura (exemplo: 800x600)');
          return;
        }

        const [width, height] = dimensions;
        
        // Validar dimensões
        if (width > 5000 || height > 5000) {
          await bot.sendMessage(chatId, '❌ Dimensões muito grandes! Máximo: 5000x5000');
          return;
        }

        await bot.sendMessage(chatId, '🔄 Processando imagem...');

        const photo = msg.reply_to_message.photo.pop();
        const file = await bot.getFile(photo.file_id);
        const input = path.join('temp', `${photo.file_id}.jpg`);
        const output = path.join('temp', `${photo.file_id}_resized.jpg`);

        try {
          // Baixar e processar imagem
          await bot.downloadFile(file.file_id, 'temp');
          await sharp(input)
            .resize(width, height)
            .jpeg({ quality: 85 })
            .toFile(output);

          // Enviar imagem processada
          await bot.sendPhoto(chatId, output, {
            caption: `✅ Imagem redimensionada para ${width}x${height}`
          });

          // Limpar arquivos temporários
          fs.unlinkSync(input);
          fs.unlinkSync(output);
        } catch (error) {
          console.error('Erro ao processar imagem:', error);
          await bot.sendMessage(chatId, '❌ Erro ao processar imagem. Tente novamente.');
        }
      }

    } catch (error) {
      console.error('Erro:', error);
      try {
        await bot.sendMessage(msg.chat.id, '❌ Ocorreu um erro ao processar sua solicitação. Tente novamente em alguns instantes.');
      } catch (sendError) {
        console.error('Erro ao enviar mensagem de erro:', sendError);
      }
    } finally {
      if (msg) {
        messageManager.endProcessing(msg.chat.id, msg.message_id);
        await messageManager.unlockMessage(msg.chat.id, msg.message_id);
      }
    }
  });

  console.log('✨ Bot Ava iniciado com sucesso!');
  console.log(`ID da Instância: ${instanceManager.instanceId}`);
  return bot;
};

// Iniciar bot
initBot();
