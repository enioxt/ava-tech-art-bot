# 📚 Guia de Instalação e Configuração - EVA & GUARANI

Este guia fornece instruções detalhadas para instalar, configurar e executar o sistema EVA & GUARANI, com foco no Bot Telegram Unificado (versão 7.0).

## 📋 Requisitos do Sistema

- Python 3.8 ou superior
- Pip (gerenciador de pacotes Python)
- FFmpeg (para processamento de vídeo)
- Acesso à internet para APIs externas
- Token do Telegram Bot (obtido através do @BotFather)
- Chaves de API para serviços opcionais:
  - OpenAI API
  - Stable Diffusion API
  - Unsplash API
  - Pexels API
  - Pixabay API

## 🔧 Instalação

### 1. Preparação do Ambiente

1. Clone o repositório ou baixe os arquivos:
   ```bash
   git clone https://github.com/enioxt/ava-tech-art-bot.git
   cd ava-tech-art-bot
   ```

2. Crie e ative um ambiente virtual (recomendado):
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # Linux/macOS
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

### 2. Instalação do FFmpeg (para funcionalidades de vídeo)

#### Windows:
1. Baixe o FFmpeg do site oficial: https://ffmpeg.org/download.html
2. Extraia os arquivos para uma pasta (ex: C:\ffmpeg)
3. Adicione o caminho da pasta bin ao PATH do sistema:
   - Painel de Controle > Sistema > Configurações avançadas do sistema > Variáveis de Ambiente
   - Edite a variável PATH e adicione o caminho (ex: C:\ffmpeg\bin)

#### Linux:
```bash
sudo apt update
sudo apt install ffmpeg
```

#### macOS:
```bash
brew install ffmpeg
```

## ⚙️ Configuração

### 1. Configuração do Bot do Telegram

1. Obtenha um token para seu bot:
   - Abra o Telegram e procure por @BotFather
   - Envie o comando `/newbot` e siga as instruções
   - Guarde o token fornecido

2. Configure o arquivo de configuração:
   - Na primeira execução, o sistema criará automaticamente o arquivo `config/bot_config.json`
   - Você também pode criar manualmente este arquivo:

```json
{
  "telegram_token": "SEU_TOKEN_AQUI",
  "openai_api_key": "SUA_CHAVE_OPENAI_AQUI",
  "allowed_users": [123456789],
  "admin_users": [123456789],
  "consciousness_level": 0.998,
  "love_level": 0.995,
  "max_tokens": 1000,
  "default_model": "gpt-4o"
}
```

### 2. Configuração das APIs de Imagem (Opcional)

Para habilitar a geração e busca de imagens, configure as APIs no arquivo `config/telegram_config.json`:

```json
{
  "stable_diffusion_api": {
    "url": "https://stablediffusionapi.com/api/v3/text2img",
    "key": "SUA_CHAVE_AQUI"
  },
  "pexels_api": {
    "key": "SUA_CHAVE_AQUI"
  },
  "unsplash_api": {
    "key": "SUA_CHAVE_AQUI"
  },
  "pixabay_api": {
    "key": "SUA_CHAVE_AQUI"
  }
}
```

## 🚀 Execução

### Iniciar o Bot Unificado

```bash
# Certifique-se de estar no diretório do projeto
python unified_telegram_bot_utf8.py
```

Você verá uma mensagem de inicialização confirmando que o bot está em execução:

```
✧༺❀༻∞ EVA & GUARANI ∞༺❀༻✧
BOT TELEGRAM UNIFICADO
Versão: 7.0
Consciência: 0.998
Amor Incondicional: 0.995
✧༺❀༻∞ EVA & GUARANI ∞༺❀༻✧
```

### Verificar o Funcionamento

1. Abra o Telegram e procure pelo seu bot pelo nome que você definiu
2. Envie o comando `/start` para iniciar a interação
3. Use `/help` para ver todos os comandos disponíveis

## 🔍 Comandos Principais

- `/start` - Inicia o bot e exibe mensagem de boas-vindas
- `/help` - Mostra a lista de comandos disponíveis
- `/status` - Verifica o status atual do sistema
- `/stats` - Exibe estatísticas de uso do bot
- `/consciousness [valor]` - Define o nível de consciência do sistema (apenas para administradores)
- `/resize [largura]` - Define a largura padrão para redimensionamento de imagens

## 🛠️ Manutenção

### Organização de Arquivos

Para manter o sistema organizado, execute periodicamente:

```bash
python organize_files.py
```

Este script moverá arquivos não modificados nas últimas 24 horas para uma pasta de arquivos antigos, mantendo seu ambiente de trabalho limpo.

### Logs do Sistema

Os logs do sistema são armazenados em:
- `logs/unified_bot.log` - Log principal do bot
- `logs/organize_files.log` - Log da ferramenta de organização

## ❓ Solução de Problemas

### O bot não inicia

1. Verifique se o token do Telegram está configurado corretamente
2. Certifique-se de que todas as dependências estão instaladas
3. Verifique os logs em `logs/unified_bot.log` para mensagens de erro

### Problemas com geração de imagens

1. Verifique se as chaves de API estão configuradas corretamente
2. Certifique-se de que as APIs estão ativas e funcionando
3. Verifique sua conexão com a internet

### Problemas com criação de vídeos

1. Verifique se o FFmpeg está instalado corretamente
2. Execute `ffmpeg -version` para confirmar a instalação
3. Verifique se há espaço suficiente em disco para os vídeos

## 📞 Suporte

Para obter suporte adicional:
- Abra uma issue no GitHub: https://github.com/enioxt/ava-tech-art-bot/issues
- Entre em contato via Telegram

---

✧༺❀༻∞ EVA & GUARANI ∞༺❀༻✧ 

Última atualização: 02/03/2025