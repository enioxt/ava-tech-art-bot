"""
Sistema de Internacionalização
Suporte para múltiplos idiomas usando i18n e tradução automática
"""

import i18n
import json
from pathlib import Path
from typing import Dict, Optional
from googletrans import Translator
from rich.console import Console

console = Console()

class TranslationManager:
    def __init__(self):
        self.translator = Translator()
        self.current_lang = "pt"  # Idioma padrão
        self.available_langs = {
            "pt": "Português",
            "en": "English",
            "es": "Español",
            "fr": "Français",
            "ja": "日本語",
            "zh": "中文"
        }
        
        # Configura i18n
        i18n.load_path.append(Path(__file__).parent / "locales")
        i18n.set("fallback", "pt")
        
    def setup(self):
        """Configura o sistema de traduções"""
        # Cria diretório de traduções se não existir
        locales_dir = Path(__file__).parent / "locales"
        locales_dir.mkdir(exist_ok=True)
        
        # Cria arquivos de tradução base se não existirem
        self._ensure_translation_files()
        
    def _ensure_translation_files(self):
        """Garante que os arquivos de tradução existam"""
        base_translations = {
            "system": {
                "welcome": "Bem-vindo ao EVA & GUARANI!",
                "language_changed": "Idioma alterado para {lang}",
                "error": "Ocorreu um erro: {error}",
                "success": "Operação realizada com sucesso!",
                "processing": "Processando...",
                "game": {
                    "start": "Iniciando jogo...",
                    "victory": "Vitória!",
                    "defeat": "Derrota...",
                    "try_again": "Tentar novamente?"
                }
            }
        }
        
        locales_dir = Path(__file__).parent / "locales"
        
        for lang in self.available_langs:
            lang_file = locales_dir / f"{lang}.json"
            if not lang_file.exists():
                # Se o arquivo não existe, traduz do português
                if lang != "pt":
                    translations = self._translate_dict(base_translations, "pt", lang)
                else:
                    translations = base_translations
                    
                # Salva arquivo
                with open(lang_file, "w", encoding="utf-8") as f:
                    json.dump(translations, f, ensure_ascii=False, indent=2)
                    
    def _translate_dict(self, data: Dict, src: str, dest: str) -> Dict:
        """Traduz um dicionário recursivamente"""
        result = {}
        
        for key, value in data.items():
            if isinstance(value, dict):
                result[key] = self._translate_dict(value, src, dest)
            elif isinstance(value, str):
                try:
                    # Traduz string mantendo placeholders
                    translated = self.translator.translate(
                        value,
                        src=src,
                        dest=dest
                    ).text
                    result[key] = translated
                except Exception as e:
                    console.print(f"[red]Erro ao traduzir '{value}': {e}[/red]")
                    result[key] = value
            else:
                result[key] = value
                
        return result
        
    def set_language(self, lang: str) -> bool:
        """Define o idioma atual"""
        if lang not in self.available_langs:
            return False
            
        self.current_lang = lang
        i18n.set("locale", lang)
        return True
        
    def get_text(self, key: str, **kwargs) -> str:
        """Obtém texto traduzido"""
        try:
            return i18n.t(key, **kwargs)
        except Exception as e:
            console.print(f"[red]Erro ao obter tradução para '{key}': {e}[/red]")
            return key
            
    def translate_text(self, text: str, dest: str) -> Optional[str]:
        """Traduz texto para outro idioma"""
        try:
            return self.translator.translate(
                text,
                dest=dest
            ).text
        except Exception as e:
            console.print(f"[red]Erro ao traduzir texto: {e}[/red]")
            return None
            
    def get_available_languages(self) -> Dict[str, str]:
        """Retorna idiomas disponíveis"""
        return self.available_langs

# Instância global do gerenciador
translation_manager = TranslationManager() 