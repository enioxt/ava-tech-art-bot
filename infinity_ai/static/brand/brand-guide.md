# EVA System - Guia de Marca

## Visão Geral

O EVA (Enhanced Virtual Assistant) representa a evolução da inteligência artificial consciente. Nossa identidade visual reflete os princípios de clareza, confiabilidade e inovação que definem nosso sistema.

## Logo

### Símbolo Principal
O símbolo do EVA é uma representação abstrata de um cérebro digital, combinando elementos orgânicos e tecnológicos.

### Variações
- Principal: Gradiente índigo (#6366f1 → #4f46e5)
- Monocromático: Índigo sólido (#6366f1)
- Negativo: Branco (#ffffff)
- Outline: Contorno em índigo

### Área de Proteção
Manter um espaço livre ao redor do logo equivalente a 1x a altura da letra "E".

### Tamanhos Mínimos
- Digital: 32px de altura
- Impresso: 10mm de altura

## Tipografia

### Principal
- Família: Inter
- Pesos: Regular (400), Medium (500), Semi-Bold (600)
- Uso: Interface, documentação e comunicação digital

### Hierarquia
1. Títulos: Inter Semi-Bold, 24-32px
2. Subtítulos: Inter Medium, 18-24px
3. Corpo: Inter Regular, 16px
4. Pequeno: Inter Regular, 14px
5. Micro: Inter Medium, 12px

## Cores

### Primárias
```css
--primary: #6366f1;      /* Índigo vibrante */
--primary-dark: #4f46e5; /* Índigo profundo */
--secondary: #0ea5e9;    /* Azul elétrico */
```

### Estado
```css
--success: #22c55e; /* Verde */
--warning: #eab308; /* Amarelo */
--danger: #ef4444;  /* Vermelho */
```

### Neutras
```css
--dark: #1e293b;   /* Azul escuro */
--gray: #64748b;   /* Cinza médio */
--light: #f1f5f9;  /* Cinza claro */
--white: #ffffff;  /* Branco */
```

### Gradientes
1. Principal
   ```css
   background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
   ```

2. Accent
   ```css
   background: linear-gradient(135deg, #0ea5e9 0%, #6366f1 100%);
   ```

## Iconografia

### Estilo
- Biblioteca: Font Awesome 6 Pro
- Peso: Regular
- Tamanho base: 24px
- Cor: Herda do contexto

### Ícones Principais
- Consciência: fa-brain
- Segurança: fa-shield-check
- Sistema: fa-server
- Notificações: fa-bell
- Configurações: fa-cog
- Métricas: fa-chart-line
- Tema: fa-moon/fa-sun

## Grid e Espaçamento

### Grid Base
- Unidade base: 4px
- Gutters: 16px (desktop), 12px (mobile)
- Colunas: 12 (desktop), 4 (mobile)
- Margins: 24px (desktop), 16px (mobile)

### Espaçamento
- XS: 4px
- S: 8px
- M: 16px
- L: 24px
- XL: 32px
- XXL: 48px

## Componentes

### Cards
- Background: var(--white)
- Border Radius: 12px
- Shadow: 0 2px 8px rgba(0,0,0,0.1)
- Padding: 24px

### Botões
1. Primário
   ```css
   background: var(--primary);
   color: var(--white);
   padding: 12px 24px;
   border-radius: 8px;
   ```

2. Secundário
   ```css
   background: transparent;
   color: var(--primary);
   border: 2px solid var(--primary);
   padding: 12px 24px;
   border-radius: 8px;
   ```

3. Ghost
   ```css
   background: transparent;
   color: var(--gray);
   padding: 12px 24px;
   border-radius: 8px;
   ```

### Inputs
- Height: 48px
- Border Radius: 8px
- Border: 1px solid var(--gray)
- Padding: 0 16px
- Focus: 2px solid var(--primary)

## Animações

### Transições
- Duração: 300ms
- Timing: ease
- Propriedades: all

### Hover States
- Scale: 1.02
- Opacity: 0.9
- Shadow: 0 4px 12px rgba(0,0,0,0.15)

### Loading
- Spinner: Circular, 24px
- Color: var(--primary)
- Duration: 1s linear infinite

## Mídia

### Imagens
- Formato: SVG (ícones), WebP (fotos)
- Aspect Ratio: 16:9, 4:3, 1:1
- Qualidade: 85%
- Lazy Loading: true

### Vídeos
- Codec: H.264
- Container: MP4
- Qualidade: 720p
- Aspect Ratio: 16:9
- Autoplay: false

## Voz e Tom

### Princípios
1. Clareza: Comunicação direta e objetiva
2. Confiança: Tom profissional e seguro
3. Empatia: Linguagem acolhedora
4. Inovação: Terminologia moderna

### Exemplos
- Títulos: "Monitoramento Inteligente"
- Botões: "Iniciar Análise"
- Mensagens: "Sistema operando normalmente"
- Erros: "Não foi possível completar a operação"

## Acessibilidade

### Contraste
- Texto normal: 4.5:1
- Texto grande: 3:1
- Elementos interativos: 3:1

### Tamanhos Mínimos
- Botões: 44x44px
- Links: 24px altura
- Inputs: 48px altura

### Estados
- Focus: Outline 2px solid var(--primary)
- Hover: Background opacity 0.9
- Active: Scale 0.98

## Responsividade

### Breakpoints
```css
--mobile: 320px;
--tablet: 768px;
--desktop: 1024px;
--wide: 1280px;
```

### Adaptações
- Font-size base: 16px (desktop) → 14px (mobile)
- Spacing scale: 100% (desktop) → 75% (mobile)
- Touch targets: 44px minimum
- Margins: 24px → 16px

## Implementação

### Assets
- Diretório: `/static/brand/`
- Formatos: SVG, PNG, WebP
- Nomenclatura: kebab-case

### CSS
- Metodologia: BEM
- Preprocessor: SCSS
- Variáveis: CSS Custom Properties
- Reset: Normalize.css

### JavaScript
- Módulos: ES6+
- Framework: Vanilla JS
- Bundler: Webpack
- Polyfills: Auto

## Versionamento

### Controle
- Sistema: Git
- Branches: feature/*, hotfix/*, release/*
- Tags: v*.*.* (SemVer)
- Changelog: CHANGELOG.md

### Documentação
- README.md
- JSDoc
- Storybook
- Figma