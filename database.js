import Redis from 'ioredis';
import { CONFIG } from '../config/config.js';
import fs from 'fs/promises';
import path from 'path';

class Database {
  constructor() {
    this.redis = new Redis(CONFIG.CACHE.REDIS_URL, {
      password: CONFIG.CACHE.REDIS_PASSWORD,
      maxRetriesPerRequest: 3
    });

    this.redis.on('error', (error) => {
      console.error('Erro na conexão Redis (Database):', error);
    });

    this.setupBackup();
  }

  /**
   * Registra uma interação do usuário
   * @param {Object} data - Dados da interação
   * @param {string} data.userId - ID do usuário
   * @param {string} data.chatId - ID do chat
   * @param {string} data.action - Tipo de ação
   * @param {Object} data.metadata - Metadados adicionais
   */
  async logInteraction(data) {
    try {
      const timestamp = Date.now();
      const key = `interaction:${timestamp}:${data.userId}`;
      
      const interaction = {
        ...data,
        timestamp,
        date: new Date(timestamp).toISOString()
      };

      // Salvar interação
      await this.redis.hmset(key, interaction);
      
      // Adicionar à lista de interações do usuário
      await this.redis.zadd(`user:${data.userId}:interactions`, timestamp, key);
      
      // Adicionar à lista geral de interações
      await this.redis.zadd('interactions', timestamp, key);
      
      // Incrementar contadores
      await this.redis.hincrby(`stats:${data.userId}`, data.action, 1);
      await this.redis.hincrby('stats:global', data.action, 1);

      console.log(`✓ Interação registrada: ${data.action} por ${data.userId}`);
    } catch (error) {
      console.error('Erro ao registrar interação:', error);
    }
  }

  /**
   * Obtém estatísticas de um usuário
   * @param {string} userId - ID do usuário
   * @returns {Promise<Object>} - Estatísticas do usuário
   */
  async getUserStats(userId) {
    try {
      const stats = await this.redis.hgetall(`stats:${userId}`);
      const interactions = await this.redis.zcard(`user:${userId}:interactions`);
      
      return {
        ...stats,
        totalInteractions: interactions
      };
    } catch (error) {
      console.error('Erro ao obter estatísticas do usuário:', error);
      return null;
    }
  }

  /**
   * Obtém estatísticas globais
   * @returns {Promise<Object>} - Estatísticas globais
   */
  async getGlobalStats() {
    try {
      const stats = await this.redis.hgetall('stats:global');
      const totalInteractions = await this.redis.zcard('interactions');
      const uniqueUsers = await this.redis.scard('users');
      
      return {
        ...stats,
        totalInteractions,
        uniqueUsers
      };
    } catch (error) {
      console.error('Erro ao obter estatísticas globais:', error);
      return null;
    }
  }

  /**
   * Obtém histórico de interações de um usuário
   * @param {string} userId - ID do usuário
   * @param {number} limit - Limite de registros
   * @returns {Promise<Array>} - Lista de interações
   */
  async getUserHistory(userId, limit = 50) {
    try {
      const keys = await this.redis.zrevrange(`user:${userId}:interactions`, 0, limit - 1);
      
      if (keys.length === 0) return [];

      const multi = this.redis.multi();
      keys.forEach(key => multi.hgetall(key));
      
      const results = await multi.exec();
      return results.map(([err, data]) => err ? null : data).filter(Boolean);
    } catch (error) {
      console.error('Erro ao obter histórico do usuário:', error);
      return [];
    }
  }

  /**
   * Configura backup automático
   * @private
   */
  setupBackup() {
    // Executar backup diário
    setInterval(async () => {
      try {
        await this.backup();
      } catch (error) {
        console.error('Erro no backup automático:', error);
      }
    }, 24 * 60 * 60 * 1000); // 24 horas
  }

  /**
   * Realiza backup dos dados
   */
  async backup() {
    try {
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
      const backupDir = CONFIG.BACKUP.PATHS.DATA;
      const backupPath = path.join(backupDir, `backup_${timestamp}.json`);

      // Obter todas as chaves
      const keys = await this.redis.keys('*');
      const data = {};

      // Processar cada tipo de dado
      for (const key of keys) {
        if (key.startsWith('interaction:')) {
          data[key] = await this.redis.hgetall(key);
        } else if (key.startsWith('stats:')) {
          data[key] = await this.redis.hgetall(key);
        } else if (key.endsWith(':interactions')) {
          data[key] = await this.redis.zrange(key, 0, -1, 'WITHSCORES');
        }
      }

      // Salvar backup
      await fs.writeFile(backupPath, JSON.stringify(data, null, 2));
      console.log(`✓ Backup realizado: ${backupPath}`);

      // Limpar backups antigos
      await this.cleanOldBackups();
    } catch (error) {
      console.error('Erro ao realizar backup:', error);
    }
  }

  /**
   * Limpa backups antigos
   * @private
   */
  async cleanOldBackups() {
    try {
      const backupDir = CONFIG.BACKUP.PATHS.DATA;
      const files = await fs.readdir(backupDir);
      const backupFiles = files.filter(f => f.startsWith('backup_') && f.endsWith('.json'));

      // Ordenar por data (mais recente primeiro)
      backupFiles.sort().reverse();

      // Manter apenas os últimos N backups
      const filesToDelete = backupFiles.slice(CONFIG.BACKUP.RETENTION_DAYS);

      for (const file of filesToDelete) {
        await fs.unlink(path.join(backupDir, file));
      }

      if (filesToDelete.length > 0) {
        console.log(`✓ ${filesToDelete.length} backups antigos removidos`);
      }
    } catch (error) {
      console.error('Erro ao limpar backups antigos:', error);
    }
  }

  /**
   * Restaura dados de um backup
   * @param {string} backupPath - Caminho do arquivo de backup
   */
  async restore(backupPath) {
    try {
      const data = JSON.parse(await fs.readFile(backupPath, 'utf8'));
      
      // Usar transação para restaurar dados
      const multi = this.redis.multi();

      for (const [key, value] of Object.entries(data)) {
        if (key.startsWith('interaction:')) {
          multi.hmset(key, value);
        } else if (key.startsWith('stats:')) {
          multi.hmset(key, value);
        } else if (key.endsWith(':interactions')) {
          const scores = value;
          for (let i = 0; i < scores.length; i += 2) {
            multi.zadd(key, scores[i + 1], scores[i]);
          }
        }
      }

      await multi.exec();
      console.log('✓ Dados restaurados com sucesso');
    } catch (error) {
      console.error('Erro ao restaurar dados:', error);
      throw error;
    }
  }
}

// Exportar instância única
const db = new Database();

export const logInteraction = (data) => db.logInteraction(data);
export const getUserStats = (userId) => db.getUserStats(userId);
export const getGlobalStats = () => db.getGlobalStats();
export const getUserHistory = (userId, limit) => db.getUserHistory(userId, limit);
export const backup = () => db.backup();
export const restore = (backupPath) => db.restore(backupPath);