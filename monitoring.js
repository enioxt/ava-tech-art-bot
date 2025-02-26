import os from 'os';
import { CONFIG } from '../config/config.js';
import TelegramBot from 'node-telegram-bot-api';
import { promisify } from 'util';
import { exec } from 'child_process';
import fs from 'fs/promises';

const execAsync = promisify(exec);

class SystemMonitor {
  constructor() {
    this.bot = new TelegramBot(process.env.TELEGRAM_BOT_TOKEN, { polling: false });
    this.adminId = CONFIG.SECURITY.ADMIN_USER_ID;
    this.lastAlert = {};
    this.startMonitoring();
  }

  async checkSystem() {
    const metrics = {
      cpu: await this.getCPUUsage(),
      memory: this.getMemoryUsage(),
      disk: await this.getDiskUsage(),
      uptime: os.uptime(),
      loadAvg: os.loadavg()
    };

    return metrics;
  }

  async getCPUUsage() {
    const { stdout } = await execAsync("ps -A -o %cpu | awk '{s+=$1} END {print s}'");
    return parseFloat(stdout.trim());
  }

  getMemoryUsage() {
    const total = os.totalmem();
    const free = os.freemem();
    const used = total - free;
    return (used / total) * 100;
  }

  async getDiskUsage() {
    const { stdout } = await execAsync('df -h / | tail -1 | awk \'{print $5}\'');
    return parseInt(stdout.trim());
  }

  async checkProcesses() {
    try {
      const { stdout } = await execAsync('pm2 jlist');
      const processes = JSON.parse(stdout);
      return processes.map(p => ({
        name: p.name,
        status: p.pm2_env.status,
        cpu: p.monit.cpu,
        memory: p.monit.memory,
        uptime: p.pm2_env.pm_uptime
      }));
    } catch (error) {
      console.error('Erro ao verificar processos:', error);
      return [];
    }
  }

  async sendAlert(type, value, threshold) {
    // Evitar spam de alertas (máximo 1 alerta do mesmo tipo a cada hora)
    const now = Date.now();
    if (this.lastAlert[type] && (now - this.lastAlert[type]) < 3600000) {
      return;
    }

    this.lastAlert[type] = now;

    const message = `⚠️ *Alerta de Sistema*
Tipo: ${type}
Valor Atual: ${value.toFixed(2)}%
Limite: ${threshold}%
Timestamp: ${new Date().toISOString()}`;

    try {
      await this.bot.sendMessage(this.adminId, message, { parse_mode: 'Markdown' });
    } catch (error) {
      console.error('Erro ao enviar alerta:', error);
    }
  }

  async checkThresholds(metrics) {
    const { CPU, MEMORY, DISK } = CONFIG.MONITORING.ALERT_THRESHOLD;

    if (metrics.cpu > CPU) {
      await this.sendAlert('CPU', metrics.cpu, CPU);
    }
    if (metrics.memory > MEMORY) {
      await this.sendAlert('Memória', metrics.memory, MEMORY);
    }
    if (metrics.disk > DISK) {
      await this.sendAlert('Disco', metrics.disk, DISK);
    }
  }

  async generateReport() {
    const metrics = await this.checkSystem();
    const processes = await this.checkProcesses();
    
    const report = `📊 *Relatório do Sistema*
    
*Recursos:*
CPU: ${metrics.cpu.toFixed(2)}%
Memória: ${metrics.memory.toFixed(2)}%
Disco: ${metrics.disk}%
Uptime: ${(metrics.uptime / 3600).toFixed(2)}h
Load Average: ${metrics.loadAvg.join(', ')}

*Processos:*
${processes.map(p => `- ${p.name}: ${p.status} (CPU: ${p.cpu}%, Mem: ${Math.round(p.memory / 1024 / 1024)}MB)`).join('\n')}

*Timestamp:* ${new Date().toISOString()}`;

    return report;
  }

  async startMonitoring() {
    const interval = CONFIG.MONITORING.HEALTH_CHECK_INTERVAL;

    setInterval(async () => {
      try {
        const metrics = await this.checkSystem();
        await this.checkThresholds(metrics);
        
        // Gerar relatório diário às 00:00
        const now = new Date();
        if (now.getHours() === 0 && now.getMinutes() === 0) {
          const report = await this.generateReport();
          await this.bot.sendMessage(this.adminId, report, { parse_mode: 'Markdown' });
        }
      } catch (error) {
        console.error('Erro no monitoramento:', error);
      }
    }, interval);

    console.log('✓ Sistema de monitoramento iniciado');
  }
}

export const monitor = new SystemMonitor(); 