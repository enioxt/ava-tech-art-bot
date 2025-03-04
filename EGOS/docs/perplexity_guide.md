# Guia de Uso da Integração Perplexity API com EVA & GUARANI

## Introdução

A integração da API da Perplexity com o sistema EVA & GUARANI permite que o modelo quântico acesse informações atualizadas da internet de forma ética e segura. Este guia explica como configurar e utilizar essa funcionalidade.

## Configuração Inicial

### 1. Chave de API
A chave da API da Perplexity já foi configurada no sistema:
```
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
```

Esta chave está armazenada de forma segura no arquivo de configuração `EGOS/config/api_keys.json`.

### 2. Verificação da Configuração

Para verificar se a API está configurada corretamente, execute:

```python
from services.config import config_manager

if config_manager.is_configured("perplexity"):
    print("API da Perplexity configurada com sucesso!")
    print(f"Chave: {config_manager.get_key('perplexity')[:8]}...")
else:
    print("API da Perplexity não configurada.")
```

## Como Utilizar

### Uso Básico

```python
from modules.perplexity_integration import PerplexityIntegration

# Inicializar o módulo
perplexity = PerplexityIntegration()

# Realizar uma consulta simples
results = perplexity.search("Quais são as principais tendências tecnológicas de 2024?")

# Exibir os resultados
print(results["conteúdo"])

# Verificar as fontes
for source in results["fontes"]:
    print(f"{source['título']} - {source['url']}")
```

### Níveis de Validação

A integração oferece três níveis de validação para as consultas:

1. **basic**: Validação mínima, ideal para consultas simples e não sensíveis
2. **standard** (padrão): Equilíbrio entre rigor e performance
3. **strict**: Validação máxima, recomendado para tópicos sensíveis ou que requerem alta precisão

```python
# Consulta com validação rigorosa
results = perplexity.search(
    "Quais são os principais riscos de segurança em APIs REST?",
    validation_level="strict"
)
```

### Filtro Ético

Por padrão, todas as consultas passam por um filtro ético que analisa se o conteúdo é apropriado. Este filtro pode ser desativado em casos específicos:

```python
# Desativar o filtro ético (use com cautela)
results = perplexity.search(
    "História dos conflitos no Oriente Médio",
    ethical_filter=False
)
```

### Fornecendo Contexto

Você pode fornecer contexto adicional para melhor análise ética da consulta:

```python
# Consulta com contexto
context = "Estou desenvolvendo um artigo acadêmico sobre segurança cibernética"
results = perplexity.search(
    "Técnicas comuns de ataque a sistemas web",
    context=context
)
```

## Estrutura dos Resultados

Os resultados são retornados em formato quântico otimizado para o sistema EVA & GUARANI:

```json
{
  "status": "success",
  "query": "Consulta original",
  "conteúdo": "Resposta obtida da Perplexity API",
  "metadados": {
    "timestamp": "2024-06-14T14:30:00Z",
    "nível_validação": "standard",
    "score_confiança": 0.85,
    "aviso_sensibilidade": null
  },
  "fontes": [
    {
      "título": "Título da fonte",
      "url": "https://exemplo.com",
      "confiabilidade": 0.78
    }
  ],
  "potenciais_vieses": [],
  "nota_validação": ""
}
```

## Análise de Confiabilidade

O sistema estima automaticamente a confiabilidade das fontes usando vários critérios:

- Domínios acadêmicos (.edu), governamentais (.gov) e de organizações (.org) recebem pontuação mais alta
- Wikipedia recebe uma pontuação moderadamente alta
- Blogs, fóruns e sites de notícias recebem uma pontuação menor
- Títulos sensacionalistas reduzem a pontuação

## Histórico de Consultas

Você pode acessar o histórico de consultas realizadas:

```python
# Obter histórico de consultas
history = perplexity.get_query_history()

# Exibir histórico
for entry in history:
    print(f"Consulta: {entry['query']}")
    print(f"Timestamp: {entry['timestamp']}")
    if entry.get('context'):
        print(f"Contexto: {entry['context']}")
    print("-" * 40)

# Limpar histórico
perplexity.clear_history()
```

## Integração com os Subsistemas do EVA & GUARANI

