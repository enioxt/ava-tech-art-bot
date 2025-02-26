const TelegramBot = require('node-telegram-bot-api');
const dotenv = require('dotenv');
const path = require('path');
const sharp = require('sharp');
const fs = require('fs').promises;
const { v4: uuidv4 } = require('uuid');
const winston = require('winston');
const Redis = require('ioredis');
const rateLimit = require('express-rate-limit');

// Carrega variáveis de ambiente
dotenv.config();

// Configuração do logger
const logger = winston.createLogger({
    level: process.env.LOG_LEVEL || 'info',
    format: winston.format.combine(
        winston.format.timestamp(),
        winston.format.json()
    ),
    transports: [
        new winston.transports.File({ filename: 'logs/error.log', level: 'error' }),
        new winston.transports.File({ filename: 'logs/combined.log' })
    ]
});

if (process.env.NODE_ENV !== 'production') {
    logger.add(new winston.transports.Console({
        format: winston.format.simple()
    }));
}

// Configuração do Redis
const redis = new Redis({
    host: process.env.REDIS_HOST || 'localhost',
    port: process.env.REDIS_PORT || 6379,
    password: process.env.REDIS_PASSWORD,
    db: process.env.REDIS_DB || 0
});

// Configuração do rate limit
const rateLimiter = {
    window: process.env.RATE_LIMIT_WINDOW || '15m',
    max: process.env.RATE_LIMIT_MAX_REQUESTS || 100
};

// Configuração do bot
const bot = new TelegramBot(process.env.BOT_TOKEN, {
    polling: !process.env.WEBHOOK_ENABLED
});

// Configuração de webhook se habilitado
if (process.env.WEBHOOK_ENABLED === 'true') {
    bot.setWebHook(`${process.env.BOT_WEBHOOK_URL}/${process.env.BOT_TOKEN}`);
}

// Handler para o comando /start
bot.onText(/\/start/, async (msg) => {
    const chatId = msg.chat.id;
    try {
        await bot.sendMessage(chatId, 
            '👋 Olá! Eu sou o AVA Bot!\n\n' +
            'Posso ajudar você a processar suas imagens de forma inteligente.\n\n' +
            'Comandos disponíveis:\n' +
            '/help - Mostra esta ajuda\n' +
            '/resize - Redimensiona uma imagem\n' +
            '/optimize - Otimiza uma imagem\n' +
            '/convert - Converte o formato de uma imagem\n' +
            '/settings - Configura suas preferências\n\n' +
            'Envie uma imagem para começar! 🎨'
        );
        logger.info(`Usuário ${msg.from.id} iniciou o bot`);
    } catch (error) {
        logger.error('Erro ao enviar mensagem de boas-vindas:', error);
        await bot.sendMessage(chatId, '❌ Ops! Ocorreu um erro. Por favor, tente novamente mais tarde.');
    }
});

// Handler para o comando /help
bot.onText(/\/help/, async (msg) => {
    const chatId = msg.chat.id;
    try {
        await bot.sendMessage(chatId,
            '🔍 *Guia de Uso do AVA Bot*\n\n' +
            '*Comandos Básicos:*\n' +
            '`/start` - Inicia o bot\n' +
            '`/help` - Mostra esta ajuda\n' +
            '`/settings` - Configura preferências\n\n' +
            '*Processamento de Imagens:*\n' +
            '`/resize` - Redimensiona imagem\n' +
            '`/optimize` - Otimiza imagem\n' +
            '`/convert` - Converte formato\n\n' +
            '*Como usar:*\n' +
            '1. Envie uma imagem\n' +
            '2. Escolha um comando\n' +
            '3. Siga as instruções\n\n' +
            '*Formatos suportados:*\n' +
            '• JPG/JPEG\n' +
            '• PNG\n' +
            '• WebP\n' +
            '• GIF\n\n' +
            '*Limites:*\n' +
            '• Tamanho máximo: 10MB\n' +
            '• Resolução máxima: 4096x4096\n\n' +
            '*Precisa de ajuda?*\n' +
            'Entre em contato: @ava_support',
            { parse_mode: 'Markdown' }
        );
        logger.info(`Usuário ${msg.from.id} solicitou ajuda`);
    } catch (error) {
        logger.error('Erro ao enviar mensagem de ajuda:', error);
        await bot.sendMessage(chatId, '❌ Ops! Ocorreu um erro. Por favor, tente novamente mais tarde.');
    }
});

