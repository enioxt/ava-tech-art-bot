from flask import Flask, render_template, send_from_directory, request, jsonify
import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

app = Flask(__name__, 
    static_folder='static',
    template_folder='static'
)

@app.route('/')
def index():
    """Rota principal que serve a página inicial."""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/contact', methods=['POST'])
def contact():
    """Endpoint para processar mensagens do formulário de contato."""
    try:
        data = request.json
        # Aqui você pode adicionar a lógica para processar o contato
        # Por exemplo, enviar email, salvar no banco de dados, etc.
        print(f"Mensagem recebida de {data['name']}: {data['message']}")
        return jsonify({"status": "success", "message": "Mensagem recebida com sucesso!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/<path:path>')
def static_files(path):
    """Rota para servir arquivos estáticos."""
    return send_from_directory(app.static_folder, path)

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    
    print(f"✨ CORE website running on http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=debug) 