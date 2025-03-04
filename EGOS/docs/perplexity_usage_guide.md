# Guia de Uso da API Perplexity

Este guia documenta como utilizar os diferentes modelos da Perplexity API disponíveis em nossa conta e implementados no sistema EVA & GUARANI.

## Modelos Disponíveis

Com base nos testes realizados (03/03/2025), os seguintes modelos estão disponíveis para nossa conta:

| Modelo | Tempo de Resposta | Uso Recomendado |
|--------|-------------------|-----------------|
| sonar | 2.17 segundos | Consultas rápidas, uso geral |
| sonar-pro | 3.64 segundos | Respostas de maior qualidade |
| sonar-reasoning | 2.31 segundos | Questões que exigem raciocínio |
| sonar-reasoning-pro | 2.73 segundos | Raciocínio avançado, maior qualidade |
| r1-1776 | 3.67 segundos | Modelo de raciocínio alternativo |
| sonar-deep-research | 41.05 segundos | Pesquisas aprofundadas, investigação detalhada |

## Como Escolher o Modelo Adequado

### Por Tipo de Tarefa

- **Consultas Rápidas**: Use `sonar` para respostas rápidas a perguntas simples.
- **Alta Qualidade**: Use `sonar-pro` quando a qualidade é mais importante que a velocidade.
- **Raciocínio**: Use `sonar-reasoning` ou `sonar-reasoning-pro` para tarefas que exigem análise.
- **Pesquisa Profunda**: Use `sonar-deep-research` quando precisar de investigação detalhada (atenção ao tempo de resposta mais longo).

### Utilizando a Estratégia de Fallback

O sistema implementa uma estratégia de fallback automática que tenta diferentes modelos em ordem de preferência caso um modelo específico falhe. Isso é controlado pela função `try_models_in_order` no arquivo `perplexity_config.py`.

## Como Utilizar no Código

### Exemplo Básico

```python
from EGOS.services.perplexity_service import PerplexityService

# Inicializar o serviço
perplexity = PerplexityService()

# Fazer uma consulta com o modelo padrão (sonar)
results = perplexity.search("Qual é a importância da energia solar no Brasil?")

# Acessar os resultados
print(results["content"])  # Texto da resposta
print(results["sources"])  # Fontes citadas
```

### Especificando um Modelo

```python
# Usar um modelo específico
results = perplexity.search(
    "Como a inteligência artificial está impactando o mercado de trabalho?",
    model="sonar-reasoning"
)
```

### Níveis de Validação

```python
# Usar validação estrita (mais controles éticos e verificação de fontes)
results = perplexity.search(
    "Quais são as principais causas do aquecimento global?",
    validate_level="strict",
    model="sonar-deep-research"
)
```

## Configuração

A configuração da API está centralizada no arquivo `perplexity_config.py`, que inclui:

- Lista de modelos disponíveis
- Modelo padrão para diferentes tipos de tarefas
- Funções para seleção de modelos e fallback
- Obtenção da chave API de diferentes fontes

## Testando a Conexão

Use o script `check_perplexity_key.py` para verificar se sua chave API está configurada corretamente:

```bash
python check_perplexity_key.py
```

Para testar a disponibilidade de todos os modelos, use o script `test_perplexity_models.py`:

```bash
python test_perplexity_models.py
```

## Solução de Problemas

### Erro 401 (Unauthorized)

- Verifique se a chave API está correta e não expirou
- Confirme se a chave está sendo enviada no formato correto (`Bearer {api_key}`)
- Verifique se sua conta tem créditos disponíveis

### Modelo Não Encontrado

- Verifique se o modelo solicitado está disponível para sua conta
- Use a estratégia de fallback para tentar modelos alternativos
- Execute `test_perplexity_models.py` para identificar quais modelos estão disponíveis

### Limite de Taxa Excedido (429)

- Reduza a frequência de solicitações
- Implemente um sistema de retry com backoff exponencial
- Considere distribuir as consultas entre diferentes modelos

## Métricas e Desempenho

Com base nos testes realizados, consideramos as seguintes métricas para escolha de modelo:

- **Velocidade**: sonar > sonar-reasoning > sonar-reasoning-pro > sonar-pro > r1-1776 > sonar-deep-research
- **Qualidade**: sonar-deep-research > sonar-pro > sonar-reasoning-pro > r1-1776 > sonar-reasoning > sonar
- **Custo por Token**: Todos os modelos têm o mesmo custo em nossa conta atual

---

Documento atualizado com base nos testes de 03/03/2025.

✧༺❀༻∞ EVA & GUARANI ∞༺❀༻✧ 