// Handler para o comando /settings
bot.onText(/\/settings/, async (msg) => {
    const chatId = msg.chat.id;
    try {
        const settings = await redis.hgetall(`settings:${msg.from.id}`);
        await bot.sendMessage(chatId,
            '⚙️ *Configurações*\n\n' +
            '*Suas preferências atuais:*\n' +
            `• Formato padrão: ${settings.format || 'jpg'}\n` +
            `• Qualidade: ${settings.quality || '80'}%\n` +
            `• Notificações: ${settings.notifications === 'true' ? 'Ativadas' : 'Desativadas'}\n\n` +
            'Para alterar, use os comandos:\n' +
            '`/format jpg|png|webp` - Define formato\n' +
            '`/quality 1-100` - Define qualidade\n' +
            '`/notify on|off` - Configura notificações',
            { parse_mode: 'Markdown' }
        );
        logger.info(`Usuário ${msg.from.id} acessou configurações`);
    } catch (error) {
        logger.error('Erro ao enviar configurações:', error);
        await bot.sendMessage(chatId, '❌ Ops! Ocorreu um erro. Por favor, tente novamente mais tarde.');
    }
});

// Handler para imagens
bot.on('photo', async (msg) => {
    const chatId = msg.chat.id;
    try {
        // Verifica rate limit
        const userRequests = await redis.incr(`ratelimit:${msg.from.id}`);
        await redis.expire(`ratelimit:${msg.from.id}`, 900); // 15 minutos
        
        if (userRequests > rateLimiter.max) {
            await bot.sendMessage(chatId, '⚠️ Você atingiu o limite de requisições. Por favor, aguarde alguns minutos.');
            return;
        }

        // Obtém a maior versão da foto
        const photo = msg.photo[msg.photo.length - 1];
        const file = await bot.getFile(photo.file_id);
        
        // Cria diretório temporário se não existir
        const tempDir = path.join(__dirname, '../../temp');
        await fs.mkdir(tempDir, { recursive: true });
        
        // Gera nome único para o arquivo
        const fileName = `${uuidv4()}.jpg`;
        const filePath = path.join(tempDir, fileName);
        
        // Baixa a imagem
        const fileUrl = `https://api.telegram.org/file/bot${process.env.BOT_TOKEN}/${file.file_path}`;
        const response = await fetch(fileUrl);
        const buffer = await response.buffer();
        await fs.writeFile(filePath, buffer);
        
        // Envia menu de opções
        await bot.sendMessage(chatId,
            '🎨 *O que você gostaria de fazer com esta imagem?*\n\n' +
            '1. `/resize` - Redimensionar\n' +
            '2. `/optimize` - Otimizar\n' +
            '3. `/convert` - Converter formato\n\n' +
            'Escolha uma opção ou envie outro comando:',
            { parse_mode: 'Markdown' }
        );
        
        // Armazena caminho da imagem no Redis
        await redis.set(`image:${chatId}`, filePath, 'EX', 3600); // Expira em 1 hora
        
        logger.info(`Usuário ${msg.from.id} enviou uma imagem`);
    } catch (error) {
        logger.error('Erro ao processar imagem:', error);
        await bot.sendMessage(chatId, '❌ Ops! Ocorreu um erro ao processar sua imagem. Por favor, tente novamente.');
    }
});

// Handler para redimensionamento
bot.onText(/\/resize/, async (msg) => {
    const chatId = msg.chat.id;
    try {
        const imagePath = await redis.get(`image:${chatId}`);
        if (!imagePath) {
            await bot.sendMessage(chatId, '⚠️ Nenhuma imagem para processar. Por favor, envie uma imagem primeiro.');
            return;
        }
        
        await bot.sendMessage(chatId,
            '📏 *Redimensionamento*\n\n' +
            'Escolha uma opção:\n\n' +
            '1. `small` - 800x600\n' +
            '2. `medium` - 1024x768\n' +
            '3. `large` - 1920x1080\n' +
            '4. `custom` - Tamanho personalizado\n\n' +
            'Responda com o número da opção ou "custom WxH":',
            { parse_mode: 'Markdown' }
        );
        
        // Armazena estado do usuário
        await redis.set(`state:${chatId}`, 'resize', 'EX', 3600);
        
        logger.info(`Usuário ${msg.from.id} iniciou redimensionamento`);
    } catch (error) {
        logger.error('Erro ao iniciar redimensionamento:', error);
        await bot.sendMessage(chatId, '❌ Ops! Ocorreu um erro. Por favor, tente novamente mais tarde.');
    }
});

