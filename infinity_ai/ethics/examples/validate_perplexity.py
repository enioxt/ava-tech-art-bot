import asyncio
from datetime import datetime
from typing import Dict, List, Optional
import platform
import sys
import os
import json
from enum import Enum

from ..source_validator import SourceValidator
from ..perplexity_validator import PerplexityValidator

class Platform(Enum):
    WINDOWS = "windows"
    LINUX = "linux"
    MACOS = "macos"
    ANDROID = "android"
    IOS = "ios"
    WEB = "web"

class ValidationHistory:
    def __init__(self, text: str, score: float, timestamp: datetime):
        self.text = text
        self.score = score
        self.timestamp = timestamp

    def to_dict(self) -> Dict:
        return {
            'text': self.text,
            'score': self.score,
            'timestamp': self.timestamp.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'ValidationHistory':
        return cls(
            text=data['text'],
            score=data['score'],
            timestamp=datetime.fromisoformat(data['timestamp'])
        )

class InteractiveValidator:
    def __init__(self):
        self.source_validator = SourceValidator()
        self.perplexity_validator = PerplexityValidator(self.source_validator)
        self.platform = self._detect_platform()
        self.current_level = 1
        self.max_level = 10
        self.history: List[ValidationHistory] = []
        self.history_file = 'validation_history.json'
        self._load_history()
        
    def _detect_platform(self) -> Platform:
        system = platform.system().lower()
        if system == "windows":
            return Platform.WINDOWS
        elif system == "linux":
            if "ANDROID_ROOT" in os.environ:
                return Platform.ANDROID
            return Platform.LINUX
        elif system == "darwin":
            return Platform.MACOS
        return Platform.WEB

    def _load_history(self) -> None:
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r') as f:
                    data = json.load(f)
                    self.history = [ValidationHistory.from_dict(item) for item in data]
        except Exception as e:
            print(f"Erro ao carregar histórico: {e}")

    def _save_history(self) -> None:
        try:
            with open(self.history_file, 'w') as f:
                json.dump([h.to_dict() for h in self.history], f)
        except Exception as e:
            print(f"Erro ao salvar histórico: {e}")

    async def show_menu(self) -> None:
        self._clear_screen()
        print(f"""
📊 AVA Interactive Validator
{'=' * 40}
Plataforma: {self.platform.value}
Nível: {self.current_level}/{self.max_level}
{'=' * 40}

1. Validar Nova Resposta
2. Ver Histórico de Validações
3. Configurar Nível de Assistência
4. Ajuda
5. Sair

Progress: {'█' * self.current_level}{'░' * (self.max_level - self.current_level)}
""")
        
    def _clear_screen(self) -> None:
        if self.platform == Platform.WINDOWS:
            os.system('cls')
        else:
            os.system('clear')

    async def handle_input(self, choice: str) -> bool:
        if choice == "1":
            await self.validate_new_response()
        elif choice == "2":
            await self.show_history()
        elif choice == "3":
            await self.configure_assistance_level()
        elif choice == "4":
            await self.show_help()
        elif choice == "5":
            return False
        return True

    async def validate_new_response(self) -> None:
        self._clear_screen()
        print("\n=== Nova Validação ===\n")
        
        if self.current_level <= 3:
            print("🔍 Por favor, cole o texto que você deseja validar:")
        else:
            print("🔍 Texto para validação:")
            
        text = input("\n> ")
        
        metadata = {
            'confidence': 0.85,
            'timestamp': datetime.now().isoformat()
        }
        
        score = await self.perplexity_validator.validate_perplexity_response(
            text,
            metadata
        )
        
        # Salvar no histórico
        self.history.append(ValidationHistory(
            text=text,
            score=score.total_score,
            timestamp=datetime.now()
        ))
        self._save_history()
        
        self._show_results(score)
        await self._wait_for_key()

    async def show_history(self) -> None:
        self._clear_screen()
        print("\n=== Histórico de Validações ===\n")
        
        if not self.history:
            print("Nenhuma validação realizada ainda.")
            await self._wait_for_key()
            return
            
        for i, h in enumerate(self.history[-5:], 1):
            print(f"{i}. {h.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
            if self.current_level <= 3:
                print(f"   Texto: {h.text[:50]}...")
                print(f"   Score: {h.score:.2f}/1.0")
            else:
                print(f"   Score: {h.score:.2f}")
            print()
            
        await self._wait_for_key()

    async def configure_assistance_level(self) -> None:
        self._clear_screen()
        print("\n=== Configurar Nível de Assistência ===\n")
        print(f"Nível atual: {self.current_level}")
        print("\nNíveis disponíveis:")
        print("1-3: Iniciante (Explicações detalhadas)")
        print("4-6: Intermediário (Informações resumidas)")
        print("7-8: Avançado (Modo rápido)")
        print("9-10: Expert (Automação máxima)")
        
        try:
            new_level = int(input("\nEscolha o novo nível (1-10): "))
            if 1 <= new_level <= 10:
                self.current_level = new_level
                print(f"\n✅ Nível atualizado para {new_level}")
            else:
                print("\n❌ Nível inválido. Mantendo nível atual.")
        except ValueError:
            print("\n❌ Entrada inválida. Mantendo nível atual.")
            
        await self._wait_for_key()

    async def show_help(self) -> None:
        self._clear_screen()
        print(f"""
=== Ajuda do AVA Interactive Validator ===

🎯 Objetivo:
Validar textos e respostas quanto à sua confiabilidade
e qualidade das fontes citadas.

📝 Comandos:
1. Validar Nova Resposta
   - Cole um texto para análise
   - Receba um score de qualidade

2. Ver Histórico
   - Veja suas últimas validações
   - Acompanhe sua evolução

3. Configurar Nível
   - Ajuste o nível de detalhamento
   - Personalize sua experiência

4. Ajuda
   - Esta tela de ajuda
   
5. Sair
   - Encerra o programa

Nível Atual: {self.current_level}/10
Plataforma: {self.platform.value}
""")
        await self._wait_for_key()

    def _show_results(self, score) -> None:
        if self.current_level <= 3:
            print("\n=== Resultados Detalhados ===")
            print(f"\nPontuação Total: {score.total_score:.2f}/1.0")
            print("\nDetalhes:")
            print(f"- Confiabilidade: {score.confidence_score:.2f}")
            print(f"- Qualidade das Fontes: {score.source_quality_score:.2f}")
        else:
            print(f"\nScore: {score.total_score:.2f} | Conf: {score.confidence_score:.2f} | Qual: {score.source_quality_score:.2f}")

    async def _wait_for_key(self) -> None:
        if self.current_level <= 5:
            input("\nPressione ENTER para continuar...")
        else:
            await asyncio.sleep(2)

async def main():
    validator = InteractiveValidator()
    running = True
    
    while running:
        await validator.show_menu()
        choice = input("\nEscolha uma opção (1-5): ")
        running = await validator.handle_input(choice)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nEncerrando AVA Interactive Validator...")
        sys.exit(0)