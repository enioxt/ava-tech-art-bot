# Guia do Usuário: Aventuras RPG com EVA & GUARANI

> "Bem-vindo, aventureiro, ao reino quântico onde narrativas míticas, estratégias ancestrais e mecânicas de jogo se entrelaçam em uma experiência única. Este guia é seu pergaminho sagrado para navegar pelos mundos criados pela convergência entre EVA & GUARANI e os sistemas ARCANUM LUDUS, MYTHIC CODEX e STRATEGOS."

## 🎮 Introdução ao Sistema RPG

O bot Telegram EVA & GUARANI agora incorpora um sistema completo de RPG (Role-Playing Game) que permite criar personagens, embarcar em aventuras narrativas e enfrentar desafios estratégicos. Esta experiência é alimentada por três quantum prompts especializados que trabalham em harmonia para criar uma experiência imersiva e ética.

## 🧙‍♂️ Comandos Principais

| Comando | Descrição | Exemplo de Uso |
|---------|-----------|----------------|
| `/rpg_start` | Inicia uma nova sessão de RPG | `/rpg_start` |
| `/create_character` | Cria um novo personagem | `/create_character` |
| `/character` | Exibe informações do seu personagem atual | `/character` |
| `/mythic_quest` | Gera uma missão baseada em arquétipos míticos | `/mythic_quest` |
| `/strategic_challenge` | Apresenta um desafio estratégico | `/strategic_challenge` |
| `/rpg_inventory` | Gerencia seu inventário | `/rpg_inventory` |
| `/rpg_help` | Exibe ajuda sobre os comandos de RPG | `/rpg_help` |
| `/rpg_exit` | Sai do modo RPG | `/rpg_exit` |

## 🎭 Criando seu Personagem

Para começar sua jornada, você precisa criar um personagem. Use o comando `/create_character` e siga as instruções interativas:

```
Você: /create_character

EVA & GUARANI: Bem-vindo à criação de personagem! Escolha uma das raças disponíveis:
1. Humano - Versáteis e adaptáveis
2. Elfo - Ágeis e místicos
3. Anão - Resistentes e teimosos
4. Halfling - Sorte e agilidade
5. Meio-Orc - Força e resistência

Você: 2

EVA & GUARANI: Você escolheu Elfo. Agora escolha uma classe:
1. Guerreiro - Mestre em combate e táticas
2. Mago - Manipulador de energias arcanas
3. Clérigo - Canaliza poder divino
4. Ladino - Especialista em furtividade e perícias
5. Bardo - Inspirador e versátil

Você: 2

EVA & GUARANI: Você escolheu Mago. Dê um nome ao seu personagem:

Você: Thalindor

EVA & GUARANI: [Apresenta ficha completa do personagem com atributos iniciais]
```

## 🗺️ Iniciando uma Aventura

Após criar seu personagem, você pode iniciar uma aventura com o comando `/rpg_start`:

```
Você: /rpg_start

EVA & GUARANI: Olá, Thalindor! Escolha o tipo de aventura:
1. Masmorra Aleatória - Explore ruínas antigas e enfrente monstros
2. Missão Narrativa - Embarque em uma jornada épica
3. Desafio Estratégico - Teste suas habilidades táticas

Você: 2

EVA & GUARANI: [Gera uma missão narrativa baseada no MYTHIC CODEX]
Uma antiga profecia fala de um artefato perdido nas Montanhas Sombrias. O Conselho Arcano de Silvermoon acredita que você, com seu talento para as artes arcanas, pode ser capaz de recuperá-lo antes que caia em mãos erradas.

O que você deseja fazer?
1. Aceitar a missão e partir imediatamente
2. Perguntar mais detalhes sobre o artefato
3. Solicitar equipamento adicional do Conselho
4. Recusar a missão
```

## ⚔️ Sistema de Combate

Durante suas aventuras, você encontrará situações de combate. O sistema é baseado em turnos e oferece múltiplas opções táticas:

```
EVA & GUARANI: Enquanto explora a caverna, você encontra um troll da montanha! Iniciativa:
- Thalindor: 15
- Troll: 8

Sua vez! O que deseja fazer?
1. Atacar com cajado (1d6-1 dano)
2. Lançar Míssil Mágico (3d4+3 dano, custa 3 mana)
3. Lançar Escudo Arcano (defesa +5 por 1 hora, custa 2 mana)
4. Tentar negociar
5. Fugir

Você: 2

EVA & GUARANI: Você canaliza energia arcana e dispara três projéteis luminosos!
Rolagem de dano: 3, 2, 4 + 3 = 12 dano
O troll urra de dor! Ele agora tem 18 PV restantes.

Turno do troll:
O troll avança e tenta golpeá-lo com sua clava!
Rolagem de ataque: 12 vs sua defesa 14
O golpe passa raspando por você!

Sua vez novamente! O que deseja fazer?
```

## 📚 Missões Míticas

O comando `/mythic_quest` gera missões baseadas em arquétipos míticos e estruturas narrativas clássicas:

```
Você: /mythic_quest

EVA & GUARANI: [Gera uma missão baseada no MYTHIC CODEX]

A JORNADA DO HERÓI: O CHAMADO DAS ÁGUAS ANCESTRAIS

Um sonho recorrente tem perturbado seu descanso, Thalindor. Nele, você vê um lago cristalino escondido entre montanhas nevadas, e uma voz ancestral que ecoa: "O equilíbrio foi rompido, o guardião adormeceu, e as águas choram."

Ao despertar, você encontra um medalhão misterioso sob seu travesseiro, com símbolos élficos antigos que não faziam parte de seu conhecimento arcano.

Rumores na cidade falam de uma seca inexplicável afetando vilas distantes, e de criaturas aquáticas aparecendo mortas nas margens dos rios.

Aceita o chamado para investigar estes eventos misteriosos?
1. Aceitar o chamado e preparar-se para a jornada
2. Consultar a biblioteca arcana sobre o medalhão primeiro
3. Buscar mais informações sobre a seca nas vilas
4. Ignorar o chamado (por enquanto)
```