// Handler para otimização
bot.onText(/\/optimize/, async (msg) => {
    const chatId = msg.chat.id;
    try {
        const imagePath = await redis.get(`image:${chatId}`);
        if (!imagePath) {
            await bot.sendMessage(chatId, '⚠️ Nenhuma imagem para processar. Por favor, envie uma imagem primeiro.');
            return;
        }
        
        await bot.sendMessage(chatId,
            '🔧 *Otimização*\n\n' +
            'Escolha um nível de qualidade:\n\n' +
            '1. `low` - Máxima compressão\n' +
            '2. `medium` - Balanceado\n' +
            '3. `high` - Alta qualidade\n' +
            '4. `custom` - Personalizado\n\n' +
            'Responda com o número da opção ou "custom 1-100":',
            { parse_mode: 'Markdown' }
        );
        
        // Armazena estado do usuário
        await redis.set(`state:${chatId}`, 'optimize', 'EX', 3600);
        
        logger.info(`Usuário ${msg.from.id} iniciou otimização`);
    } catch (error) {
        logger.error('Erro ao iniciar otimização:', error);
        await bot.sendMessage(chatId, '❌ Ops! Ocorreu um erro. Por favor, tente novamente mais tarde.');
    }
});

// Handler para conversão
bot.onText(/\/convert/, async (msg) => {
    const chatId = msg.chat.id;
    try {
        const imagePath = await redis.get(`image:${chatId}`);
        if (!imagePath) {
            await bot.sendMessage(chatId, '⚠️ Nenhuma imagem para processar. Por favor, envie uma imagem primeiro.');
            return;
        }
        
        await bot.sendMessage(chatId,
            '🔄 *Conversão*\n\n' +
            'Escolha o formato de saída:\n\n' +
            '1. `JPG` - Melhor para fotos\n' +
            '2. `PNG` - Melhor para gráficos\n' +
            '3. `WebP` - Otimizado para web\n' +
            '4. `AVIF` - Formato moderno\n\n' +
            'Responda com o número da opção:',
            { parse_mode: 'Markdown' }
        );
        
        // Armazena estado do usuário
        await redis.set(`state:${chatId}`, 'convert', 'EX', 3600);
        
        logger.info(`Usuário ${msg.from.id} iniciou conversão`);
    } catch (error) {
        logger.error('Erro ao iniciar conversão:', error);
        await bot.sendMessage(chatId, '❌ Ops! Ocorreu um erro. Por favor, tente novamente mais tarde.');
    }
});

// Handler para respostas de texto
bot.on('text', async (msg) => {
    const chatId = msg.chat.id;
    try {
        // Ignora comandos
        if (msg.text.startsWith('/')) return;
        
        const state = await redis.get(`state:${chatId}`);
        const imagePath = await redis.get(`image:${chatId}`);
        
        if (!state || !imagePath) return;
        
        switch (state) {
            case 'resize':
                await handleResize(msg, chatId, imagePath);
                break;
            case 'optimize':
                await handleOptimize(msg, chatId, imagePath);
                break;
            case 'convert':
                await handleConvert(msg, chatId, imagePath);
                break;
        }
        
        // Limpa estado
        await redis.del(`state:${chatId}`);
    } catch (error) {
        logger.error('Erro ao processar resposta:', error);
        await bot.sendMessage(chatId, '❌ Ops! Ocorreu um erro ao processar sua resposta. Por favor, tente novamente.');
    }
});

// Função para processar redimensionamento
async function handleResize(msg, chatId, imagePath) {
    let width, height;
    
    switch (msg.text.toLowerCase()) {
        case '1':
        case 'small':
            width = 800;
            height = 600;
            break;
        case '2':
        case 'medium':
            width = 1024;
            height = 768;
            break;
        case '3':
        case 'large':
            width = 1920;
            height = 1080;
            break;
        default:
            if (msg.text.toLowerCase().startsWith('custom')) {
                const dimensions = msg.text.split(' ')[1];
                const [w, h] = dimensions.split('x').map(Number);
                if (w && h && w > 0 && h > 0) {
                    width = w;
                    height = h;
                }
            }
    }
    
    if (!width || !height) {
        await bot.sendMessage(chatId, '⚠️ Dimensões inválidas. Por favor, tente novamente.');
        return;
    }
    
    const status = await bot.sendMessage(chatId, '🔄 Processando...');
    
    try {
        const outputPath = path.join(path.dirname(imagePath), `resized_${path.basename(imagePath)}`);
        
        await sharp(imagePath)
            .resize(width, height, {
                fit: 'inside',
                withoutEnlargement: true
            })
            .toFile(outputPath);
        
        await bot.editMessageText('✅ Imagem redimensionada com sucesso!', {
            chat_id: chatId,
            message_id: status.message_id
        });
        
        await bot.sendDocument(chatId, outputPath, {
            caption: `📏 Nova resolução: ${width}x${height}`
        });
        
        // Limpa arquivos
        await fs.unlink(imagePath);
        await fs.unlink(outputPath);
        
        logger.info(`Usuário ${msg.from.id} redimensionou imagem para ${width}x${height}`);
    } catch (error) {
        logger.error('Erro ao redimensionar:', error);
        await bot.editMessageText('❌ Erro ao redimensionar imagem. Por favor, tente novamente.', {
            chat_id: chatId,
            message_id: status.message_id
        });
    }
}

