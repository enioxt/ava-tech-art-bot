"""
EVA Static Server
Servidor web seguro para interface gráfica
"""

import os
import sys
import logging
import hashlib
import hmac
import secrets
import base64
from datetime import datetime, timezone
from http.server import HTTPServer, SimpleHTTPRequestHandler
from socketserver import ThreadingMixIn
from urllib.parse import urlparse, parse_qs
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import json
from functools import lru_cache
from typing import Dict, Optional

# Configuração de logging otimizada
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

class SecurityManager:
    def __init__(self):
        self.secret_key = self._generate_key()
        self.fernet = self._setup_encryption()
        self.sessions = {}
        
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
        
    def create_session(self, client_ip: str) -> str:
        """Cria nova sessão segura"""
        session_id = secrets.token_urlsafe(32)
        timestamp = datetime.now(timezone.utc)
        self.sessions[session_id] = {
            'ip': client_ip,
            'created_at': timestamp,
            'last_activity': timestamp
        }
        return session_id
        
    def validate_session(self, session_id: str, client_ip: str) -> bool:
        """Valida sessão existente"""
        if session_id not in self.sessions:
            return False
            
        session = self.sessions[session_id]
        if session['ip'] != client_ip:
            return False
            
        age = datetime.now(timezone.utc) - session['last_activity']
        if age.total_seconds() > 3600:  # 1 hora
            del self.sessions[session_id]
            return False
            
        session['last_activity'] = datetime.now(timezone.utc)
        return True
        
    def secure_headers(self) -> dict:
        """Gera headers de segurança"""
        nonce = secrets.token_hex(16)
        return {
            'Content-Security-Policy': "default-src 'self'; script-src 'self' 'nonce-{nonce}'",
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
            'Referrer-Policy': 'strict-origin-when-cross-origin',
            'Permissions-Policy': 'geolocation=(), microphone=()',
            'Cache-Control': 'no-store, max-age=0'
        }

class OptimizedHandler(SimpleHTTPRequestHandler):
    """Handler otimizado com cache e logging eficiente"""
    
    def __init__(self, *args, **kwargs):
        self.security = SecurityManager()
        super().__init__(*args, directory=os.path.dirname(__file__), **kwargs)
        
    @lru_cache(maxsize=100)
    def get_content_type(self, path: str) -> str:
        """Cache para tipos MIME comuns"""
        ext = os.path.splitext(path)[1]
        return {
            '.html': 'text/html',
            '.css': 'text/css',
            '.js': 'application/javascript',
            '.json': 'application/json',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.svg': 'image/svg+xml',
        }.get(ext, 'text/plain')

    def log_message(self, format: str, *args: str) -> None:
        """Log otimizado"""
        if args[1] not in ['200', '304']:  # Só loga erros e requests não comuns
            logging.info(format%args)

    def do_GET(self) -> None:
        """GET handler otimizado"""
        try:
            # Servir arquivos estáticos de forma eficiente
            file_path = self.translate_path(self.path)
            
            if os.path.isfile(file_path):
                self.send_response(200)
                self.send_header('Content-type', self.get_content_type(file_path))
                self.send_header('Cache-Control', 'max-age=3600')  # Cache por 1h
                self.end_headers()
                
                with open(file_path, 'rb') as f:
                    self.wfile.write(f.read())
            else:
                self.send_error(404, "Arquivo não encontrado")
                
        except Exception as e:
            logging.error(f"Erro ao servir {self.path}: {e}")
            self.send_error(500, "Erro interno do servidor")

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread"""
    daemon_threads = True

def run(port=8000, bind=""):
    """Executa servidor com suporte a múltiplas conexões"""
    server_address = (bind, port)
    httpd = ThreadedHTTPServer(server_address, OptimizedHandler)
    
    # Configurações de segurança do servidor
    httpd.socket.setsockopt(1, 2, 1)  # TCP_NODELAY
    httpd.request_queue_size = 100
    
    logger.info(f"🚀 Servidor iniciado em http://{bind or 'localhost'}:{port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("\n⚡ Servidor encerrado")
        httpd.server_close()
    except Exception as e:
        logger.error(f"Erro crítico: {str(e)}")
        httpd.server_close()
        raise

if __name__ == "__main__":
    if len(sys.argv) > 1:
        run(port=int(sys.argv[1]))
    else:
        run()