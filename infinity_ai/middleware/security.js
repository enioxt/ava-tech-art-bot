const { RateLimiterRedis } = require('rate-limiter-flexible');
const Redis = require('redis');
const jwt = require('jsonwebtoken');
const winston = require('winston');

// Configuração do logger
const logger = winston.createLogger({
    level: 'info',
    format: winston.format.combine(
        winston.format.timestamp(),
        winston.format.json()
    ),
    transports: [
        new winston.transports.File({ filename: 'logs/security-error.log', level: 'error' }),
        new winston.transports.File({ filename: 'logs/security-combined.log' })
    ]
});

if (process.env.NODE_ENV !== 'production') {
    logger.add(new winston.transports.Console({
        format: winston.format.simple()
    }));
}

// Configuração do Redis
const redisClient = Redis.createClient({
    host: process.env.REDIS_HOST || 'localhost',
    port: process.env.REDIS_PORT || 6379,
    password: process.env.REDIS_PASSWORD || ''
});

// Configuração do Rate Limiter
const rateLimiter = new RateLimiterRedis({
    storeClient: redisClient,
    keyPrefix: 'rate_limit',
    points: 100, // Número de requisições
    duration: 60, // Por minuto
    blockDuration: 60 * 15 // 15 minutos de bloqueio após exceder
});

// Rate Limiter por usuário
const userRateLimiter = new RateLimiterRedis({
    storeClient: redisClient,
    keyPrefix: 'user_rate_limit',
    points: 50, // Requisições por usuário
    duration: 60, // Por minuto
    blockDuration: 60 * 10 // 10 minutos de bloqueio
});

// Middleware de Rate Limiting
const rateLimitMiddleware = async (req, res, next) => {
    try {
        // Rate limit global
        await rateLimiter.consume(req.ip);
        
        // Rate limit por usuário se autenticado
        if (req.user && req.user.id) {
            await userRateLimiter.consume(req.user.id);
        }
        
        next();
    } catch (error) {
        logger.warn(`Rate limit excedido - IP: ${req.ip}, User: ${req.user?.id}`);
        res.status(429).json({
            error: 'Muitas requisições. Por favor, aguarde alguns minutos.'
        });
    }
};

// Middleware de autenticação
const authMiddleware = (req, res, next) => {
    try {
        const token = req.headers.authorization?.split(' ')[1];
        
        if (!token) {
            throw new Error('Token não fornecido');
        }

        const decoded = jwt.verify(token, process.env.JWT_SECRET);
        req.user = decoded;
        
        next();
    } catch (error) {
        logger.error(`Erro de autenticação: ${error.message}`);
        res.status(401).json({
            error: 'Não autorizado'
        });
    }
};

// Middleware de validação de token de bot
const botAuthMiddleware = (req, res, next) => {
    try {
        const botToken = req.headers['x-bot-token'];
        const botType = req.headers['x-bot-type'];

        if (!botToken || !botType) {
            throw new Error('Credenciais do bot não fornecidas');
        }

        // Valida token baseado no tipo de bot
        let isValid = false;
        switch (botType) {
            case 'whatsapp':
                isValid = botToken === process.env.WHATSAPP_TOKEN;
                break;
            case 'telegram':
                isValid = botToken === process.env.TELEGRAM_TOKEN;
                break;
            case 'instagram':
                isValid = botToken === process.env.INSTAGRAM_TOKEN;
                break;
            default:
                throw new Error('Tipo de bot inválido');
        }

        if (!isValid) {
            throw new Error('Token do bot inválido');
        }

        req.botType = botType;
        next();
    } catch (error) {
        logger.error(`Erro de autenticação do bot: ${error.message}`);
        res.status(401).json({
            error: 'Bot não autorizado'
        });
    }
};

// Middleware de logging de segurança
const securityLoggingMiddleware = (req, res, next) => {
    const start = Date.now();
    
    res.on('finish', () => {
        const duration = Date.now() - start;
        logger.info('Requisição processada', {
            method: req.method,
            path: req.path,
            status: res.statusCode,
            duration,
            ip: req.ip,
            user: req.user?.id,
            botType: req.botType
        });
    });

    next();
};

module.exports = {
    rateLimitMiddleware,
    authMiddleware,
    botAuthMiddleware,
    securityLoggingMiddleware
}; 