// Função para processar otimização
async function handleOptimize(msg, chatId, imagePath) {
    let quality;
    
    switch (msg.text.toLowerCase()) {
        case '1':
        case 'low':
            quality = 60;
            break;
        case '2':
        case 'medium':
            quality = 80;
            break;
        case '3':
        case 'high':
            quality = 90;
            break;
        default:
            if (msg.text.toLowerCase().startsWith('custom')) {
                const q = parseInt(msg.text.split(' ')[1]);
                if (q >= 1 && q <= 100) quality = q;
            }
    }
    
    if (!quality) {
        await bot.sendMessage(chatId, '⚠️ Qualidade inválida. Por favor, tente novamente.');
        return;
    }
    
    const status = await bot.sendMessage(chatId, '🔄 Processando...');
    
    try {
        const outputPath = path.join(path.dirname(imagePath), `optimized_${path.basename(imagePath)}`);
        
        await sharp(imagePath)
            .jpeg({ quality })
            .toFile(outputPath);
        
        const originalSize = (await fs.stat(imagePath)).size;
        const optimizedSize = (await fs.stat(outputPath)).size;
        const reduction = ((originalSize - optimizedSize) / originalSize * 100).toFixed(1);
        
        await bot.editMessageText('✅ Imagem otimizada com sucesso!', {
            chat_id: chatId,
            message_id: status.message_id
        });
        
        await bot.sendDocument(chatId, outputPath, {
            caption: `🔧 Otimização concluída!\n` +
                    `• Qualidade: ${quality}%\n` +
                    `• Redução: ${reduction}%\n` +
                    `• Tamanho original: ${(originalSize / 1024).toFixed(1)}KB\n` +
                    `• Tamanho final: ${(optimizedSize / 1024).toFixed(1)}KB`
        });
        
        // Limpa arquivos
        await fs.unlink(imagePath);
        await fs.unlink(outputPath);
        
        logger.info(`Usuário ${msg.from.id} otimizou imagem com qualidade ${quality}%`);
    } catch (error) {
        logger.error('Erro ao otimizar:', error);
        await bot.editMessageText('❌ Erro ao otimizar imagem. Por favor, tente novamente.', {
            chat_id: chatId,
            message_id: status.message_id
        });
    }
}

// Função para processar conversão
async function handleConvert(msg, chatId, imagePath) {
    let format;
    
    switch (msg.text.toLowerCase()) {
        case '1':
        case 'jpg':
            format = 'jpeg';
            break;
        case '2':
        case 'png':
            format = 'png';
            break;
        case '3':
        case 'webp':
            format = 'webp';
            break;
        case '4':
        case 'avif':
            format = 'avif';
            break;
        default:
            await bot.sendMessage(chatId, '⚠️ Formato inválido. Por favor, tente novamente.');
            return;
    }
    
    const status = await bot.sendMessage(chatId, '🔄 Processando...');
    
    try {
        const outputPath = path.join(path.dirname(imagePath), `converted_${path.basename(imagePath, path.extname(imagePath))}.${format}`);
        
        await sharp(imagePath)[format]().toFile(outputPath);
        
        await bot.editMessageText('✅ Imagem convertida com sucesso!', {
            chat_id: chatId,
            message_id: status.message_id
        });
        
        await bot.sendDocument(chatId, outputPath, {
            caption: `🔄 Conversão concluída!\nNovo formato: ${format.toUpperCase()}`
        });
        
        // Limpa arquivos
        await fs.unlink(imagePath);
        await fs.unlink(outputPath);
        
        logger.info(`Usuário ${msg.from.id} converteu imagem para ${format}`);
    } catch (error) {
        logger.error('Erro ao converter:', error);
        await bot.editMessageText('❌ Erro ao converter imagem. Por favor, tente novamente.', {
            chat_id: chatId,
            message_id: status.message_id
        });
    }
}

// Handler para erros
bot.on('polling_error', (error) => {
    logger.error('Erro no polling:', error);
});

// Inicialização
logger.info('Bot iniciado com sucesso!');
console.log('🤖 AVA Bot está rodando...'); 