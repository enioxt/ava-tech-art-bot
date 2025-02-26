require('dotenv').config();
const express = require('express');
const axios = require('axios');
const { IgApiClient } = require('instagram-private-api');
const { withFbnsAndRealtime } = require('instagram_mqtt');
const winston = require('winston');

// Configuração do logger
const logger = winston.createLogger({
    level: 'info',
    format: winston.format.combine(
        winston.format.timestamp(),
        winston.format.json()
    ),
    transports: [
        new winston.transports.File({ filename: 'logs/instagram-error.log', level: 'error' }),
        new winston.transports.File({ filename: 'logs/instagram-combined.log' })
    ]
});

if (process.env.NODE_ENV !== 'production') {
    logger.add(new winston.transports.Console({
        format: winston.format.simple()
    }));
}

const app = express();
app.use(express.json());

// Sistema de métricas
class Metrics {
    constructor() {
        this.messagesReceived = 0;
        this.messagesSent = 0;
        this.errors = 0;
        this.activeUsers = new Set();
        this.photosPosted = 0;
        this.storiesPosted = 0;
        this.responseTimes = [];
        this.lastUpdated = new Date();
    }

    updateResponseTime(timeMs) {
        this.responseTimes.push(timeMs);
        if (this.responseTimes.length > 1000) {
            this.responseTimes = this.responseTimes.slice(-1000);
        }
    }

    get averageResponseTime() {
        if (this.responseTimes.length === 0) return 0;
        return this.responseTimes.reduce((a, b) => a + b, 0) / this.responseTimes.length;
    }

    toJSON() {
        return {
            messagesReceived: this.messagesReceived,
            messagesSent: this.messagesSent,
            errors: this.errors,
            activeUsers: this.activeUsers.size,
            photosPosted: this.photosPosted,
            storiesPosted: this.storiesPosted,
            averageResponseTime: this.averageResponseTime,
            lastUpdated: this.lastUpdated
        };
    }
}

class InfinityInstagramBot {
    constructor() {
        this.ig = withFbnsAndRealtime(new IgApiClient());
        this.ig.state.generateDevice(process.env.INSTAGRAM_USERNAME || process.env.IG_USERNAME);
        this.metrics = new Metrics();
        this.setupEventHandlers();
    }

    async login() {
        try {
            const username = process.env.INSTAGRAM_USERNAME || process.env.IG_USERNAME;
            const password = process.env.INSTAGRAM_PASSWORD || process.env.IG_PASSWORD;

            if (!username || !password) {
                throw new Error('Credenciais do Instagram não configuradas');
            }

            await this.ig.simulate.preLoginFlow();
            await this.ig.account.login(username, password);
            await this.ig.simulate.postLoginFlow();
            logger.info('Login no Instagram realizado com sucesso!');
        } catch (error) {
            logger.error('Erro ao fazer login no Instagram:', error);
            throw error;
        }
    }

    validateMessage(text) {
        if (!text || typeof text !== 'string') {
            throw new Error('Mensagem inválida');
        }
        if (text.length > 1000) { // Limite do Instagram
            throw new Error('Mensagem muito longa');
        }
        return text.trim();
    }

    setupEventHandlers() {
        this.ig.fbns.on('direct_v2_message', async (message) => {
            const startTime = Date.now();
            try {
                if (message.message && message.message.text) {
                    this.metrics.messagesReceived++;
                    this.metrics.activeUsers.add(message.user_id);

                    const validatedMessage = this.validateMessage(message.message.text);
                    const response = await this.processMessage(
                        validatedMessage,
                        message.user_id
                    );
                    await this.sendDirectMessage(message.user_id, response);
                    
                    this.metrics.messagesSent++;
                }
            } catch (error) {
                logger.error('Erro ao processar mensagem:', error);
                this.metrics.errors++;
                let errorMessage = 'Desculpe, tive um problema ao processar sua mensagem. Por favor, tente novamente em alguns instantes.';
                if (error.message === 'Mensagem muito longa') {
                    errorMessage = 'Por favor, envie uma mensagem mais curta.';
                }
                await this.sendDirectMessage(message.user_id, errorMessage);
            } finally {
                const responseTime = Date.now() - startTime;
                this.metrics.updateResponseTime(responseTime);
                this.metrics.lastUpdated = new Date();
            }
        });

        this.ig.fbns.on('error', (error) => {
            logger.error('Erro no FBNS:', error);
            this.metrics.errors++;
        });
    }

