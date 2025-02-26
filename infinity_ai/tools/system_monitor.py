"""
EVA System Monitor
Monitoramento e Gerenciamento do Sistema
"""

import os
import sys
import logging
import asyncio
import psutil
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from ..core.sync_manager import SyncManager
from ..core.bot_core import EVACore
from .system_restore import SystemRestore

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("system_monitor.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("EVA.Monitor")

@dataclass
class SystemMetrics:
    """Métricas do sistema"""
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    network_sent: int
    network_recv: int
    timestamp: str
    processes: int
    threads: int
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
        
    @property
    def is_healthy(self) -> bool:
        return (
            self.cpu_percent < 80 and
            self.memory_percent < 80 and
            self.disk_percent < 80
        )

class SystemMonitor:
    def __init__(self):
        self.sync_manager = SyncManager()
        self.restore = SystemRestore()
        self.metrics_history: List[SystemMetrics] = []
        self.max_history = 1000
        self.check_interval = 60  # 1 minuto
        self.backup_interval = 3600  # 1 hora
        self.last_backup = datetime.now()
        self.running = True
        
        # Diretórios
        self.data_dir = Path("data")
        self.logs_dir = Path("logs")
        self.metrics_dir = Path("metrics")
        
        # Cria diretórios
        for dir_path in [self.data_dir, self.logs_dir, self.metrics_dir]:
            dir_path.mkdir(exist_ok=True)
            
    async def collect_metrics(self) -> SystemMetrics:
        """Coleta métricas do sistema"""
        try:
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            net = psutil.net_io_counters()
            
            metrics = SystemMetrics(
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                disk_percent=disk.percent,
                network_sent=net.bytes_sent,
                network_recv=net.bytes_recv,
                timestamp=datetime.now().isoformat(),
                processes=len(psutil.pids()),
                threads=sum(p.num_threads() for p in psutil.process_iter(['num_threads']))
            )
            
            # Atualiza histórico
            self.metrics_history.append(metrics)
            if len(self.metrics_history) > self.max_history:
                self.metrics_history.pop(0)
                
            # Salva métricas
            metrics_file = self.metrics_dir / f"metrics_{datetime.now().strftime('%Y%m%d')}.json"
            metrics_data = [m.to_dict() for m in self.metrics_history[-100:]]  # Últimas 100 métricas
            
            with open(metrics_file, "w") as f:
                json.dump(metrics_data, f, indent=2)
                
            return metrics
            
        except Exception as e:
            logger.error(f"Erro ao coletar métricas: {e}")
            raise
            
    def analyze_metrics(self, metrics: SystemMetrics) -> Dict[str, Any]:
        """Analisa métricas e retorna recomendações"""
        try:
            analysis = {
                "status": "healthy" if metrics.is_healthy else "warning",
                "issues": [],
                "recommendations": []
            }
            
            # CPU
            if metrics.cpu_percent > 80:
                analysis["issues"].append("CPU em uso elevado")
                analysis["recommendations"].append("Verificar processos consumindo CPU")
            elif metrics.cpu_percent > 60:
                analysis["recommendations"].append("Monitorar uso de CPU")
                
            # Memória
            if metrics.memory_percent > 80:
                analysis["issues"].append("Uso de memória crítico")
                analysis["recommendations"].append("Liberar memória ou aumentar recursos")
            elif metrics.memory_percent > 60:
                analysis["recommendations"].append("Considerar otimização de memória")
                
            # Disco
            if metrics.disk_percent > 80:
                analysis["issues"].append("Pouco espaço em disco")
                analysis["recommendations"].append("Limpar arquivos ou aumentar espaço")
            elif metrics.disk_percent > 60:
                analysis["recommendations"].append("Planejar limpeza de disco")
                
            return analysis
            
        except Exception as e:
            logger.error(f"Erro na análise de métricas: {e}")
            return {"status": "error", "issues": [str(e)]}
            
    async def check_system_health(self) -> Dict[str, Any]:
        """Verifica saúde do sistema"""
        try:
            # Coleta métricas
            metrics = await self.collect_metrics()
            analysis = self.analyze_metrics(metrics)
            
            # Verifica processos críticos
            critical_processes = ["python", "bot", "eva"]
            missing_processes = []
            
            for proc in critical_processes:
                found = False
                for p in psutil.process_iter(['name']):
                    if proc.lower() in p.info['name'].lower():
                        found = True
                        break
                if not found:
                    missing_processes.append(proc)
                    
            if missing_processes:
                analysis["issues"].append(f"Processos ausentes: {', '.join(missing_processes)}")
                
            # Verifica logs
            log_issues = await self.check_logs()
            if log_issues:
                analysis["issues"].extend(log_issues)
                
            # Verifica backups
            backup_status = await self.check_backups()
            if not backup_status["healthy"]:
                analysis["issues"].extend(backup_status["issues"])
                
            return analysis
            
        except Exception as e:
            logger.error(f"Erro na verificação de saúde: {e}")
            return {"status": "error", "issues": [str(e)]}
            
    async def check_logs(self) -> List[str]:
        """Verifica logs por erros"""
        issues = []
        try:
            for log_file in self.logs_dir.glob("*.log"):
                with open(log_file) as f:
                    for line in f:
                        if "ERROR" in line or "CRITICAL" in line:
                            issues.append(f"Erro em {log_file.name}: {line.strip()}")
            return issues
        except Exception as e:
            logger.error(f"Erro ao verificar logs: {e}")
            return [str(e)]
            
    async def check_backups(self) -> Dict[str, Any]:
        """Verifica estado dos backups"""
        try:
            backups = list(Path("backups").glob("*.tar.gz"))
            latest = max(backups, key=lambda x: x.stat().st_mtime) if backups else None
            
            status = {
                "healthy": True,
                "issues": [],
                "backups": len(backups),
                "latest": str(latest) if latest else None
            }
            
            if not backups:
                status["healthy"] = False
                status["issues"].append("Nenhum backup encontrado")
            elif latest:
                age = (datetime.now() - datetime.fromtimestamp(latest.stat().st_mtime)).total_seconds()
                if age > 86400:  # Mais de 24h
                    status["healthy"] = False
                    status["issues"].append("Último backup muito antigo")
                    
            return status
            
        except Exception as e:
            logger.error(f"Erro ao verificar backups: {e}")
            return {"healthy": False, "issues": [str(e)]}
            
    async def auto_heal(self, issues: List[str]) -> Dict[str, Any]:
        """Tenta resolver problemas automaticamente"""
        results = {
            "actions_taken": [],
            "resolved": [],
            "failed": []
        }
        
        try:
            for issue in issues:
                try:
                    if "CPU em uso elevado" in issue:
                        # Tenta otimizar processos
                        for proc in psutil.process_iter(['cpu_percent', 'name']):
                            if proc.info['cpu_percent'] > 80:
                                proc.nice(10)  # Reduz prioridade
                        results["actions_taken"].append("Ajustada prioridade de processos")
                        results["resolved"].append(issue)
                        
                    elif "Uso de memória crítico" in issue:
                        # Limpa cache
                        subprocess.run(["sync; echo 3 > /proc/sys/vm/drop_caches"], shell=True)
                        results["actions_taken"].append("Cache do sistema limpo")
                        results["resolved"].append(issue)
                        
                    elif "Pouco espaço em disco" in issue:
                        # Otimiza armazenamento
                        if await self.sync_manager.optimize_storage():
                            results["actions_taken"].append("Armazenamento otimizado")
                            results["resolved"].append(issue)
                            
                    elif "Último backup muito antigo" in issue:
                        # Força backup
                        success, _ = await self.sync_manager.create_backup()
                        if success:
                            results["actions_taken"].append("Novo backup criado")
                            results["resolved"].append(issue)
                            
                except Exception as e:
                    logger.error(f"Erro ao resolver {issue}: {e}")
                    results["failed"].append(issue)
                    
            return results
            
        except Exception as e:
            logger.error(f"Erro no auto-heal: {e}")
            return {"error": str(e)}
            
    async def monitor_loop(self):
        """Loop principal de monitoramento"""
        try:
            while self.running:
                try:
                    # Verifica saúde
                    health = await self.check_system_health()
                    
                    # Registra estado
                    logger.info(f"Status do sistema: {health['status']}")
                    if health.get("issues"):
                        logger.warning(f"Problemas encontrados: {health['issues']}")
                        
                        # Tenta resolver
                        heal_results = await self.auto_heal(health["issues"])
                        if heal_results.get("actions_taken"):
                            logger.info(f"Ações tomadas: {heal_results['actions_taken']}")
                        if heal_results.get("failed"):
                            logger.warning(f"Problemas não resolvidos: {heal_results['failed']}")
                            
                    # Verifica necessidade de backup
                    now = datetime.now()
                    if (now - self.last_backup).total_seconds() > self.backup_interval:
                        success, backup_path = await self.sync_manager.create_backup()
                        if success:
                            logger.info(f"Backup automático criado: {backup_path}")
                            self.last_backup = now
                            
                    # Aguarda próxima verificação
                    await asyncio.sleep(self.check_interval)
                    
                except Exception as e:
                    logger.error(f"Erro no loop de monitoramento: {e}")
                    await asyncio.sleep(self.check_interval)
                    
        except Exception as e:
            logger.critical(f"Erro fatal no monitor: {e}")
            raise
            
    async def start(self):
        """Inicia o monitor"""
        try:
            logger.info("Iniciando monitor do sistema...")
            await self.monitor_loop()
        except Exception as e:
            logger.critical(f"Erro ao iniciar monitor: {e}")
            raise
            
    async def stop(self):
        """Para o monitor"""
        try:
            logger.info("Parando monitor do sistema...")
            self.running = False
        except Exception as e:
            logger.error(f"Erro ao parar monitor: {e}")

async def main():
    """Função principal"""
    monitor = SystemMonitor()
    try:
        await monitor.start()
    except KeyboardInterrupt:
        await monitor.stop()
    except Exception as e:
        logger.critical(f"Erro fatal: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())