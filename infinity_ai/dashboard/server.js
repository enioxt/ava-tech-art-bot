const express = require('express');
const http = require('http');
const socketIo = require('socket.io');
const winston = require('winston');
const path = require('path');
const { promisify } = require('util');

// Configuração do logger
const logger = winston.createLogger({
    level: 'info',
    format: winston.format.combine(
        winston.format.timestamp(),
        winston.format.json()
    ),
    transports: [
        new winston.transports.File({ filename: 'logs/dashboard-error.log', level: 'error' }),
        new winston.transports.File({ filename: 'logs/dashboard-combined.log' })
    ]
});

if (process.env.NODE_ENV !== 'production') {
    logger.add(new winston.transports.Console({
        format: winston.format.simple()
    }));
}

// Mock do Redis em memória
class RedisMock {
    constructor() {
        this.data = new Map();
        this.isOpen = true;
    }

    async connect() {
        this.isOpen = true;
        logger.info('Mock Redis conectado');
        return true;
    }

    async get(key) {
        return this.data.get(key);
    }

    async set(key, value) {
        this.data.set(key, value);
        return 'OK';
    }

    on(event, callback) {
        // Mock dos eventos
    }
}

// Usar mock do Redis em vez do cliente real
const redis = new RedisMock();

// Conectar ao Redis (mock)
(async () => {
    try {
        await redis.connect();
        logger.info('Conectado ao Redis com sucesso');
        
        // Inicializar com dados mock
        await redis.set('infinity_metrics', JSON.stringify({
            average_response_time: 1500,
            failed_responses: 0,
            total_conversations: 100,
            channel_stats: {
                telegram: { success_rate: 98 },
                whatsapp: { success_rate: 97 },
                instagram: { success_rate: 96 }
            }
        }));
    } catch (error) {
        logger.error('Erro ao conectar ao Redis:', error);
        process.exit(1);
    }
})();

// Tratamento de erros do Redis
redis.on('error', (error) => {
    logger.error('Erro no cliente Redis:', error);
});

redis.on('reconnecting', () => {
    logger.info('Reconectando ao Redis...');
});

const getAsync = promisify(redis.get).bind(redis);

// Configuração do Express
const app = express();
const server = http.createServer(app);
const io = socketIo(server);

// Servir arquivos estáticos
app.use(express.static(path.join(__dirname, 'public')));

// Rota principal
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// KPIs e Alertas
const KPI_THRESHOLDS = {
    responseTime: 2000, // ms
    errorRate: 0.05, // 5%
    successRate: 0.95 // 95%
};

// Função para verificar alertas
function checkAlerts(metrics) {
    const alerts = [];
    
    // Verifica tempo de resposta
    if (metrics.average_response_time > KPI_THRESHOLDS.responseTime) {
        alerts.push({
            type: 'warning',
            message: `Tempo de resposta alto: ${metrics.average_response_time}ms`
        });
    }

    // Verifica taxa de erro
    const errorRate = metrics.failed_responses / (metrics.total_conversations || 1);
    if (errorRate > KPI_THRESHOLDS.errorRate) {
        alerts.push({
            type: 'error',
            message: `Taxa de erro alta: ${(errorRate * 100).toFixed(2)}%`
        });
    }

    // Verifica taxa de sucesso por canal
    Object.entries(metrics.channel_stats).forEach(([channel, stats]) => {
        if (stats.success_rate < KPI_THRESHOLDS.successRate * 100) {
            alerts.push({
                type: 'warning',
                message: `Taxa de sucesso baixa no ${channel}: ${stats.success_rate.toFixed(2)}%`
            });
        }
    });

    return alerts;
}

// Socket.IO para atualizações em tempo real
io.on('connection', async (socket) => {
    logger.info('Cliente conectado ao dashboard');

    // Envia dados iniciais
    async function sendInitialData() {
        try {
            if (!redis.isOpen) {
                logger.warn('Cliente Redis não está conectado. Tentando reconectar...');
                await redis.connect();
            }
            const metricsData = await redis.get('infinity_metrics');
            if (metricsData) {
                const metrics = JSON.parse(metricsData);
                const alerts = checkAlerts(metrics);
                socket.emit('metrics-update', { metrics, alerts });
            }
        } catch (error) {
            logger.error('Erro ao enviar dados iniciais:', error);
        }
    }

    sendInitialData();

    // Atualiza dados a cada 5 segundos
    const updateInterval = setInterval(async () => {
        try {
            const metricsData = await getAsync('infinity_metrics');
            const metrics = JSON.parse(metricsData);
            const alerts = checkAlerts(metrics);
            
            socket.emit('metrics-update', {
                metrics,
                alerts
            });
        } catch (error) {
            logger.error('Erro ao atualizar métricas:', error);
        }
    }, 5000);

    socket.on('disconnect', () => {
        clearInterval(updateInterval);
        logger.info('Cliente desconectado do dashboard');
    });
});

// Inicia o servidor
const PORT = process.env.DASHBOARD_PORT || 3002;
server.listen(PORT, () => {
    logger.info(`Dashboard rodando na porta ${PORT}`);
}); 