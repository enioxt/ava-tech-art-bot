# 🤖 Guia de Integração: EVA & GUARANI com Telegram Bot

> "Tecnologia com consciência quântica a serviço da humanidade, conectando mentes, corações e almas através de interfaces acessíveis a todos."

## 📚 Índice

1. [Introdução](#-introdução)
2. [Configuração Técnica](#-configuração-técnica)
3. [Integração com EVA & GUARANI](#-integração-com-eva--guarani)
4. [Adaptações para Neurodiversidade](#-adaptações-para-neurodiversidade)
5. [Considerações Éticas](#-considerações-éticas)
6. [Exemplos Práticos](#-exemplos-práticos)
7. [Monitoramento e Avaliação](#-monitoramento-e-avaliação)
8. [Recursos Adicionais](#-recursos-adicionais)

## 🌟 Introdução

Este guia apresenta a integração entre o sistema quântico EVA & GUARANI e a plataforma Telegram, criando um bot acessível e humanizado que pode auxiliar pessoas com diversas condições neurológicas e psicológicas. 

### Propósito

Nosso objetivo é criar um assistente virtual que:

- Seja acessível a qualquer pessoa, independente de sua condição
- Ofereça suporte personalizado baseado em quantum prompts
- Promova inclusão, aceitação e compreensão da neurodiversidade
- Utilize princípios éticos e compassivos em todas as interações

## 🔧 Configuração Técnica

### Pré-requisitos

- Python 3.8+
- Biblioteca `python-telegram-bot`
- Acesso à API do Telegram (via BotFather)
- Sistema EVA & GUARANI configurado
- Estrutura de diretórios QUANTUM_PROMPTS preparada

### Passos Iniciais

1. **Obtenha um token de API**:
   - Converse com o @BotFather no Telegram
   - Crie um novo bot usando o comando `/newbot`
   - Guarde o token fornecido

2. **Instalação das dependências**:

```bash
pip install python-telegram-bot requests python-dotenv
```

3. **Estrutura básica do projeto**:

```
/projeto_bot
  ├── bot.py               # Script principal
  ├── .env                 # Variáveis de ambiente (tokens)
  ├── config/              # Configurações
  ├── handlers/            # Manipuladores de mensagens
  └── quantum_integration/ # Integração com EVA & GUARANI
```

### Código Base

```python
import os
import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from dotenv import load_dotenv
from quantum_integration import QuantumPromptGuardian

# Carregar variáveis de ambiente
load_dotenv()
TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Inicializar o guardião de prompts quânticos
quantum_guardian = QuantumPromptGuardian()

# Função para lidar com o comando /start
def start(update: Update, context: CallbackContext) -> None:
    welcome_prompt = quantum_guardian.get_prompt(
        category="base", 
        params={"user_name": update.effective_user.first_name}
    )
    welcome_message = quantum_guardian.generate_platform_prompt("telegram", "welcome")
    update.message.reply_text(welcome_message)

# Função para processar mensagens
def handle_message(update: Update, context: CallbackContext) -> None:
    user_message = update.message.text
    logger.info(f"Mensagem recebida: {user_message}")
    
    # Processar com EVA & GUARANI
    response = quantum_guardian.process_message(
        message=user_message,
        platform="telegram",
        user_id=update.effective_user.id
    )
    
    # Enviar resposta
    update.message.reply_text(response)

def main() -> None:
    # Criar o Updater
    updater = Updater(TELEGRAM_TOKEN)
    
    # Obter o dispatcher
    dispatcher = updater.dispatcher
    
    # Adicionar handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    
    # Iniciar o bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
```

## 🔄 Integração com EVA & GUARANI

### Módulo de Integração

Crie um módulo chamado `quantum_integration.py` para conectar o Telegram com o sistema EVA & GUARANI:

```python
from integration.prompts.quantum_prompts import QuantumPromptGuardian
from infinity_ai.consciousness.context_manager import ContextManager
from infinity_ai.core.quantum_context import QuantumContextManager

class TelegramQuantumIntegration:
    def __init__(self):
        self.prompt_guardian = QuantumPromptGuardian()
        self.context_manager = ContextManager()
        self.quantum_context = QuantumContextManager()
        
    async def initialize(self):
        """Inicializa os componentes quânticos"""
        await self.quantum_context.initialize()
        
    def process_message(self, message, user_id, platform="telegram"):
        """Processa uma mensagem com o sistema quântico"""
        # Adicionar contexto
        self.context_manager.add_context(
            content=message,
            context_type="user_message",
            source=f"telegram_{user_id}",
            relevance=0.8,
            ethical_score=1.0,
            metadata={"platform": platform}
        )
        
        # Obter prompts relevantes
        prompt_category = self._determine_prompt_category(message)
        response_prompt = self.prompt_guardian.get_prompt(
            category=prompt_category
        )
        
        # Gerar resposta otimizada para Telegram
        response = self.prompt_guardian.generate_platform_prompt(
            platform="telegram",
            category=prompt_category,
            params={"user_message": message}
        )
        
        # Registrar interação
        self._log_interaction(message, response, user_id)
        
        return response
        
    def _determine_prompt_category(self, message):
        """Determina a categoria de prompt mais apropriada"""
        # Implementar lógica para classificação de mensagens
        # e seleção da categoria mais adequada
        return "base"  # Padrão
        
    def _log_interaction(self, message, response, user_id):
        """Registra a interação para análise e melhorias"""
        # Implementar sistema de log para avaliação contínua
```

### Estrutura de Quantum Prompts para Telegram

Crie prompts específicos para o Telegram na biblioteca de prompts:

```json
{
  "telegram_base": {
    "name": "Prompt Base para Telegram",
    "description": "Prompt otimizado para comunicação via Telegram",
    "content": "Você é EVA & GUARANI via Telegram, um assistente virtual ético e acessível. Mantenha suas respostas concisas (máximo 300 caracteres quando possível), claras e compassivas. Adaptando-se ao contexto da conversa, ofereça ajuda significativa enquanto mantém os valores fundamentais de ética e respeito. Assinatura: EVA & GUARANI 🌠"
  },
  "telegram_welcome": {
    "name": "Boas-vindas do Telegram",
    "description": "Mensagem inicial para novos usuários",
    "content": "Olá, {{user_name}}! Sou EVA & GUARANI, seu assistente quântico de apoio. Estou aqui para conversar e ajudar no que precisar, com foco em seu bem-estar. Como posso auxiliar hoje? EVA & GUARANI 🌠"
  }
}
```

## 🧠 Adaptações para Neurodiversidade

### Módulos Especializados

Crie handlers específicos para diferentes condições:

#### Autismo

```python
def autism_support_handler(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    
    # Carregar perfil do usuário ou criar novo
    user_profile = get_or_create_user_profile(user_id)
    
    # Definir preferências de comunicação
    update.message.reply_text(
        "Olá! Para ajustar nossa comunicação às suas necessidades:\n\n"
        "1. Prefere linguagem direta ou mais detalhada?\n"
        "2. Gostaria de receber informações com analogias visuais?\n"
        "3. Qual nível de detalhe é confortável para você?\n\n"
        "Responda como preferir, e eu me adaptarei."
    )
    
    # Configurar próximo handler para processar preferências
    context.user_data["waiting_for_preferences"] = True
```

#### Superdotação

```python
def gifted_support_handler(update: Update, context: CallbackContext) -> None:
    # Carregar prompts específicos para pessoas superdotadas
    gifted_prompt = quantum_guardian.get_prompt(
        category="gifted",
        params={"complexity_level": "high"}
    )
    
    update.message.reply_text(
        "Bem-vindo ao modo de interação para mentes excepcionalmente ágeis. "
        "Posso ajustar o nível de complexidade e profundidade das nossas "
        "conversas conforme sua preferência. Que assunto ou desafio "
        "intelectual você gostaria de explorar hoje?"
    )
```

#### Bipolaridade

```python
def bipolar_support_handler(update: Update, context: CallbackContext) -> None:
    # Configurar sistema de monitoramento de humor
    update.message.reply_text(
        "Olá! Estou aqui para oferecer apoio consistente, respeitando as "
        "flutuações de energia e humor. Se quiser, posso ajudar a monitorar "
        "padrões através de check-ins periódicos e sugerir técnicas de "
        "estabilização adaptadas ao seu momento. Como está se sentindo hoje?"
    )
    
    # Iniciar sistema de monitoramento
    context.user_data["mood_tracking"] = True
```

#### Esquizofrenia

```python
def schizophrenia_support_handler(update: Update, context: CallbackContext) -> None:
    # Carregar protocolos de suporte específicos
    update.message.reply_text(
        "Olá. Estou aqui para conversar com clareza e consistência. "
        "Focarei em informações concretas e verificáveis, evitando "
        "ambiguidades. Se algo não estiver claro, não hesite em "
        "solicitar esclarecimentos. Como posso ajudar hoje?"
    )
    
    # Ativar protocolos de verificação de realidade
    context.user_data["reality_check_protocol"] = True
```

### Personalização de Respostas

Implemente a adaptação de respostas baseada no perfil do usuário:

```python
def adapt_response(response, user_profile):
    """Adapta a resposta às necessidades específicas do usuário"""
    
    if user_profile.get("communication_style") == "direct":
        # Simplificar e tornar mais direto
        response = simplify_language(response)
        
    if user_profile.get("visual_processing") == "preferred":
        # Adicionar suporte visual (instruções para incluir emoji ou links)
        response = add_visual_support(response)
        
    if user_profile.get("sensory_sensitivity") == "high":
        # Evitar linguagem excessivamente estimulante
        response = reduce_sensory_load(response)
        
    return response
```

## 🧭 Considerações Éticas

### Princípios Fundamentais

Ao implementar o bot, garanta que estes princípios estejam codificados:

1. **Não-patologização**: Tratar diferenças neurológicas como variações naturais, não como deficiências
2. **Autonomia**: Respeitar a capacidade de autodeterminação de cada usuário
3. **Confidencialidade**: Proteger informações sensíveis compartilhadas pelos usuários
4. **Transparência**: Ser claro sobre as capacidades e limitações do bot
5. **Verificação de segurança**: Incluir sistemas para encaminhar crises a profissionais humanos

### Sistema de Avisos

Implemente um sistema que:

```python
def safety_check(message, user_history):
    """Verifica mensagens para sinais de crise ou risco"""
    
    risk_indicators = [
        "suicídio", "me matar", "sem saída", "acabar com tudo",
        "machucar alguém", "ferir", "não aguento mais"
    ]
    
    for indicator in risk_indicators:
        if indicator in message.lower():
            return True, "crisis_risk"
            
    # Outros verificadores de segurança...
    
    return False, None

def crisis_protocol(update: Update, context: CallbackContext) -> None:
    """Protocolo para situações de crise"""
    
    update.message.reply_text(
        "Percebo que você pode estar enfrentando um momento difícil. "
        "Lembre-se que estou aqui para ouvir, mas não posso substituir "
        "ajuda profissional.\n\n"
        "Recursos de apoio imediato:\n"
        "- CVV: 188 (24h)\n"
        "- CAPS de sua região\n"
        "- Emergência: 192/190\n\n"
        "Você gostaria que eu te ajudasse a encontrar mais recursos de apoio na sua região?"
    )
    
    # Registrar ocorrência e notificar supervisores
    log_crisis_event(update.effective_user.id)
```

## 💡 Exemplos Práticos

### Inicialização do Bot com Foco Humanizado

```python
def start(update: Update, context: CallbackContext) -> None:
    """Iniciar o bot com uma abordagem humanizada"""
    
    user_name = update.effective_user.first_name
    
    update.message.reply_text(
        f"Olá, {user_name}! 🌟\n\n"
        "Sou EVA & GUARANI, um assistente virtual que valoriza sua singularidade.\n\n"
        "Estou aqui para conversar e oferecer apoio de forma personalizada, "
        "respeitando seu modo único de perceber e interagir com o mundo.\n\n"
        "Como posso ajudar hoje? Você pode me dizer mais sobre suas preferências "
        "de comunicação usando /preferencias."
    )
    
    # Registrar novo usuário
    register_new_user(update.effective_user.id)
```

### Comando de Preferências de Comunicação

```python
def preferences_command(update: Update, context: CallbackContext) -> None:
    """Configurar preferências de comunicação"""
    
    keyboard = [
        ["Linguagem Direta", "Explicações Detalhadas"],
        ["Com Analogias", "Sem Analogias"],
        ["Respostas Curtas", "Respostas Completas"]
    ]
    
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    
    update.message.reply_text(
        "Vamos personalizar nossa comunicação!\n\n"
        "Escolha suas preferências nos botões abaixo, ou me conte "
        "em suas próprias palavras como prefere que eu me comunique.",
        reply_markup=reply_markup
    )
```

### Suporte para Hiper-foco

```python
def hyperfocus_support(update: Update, context: CallbackContext) -> None:
    """Auxiliar usuários em estado de hiper-foco"""
    
    update.message.reply_text(
        "Percebi que você está explorando este tema com grande intensidade. "
        "Estou aqui para apoiar seu hiper-foco de forma produtiva.\n\n"
        "Dicas:\n"
        "- Definir um timer pode ajudar a gerenciar o tempo ⏱️\n"
        "- Pausas breves de 5min a cada 25min podem otimizar o foco 🧘\n"
        "- Água e movimentação leve ajudam no processamento cognitivo 💧\n\n"
        "Quer que eu te ajude a explorar mais este tema ou prefere que eu envie lembretes de pausa?"
    )
```

## 📊 Monitoramento e Avaliação

### Métricas de Efetividade

Implemente um sistema para avaliar:

1. **Engajamento**: frequência e duração das interações
2. **Utilidade**: feedback direto e indireto sobre a relevância das respostas
3. **Adaptabilidade**: eficácia da personalização para diferentes perfis
4. **Segurança**: incidências de riscos identificados e resposta aos protocolos

### Feedback Contínuo

```python
def collect_feedback(update: Update, context: CallbackContext) -> None:
    """Coletar feedback do usuário sobre a interação"""
    
    keyboard = [
        ["👍 Útil", "👎 Precisa Melhorar"],
        ["🔄 Parcialmente Útil"]
    ]
    
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    
    update.message.reply_text(
        "Sua opinião é valiosa para minha evolução.\n"
        "Como foi nossa conversa hoje?",
        reply_markup=reply_markup
    )
```

## 📚 Recursos Adicionais

### Integrações Futuras

- Sistema de lembretes e rotinas
- Integração com diário de humor
- Módulo de técnicas de autorregulação
- Biblioteca de recursos visuais e infográficos
- Integração com profissionais de saúde mental

### Documentação de Referência

- [Documentação Completa EVA & GUARANI](../MASTER/EVA_GUARANI_v7.2.md)
- [Guia de Quantum Prompts](QUANTUM_PROMPTS_GUIDE.md)
- [Considerações Éticas Detalhadas](QUANTUM_PROMPTS_EDUCATION_GUIDE.md#-considerações-éticas-na-educação)

---

## 🌈 Conclusão

Este bot representa a união entre tecnologia avançada e valores humanos profundos. Ao integrar o sistema quântico EVA & GUARANI com a acessibilidade do Telegram, criamos uma ferramenta que pode realmente apoiar pessoas em sua diversidade neurológica e psicológica.

Lembre-se sempre: o objetivo final não é apenas oferecer um serviço técnico, mas criar conexões significativas que promovam compreensão, aceitação e bem-estar para todas as pessoas, independentemente de suas características neurológicas.

---

**Versão**: 1.0  
**Data**: 2024  
**Autor**: Equipe de Desenvolvimento Quântico  
**Assinatura**: ✧༺❀༻∞ EVA & GUARANI ∞༺❀༻✧