    async processMessage(text, userId) {
        try {
            const response = await axios.post('http://localhost:8000/chat', {
                messages: [{
                    role: "user",
                    content: text
                }],
                channel: "instagram",
                user_id: userId
            });

            return response.data.response;
        } catch (error) {
            logger.error('Erro ao processar mensagem com IA:', error);
            throw error;
        }
    }

    async sendDirectMessage(userId, text) {
        try {
            const thread = await this.ig.direct.createGroupThread([userId.toString()]);
            await this.ig.direct.sendText(thread.thread_id, text);
        } catch (error) {
            logger.error('Erro ao enviar mensagem:', error);
            this.metrics.errors++;
            throw error;
        }
    }

    async postPhoto(imagePath, caption) {
        try {
            await this.ig.publish.photo({
                file: imagePath,
                caption: caption
            });
            this.metrics.photosPosted++;
            logger.info('Foto publicada com sucesso!');
        } catch (error) {
            logger.error('Erro ao publicar foto:', error);
            this.metrics.errors++;
            throw error;
        }
    }

    async postStory(imagePath, text) {
        try {
            await this.ig.publish.story({
                file: imagePath,
                caption: text
            });
            this.metrics.storiesPosted++;
            logger.info('Story publicado com sucesso!');
        } catch (error) {
            logger.error('Erro ao publicar story:', error);
            this.metrics.errors++;
            throw error;
        }
    }
}

// Instancia o bot
const bot = new InfinityInstagramBot();

// Rota de healthcheck
app.get('/health', (req, res) => {
    const status = bot.ig.state.deviceString ? 'connected' : 'disconnected';
    res.json({ 
        status,
        metrics: bot.metrics.toJSON()
    });
});

// Rota para métricas
app.get('/metrics', (req, res) => {
    res.json(bot.metrics.toJSON());
});

// Rota para publicar foto
app.post('/post/photo', async (req, res) => {
    try {
        const { imagePath, caption } = req.body;
        if (!imagePath) {
            throw new Error('Caminho da imagem é obrigatório');
        }
        await bot.postPhoto(imagePath, caption);
        res.json({ success: true });
    } catch (error) {
        logger.error('Erro na rota /post/photo:', error);
        res.status(500).json({ error: error.message });
    }
});

// Rota para publicar story
app.post('/post/story', async (req, res) => {
    try {
        const { imagePath, text } = req.body;
        if (!imagePath) {
            throw new Error('Caminho da imagem é obrigatório');
        }
        await bot.postStory(imagePath, text);
        res.json({ success: true });
    } catch (error) {
        logger.error('Erro na rota /post/story:', error);
        res.status(500).json({ error: error.message });
    }
});

// Rota para enviar mensagem direta
app.post('/send/dm', async (req, res) => {
    try {
        const { userId, message } = req.body;
        if (!userId || !message) {
            throw new Error('UserId e mensagem são obrigatórios');
        }
        await bot.sendDirectMessage(userId, message);
        res.json({ success: true });
    } catch (error) {
        logger.error('Erro na rota /send/dm:', error);
        res.status(500).json({ error: error.message });
    }
});

// Tratamento de erros não capturados
process.on('uncaughtException', (err) => {
    logger.error('Erro não capturado:', err);
});

process.on('unhandledRejection', (reason, promise) => {
    logger.error('Promessa rejeitada não tratada:', reason);
});

// Inicia o bot
(async () => {
    try {
        await bot.login();
        const PORT = process.env.INSTAGRAM_PORT || 3001;
        app.listen(PORT, () => {
            logger.info(`Servidor Instagram rodando na porta ${PORT}`);
        });
    } catch (error) {
        logger.error('Erro fatal ao iniciar o bot:', error);
        process.exit(1);
    }
})(); 