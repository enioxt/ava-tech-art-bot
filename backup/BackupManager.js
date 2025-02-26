/**
 * BackupManager.js
 * Sistema de backup seguro e redundante para o EaaS
 */

const fs = require('fs').promises;
const path = require('path');
const crypto = require('crypto');
const { Supabase } = require('@supabase/supabase-js');
const TelegramBot = require('node-telegram-bot-api');
const logger = require('../logger');

class BackupManager {
    constructor(config) {
        this.supabase = new Supabase(config.supabase.url, config.supabase.key);
        this.bot = new TelegramBot(config.telegram.token);
        this.adminId = config.telegram.adminId;
        this.backupDir = config.backup.directory;
        
        // Provedores de armazenamento
        this.storageProviders = {
            local: this.localStorageProvider(),
            supabase: this.supabaseStorageProvider(),
            // Adicionar mais provedores conforme necessário
        };
    }

    /**
     * Provedor de armazenamento local
     */
    localStorageProvider() {
        return {
            store: async (data, metadata) => {
                const filename = `backup_${Date.now()}.zip`;
                const filepath = path.join(this.backupDir, filename);
                
                await fs.writeFile(filepath, data);
                await fs.writeFile(
                    `${filepath}.meta.json`,
                    JSON.stringify(metadata)
                );
                
                return {
                    provider: 'local',
                    path: filepath,
                    checksum: this.generateChecksum(data)
                };
            }
        };
    }

    /**
     * Provedor de armazenamento Supabase
     */
    supabaseStorageProvider() {
        return {
            store: async (data, metadata) => {
                const filename = `backup_${Date.now()}.zip`;
                
                const { data: uploadData, error } = await this.supabase
                    .storage
                    .from('backups')
                    .upload(filename, data);

                if (error) throw error;

                await this.supabase
                    .from('backup_metadata')
                    .insert({
                        filename,
                        metadata,
                        checksum: this.generateChecksum(data)
                    });

                return {
                    provider: 'supabase',
                    path: uploadData.path,
                    checksum: this.generateChecksum(data)
                };
            }
        };
    }

    /**
     * Gera checksum para validação de integridade
     */
    generateChecksum(data) {
        return crypto
            .createHash('sha256')
            .update(data)
            .digest('hex');
    }

    /**
     * Realiza backup com redundância
     */
    async createBackup(data, metadata) {
        const backupInfo = {
            timestamp: Date.now(),
            status: 'pending',
            results: [],
            checksum: this.generateChecksum(data)
        };

        try {
            // Realiza backup em todos os provedores
            const backupPromises = Object.values(this.storageProviders)
                .map(provider => provider.store(data, metadata));

            const results = await Promise.allSettled(backupPromises);

            // Processa resultados
            backupInfo.results = results.map((result, index) => ({
                provider: Object.keys(this.storageProviders)[index],
                status: result.status,
                value: result.status === 'fulfilled' ? result.value : null,
                error: result.status === 'rejected' ? result.reason : null
            }));

            // Verifica se pelo menos um backup foi bem sucedido
            const hasSuccess = backupInfo.results.some(r => r.status === 'fulfilled');
            
            if (!hasSuccess) {
                throw new Error('Nenhum backup foi concluído com sucesso');
            }

            // Atualiza status
            backupInfo.status = 'completed';

            // Registra informações do backup
            await this.logBackup(backupInfo);

            // Verifica integridade
            await this.verifyBackupIntegrity(backupInfo);

            return backupInfo;

        } catch (error) {
            backupInfo.status = 'failed';
            backupInfo.error = error.message;

            await this.logBackup(backupInfo);
            await this.sendAlert(
                `❌ Falha no backup:\n${JSON.stringify(backupInfo, null, 2)}`
            );

            throw error;
        }
    }

    /**
     * Verifica integridade do backup
     */
    async verifyBackupIntegrity(backupInfo) {
        const verificationResults = await Promise.all(
            backupInfo.results
                .filter(r => r.status === 'fulfilled')
                .map(async result => {
                    try {
                        const data = await this.retrieveBackup(result.value);
                        const checksum = this.generateChecksum(data);
                        
                        return {
                            provider: result.provider,
                            integrity: checksum === backupInfo.checksum
                        };
                    } catch (error) {
                        return {
                            provider: result.provider,
                            integrity: false,
                            error: error.message
                        };
                    }
                })
        );

        const hasValidBackup = verificationResults.some(r => r.integrity);

        if (!hasValidBackup) {
            throw new Error('Nenhum backup válido encontrado após verificação');
        }

        return verificationResults;
    }

    /**
     * Recupera backup de um provedor
     */
    async retrieveBackup(backupLocation) {
        switch (backupLocation.provider) {
            case 'local':
                return fs.readFile(backupLocation.path);
            
            case 'supabase':
                const { data, error } = await this.supabase
                    .storage
                    .from('backups')
                    .download(backupLocation.path);
                
                if (error) throw error;
                return data;
            
            default:
                throw new Error(`Provedor não suportado: ${backupLocation.provider}`);
        }
    }

    /**
     * Registra informações do backup
     */
    async logBackup(backupInfo) {
        try {
            await this.supabase
                .from('backup_logs')
                .insert(backupInfo);

            logger.info('Backup registrado:', backupInfo);

        } catch (error) {
            logger.error('Erro ao registrar backup:', error);
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

module.exports = BackupManager; 