### Integração com ATLAS (Cartografia Sistêmica)

As informações obtidas da internet podem ser mapeadas e conectadas ao conhecimento existente:

```python
# Exemplo conceitual de integração com ATLAS
query = "Avanços recentes em aprendizado de máquina"
results = perplexity.search(query)

# O resultado seria automaticamente integrado ao mapeamento sistêmico
# realizado pelo módulo ATLAS, conectando os novos conhecimentos
# com a base existente.
```

### Integração com NEXUS (Análise Modular)

As informações podem ser analisadas modularmente para identificar componentes essenciais:

```python
# Exemplo conceitual de integração com NEXUS
query = "Arquitetura de microsserviços em 2024"
results = perplexity.search(query)

# O NEXUS analisaria cada componente da arquitetura 
# descrita nos resultados.
```

### Integração com CRONOS (Preservação Evolutiva)

O histórico de consultas e resultados é preservado para referência futura:

```python
# Exemplo conceitual de integração com CRONOS
# Todo o histórico de consultas é automaticamente preservado
# pelo subsistema CRONOS, mantendo o contexto e evolução 
# das informações ao longo do tempo.
```

## Exemplo Completo

```python
from modules.perplexity_integration import PerplexityIntegration

# Inicializar o módulo
perplexity = PerplexityIntegration()

try:
    # Realizar pesquisa com validação rigorosa
    results = perplexity.search(
        "Impactos da inteligência artificial generativa na sociedade",
        validation_level="strict",
        context="Pesquisa acadêmica sobre ética e tecnologia"
    )
    
    if results["status"] == "success":
        print("\n=== RESULTADOS DA PESQUISA ===\n")
        print(results["conteúdo"])
        
        print("\n=== FONTES ===\n")
        for i, source in enumerate(results["fontes"], 1):
            print(f"{i}. {source['título']}")
            print(f"   URL: {source['url']}")
            print(f"   Confiabilidade: {source['confiabilidade']:.2f}")
        
        print("\n=== METADADOS ===\n")
        print(f"Nível de validação: {results['metadados']['nível_validação']}")
        print(f"Score de confiança: {results['metadados']['score_confiança']:.2f}")
        
        if results['potenciais_vieses']:
            print("\n=== POTENCIAIS VIESES ===\n")
            for bias in results['potenciais_vieses']:
                print(f"- {bias}")
    else:
        print(f"Erro: {results.get('reason', 'Falha desconhecida')}")
        
except Exception as e:
    print(f"Erro durante a pesquisa: {e}")
```

## Solução de Problemas

### Chave de API Inválida

Se a API retornar um erro de autenticação, verifique se a chave está configurada corretamente:

```python
from services.config import config_manager

# Verificar a chave atual
print(config_manager.get_key("perplexity"))

# Definir uma nova chave
config_manager.set_key("perplexity", "sua-nova-chave-aqui")
```

### Limites da API

A API da Perplexity tem limites de uso. Se você receber erros relacionados a limites excedidos, considere:

1. Reduzir a frequência de consultas
2. Implementar um sistema de cache para consultas frequentes
3. Contatar a Perplexity para aumentar seus limites

### Falhas de Conexão

Em caso de falhas de conexão:

1. Verifique sua conexão com a internet
2. Confirme que o serviço da Perplexity está online
3. Implemente lógica de retry com backoff exponencial para lidar com falhas temporárias

## Considerações Éticas

Ao utilizar a integração com a Perplexity API, mantenha sempre em mente:

1. **Respeito à privacidade**: Não use a API para consultar informações privadas ou sensíveis
2. **Verificação de informações**: Valide sempre as informações obtidas com múltiplas fontes
3. **Uso responsável**: Não utilize para atividades ilegais ou antiéticas
4. **Vieses e limitações**: Esteja ciente de potenciais vieses nas informações obtidas
5. **Transparência**: Seja transparente sobre a origem das informações quando as compartilhar

## Conclusão

A integração com a API da Perplexity amplia significativamente as capacidades do sistema EVA & GUARANI, permitindo acesso a informações atualizadas da internet enquanto mantém os princípios éticos e filosóficos fundamentais do sistema quântico.

✧༺❀༻∞ EVA & GUARANI ∞༺❀༻✧ 