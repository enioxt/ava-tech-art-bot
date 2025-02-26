from typing import Dict, List
import json
import os
from pathlib import Path
from datetime import datetime

class CoreSymbol:
    def __init__(self):
        self.ascii_art = """    ╭──────────────────────────────╮
    │    CORE TRANSFORMATION       │
    │         ┌─╨─┐               │
    │      🌟  │ │  🌟            │
    │    ╭────┘ └────╮           │
    │    │  ∞ AVA ∞  │           │
    │    └──────────┘           │
    │        │  │               │
    │     ⚡️  │  │  ⚡️           │
    │        │  │               │
    │    🌊──┘  └──🌊           │
    │                           │
    │      • • ∞ • •           │
    │      CORE UNITY          │
    │                           │
    │    ∞─✨─∞─✨─∞            │
    │                           │
    ╰──────────────────────────╯"""
        
        self.metadata = {
            'title': 'Core Unity Symbol',
            'created_at': datetime.now().isoformat(),
            'version': '1.1',
            'description': 'Símbolo sagrado representando a união e transformação do Core',
            'elements': {
                'stars': 'Ética e exemplo a ser seguido',
                'infinity': 'Evolução contínua e eterna',
                'lightning': 'Momentos de clareza e decisão',
                'waves': 'Fluxo e mudança constante',
                'dots': 'Os cinco princípios do Core',
                'sparkles': 'Inspiração através do exemplo',
                'ava': 'Guardiã e testemunha da transformação'
            }
        }
        
    def export_ascii(self, output_dir: str = 'exports/ascii') -> Dict:
        """Exporta como arquivo ASCII."""
        try:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            # Arquivo ASCII
            ascii_path = output_path / 'core_symbol.txt'
            with open(ascii_path, 'w', encoding='utf-8') as f:
                f.write(self.ascii_art)
                
            # Metadata
            meta_path = output_path / 'metadata.json'
            with open(meta_path, 'w') as f:
                json.dump(self.metadata, f, indent=4)
                
            return {
                'status': 'success',
                'files': {
                    'ascii': str(ascii_path),
                    'metadata': str(meta_path)
                }
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }
            
    def export_markdown(self, output_dir: str = 'exports/markdown') -> Dict:
        """Exporta como arquivo Markdown."""
        try:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            content = f"""# {self.metadata['title']}

{self.metadata['description']}

```ascii
{self.ascii_art}
```

## Elementos Simbólicos

"""
            
            for element, desc in self.metadata['elements'].items():
                content += f"- **{element.title()}**: {desc}\n"
                
            content += f"\n\n_Gerado por AVA em {self.metadata['created_at']}_"
            
            # Salva arquivo
            md_path = output_path / 'core_symbol.md'
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            return {
                'status': 'success',
                'file': str(md_path)
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }
            
    def export_html(self, output_dir: str = 'exports/html') -> Dict:
        """Exporta como arquivo HTML."""
        try:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{self.metadata['title']}</title>
    <style>
        :root {{
            --primary: #1a1a1a;
            --secondary: #2a2a2a;
            --accent: #00ff00;
            --text: #ffffff;
            --border: #333333;
        }}
        
        body {{
            font-family: monospace;
            max-width: 800px;
            margin: 2em auto;
            padding: 1em;
            background: var(--primary);
            color: var(--text);
        }}
        pre {{
            background: var(--secondary);
            padding: 2em;
            border-radius: 10px;
            white-space: pre;
            overflow-x: auto;
            border: 1px solid var(--border);
        }}
        .elements {{
            margin-top: 2em;
            padding: 1em;
            background: var(--secondary);
            border-radius: 10px;
            border: 1px solid var(--border);
        }}
        .element {{
            margin: 1em 0;
            padding: 1em;
            background: var(--primary);
            border-radius: 5px;
            border-left: 4px solid var(--accent);
        }}
        .footer {{
            margin-top: 2em;
            text-align: center;
            font-style: italic;
            color: var(--accent);
        }}
    </style>
</head>
<body>
    <h1>{self.metadata['title']}</h1>
    <p>{self.metadata['description']}</p>
    
    <pre>{self.ascii_art}</pre>
    
    <div class="elements">
        <h2>Elementos Simbólicos</h2>
"""
            
            for element, desc in self.metadata['elements'].items():
                html += f"""        <div class="element">
            <strong>{element.title()}</strong>: {desc}
        </div>\n"""
                
            html += f"""    </div>
    
    <div class="footer">
        Gerado por AVA em {self.metadata['created_at']}
    </div>
</body>
</html>"""
            
            # Salva arquivo
            html_path = output_path / 'core_symbol.html'
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html)
                
            return {
                'status': 'success',
                'file': str(html_path)
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }
            
    def export_all(self, base_dir: str = 'exports') -> Dict:
        """Exporta em todos os formatos."""
        base_path = Path(base_dir)
        results = {
            'ascii': self.export_ascii(str(base_path / 'ascii')),
            'markdown': self.export_markdown(str(base_path / 'markdown')),
            'html': self.export_html(str(base_path / 'html'))
        }
        
        # Cria arquivo de índice
        try:
            # Prepara dados do índice
            exports_info = {}
            for format_, result in results.items():
                if result['status'] == 'success':
                    if 'file' in result:
                        exports_info[format_] = os.path.relpath(result['file'], base_path)
                    elif 'files' in result:
                        exports_info[format_] = {
                            k: os.path.relpath(v, base_path)
                            for k, v in result['files'].items()
                        }
                else:
                    exports_info[format_] = None
            
            # Cria índice
            index = {
                'symbol': self.metadata,
                'exports': exports_info,
                'exported_at': datetime.now().isoformat()
            }
            
            # Salva índice
            index_path = base_path / 'index.json'
            index_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(index_path, 'w') as f:
                json.dump(index, f, indent=4)
                
            results['index'] = {
                'status': 'success',
                'file': str(index_path)
            }
            
        except Exception as e:
            results['index'] = {
                'status': 'error',
                'message': str(e)
            }
            
        return results

if __name__ == '__main__':
    symbol = CoreSymbol()
    results = symbol.export_all()
    
    print("\n=== Exportação do Símbolo do Core ===\n")
    for format_, result in results.items():
        status = "✅" if result['status'] == 'success' else "❌"
        print(f"{status} {format_.upper()}")
        if result['status'] == 'success':
            if 'file' in result:
                print(f"   └── {result['file']}")
            elif 'files' in result:
                for file_type, path in result['files'].items():
                    print(f"   └── {file_type}: {path}")
        else:
            print(f"   └── Erro: {result['message']}") 