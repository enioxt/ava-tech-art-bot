/**
 * EthicsValidator.js
 * Sistema de validação ética aprimorado para o EaaS
 */

const crypto = require('crypto');
const { Supabase } = require('@supabase/supabase-js');
const TelegramBot = require('node-telegram-bot-api');
const logger = require('./logger');

class EthicsValidator {
    constructor(config) {
        this.supabase = new Supabase(config.supabase.url, config.supabase.key);
        this.bot = new TelegramBot(config.telegram.token);
        this.adminId = config.telegram.adminId;
        
        this.principles = {
            transparency: "Transparência em todas as operações",
            fairness: "Equidade nas decisões",
            accountability: "Responsabilidade pelas ações",
            sustainability: "Sustentabilidade digital"
        };
    }

    /**
     * Gera checksum para validação de integridade
     */
    generateChecksum(data) {
        return crypto
            .createHash('sha256')
            .update(JSON.stringify(data))
            .digest('hex');
    }

    /**
     * Valida princípios éticos de uma operação
     */
    async validateEthicalPrinciples(operation) {
        const validation = {
            timestamp: Date.now(),
            operation: operation.type,
            checks: [],
            status: 'pending'
        };

        try {
            // Validação de transparência
            validation.checks.push({
                principle: 'transparency',
                passed: this.validateTransparency(operation)
            });

            // Validação de equidade
            validation.checks.push({
                principle: 'fairness',
                passed: this.validateFairness(operation)
            });

            // Validação de responsabilidade
            validation.checks.push({
                principle: 'accountability',
                passed: this.validateAccountability(operation)
            });

            // Validação de sustentabilidade
            validation.checks.push({
                principle: 'sustainability',
                passed: this.validateSustainability(operation)
            });

            // Gera checksum da validação
            validation.checksum = this.generateChecksum(validation);
            
            // Atualiza status
            validation.status = validation.checks.every(check => check.passed) 
                ? 'approved' 
                : 'rejected';

            // Salva log da validação
            await this.logValidation(validation);

            // Envia alerta se necessário
            if (validation.status === 'rejected') {
                await this.sendAlert(
                    `⚠️ Validação ética falhou:\n${JSON.stringify(validation, null, 2)}`
                );
            }

            return validation;

        } catch (error) {
            logger.error('Erro na validação ética:', error);
            await this.sendAlert(`❌ Erro na validação ética: ${error.message}`);
            throw error;
        }
    }

    /**
     * Valida transparência da operação
     */
    validateTransparency(operation) {
        return (
            operation.metadata &&
            operation.metadata.purpose &&
            operation.metadata.impact &&
            operation.metadata.stakeholders
        );
    }

    /**
     * Valida equidade da operação
     */
    validateFairness(operation) {
        return (
            operation.impact &&
            operation.impact.positive >= operation.impact.negative &&
            !operation.impact.discriminatory
        );
    }

    /**
     * Valida responsabilidade da operação
     */
    validateAccountability(operation) {
        return (
            operation.responsible &&
            operation.responsible.id &&
            operation.responsible.role &&
            operation.audit_trail
        );
    }

    /**
     * Valida sustentabilidade da operação
     */
    validateSustainability(operation) {
        return (
            operation.resources &&
            operation.resources.usage <= operation.resources.limit &&
            operation.environmental_impact <= config.maxEnvironmentalImpact
        );
    }

    /**
     * Salva log da validação
     */
    async logValidation(validation) {
        try {
            await this.supabase
                .from('ethical_validations')
                .insert(validation);

            logger.info('Validação ética registrada:', validation);

        } catch (error) {
            logger.error('Erro ao salvar validação:', error);
            throw error;
        }
    }

    /**
     * Envia alerta via Telegram
     */
    async sendAlert(message) {
        try {
            await this.bot.sendMessage(this.adminId, message);
            logger.info('Alerta enviado:', message);
        } catch (error) {
            logger.error('Erro ao enviar alerta:', error);
            throw error;
        }
    }
}

module.exports = EthicsValidator; 