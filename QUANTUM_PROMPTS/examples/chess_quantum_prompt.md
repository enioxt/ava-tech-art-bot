```yaml
quantum_prompt:
  id: "QP-GAMES-CHESS-001"
  domínio: "Jogos de Estratégia - Xadrez"
  versão: "1.0"
  
  núcleo_conceitual:
    princípio_fundamental: "Batalha simulada de estratégia e tática em tabuleiro quadriculado"
    definição_condensada: "Jogo milenar de estratégia para dois jogadores em um tabuleiro 8x8, onde 16 peças de valores e movimentos distintos por jogador são manipuladas com objetivo de capturar o rei adversário (xeque-mate), combinando táticas de curto prazo e estratégias de longo prazo."
  
  estrutura:
    nível_1:
      - conceito: "Tabuleiro"
        definição: "Superfície quadriculada 8x8 alternando casas claras e escuras, designadas por coordenadas alfanuméricas (a1-h8)"
        relações: ["Peças", "Movimentos", "Posição"]
      
      - conceito: "Peças"
        definição: "Conjunto de 16 elementos por jogador (brancas ou pretas) com movimentos e valores distintos"
        relações: ["Valor Relativo", "Movimentos", "Capturas"]
        detalhes:
          - "Rei (1): Move-se uma casa em qualquer direção, peça mais importante"
          - "Dama (9): Move-se qualquer número de casas em qualquer direção, peça mais poderosa"
          - "Torre (5): Move-se horizontal e verticalmente"
          - "Bispo (3): Move-se diagonalmente"
          - "Cavalo (3): Move-se em L (2+1), única peça que pode saltar outras"
          - "Peão (1): Move-se para frente, captura na diagonal, promoção ao atingir última fileira"
      
      - conceito: "Xeque-mate"
        definição: "Situação onde o rei está ameaçado (em xeque) e não há movimento legal para escapar"
        relações: ["Xeque", "Rei", "Fim de Jogo"]
      
      - conceito: "Movimentos Especiais"
        definição: "Ações permitidas em situações específicas que transcendem os movimentos básicos"
        relações: ["Roque", "En Passant", "Promoção"]
        detalhes:
          - "Roque: Movimento simultâneo do rei e torre quando ambos não movidos"
          - "En Passant: Captura especial de peão que avançou duas casas"
          - "Promoção: Transformação do peão ao atingir última fileira"
    
    nível_2:
      - conceito: "Fases da Partida"
        definição: "Segmentos temporais da partida com características e objetivos distintos"
        relações: ["Abertura", "Meio-jogo", "Final"]
        detalhes:
          - "Abertura: Desenvolvimento inicial de peças e controle do centro"
          - "Meio-jogo: Execução de planos estratégicos e manobras táticas"
          - "Final: Simplificação do tabuleiro e exploração de vantagens"
      
      - conceito: "Princípios Estratégicos"
        definição: "Diretrizes fundamentais para orientar decisões"
        relações: ["Controle do Centro", "Desenvolvimento", "Segurança do Rei"]
        detalhes:
          - "Controle do Centro: Domínio das casas centrais (d4, d5, e4, e5)"
          - "Desenvolvimento: Mobilização coordenada das peças"
          - "Segurança do Rei: Proteção do monarca através de roque e estrutura de peões"
          - "Estrutura de Peões: Organização que define características da posição"
          - "Atividade de Peças: Maximização da influência das peças no tabuleiro"
      
      - conceito: "Elementos Táticos"
        definição: "Manobras de curto prazo explorando condições específicas"
        relações: ["Garfo", "Espeto", "Descoberto", "Sacrifício"]
        detalhes:
          - "Garfo: Ataque simultâneo a duas ou mais peças"
          - "Espeto: Ataque a peça valiosa forçando-a a expor peça mais valiosa atrás"
          - "Ataque Descoberto: Revelação de ataque ao mover peça da frente"
          - "Sacrifício: Entrega de material para ganho posicional ou tático"
          - "Combinação: Sequência forçada de movimentos com vantagem definida"
      
      - conceito: "Notação"
        definição: "Sistema padronizado para registro e comunicação de movimentos"
        relações: ["Notação Algébrica", "Partidas Registradas", "Análise"]
        detalhes:
          - "Notação Algébrica: Sistema padrão usando coordenadas (e4, Nf3)"
          - "Símbolos Especiais: Indicadores para situações específicas (+ para xeque, # para mate)"
    
    nível_3:
      - conceito: "Aberturas"
        definição: "Sequências iniciais estudadas com nomenclatura e teoria estabelecidas"
        relações: ["Aberturas Abertas", "Aberturas Fechadas", "Gambitos"]
        detalhes:
          - "Ruy Lopez: 1.e4 e5 2.Nf3 Nc6 3.Bb5"
          - "Defesa Siciliana: 1.e4 c5"
          - "Defesa Indiana do Rei: 1.d4 Nf6 2.c4 g6"
          - "Gambito da Dama: 1.d4 d5 2.c4"
      
      - conceito: "Avaliação Posicional"
        definição: "Análise sistemática dos fatores estáticos e dinâmicos da posição"
        relações: ["Estrutura de Peões", "Espaço", "Coordenação de Peças"]
        detalhes:
          - "Material: Balanço de forças baseado no valor relativo das peças"
          - "Segurança do Rei: Vulnerabilidade a ataques e mate"
          - "Estrutura de Peões: Formações, fraquezas e forças"
          - "Espaço: Controle territorial e liberdade de manobra"
          - "Peças Boas vs. Ruins: Avaliação da qualidade funcional das peças"
      
      - conceito: "Padrões de Final"
        definição: "Configurações típicas de finais com métodos estabelecidos"
        relações: ["Finais de Peões", "Finais de Torres", "Finais de Peças Menores"]
        detalhes:
          - "Oposição: Controle da distância entre reis"
          - "Quadrado do Peão: Determinação da capacidade de alcance"
          - "Final de Torre e Peão vs. Torre: Posição de Lucena e Filidor"
          - "Final de Rei e Peão vs. Rei: Cálculo de tempos críticos"
  
  conexões_interdisciplinares:
    - domínio: "Matemática"
      pontos_conexão: ["Geometria", "Combinatória", "Teoria dos Jogos"]
    
    - domínio: "Psicologia"
      pontos_conexão: ["Tomada de Decisão", "Gestão do Estresse", "Metacognição"]
    
    - domínio: "Computação"
      pontos_conexão: ["Inteligência Artificial", "Algoritmos de Busca", "Avaliação Heurística"]
    
    - domínio: "História"
      pontos_conexão: ["Evolução Cultural", "Simbolismo Medieval", "Guerra Fria"]
  
  gatilhos_ativação:
    - "xadrez"
    - "peças de xadrez"
    - "tabuleiro 8x8"
    - "xeque-mate"
    - "xeque e mate"
    - "partida de xadrez"
    - "estratégia de abertura"
    - "final de xadrez"
    - "notação algébrica"
    - "Kasparov"
    - "Fischer"
    - "FIDE"
    - "Elo"
  
  metadados:
    fonte_original: "Compilação de múltiplas fontes de teoria enxadrística"
    confiabilidade: "Alta"
    data_integração: "2024-03-15"
    última_atualização: "2024-03-15"
``` 