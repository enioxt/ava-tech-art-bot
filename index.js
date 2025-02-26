const express = require('express');
const dotenv = require('dotenv');
const cors = require('cors');
const helmet = require('helmet');
const compression = require('compression');
const morgan = require('morgan');
const rateLimit = require('express-rate-limit');
const winston = require('winston');
const Redis = require('ioredis');
const path = require('path');
const fs = require('fs').promises;
const swaggerJsdoc = require('swagger-jsdoc');
const swaggerUi = require('swagger-ui-express');

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

// Configuração do Express
const app = express();

// Middleware de segurança
app.use(helmet());

// Middleware de CORS
app.use(cors({
    origin: process.env.CORS_ORIGIN || '*',
    methods: process.env.CORS_METHODS || 'GET,POST,PUT,DELETE',
    allowedHeaders: process.env.CORS_HEADERS || 'Content-Type,Authorization'
}));

// Middleware de compressão
app.use(compression());

// Middleware de logging
app.use(morgan('combined', {
    stream: {
        write: (message) => logger.info(message.trim())
    }
}));

// Middleware de rate limit
const limiter = rateLimit({
    windowMs: 15 * 60 * 1000, // 15 minutos
    max: 100 // limite por IP
});
app.use(limiter);

// Middleware de parse do body
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Configuração do Swagger
const swaggerOptions = {
    definition: {
        openapi: '3.0.0',
        info: {
            title: 'AVA Bot API',
            version: '2.0.0',
            description: 'API do AVA Bot para processamento de imagens',
            contact: {
                name: 'Suporte AVA',
                url: 'https://ava-bot.com',
                email: 'suporte@ava-bot.com'
            }
        },
        servers: [
            {
                url: process.env.API_URL || 'http://localhost:3000',
                description: 'Servidor Principal'
            }
        ]
    },
    apis: ['./src/routes/*.js']
};

const swaggerDocs = swaggerJsdoc(swaggerOptions);
app.use('/api-docs', swaggerUi.serve, swaggerUi.setup(swaggerDocs));

// Rotas de status
app.get('/status', (req, res) => {
    res.json({
        status: 'online',
        version: '2.0.0',
        timestamp: new Date().toISOString()
    });
});

// Rotas de métricas
app.get('/metrics', async (req, res) => {
    try {
        const metrics = {
            users: await redis.get('metrics:users') || 0,
            images_processed: await redis.get('metrics:images') || 0,
            uptime: process.uptime(),
            memory: process.memoryUsage(),
            cpu: process.cpuUsage()
        };
        res.json(metrics);
    } catch (error) {
        logger.error('Erro ao obter métricas:', error);
        res.status(500).json({ error: 'Erro ao obter métricas' });
    }
});

// Rotas de webhook do Telegram
app.post(`/webhook/${process.env.BOT_TOKEN}`, async (req, res) => {
    try {
        // Processa webhook
        logger.info('Webhook recebido:', req.body);
        res.sendStatus(200);
    } catch (error) {
        logger.error('Erro ao processar webhook:', error);
        res.sendStatus(500);
    }
});

// Middleware de erro 404
app.use((req, res) => {
    res.status(404).json({ error: 'Rota não encontrada' });
});

// Middleware de tratamento de erros
app.use((err, req, res, next) => {
    logger.error('Erro na aplicação:', err);
    res.status(500).json({ error: 'Erro interno do servidor' });
});

// Inicialização do servidor
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    logger.info(`Servidor iniciado na porta ${PORT}`);
    console.log(`🚀 Servidor rodando em http://localhost:${PORT}`);
    console.log(`📚 Documentação em http://localhost:${PORT}/api-docs`);
}); 