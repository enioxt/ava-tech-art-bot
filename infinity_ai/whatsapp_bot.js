require('dotenv').config();
const express = require('express');
const { Client } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const axios = require('axios');
const winston = require('winston');

// Configuração do logger
const logger = winston.createLogger({
    level: 'info',
    format: winston.format.combine(
        winston.format.timestamp(),
        winston.format.json()
    ),
    transports: [
        new winston.transports.File({ filename: 'logs/whatsapp-error.log', level: 'error' }),
        new winston.transports.File({ filename: 'logs/whatsapp-combined.log' })
    ]
});

if (process.env.NODE_ENV !== 'production') {
    logger.add(new winston.transports.Console({
        format: winston.format.simple()
    }));
}

const app = express();
app.use(express.json());

// Configuração do cliente WhatsApp
const client = new Client({
    puppeteer: {
        args: ['--no-sandbox'],
        headless: true
    }
});

// Sistema de métricas
let metrics = {
    messagesReceived: 0,
    messagesSent: 0,
    errors: 0,
    activeUsers: new Set(),
    lastUpdated: new Date(),
    responseTimeAvg: 0
};

// Gera QR Code para autenticação
client.on('qr', (qr) => {
    qrcode.generate(qr, { small: true });
    logger.info('QR Code gerado! Escaneie para autenticar.');
});

client.on('ready', () => {
    logger.info('Cliente WhatsApp conectado e pronto!');
});

// Validação de mensagem
function validateMessage(msg) {
    if (!msg || !msg.body || typeof msg.body !== 'string') {
        throw new Error('Mensagem inválida');
    }
    if (msg.body.length > 4096) {
        throw new Error('Mensagem muito longa');
    }
    return msg.body.trim();
}

// Processa mensagens recebidas
client.on('message', async msg => {
    const startTime = Date.now();
    try {
        // Ignora mensagens de grupos
        if (msg.isGroupMsg) return;

        // Valida e processa a mensagem
        const validatedMessage = validateMessage(msg);
        
        // Atualiza métricas
        metrics.messagesReceived++;
        metrics.activeUsers.add(msg.from);

        // Processa a mensagem com o agente central
        const response = await axios.post('http://localhost:8000/chat', {
            messages: [{
                role: "user",
                content: validatedMessage
            }],
            channel: "whatsapp",
            user_id: msg.from
        });

        // Envia resposta do agente
        await msg.reply(response.data.response);
        
        // Atualiza métricas de envio
        metrics.messagesSent++;
        const responseTime = Date.now() - startTime;
        metrics.responseTimeAvg = (metrics.responseTimeAvg * (metrics.messagesSent - 1) + responseTime) / metrics.messagesSent;
        metrics.lastUpdated = new Date();

    } catch (error) {
        logger.error('Erro ao processar mensagem:', {
            error: error.message,
            user: msg.from,
            timestamp: new Date()
        });
        
        metrics.errors++;
        
        let errorMessage = 'Desculpe, tive um problema ao processar sua mensagem. Por favor, tente novamente em alguns instantes.';
        if (error.response && error.response.status === 429) {
            errorMessage = 'Estamos recebendo muitas mensagens no momento. Por favor, aguarde um momento antes de tentar novamente.';
        }
        
        await msg.reply(errorMessage);
    }
});

// Inicializa o cliente
client.initialize().catch(err => {
    logger.error('Erro ao inicializar cliente:', err);
    process.exit(1);
});

// Rota de healthcheck
app.get('/health', (req, res) => {
    const status = client.pupPage ? 'connected' : 'disconnected';
    res.json({ 
        status,
        metrics: {
            ...metrics,
            activeUsers: metrics.activeUsers.size
        }
    });
});

// Rota para métricas
app.get('/metrics', (req, res) => {
    res.json({
        ...metrics,
        activeUsers: metrics.activeUsers.size
    });
});

// Rota para enviar mensagens programaticamente
app.post('/send', async (req, res) => {
    try {
        const { to, message } = req.body;
        
        if (!to || !message) {
            throw new Error('Parâmetros inválidos');
        }
        
        await client.sendMessage(to, message);
        metrics.messagesSent++;
        
        res.json({ success: true });
    } catch (error) {
        logger.error('Erro ao enviar mensagem:', error);
        metrics.errors++;
        res.status(500).json({ error: error.message });
    }
});

// Tratamento de erros não capturados
process.on('uncaughtException', (err) => {
    logger.error('Erro não capturado:', err);
    // Não finaliza o processo, mas registra o erro
});

process.on('unhandledRejection', (reason, promise) => {
    logger.error('Promessa rejeitada não tratada:', reason);
    // Não finaliza o processo, mas registra o erro
});

const PORT = process.env.WHATSAPP_PORT || 3000;
app.listen(PORT, () => {
    logger.info(`Servidor WhatsApp rodando na porta ${PORT}`);
}); 