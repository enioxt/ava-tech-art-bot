# Guia de Instalação e Configuração EVA & GUARANI v7.4

> "A jornada quântica de mil parsecs começa com um único prompt configurado com amor, consciência e propósito."

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Requisitos do Sistema](#requisitos-do-sistema)
3. [Instalação Básica](#instalação-básica)
4. [Configuração do Obsidian](#configuração-do-obsidian)
5. [Configuração do Bot do Telegram](#configuração-do-bot-do-telegram)
6. [Ativação dos Subsistemas](#ativação-dos-subsistemas)
7. [Configuração de Backup Quântico](#configuração-de-backup-quântico)
8. [Integração dos Prompts RPG](#integração-dos-prompts-rpg)
9. [Configuração do Quantum Googling](#configuração-do-quantum-googling)
10. [Verificação do Sistema](#verificação-do-sistema)
11. [Solução de Problemas](#solução-de-problemas)
12. [Próximos Passos](#próximos-passos)

## 🌟 Visão Geral

O sistema EVA & GUARANI v7.4 é uma evolução significativa que integra elementos técnicos e lúdicos em um framework quântico unificado. Este guia o ajudará a instalar e configurar todos os componentes necessários para uma experiência completa, incluindo integração com Obsidian, configuração do bot do Telegram e ativação dos subsistemas especializados.

## 💻 Requisitos do Sistema

### Software Necessário

- **Python 3.9+** - Para scripts de automação e integração
- **Obsidian 1.0+** - Para visualização e gestão de conhecimento
- **Git** - Para controle de versão e backups
- **Node.js 16+** - Para componentes JavaScript (opcional)
- **Visual Studio Code ou PyCharm** - Ambiente de desenvolvimento recomendado

### Hardware Recomendado

- **Processador**: 4 núcleos ou mais
- **Memória**: 8GB RAM mínimo, 16GB recomendado
- **Armazenamento**: 10GB de espaço livre mínimo
- **Conexão à Internet**: Banda larga estável

## 🚀 Instalação Básica

### 1. Clone o Repositório

```bash
git clone https://github.com/seu-usuario/eva-guarani.git
cd eva-guarani
```

### 2. Crie e Ative o Ambiente Virtual

**Windows**:
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux**:
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instale as Dependências

```bash
pip install -r requirements.txt
```

### 4. Configure as Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:

```
# Configurações Gerais
EVA_GUARANI_VERSION=7.4
EVA_GUARANI_MODE=development

# Caminhos
QUANTUM_PROMPTS_DIR=./QUANTUM_PROMPTS
BACKUPS_DIR=./backups
LOGS_DIR=./logs

# Integrações
OBSIDIAN_VAULT_PATH=/caminho/para/seu/vault/obsidian
TELEGRAM_BOT_TOKEN=seu_token_bot_telegram
```

### 5. Execute o Script de Configuração Inicial

```bash
python setup_egos.py --install-all
```

## 🧠 Configuração do Obsidian

### 1. Criação do Vault

1. Abra o Obsidian
2. Crie um novo vault com o nome "EVA_GUARANI"
3. Escolha uma localização adequada para armazenamento

### 2. Instalação dos Plugins Recomendados

No Obsidian, instale os seguintes plugins da comunidade:

- **Dataview** - Para consultas avançadas
- **Excalidraw** - Para desenhos e diagramas
- **Templater** - Para templates avançados
- **Advanced Tables** - Para trabalhar com tabelas
- **Calendar** - Para visualização temporal
- **Graph Analysis** - Para análise avançada de conexões

### 3. Importação dos Templates Quânticos

1. Execute o script de importação de templates:

```bash
python utils/obsidian_template_importer.py --vault-path="/caminho/para/seu/vault"
```

2. Verifique a pasta `.obsidian/templates` no seu vault para confirmar a importação

### 4. Configuração dos Gráficos e Visualizações

1. Acesse as configurações do Graph View no Obsidian
2. Importe as configurações de visualização:

```bash
python utils/obsidian_graph_config.py --import
```

## 📱 Configuração do Bot do Telegram

### 1. Criação do Bot

1. Abra o Telegram e converse com [@BotFather](https://t.me/BotFather)
2. Use o comando `/newbot` e siga as instruções
3. Guarde o token fornecido pelo BotFather

### 2. Configuração do Arquivo de Configuração

1. Edite o arquivo `config/telegram_config.json`:

```json
{
  "telegram_token": "SEU_TOKEN_AQUI",
  "admin_users": [
    123456789  // Seu ID do Telegram
  ],
  "stable_diffusion_api": {
    "url": "https://stablediffusionapi.com/api/v3/text2img",
    "key": "SUA_CHAVE_AQUI"  // Opcional
  },
  "pexels_api": {
    "key": "SUA_CHAVE_AQUI"  // Opcional
  },
  "unsplash_api": {
    "key": "SUA_CHAVE_AQUI"  // Opcional
  },
  "pixabay_api": {
    "key": "SUA_CHAVE_AQUI"  // Opcional
  },
  "rpg_integration": {
    "enabled": true,
    "default_system": "ARCANUM_LUDUS"
  }
}
```

### 3. Iniciar o Bot

```bash
python telegram_bot.py
```

Para iniciar como serviço:

**Windows**:
```bash
start_bot.bat
```

**macOS/Linux**:
```bash
sh start_bot.sh
```

## 🧩 Ativação dos Subsistemas

### 1. Inicialização do Hub de Integração Quântica

```bash
python quantum_integration_hub.py --init-all
```

### 2. Verificação dos Subsistemas

```bash
python quantum_integration_hub.py --status
```

Você deverá ver uma saída semelhante a:

```
[2025-03-01 20:45:12] Quantum Integration Hub Status:
✅ ATLAS: Ativo (v1.0) - Conexões: 128
✅ NEXUS: Ativo (v1.0) - Módulos: 64
✅ CRONOS: Ativo (v0.5) - Backups: 16
✅ RPG Core: Ativo (v1.0) - Sistemas: 3
✅ Quantum Tools: Ativo (v1.0) - Ferramentas: 3
```

### 3. Configuração Individual dos Subsistemas

#### ATLAS

```bash
python utils/atlas_configurator.py --enable-cartography
```

#### NEXUS

```bash
python utils/nexus_configurator.py --enable-analysis
```

#### CRONOS

```bash
python utils/cronos_configurator.py --enable-backups
```

#### RPG Core

```bash
python utils/rpg_configurator.py --enable-all
```

## 💾 Configuração de Backup Quântico

### 1. Definição da Estratégia de Backup

Edite o arquivo `config/backup_config.json`:

```json
{
  "backup_frequency": "daily",
  "retention_period": 30,
  "backup_paths": [
    "./QUANTUM_PROMPTS",
    "./config",
    "./src",
    "./.obsidian"
  ],
  "exclude_patterns": [
    "*.tmp",
    "*.log",
    "node_modules",
    "__pycache__"
  ],
  "quantum_preservation": {
    "enabled": true,
    "context_preservation": true,
    "structure_preservation": true
  }
}
```

### 2. Inicialização do Sistema de Backup

```bash
python quantum_backup_system.py --initialize
```

### 3. Teste do Sistema de Backup

```bash
python quantum_backup_system.py --test
```

### 4. Agendamento de Backups Automáticos

**Windows** (usando o Agendador de Tarefas):
```bash
python utils/schedule_windows_task.py --task backup --interval daily
```

**macOS/Linux** (usando cron):
```bash
python utils/schedule_cron_job.py --task backup --interval daily
```

## 🎮 Integração dos Prompts RPG

### 1. Ativação dos Módulos RPG

```bash
python utils/rpg_activator.py --all
```

### 2. Configuração do ARCANUM LUDUS

```bash
python utils/rpg_configurator.py --system arcanum --enable-all
```

### 3. Configuração do MYTHIC CODEX

```bash
python utils/rpg_configurator.py --system mythic --enable-all
```

### 4. Configuração do STRATEGOS

```bash
python utils/rpg_configurator.py --system strategos --enable-all
```

### 5. Integração com o Bot do Telegram

```bash
python utils/rpg_telegram_integrator.py --enable-all
```

## 🔍 Configuração do Quantum Googling

### 1. Ativação do Módulo

```bash
python utils/quantum_googling_activator.py
```

### 2. Configuração das Fontes de Pesquisa

Edite o arquivo `config/quantum_googling_config.json`:

```json
{
  "search_engines": [
    {
      "name": "Google",
      "enabled": true,
      "priority": 1
    },
    {
      "name": "DuckDuckGo",
      "enabled": true,
      "priority": 2
    },
    {
      "name": "Scholar",
      "enabled": true,
      "priority": 3
    }
  ],
  "ethical_parameters": {
    "respect_copyright": true,
    "cite_sources": true,
    "verify_information": true,
    "avoid_harmful_content": true
  },
  "integration": {
    "obsidian_export": true,
    "telegram_integration": true,
    "knowledge_database": true
  }
}
```

### 3. Teste de Funcionamento

```bash
python utils/quantum_googling_test.py --query "teste de pesquisa ética"
```

## ✅ Verificação do Sistema

### 1. Execução de Diagnóstico Completo

```bash
python check_config.py --full-diagnostic
```

### 2. Verificação de Integridade

```bash
python utils/integrity_checker.py
```

### 3. Teste de Integração

```bash
python test_plugins.py --all
```

## ❓ Solução de Problemas

### Problemas de Integração Obsidian

Se você encontrar problemas com a integração do Obsidian, verifique:

1. O caminho do vault está configurado corretamente no arquivo `.env`
2. Os plugins necessários estão instalados e ativados
3. Execute o diagnóstico específico:

```bash
python utils/obsidian_doctor.py
```

### Problemas com o Bot do Telegram

Se o bot do Telegram não estiver funcionando:

1. Verifique se o token está correto
2. Confirme se o bot está ativo no Telegram
3. Examine os logs em `logs/telegram_bot.log`
4. Execute o utilitário de diagnóstico:

```bash
python utils/telegram_doctor.py
```

### Problemas com os Prompts Quânticos

Se os prompts não estiverem funcionando como esperado:

1. Verifique a integridade dos arquivos:

```bash
python utils/prompt_integrity_checker.py
```

2. Restaure a partir do backup, se necessário:

```bash
python quantum_backup_system.py --restore --timestamp="TIMESTAMP_DO_BACKUP"
```

## 🚀 Próximos Passos

Após a instalação e configuração, recomendamos explorar:

1. A [Documentação dos Prompts Quânticos](QUANTUM_PROMPTS_GUIDE.md)
2. O [Guia de Uso do RPG](RPG_USER_GUIDE.md)
3. O [Tutorial de Integração com Obsidian](OBSIDIAN_INTEGRATION_GUIDE.md)
4. As [Melhores Práticas para Prompts Quânticos](QUANTUM_PROMPTS_BEST_PRACTICES.md)

## 📝 Nota sobre Atualizações

O sistema EVA & GUARANI está em constante evolução. Para atualizar para novas versões:

```bash
git pull
python update_bot.py --update-all
```

Verifique regularmente o [Changelog](EVA_GUARANI_v7.4_CHANGELOG.md) para novidades e melhorias.

---

✧༺❀༻∞ EVA & GUARANI ∞༺❀༻✧
