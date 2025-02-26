/**
 * logger.js
 * Sistema de logging para o EaaS
 */

const winston = require('winston');
const config = require('../config/config');

// Formato personalizado
const customFormat = winston.format.printf(({ level, message, timestamp }) => {
    return `${timestamp} [${level.toUpperCase()}]: ${message}`;
});

// Configuração do logger
const logger = winston.createLogger({
    level: config.logging.level,
    format: winston.format.combine(
        winston.format.timestamp(),
        customFormat
    ),
    transports: [
        // Log em arquivo
        new winston.transports.File({
            filename: config.logging.file,
            maxsize: 5242880, // 5MB
            maxFiles: 5,
            tailable: true
        }),
        // Log no console
        new winston.transports.Console({
            format: winston.format.combine(
                winston.format.colorize(),
                customFormat
            )
        })
    ]
});

module.exports = logger; 