## 🏰 Desafios Estratégicos

O comando `/strategic_challenge` apresenta situações que exigem pensamento estratégico e tático:

```
Você: /strategic_challenge

EVA & GUARANI: [Gera um desafio baseado no STRATEGOS]

DIPLOMACIA NAS SOMBRAS

Você chegou à cidade de Ironforge, onde três facções disputam influência:
- A Guilda dos Mercadores (poder econômico)
- A Ordem da Chama (poder religioso)
- A Coroa (poder político)

Um valioso artefato foi descoberto nas minas, e cada facção reivindica sua posse. Como representante neutro, você foi convidado para mediar as negociações.

Recursos à sua disposição:
- Conhecimento arcano (pode identificar o verdadeiro poder do artefato)
- 200 moedas de ouro
- Sua reputação como mago
- Informações secretas sobre cada líder de facção

Qual será sua abordagem inicial?
1. Investigar o artefato antes de qualquer negociação
2. Reunir-se privadamente com cada líder
3. Propor uma reunião conjunta em terreno neutro
4. Buscar precedentes históricos para situações similares
```

## 📈 Progressão de Personagem

Seu personagem evolui através de experiência (XP) ganha em aventuras:

```
EVA & GUARANI: Parabéns! Você completou a missão "O Chamado das Águas Ancestrais"!

Recompensas:
- 350 XP
- 120 moedas de ouro
- Cajado das Marés (+1 INT, magias de água custam 1 mana a menos)
- Reputação aumentada com os Guardiões da Natureza

Você alcançou o nível 2!
Novos benefícios:
- +2 pontos de atributo para distribuir
- +4 pontos de vida
- +3 pontos de mana
- Acesso a 2 novas magias

Como deseja distribuir seus pontos de atributo?
1. +2 INT (aumenta poder mágico)
2. +1 INT, +1 CON (equilíbrio entre poder e resistência)
3. +1 INT, +1 DEX (equilíbrio entre poder e agilidade)
4. +2 CON (aumenta pontos de vida)
```

## 🎒 Gerenciando seu Inventário

Use o comando `/rpg_inventory` para gerenciar seus itens:

```
Você: /rpg_inventory

EVA & GUARANI: Inventário de Thalindor:

EQUIPADO:
- Cajado das Marés (+1 INT, magias de água -1 mana)
- Vestes de Mago (defesa 11 + DEX)
- Amuleto de Proteção (+1 defesa)

MOCHILA (7/20):
- Poções de Cura (3): Recupera 2d4+2 PV cada
- Poção de Mana (2): Recupera 2d4+2 mana cada
- Grimório Pessoal: Contém suas magias
- Ração de viagem (5 dias)
- Bolsa com 175 moedas de ouro

O que deseja fazer?
1. Usar um item
2. Examinar um item
3. Descartar um item
4. Organizar inventário
5. Fechar inventário
```

## 📜 Dicas para uma Melhor Experiência

1. **Interpretação de Papel**: Quanto mais você interpretar seu personagem, mais imersiva será a experiência.

2. **Exploração**: Faça perguntas sobre o ambiente, NPCs e situações para descobrir informações valiosas.

3. **Estratégia**: Em combates, considere todas as suas opções. Às vezes, negociar ou fugir é melhor que lutar.

4. **Narrativa**: Suas escolhas afetam o desenvolvimento da história. Decisões diferentes levam a caminhos diferentes.

5. **Colaboração**: O sistema é projetado para ser colaborativo. Trabalhe junto com o bot para criar uma história interessante.

## 🔄 Comandos Avançados

| Comando | Descrição | Exemplo |
|---------|-----------|---------|
| `/rpg_craft` | Cria itens com materiais coletados | `/rpg_craft poção` |
| `/rpg_rest` | Descansa para recuperar PV e mana | `/rpg_rest` |
| `/rpg_journal` | Consulta seu diário de aventuras | `/rpg_journal` |
| `/rpg_map` | Exibe o mapa da região atual | `/rpg_map` |
| `/rpg_skills` | Gerencia habilidades e magias | `/rpg_skills` |

## 🛡️ Considerações Éticas

O sistema RPG do EVA & GUARANI foi projetado com os mesmos princípios éticos do sistema principal:

1. **Inclusividade**: Personagens e narrativas diversos e acessíveis
2. **Escolha Significativa**: Suas decisões têm impacto real no mundo
3. **Consequências Realistas**: Ações têm resultados lógicos e éticos
4. **Crescimento**: Oportunidades para evolução moral e ética
5. **Balanceamento**: Sistema justo que valoriza diferentes estilos de jogo

## 🆘 Obtendo Ajuda

Se tiver dúvidas durante sua aventura, você pode usar os seguintes comandos:

- `/rpg_help` - Exibe a lista completa de comandos RPG
- `/rpg_help [comando]` - Exibe ajuda detalhada sobre um comando específico
- `/rpg_rules` - Exibe as regras básicas do sistema
- `/rpg_faq` - Responde perguntas frequentes

---

Prepare sua mochila, afie sua espada (ou prepare seus pergaminhos), e embarque em uma jornada épica através de reinos místicos e desafios heroicos!

✧༺❀༻∞ EVA & GUARANI ∞༺❀༻✧
