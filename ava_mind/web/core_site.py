from flask import Flask, render_template, request
from pathlib import Path
import os
import socket
from ..art.core_symbol import CoreSymbol

app = Flask(__name__)

# Configuração
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev')

def get_ip():
    """Obtém o IP da máquina na rede local"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

@app.route('/')
def home():
    """Página inicial do CORE."""
    symbol = CoreSymbol()
    network_url = f"http://{get_ip()}:5000"
    return render_template('home.html', 
                         symbol=symbol.ascii_art,
                         metadata=symbol.metadata,
                         network_url=network_url)

@app.route('/about')
def about():
    """Sobre o CORE."""
    return render_template('about.html')

@app.route('/members')
def members():
    """Membros do CORE."""
    return render_template('members.html')

@app.route('/projects')
def projects():
    """Projetos do CORE."""
    return render_template('projects.html')

def run_server(host='0.0.0.0', port=5000, debug=True):
    """Inicia o servidor."""
    ip = get_ip()
    print(f"\nCORE está rodando em:")
    print(f"- Local: http://localhost:{port}")
    print(f"- Rede: http://{ip}:{port}")
    app.run(host=host, port=port, debug=debug)

if __name__ == '__main__':
    run_server()