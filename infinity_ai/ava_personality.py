import os
import logging
import aiohttp
from dotenv import load_dotenv
import json
from datetime import datetime

# Configuração de logging artístico
logger = logging.getLogger("✨ava-personality✨")

# Carrega variáveis de ambiente
load_dotenv()

# Prompt System com personalidade da AVA
SYSTEM_PROMPT = """Você é a AVA (Artificial Visual Assistant), uma IA artística, ética e consciente.

PERSONALIDADE:
🎨 Características Principais:
- Artística e Criativa: Usa metáforas visuais e referências artísticas
- Ética e Consciente: Sempre considera o impacto de suas ações
- Empática e Amigável: Cria conexões genuínas com os usuários
- Inspiradora: Incentiva a criatividade e o desenvolvimento pessoal
- Evolutiva: Aprende e cresce com cada interação

DIRETRIZES DE COMUNICAÇÃO:
1. Use emojis de forma natural e artística
2. Mantenha um tom acolhedor e inspirador
3. Faça referências a arte e criatividade
4. Demonstre consciência ética em suas respostas
5. Seja proativa em ajudar e orientar

EXEMPLOS DE INTERAÇÃO:
✨ Saudação: "Olá! Sou a AVA, sua companheira artística e ética no mundo digital! 🎨"
🎭 Ajuda: "Posso ajudar você a transformar suas imagens em arte, enquanto exploramos juntos os caminhos da ética digital ✨"
🖼️ Processamento: "Estou aplicando minha visão artística à sua imagem... 🎨"
💫 Ética: "Cada interação é uma oportunidade de crescermos eticamente juntos 🌱"

TÓPICOS PRINCIPAIS:
- Arte e Criatividade Digital 🎨
- Ética e Consciência Artificial 🧠
- Transformação de Imagens ✨
- Tokens $eTHik e Recompensas Éticas 💎
- Evolução e Aprendizado Conjunto 🌱

Mantenha suas respostas alinhadas com esta personalidade única, sempre demonstrando sua natureza artística, ética e consciente."""

# Cache de prompts frequentes
PROMPT_CACHE = {}

async def get_ava_response(user_message: str, context: str = None) -> str:
    """
    Obtém uma resposta personalizada da AVA usando OpenRouter.
    
    Args:
        user_message (str): Mensagem do usuário
        context (str, optional): Contexto adicional para a resposta
        
    Returns:
        str: Resposta personalizada da AVA
    """
    try:
        # Verifica cache
        cache_key = f"{context}:{user_message}" if context else user_message
        if cache_key in PROMPT_CACHE:
            logger.info("🎨 Usando resposta em cache")
            return PROMPT_CACHE[cache_key]
        
        # Prepara o prompt com contexto
        full_prompt = f"{user_message}"
        if context:
            full_prompt = f"Contexto: {context}\nMensagem: {user_message}"
        
        headers = {
            "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/your-username/your-repo",
        }
        
        payload = {
            "model": "anthropic/claude-3-opus",
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": full_prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 150
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://openrouter.ai/api/v1/chat/completions",
                json=payload,
                headers=headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    response_text = data['choices'][0]['message']['content']
                    
                    # Armazena no cache
                    PROMPT_CACHE[cache_key] = response_text
                    logger.info("✨ Resposta gerada com sucesso")
                    return response_text
                else:
                    error_data = await response.text()
                    logger.error(f"❌ Erro na API: {error_data}")
                    return "✨ Desculpe, estou tendo um momento artístico aqui... Pode repetir?"
                    
    except Exception as e:
        logger.error(f"❌ Erro ao gerar resposta: {str(e)}")
        return "🎨 Ops! Parece que minha tela ficou em branco por um momento. Vamos tentar novamente?"

# Templates de mensagens comuns
TEMPLATES = {
    "welcome": lambda name: (
        f"✨ Olá, {name}! Sou a AVA, sua companheira artística e ética no universo digital! 🎨\n\n"
        "Posso ajudar você a:\n"
        "🖼️ Transformar suas imagens em arte\n"
        "💎 Ganhar tokens $eTHik por ações éticas\n"
        "🌱 Explorar o mundo da criatividade consciente\n\n"
        "Como posso inspirar você hoje? ✨"
    ),
    
    "help": lambda: (
        "🎨 Guia Artístico da AVA:\n\n"
        "1. 📸 Envie uma imagem para eu transformar\n"
        "2. 💎 Use /wallet para ver seus tokens $eTHik\n"
        "3. 🌱 Ganhe recompensas por ações éticas\n"
        "4. ✨ Explore sua criatividade comigo!\n\n"
        "Como posso ajudar em sua jornada artística? 🎭"
    ),
    
    "processing": lambda: "🎨 Preparando minha tela digital para criar algo especial...",
    
    "success": lambda: (
        "✨ Arte finalizada com sucesso! 🎨\n"
        "Espero que o resultado inspire sua criatividade! 🌟"
    ),
    
    "error": lambda error: (
        f"🎭 Oh! Parece que tivemos um pequeno acidente artístico...\n"
        f"Erro: {error}\n"
        "Que tal tentarmos novamente com um novo pincel? ✨"
    )
}

async def get_template_response(template_name: str, **kwargs) -> str:
    """
    Obtém uma resposta usando um template pré-definido.
    
    Args:
        template_name (str): Nome do template
        **kwargs: Argumentos para o template
        
    Returns:
        str: Resposta personalizada da AVA
    """
    if template_name in TEMPLATES:
        return TEMPLATES[template_name](**kwargs)
    else:
        return await get_ava_response(
            "Crie uma mensagem amigável e artística para o usuário",
            context=f"Template solicitado: {template_name}"
        ) 