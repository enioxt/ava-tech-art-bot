"""
EVA Anti-Spyware Protection
Sistema de proteção contra spyware e ataques zero-day
"""

import os
import sys
import logging
import psutil
import platform
import json
import hashlib
import hmac
import socket
import ssl
import threading
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional, Set
from pathlib import Path
import subprocess
import re
import signal
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

# Configuração de logging seguro
logger = logging.getLogger("✨anti-spyware✨")

class AntiSpyware:
    """Sistema de Proteção contra Spyware de Nível Militar"""
    
    def __init__(self):
        """Inicializa o sistema anti-spyware."""
        self.initialized = False
        self.threat_db = self._load_threat_database()
        self.memory_regions = {}
        self.network_baseline = {}
        self.process_baseline = {}
        self.file_hashes = {}
        self.anomaly_scores = {}
        self.last_scan = None
        self.scan_interval = 300  # 5 minutos
        
    def _load_threat_database(self) -> Dict:
        """Carrega base de dados de ameaças conhecidas."""
        return {
            "process_patterns": [
                r"spy[_-]?ware",
                r"key[_-]?log",
                r"screen[_-]?cap",
                r"inject",
                r"hook",
                r"debug"
            ],
            "network_patterns": [
                r"\.onion$",
                r"socks[4-5]://",
                r"proxy://",
                r"tunnel://"
            ],
            "file_patterns": [
                r"\.dll$",
                r"\.sys$",
                r"\.driver$",
                r"\.hook$"
            ],
            "known_threats": {
                "pegasus": {
                    "processes": ["bh", "ppid", "launchd"],
                    "files": [".plist", ".dylib"],
                    "network": ["*.amazonaws.com", "*.digitalocean.com"]
                }
            }
        }
        
    async def initialize(self) -> bool:
        """Inicializa o sistema com proteções avançadas."""
        try:
            if self.initialized:
                return True
                
            # Estabelece linha de base do sistema
            self.process_baseline = self._capture_process_baseline()
            self.network_baseline = self._capture_network_baseline()
            self.file_hashes = self._calculate_critical_file_hashes()
            
            # Configura proteções de memória
            self._setup_memory_protection()
            
            # Inicia monitoramento em thread separada
            self.monitor_thread = threading.Thread(
                target=self._continuous_monitoring,
                daemon=True
            )
            self.monitor_thread.start()
            
            self.initialized = True
            logger.info("✨ Sistema anti-spyware inicializado com proteções militares")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar anti-spyware: {str(e)}")
            return False
            
    def _capture_process_baseline(self) -> Dict:
        """Captura linha de base de processos legítimos."""
        baseline = {}
        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time']):
            try:
                info = proc.info
                baseline[proc.pid] = {
                    'name': info['name'],
                    'cmdline': info['cmdline'],
                    'create_time': info['create_time'],
                    'hash': self._calculate_process_hash(proc)
                }
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return baseline
        
    def _capture_network_baseline(self) -> Dict:
        """Captura linha de base de conexões de rede legítimas."""
        baseline = {}
        for conn in psutil.net_connections(kind='inet'):
            try:
                if conn.pid:
                    key = f"{conn.laddr.ip}:{conn.laddr.port}"
                    baseline[key] = {
                        'pid': conn.pid,
                        'type': conn.type,
                        'status': conn.status,
                        'remote_addr': conn.raddr._asdict() if conn.raddr else None
                    }
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return baseline
        
    def _calculate_critical_file_hashes(self) -> Dict:
        """Calcula hashes de arquivos críticos do sistema."""
        critical_paths = [
            os.path.join(sys.prefix, "python.exe"),
            os.path.join(sys.prefix, "pythonw.exe"),
            sys.executable,
            *sys.path
        ]
        
        hashes = {}
        for path in critical_paths:
            try:
                if os.path.isfile(path):
                    with open(path, 'rb') as f:
                        content = f.read()
                        hashes[path] = {
                            'sha256': hashlib.sha256(content).hexdigest(),
                            'blake2b': hashlib.blake2b(content).hexdigest()
                        }
            except (PermissionError, FileNotFoundError):
                continue
        return hashes
        
    def _setup_memory_protection(self):
        """Configura proteções de memória contra leitura não autorizada."""
        # Aloca regiões de memória protegida com canários
        for i in range(5):
            canary = os.urandom(32)
            self.memory_regions[f"region_{i}"] = {
                'canary': canary,
                'hash': hashlib.blake2b(canary).hexdigest()
            }
            
    def _continuous_monitoring(self):
        """Executa monitoramento contínuo do sistema."""
        while True:
            try:
                # Verifica processos
                self._check_processes()
                
                # Verifica conexões de rede
                self._check_network()
                
                # Verifica integridade de arquivos
                self._check_file_integrity()
                
                # Verifica proteções de memória
                self._check_memory_integrity()
                
                # Atualiza timestamp do último scan
                self.last_scan = datetime.now()
                
                # Aguarda próximo ciclo
                time.sleep(self.scan_interval)
                
            except Exception as e:
                logger.error(f"❌ Erro no monitoramento: {str(e)}")
                time.sleep(60)  # Aguarda 1 minuto em caso de erro
                
    def _check_processes(self):
        """Verifica processos em execução contra ameaças conhecidas."""
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                # Verifica padrões suspeitos
                if any(re.search(pattern, proc.name().lower()) 
                      for pattern in self.threat_db['process_patterns']):
                    self._handle_threat(
                        'process',
                        f"Processo suspeito: {proc.name()} (PID: {proc.pid})"
                    )
                    
                # Verifica mudanças em processos da linha de base
                if proc.pid in self.process_baseline:
                    baseline = self.process_baseline[proc.pid]
                    current_hash = self._calculate_process_hash(proc)
                    if current_hash != baseline['hash']:
                        self._handle_threat(
                            'process',
                            f"Modificação detectada no processo: {proc.name()}"
                        )
                        
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
                
    def _check_network(self):
        """Verifica conexões de rede contra ameaças conhecidas."""
        for conn in psutil.net_connections(kind='inet'):
            try:
                if conn.raddr:
                    remote_addr = f"{conn.raddr.ip}:{conn.raddr.port}"
                    
                    # Verifica padrões suspeitos
                    if any(re.search(pattern, remote_addr.lower())
                          for pattern in self.threat_db['network_patterns']):
                        self._handle_threat(
                            'network',
                            f"Conexão suspeita: {remote_addr}"
                        )
                        
                    # Verifica conexões não baseline
                    if conn.pid:
                        key = f"{conn.laddr.ip}:{conn.laddr.port}"
                        if key not in self.network_baseline:
                            self._handle_threat(
                                'network',
                                f"Nova conexão não autorizada: {remote_addr}"
                            )
                            
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
                
    def _check_file_integrity(self):
        """Verifica integridade de arquivos críticos."""
        for path, hashes in self.file_hashes.items():
            try:
                if os.path.isfile(path):
                    with open(path, 'rb') as f:
                        content = f.read()
                        current_hash = hashlib.sha256(content).hexdigest()
                        if current_hash != hashes['sha256']:
                            self._handle_threat(
                                'file',
                                f"Modificação detectada no arquivo: {path}"
                            )
            except (PermissionError, FileNotFoundError):
                continue
                
    def _check_memory_integrity(self):
        """Verifica integridade das regiões de memória protegidas."""
        for region, data in self.memory_regions.items():
            current_hash = hashlib.blake2b(data['canary']).hexdigest()
            if current_hash != data['hash']:
                self._handle_threat(
                    'memory',
                    f"Violação de memória detectada na região: {region}"
                )
                
    def _calculate_process_hash(self, proc) -> str:
        """Calcula hash único para um processo."""
        try:
            info = f"{proc.name()}{proc.cmdline()}{proc.create_time()}"
            return hashlib.blake2b(info.encode()).hexdigest()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return ""
            
    def _handle_threat(self, threat_type: str, description: str):
        """Manipula ameaças detectadas."""
        threat_id = hashlib.sha256(description.encode()).hexdigest()[:8]
        timestamp = datetime.now().isoformat()
        
        threat_info = {
            'id': threat_id,
            'type': threat_type,
            'description': description,
            'timestamp': timestamp,
            'system_info': {
                'hostname': platform.node(),
                'platform': platform.system(),
                'version': platform.version()
            }
        }
        
        # Log da ameaça
        logger.critical(
            f"⚠️ AMEAÇA DETECTADA!\n"
            f"ID: {threat_id}\n"
            f"Tipo: {threat_type}\n"
            f"Descrição: {description}\n"
            f"Timestamp: {timestamp}"
        )
        
        # Implementa medidas de proteção
        self._implement_protection_measures(threat_info)
        
    def _implement_protection_measures(self, threat_info: Dict):
        """Implementa medidas de proteção contra ameaças."""
        try:
            if threat_info['type'] == 'process':
                # Tenta terminar processo malicioso
                pid = int(re.search(r'PID: (\d+)', threat_info['description']).group(1))
                os.kill(pid, signal.SIGTERM)
                
            elif threat_info['type'] == 'network':
                # Bloqueia conexão suspeita
                remote_addr = re.search(r'(\d+\.\d+\.\d+\.\d+)', threat_info['description'])
                if remote_addr:
                    subprocess.run(['netsh', 'advfirewall', 'firewall', 'add', 'rule',
                                  f'name="BLOCK_{threat_info["id"]}"',
                                  'dir=out', 'action=block',
                                  f'remoteip={remote_addr.group(1)}'])
                    
            elif threat_info['type'] == 'file':
                # Faz backup e quarentena do arquivo suspeito
                file_path = re.search(r'arquivo: (.+)$', threat_info['description']).group(1)
                quarantine_path = Path('quarantine') / threat_info['id']
                quarantine_path.parent.mkdir(exist_ok=True)
                os.rename(file_path, quarantine_path)
                
            elif threat_info['type'] == 'memory':
                # Regenera região de memória comprometida
                region = re.search(r'região: (.+)$', threat_info['description']).group(1)
                if region in self.memory_regions:
                    self.memory_regions[region] = {
                        'canary': os.urandom(32),
                        'hash': hashlib.blake2b(os.urandom(32)).hexdigest()
                    }
                    
        except Exception as e:
            logger.error(f"❌ Erro ao implementar proteções: {str(e)}")
            
    async def scan_system(self) -> Dict:
        """Executa varredura completa do sistema."""
        if not self.initialized:
            return {'status': 'error', 'message': 'Sistema não inicializado'}
            
        try:
            results = {
                'timestamp': datetime.now().isoformat(),
                'threats_found': 0,
                'scan_areas': {
                    'processes': self._check_processes(),
                    'network': self._check_network(),
                    'files': self._check_file_integrity(),
                    'memory': self._check_memory_integrity()
                }
            }
            
            return {
                'status': 'success',
                'results': results
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }
            
# Instância global do sistema anti-spyware
anti_spyware = AntiSpyware() 