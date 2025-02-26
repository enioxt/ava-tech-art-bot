import Redis from 'ioredis';
import { CONFIG } from '../config/config.js';

class RateLimiter {
  constructor() {
    this.redis = new Redis(CONFIG.CACHE.REDIS_URL, {
      password: CONFIG.CACHE.REDIS_PASSWORD,
      maxRetriesPerRequest: 3
    });

    this.windowMs = CONFIG.RATE_LIMIT.WINDOW_MS;
    this.maxRequests = CONFIG.RATE_LIMIT.MAX_REQUESTS;

    this.redis.on('error', (error) => {
      console.error('Erro na conexão Redis (Rate Limiter):', error);
    });
  }

  /**
   * Verifica se um usuário pode fazer mais requisições
   * @param {string} userId - ID do usuário
   * @returns {Promise<boolean>} - true se o usuário pode fazer mais requisições
   */
  async checkRateLimit(userId) {
    const key = `ratelimit:${userId}`;
    
    try {
      // Usar transação Redis para garantir atomicidade
      const multi = this.redis.multi();
      
      // Obter contagem atual
      multi.get(key);
      // Verificar TTL
      multi.ttl(key);
      
      const [count, ttl] = await multi.exec();
      const currentCount = parseInt(count?.[1]) || 0;
      
      if (currentCount >= this.maxRequests) {
        return false;
      }

      // Se é a primeira requisição ou a chave expirou
      if (currentCount === 0) {
        await this.redis.setex(key, this.windowMs / 1000, 1);
      } else {
        // Incrementar contador
        await this.redis.incr(key);
        
        // Se o TTL não existe, definir novo TTL
        if (ttl?.[1] === -1) {
          await this.redis.expire(key, this.windowMs / 1000);
        }
      }

      return true;
    } catch (error) {
      console.error('Erro ao verificar rate limit:', error);
      // Em caso de erro, permitir a requisição
      return true;
    }
  }

  /**
   * Obtém informações sobre o rate limit de um usuário
   * @param {string} userId - ID do usuário
   * @returns {Promise<Object>} - Informações do rate limit
   */
  async getRateLimitInfo(userId) {
    const key = `ratelimit:${userId}`;
    
    try {
      const multi = this.redis.multi();
      multi.get(key);
      multi.ttl(key);
      
      const [count, ttl] = await multi.exec();
      const currentCount = parseInt(count?.[1]) || 0;
      const remainingTime = ttl?.[1] > 0 ? ttl[1] : 0;
      
      return {
        total: this.maxRequests,
        remaining: Math.max(0, this.maxRequests - currentCount),
        reset: remainingTime,
        exceeded: currentCount >= this.maxRequests
      };
    } catch (error) {
      console.error('Erro ao obter informações de rate limit:', error);
      return null;
    }
  }

  /**
   * Reseta o rate limit de um usuário
   * @param {string} userId - ID do usuário
   */
  async resetRateLimit(userId) {
    try {
      await this.redis.del(`ratelimit:${userId}`);
    } catch (error) {
      console.error('Erro ao resetar rate limit:', error);
    }
  }

  /**
   * Obtém estatísticas gerais do rate limit
   * @returns {Promise<Object>} - Estatísticas do rate limit
   */
  async getStats() {
    try {
      const keys = await this.redis.keys('ratelimit:*');
      const stats = {
        totalUsers: keys.length,
        exceededUsers: 0,
        averageUsage: 0
      };

      if (keys.length > 0) {
        const multi = this.redis.multi();
        keys.forEach(key => multi.get(key));
        const counts = await multi.exec();
        
        let total = 0;
        counts.forEach(([err, count]) => {
          if (!err && count) {
            const value = parseInt(count);
            total += value;
            if (value >= this.maxRequests) {
              stats.exceededUsers++;
            }
          }
        });

        stats.averageUsage = total / keys.length;
      }

      return stats;
    } catch (error) {
      console.error('Erro ao obter estatísticas:', error);
      return null;
    }
  }
}

// Exportar instância única
const limiter = new RateLimiter();

/**
 * Função de verificação de rate limit
 * @param {string} userId - ID do usuário
 * @returns {Promise<boolean>} - true se o usuário pode fazer mais requisições
 */
export async function checkRateLimit(userId) {
  return limiter.checkRateLimit(userId);
}

/**
 * Função para obter informações do rate limit
 * @param {string} userId - ID do usuário
 * @returns {Promise<Object>} - Informações do rate limit
 */
export async function getRateLimitInfo(userId) {
  return limiter.getRateLimitInfo(userId);
}

/**
 * Função para resetar o rate limit
 * @param {string} userId - ID do usuário
 */
export async function resetRateLimit(userId) {
  return limiter.resetRateLimit(userId);
}

/**
 * Função para obter estatísticas do rate limit
 * @returns {Promise<Object>} - Estatísticas do rate limit
 */
export async function getRateLimitStats() {
  return limiter.getStats();
} 