"""
EVA System Monitor
Monitoramento em tempo real com interface elegante e segurança aprimorada
"""

import logging
import time
from datetime import datetime, timezone
import psutil
import os
from pathlib import Path
import json
import hmac
import hashlib
import secrets
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from typing import Dict, List
import sys
import threading
import asyncio
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.layout import Layout
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn

console = Console()
layout = Layout()

class SecurityManager:
    def __init__(self):
        self.secret_key = self._generate_key()
        self.fernet = self._setup_encryption()
        self.session_token = secrets.token_urlsafe(32)
        self.last_validation = time.time()
        
    def _generate_key(self):
        """Gera chave segura para operações criptográficas"""
        return base64.urlsafe_b64encode(secrets.token_bytes(32))
        
    def _setup_encryption(self):
        """Configura sistema de encriptação"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=secrets.token_bytes(16),
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.secret_key))
        return Fernet(key)
        
    def secure_timestamp(self):
        """Gera timestamp seguro com assinatura"""
        timestamp = datetime.now(timezone.utc).isoformat()
        nonce = secrets.token_hex(8)
        data = f"{timestamp}:{nonce}"
        signature = hmac.new(
            self.secret_key,
            data.encode(),
            hashlib.sha256
        ).hexdigest()
        return self.fernet.encrypt(f"{data}|{signature}".encode())
        
    def verify_timestamp(self, encrypted_data):
        """Verifica e valida timestamp"""
        try:
            decrypted = self.fernet.decrypt(encrypted_data)
            data, signature = decrypted.decode().split("|")
            timestamp_str, nonce = data.split(":")
            
            # Verifica assinatura
            expected = hmac.new(
                self.secret_key,
                data.encode(),
                hashlib.sha256
            ).hexdigest()
            
            if not hmac.compare_digest(signature, expected):
                return False
                
            # Verifica idade do timestamp
            timestamp = datetime.fromisoformat(timestamp_str)
            age = datetime.now(timezone.utc) - timestamp
            
            return age.total_seconds() <= 300  # 5 minutos
            
        except Exception:
            return False
            
    def validate_session(self):
        """Valida sessão atual"""
        current_time = time.time()
        if current_time - self.last_validation > 300:  # 5 minutos
            self.session_token = secrets.token_urlsafe(32)
            self.last_validation = current_time
        return self.session_token

class StatusBar:
    def __init__(self, security_manager):
        self.start_time = datetime.now(timezone.utc)
        self.last_status = "Iniciando..."
        self.security = security_manager
        self.progress = Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]EVA Core[/]"),
            BarColumn(),
            TextColumn("[bold]{task.percentage:.0f}%"),
            expand=True
        )
        self.task_id = self.progress.add_task("", total=100)
        
    def update(self, status: str, progress: float = None):
        """Atualiza status com validação de segurança"""
        if not self.security.validate_session():
            raise SecurityError("Sessão inválida")
            
        self.last_status = status
        if progress is not None:
            self.progress.update(self.task_id, completed=progress * 100)
        
    def get_uptime(self) -> str:
        """Retorna uptime com timestamp seguro"""
        if not self.security.validate_session():
            raise SecurityError("Sessão inválida")
            
        delta = datetime.now(timezone.utc) - self.start_time
        hours = delta.seconds // 3600
        minutes = (delta.seconds % 3600) // 60
        
        # Adiciona timestamp seguro
        timestamp = self.security.secure_timestamp()
        return f"{hours:02d}:{minutes:02d}:00 [TS:{timestamp.decode()[:32]}...]"

class SystemMonitor:
    def __init__(self):
        self.security = SecurityManager()
        self.status_bar = StatusBar(self.security)
        self.log_path = Path("logs") / f"eva_{datetime.now().strftime('%Y%m%d')}.log"
        self.log_path.parent.mkdir(exist_ok=True)
        
        # Configuração de logging seguro
        self.logger = logging.getLogger("EVA.Monitor")
        self.logger.setLevel(logging.INFO)
        
        # Handler para arquivo com encriptação
        file_handler = EncryptedFileHandler(
            self.log_path,
            self.security.fernet,
            mode='a'
        )
        file_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        )
        self.logger.addHandler(file_handler)
        
    def get_system_stats(self) -> Dict:
        """Coleta estatísticas com validação de segurança"""
        if not self.security.validate_session():
            raise SecurityError("Sessão inválida")
            
        stats = {
            "cpu": psutil.cpu_percent() / 100,
            "memory": psutil.virtual_memory().percent / 100,
            "disk": psutil.disk_usage('/').percent / 100,
            "timestamp": self.security.secure_timestamp()
        }
        
        # Assina os dados
        data_str = f"{stats['cpu']}:{stats['memory']}:{stats['disk']}"
        stats['signature'] = hmac.new(
            self.security.secret_key,
            data_str.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return stats
        
    def generate_status_table(self) -> Table:
        """Gera tabela de status com dados validados"""
        stats = self.get_system_stats()
        if not self.verify_stats(stats):
            raise SecurityError("Dados de status inválidos")
            
        table = Table(show_header=False, expand=True)
        
        table.add_row(
            "CPU",
            self.get_progress_bar(stats["cpu"])
        )
        table.add_row(
            "RAM",
            self.get_progress_bar(stats["memory"])
        )
        table.add_row(
            "Disco",
            self.get_progress_bar(stats["disk"])
        )
        
        return table
        
    def verify_stats(self, stats: Dict) -> bool:
        """Verifica integridade dos dados de status"""
        if 'signature' not in stats:
            return False
            
        data_str = f"{stats['cpu']}:{stats['memory']}:{stats['disk']}"
        expected = hmac.new(
            self.security.secret_key,
            data_str.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(stats['signature'], expected)
        
    def get_progress_bar(self, value: float, width: int = 30) -> str:
        """Gera barra de progresso com valor validado"""
        if not 0 <= value <= 1:
            raise ValueError("Valor inválido para barra de progresso")
            
        filled = int(width * value)
        bar = '█' * filled + '░' * (width - filled)
        color = 'green' if value < 0.7 else 'yellow' if value < 0.9 else 'red'
        return f"[{color}]{bar}[/] {value*100:.1f}%"
        
    def log_event(self, message: str, level: str = "info"):
        """Registra evento com timestamp seguro"""
        timestamp = self.security.secure_timestamp()
        encrypted_message = self.security.fernet.encrypt(message.encode())
        getattr(self.logger, level)(f"{encrypted_message.decode()} [TS:{timestamp.decode()[:32]}...]")
        self.status_bar.update(message)
        
    async def run(self):
        """Executa monitor com verificações de segurança"""
        try:
            with Live(console=console, refresh_per_second=4) as live:
                while True:
                    if not self.security.validate_session():
                        raise SecurityError("Sessão expirada")
                        
                    layout["header"] = Panel(
                        self.status_bar.progress,
                        title="EVA System Monitor",
                        border_style="blue"
                    )
                    
                    try:
                        layout["body"] = Panel(
                            self.generate_status_table(),
                            title="Recursos do Sistema",
                            border_style="green"
                        )
                    except SecurityError as e:
                        self.log_event(f"Erro de segurança: {str(e)}", "error")
                        break
                        
                    live.update(layout)
                    await asyncio.sleep(0.25)
                    
        except KeyboardInterrupt:
            self.log_event("Monitor encerrado pelo usuário", "info")
        except Exception as e:
            self.log_event(f"Erro no monitor: {str(e)}", "error")
            raise

class EncryptedFileHandler(logging.FileHandler):
    """Handler personalizado para logs encriptados"""
    def __init__(self, filename, fernet, mode='a', encoding=None, delay=False):
        super().__init__(filename, mode, encoding, delay)
        self.fernet = fernet
        
    def emit(self, record):
        """Emite log encriptado"""
        try:
            msg = self.format(record)
            encrypted = self.fernet.encrypt(msg.encode())
            stream = self.stream
            stream.write(encrypted.decode() + self.terminator)
            self.flush()
        except Exception:
            self.handleError(record)

class SecurityError(Exception):
    """Exceção para erros de segurança"""
    pass

class OptimizedMonitor:
    def __init__(self):
        self._cache = {}
        self._cache_timeout = 5  # segundos
        self._last_update = 0
        self.setup_logging()
        
    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('monitor.log', mode='a', encoding='utf-8')
            ]
        )
        self.logger = logging.getLogger('EVA.Monitor')

    async def get_system_stats(self) -> Dict:
        current_time = datetime.now().timestamp()
        
        if current_time - self._last_update < self._cache_timeout:
            return self._cache
            
        try:
            stats = {
                'cpu': psutil.cpu_percent(interval=0.1),
                'memory': psutil.virtual_memory().percent,
                'disk': psutil.disk_usage('/').percent,
                'processes': len(psutil.process_iter(['name'])),
                'timestamp': current_time
            }
            self._cache = stats
            self._last_update = current_time
            return stats
        except Exception as e:
            self.logger.error(f"Erro ao coletar estatísticas: {e}")
            return {}

    async def monitor_services(self) -> List[Dict]:
        services = [
            {'name': 'Web Server', 'port': 8000},
            {'name': 'Bot Telegram', 'port': 8443},
            {'name': 'Sistema Ético', 'port': 5000}
        ]
        
        status = []
        for service in services:
            try:
                conn = psutil.net_connections()
                is_running = any(c.laddr.port == service['port'] for c in conn)
                status.append({
                    'name': service['name'],
                    'status': '✅' if is_running else '❌'
                })
            except:
                status.append({
                    'name': service['name'],
                    'status': '❌'
                })
        return status

    def format_status(self, stats: Dict, services: List[Dict]) -> str:
        if not stats:
            return "⚠️ Monitor temporariamente indisponível"
            
        status = "=== EVA System Monitor ===\n"
        status += f"🕒 Uptime: {int(psutil.boot_time())}s\n"
        status += "=== Recursos do Sistema ===\n"
        
        for key in ['cpu', 'memory', 'disk']:
            value = stats.get(key, 0)
            bars = '█' * int(value/5) + '░' * (20 - int(value/5))
            status += f"{key.title()}: [{bars}] {value}%\n"
        
        status += "=== Status dos Serviços ===\n"
        for service in services:
            status += f"{service['name']}: {service['status']}\n"
            
        return status

    async def run(self):
        try:
            while True:
                stats = await self.get_system_stats()
                services = await self.monitor_services()
                status = self.format_status(stats, services)
                print(status)
                await asyncio.sleep(5)
        except Exception as e:
            self.logger.error(f"Erro no monitor: {e}")
            
if __name__ == "__main__":
    monitor = OptimizedMonitor()
    asyncio.run(monitor.run())