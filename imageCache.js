import Redis from 'ioredis';
import { CONFIG } from '../config/config.js';
import crypto from 'crypto';

class ImageCache {
  constructor() {
    this.redis = new Redis(CONFIG.CACHE.REDIS_URL, {
      password: CONFIG.CACHE.REDIS_PASSWORD,
      maxRetriesPerRequest: 3,
      retryStrategy(times) {
        const delay = Math.min(times * 50, 2000);
        return delay;
      }
    });

    this.redis.on('error', (error) => {
      console.error('Erro na conexão Redis:', error);
    });

    this.redis.on('connect', () => {
      console.log('✓ Conectado ao Redis');
    });

    // Configurar limpeza periódica
    this.setupCacheCleaning();
  }

  /**
   * Gera uma chave única para a imagem e suas dimensões
   * @private
   */
  generateKey(imageBuffer, width, height) {
    const hash = crypto
      .createHash('sha256')
      .update(imageBuffer)
      .update(`${width}x${height}`)
      .digest('hex');
    
    return `image:${hash}`;
  }

  /**
   * Obtém uma imagem do cache
   * @param {Buffer} originalBuffer - Buffer da imagem original
   * @param {number} width - Largura desejada
   * @param {number} height - Altura desejada
   * @returns {Promise<Buffer|null>} Buffer da imagem processada ou null se não encontrada
   */
  async get(originalBuffer, width, height) {
    try {
      const key = this.generateKey(originalBuffer, width, height);
      const cached = await this.redis.getBuffer(key);
      
      if (cached) {
        console.log('✓ Imagem encontrada no cache');
        return cached;
      }
      
      return null;
    } catch (error) {
      console.error('Erro ao buscar do cache:', error);
      return null;
    }
  }

  /**
   * Armazena uma imagem no cache
   * @param {Buffer} originalBuffer - Buffer da imagem original
   * @param {Buffer} processedBuffer - Buffer da imagem processada
   * @param {number} width - Largura
   * @param {number} height - Altura
   */
  async set(originalBuffer, processedBuffer, width, height) {
    try {
      const key = this.generateKey(originalBuffer, width, height);
      
      await this.redis.setBuffer(key, processedBuffer, 'EX', CONFIG.CACHE.CACHE_TTL);
      console.log('✓ Imagem armazenada no cache');
      
      // Adicionar à lista de chaves para limpeza
      await this.redis.zadd('image_cache_keys', Date.now(), key);
      
    } catch (error) {
      console.error('Erro ao armazenar no cache:', error);
    }
  }

  /**
   * Remove uma imagem do cache
   * @param {Buffer} originalBuffer - Buffer da imagem original
   * @param {number} width - Largura
   * @param {number} height - Altura
   */
  async delete(originalBuffer, width, height) {
    try {
      const key = this.generateKey(originalBuffer, width, height);
      await this.redis.del(key);
      await this.redis.zrem('image_cache_keys', key);
      console.log('✓ Imagem removida do cache');
    } catch (error) {
      console.error('Erro ao remover do cache:', error);
    }
  }

  /**
   * Configura limpeza periódica do cache
   * @private
   */
  setupCacheCleaning() {
    // Limpar cache a cada hora
    setInterval(async () => {
      try {
        const now = Date.now();
        const expirationTime = now - (CONFIG.CACHE.CACHE_TTL * 1000);
        
        // Remover chaves expiradas
        const expiredKeys = await this.redis.zrangebyscore('image_cache_keys', 0, expirationTime);
        
        if (expiredKeys.length > 0) {
          await this.redis.del(...expiredKeys);
          await this.redis.zremrangebyscore('image_cache_keys', 0, expirationTime);
          console.log(`✓ ${expiredKeys.length} imagens removidas do cache`);
        }

        // Verificar tamanho do cache
        const cacheSize = await this.redis.zcard('image_cache_keys');
        if (cacheSize > CONFIG.CACHE.MAX_CACHE_SIZE) {
          const keysToRemove = cacheSize - CONFIG.CACHE.MAX_CACHE_SIZE;
          const oldestKeys = await this.redis.zrange('image_cache_keys', 0, keysToRemove - 1);
          
          await this.redis.del(...oldestKeys);
          await this.redis.zremrangebyrank('image_cache_keys', 0, keysToRemove - 1);
          console.log(`✓ Cache reduzido em ${keysToRemove} itens`);
        }
      } catch (error) {
        console.error('Erro na limpeza do cache:', error);
      }
    }, 3600000); // 1 hora
  }

  /**
   * Limpa todo o cache
   */
  async clear() {
    try {
      const keys = await this.redis.zrange('image_cache_keys', 0, -1);
      if (keys.length > 0) {
        await this.redis.del(...keys);
        await this.redis.del('image_cache_keys');
        console.log(`✓ Cache limpo: ${keys.length} imagens removidas`);
      }
    } catch (error) {
      console.error('Erro ao limpar cache:', error);
    }
  }

  /**
   * Obtém estatísticas do cache
   * @returns {Promise<Object>} Estatísticas do cache
   */
  async getStats() {
    try {
      const cacheSize = await this.redis.zcard('image_cache_keys');
      const memoryInfo = await this.redis.info('memory');
      const usedMemory = memoryInfo.match(/used_memory_human:(\S+)/)[1];

      return {
        items: cacheSize,
        memory: usedMemory,
        maxItems: CONFIG.CACHE.MAX_CACHE_SIZE
      };
    } catch (error) {
      console.error('Erro ao obter estatísticas:', error);
      return null;
    }
  }
}

// Exportar instância única
export const imageCache = new ImageCache(); 