"""
🎮 EVA & GUARANI - Sistema de Mini-Games
Inspirado em clássicos dos videogames
"""

import random
import asyncio
from typing import Dict, List, Optional
from dataclasses import dataclass
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress

console = Console()

@dataclass
class GameReward:
    xp: int
    item: str
    description: str
    rarity: str  # Common, Rare, Epic, Legendary

class MiniGames:
    def __init__(self):
        self.games = {
            "riddle": self._zelda_style_riddle,
            "memory": self._chrono_trigger_memory,
            "pattern": self._simon_says_pattern,
            "quiz": self._final_fantasy_quiz
        }
        
        # Inspirado no sistema de conquistas do Steam
        self.achievements = {
            "first_win": {"name": "Primeira Vitória", "description": "Como ganhar seu primeiro Blue Buff no LoL"},
            "perfect_score": {"name": "Pontuação Perfeita", "description": "Tipo aquele Perfect no Street Fighter"},
            "speed_runner": {"name": "Speed Runner", "description": "Mais rápido que o Sonic!"},
            "puzzle_master": {"name": "Mestre dos Puzzles", "description": "Resolveu como o Link em Ocarina of Time"}
        }
        
    async def _zelda_style_riddle(self) -> bool:
        """
        Puzzle inspirado nas dungeons de Zelda
        Exemplo: Temple of Time de Ocarina of Time
        """
        riddles = [
            {
                "question": "Sou eterno mas sempre mudo, \nTodos me seguem mas ninguém me alcança. \nO que sou eu?",
                "answer": "tempo",
                "hint": "Link viaja através de mim em Ocarina of Time"
            },
            {
                "question": "Quanto mais você tira, \nMaior eu fico. \nO que sou eu?",
                "answer": "buraco",
                "hint": "Como os buracos que você cava em Minecraft"
            }
        ]
        
        riddle = random.choice(riddles)
        console.print(Panel(
            f"[cyan]🗡️ Enigma do Templo[/cyan]\n\n{riddle['question']}\n",
            title="[gold1]Desafio de Zelda[/gold1]"
        ))
        
        return await self._handle_answer(riddle)
        
    async def _chrono_trigger_memory(self) -> bool:
        """
        Jogo de memória inspirado nas sequências de Chrono Trigger
        Como a famosa sequência do julgamento
        """
        sequence = [
            "🗡️", "🛡️", "💎", "🔮"
        ]
        player_sequence = []
        
        console.print("\n[cyan]⏰ Desafio da Memória do Tempo[/cyan]")
        console.print("Memorize a sequência:")
        
        # Mostra sequência
        for item in sequence:
            console.print(item, end=" ")
            await asyncio.sleep(1)
            console.print("\r" + " " * 50 + "\r", end="")
            await asyncio.sleep(0.5)
            
        return await self._check_sequence(sequence)
        
    async def _simon_says_pattern(self) -> bool:
        """
        Padrões tipo Simon Says
        Inspirado nos puzzles de Portal e padrões de boss fights
        """
        patterns = [
            "⬆️ ⬆️ ⬇️ ⬇️ ⬅️ ➡️",  # Konami Code!
            "🔵 🔴 🔵 🔴 🟡",      # Padrão tipo Among Us
            "⚔️ 🛡️ ⚔️ 🔮"          # Combo de RPG
        ]
        
        pattern = random.choice(patterns)
        console.print(Panel(
            f"[cyan]Memorize o padrão:[/cyan]\n\n{pattern}",
            title="[gold1]Desafio de Padrões[/gold1]"
        ))
        
        await asyncio.sleep(3)
        console.clear()
        return await self._verify_pattern(pattern)
        
    async def _final_fantasy_quiz(self) -> bool:
        """
        Quiz de conhecimentos gerais estilo RPG
        Com referências a vários jogos
        """
        questions = [
            {
                "question": "Qual é o nome do protagonista de FF7?",
                "answer": "cloud",
                "hint": "Ex-SOLDIER de cabelo espetado"
            },
            {
                "question": "Qual campeão de LoL diz: 'A morte é como o vento, está sempre ao meu lado'?",
                "answer": "yasuo",
                "hint": "Samurai com windwall"
            },
            {
                "question": "Em Diablo, qual classe usa magia arcana?",
                "answer": "mago",
                "hint": "Especialista em elementos"
            }
        ]
        
        question = random.choice(questions)
        console.print(Panel(
            f"[cyan]❓ Quiz dos Games[/cyan]\n\n{question['question']}\n",
            title="[gold1]Desafio Final Fantasy[/gold1]"
        ))
        
        return await self._handle_answer(question)
        
    async def _handle_answer(self, challenge: Dict) -> bool:
        """Sistema de dicas inspirado em Persona 5"""
        attempts = 3
        while attempts > 0:
            answer = input("\nSua resposta: ").lower().strip()
            
            if answer == challenge['answer']:
                console.print("[green]✨ Correto! Você é um verdadeiro herói![/green]")
                return True
                
            attempts -= 1
            if attempts > 0:
                console.print(f"[yellow]❌ Tente novamente! Dica: {challenge['hint']}[/yellow]")
                console.print(f"Tentativas restantes: {attempts}")
            else:
                console.print("[red]❌ Game Over! Tente novamente depois de treinar mais![/red]")
                
        return False
        
    async def _check_sequence(self, correct: List) -> bool:
        """Verificação de sequência estilo Guitar Hero"""
        try:
            console.print("\nRepita a sequência (use os emojis):")
            sequence = input().split()
            return sequence == correct
        except Exception:
            return False
            
    async def _verify_pattern(self, pattern: str) -> bool:
        """Verificação de padrão estilo DDR"""
        try:
            console.print("\nRepita o padrão:")
            user_pattern = input()
            return user_pattern.strip() == pattern.strip()
        except Exception:
            return False
            
    def get_reward(self, game_type: str, score: int) -> GameReward:
        """Sistema de recompensas inspirado em MMORPGs"""
        rewards = {
            "riddle": GameReward(
                xp=100,
                item="📜 Pergaminho da Sabedoria",
                description="Como os pergaminhos de Diablo",
                rarity="Rare"
            ),
            "memory": GameReward(
                xp=150,
                item="⏰ Relógio do Tempo",
                description="Tipo o relógio de Majora's Mask",
                rarity="Epic"
            ),
            "pattern": GameReward(
                xp=80,
                item="🎵 Nota Musical",
                description="Lembra as notas de Ocarina of Time",
                rarity="Common"
            ),
            "quiz": GameReward(
                xp=200,
                item="📚 Tomo do Conhecimento",
                description="Como os tomos de Skyrim",
                rarity="Legendary"
            )
        }
        
        return rewards.get(game_type)
        
    async def play_game(self, game_type: str) -> Optional[GameReward]:
        """
        Interface principal dos mini-games
        Com loading screens estilo Dark Souls
        """
        loading_tips = [
            "Dica: Em Dark Souls, a morte é apenas o começo...",
            "Dica: Em LoL, farm > kills no early game!",
            "Dica: O bolo é uma mentira (Portal reference)",
            "Dica: WOLOLO pode converter unidades (Age of Empires)",
            "Dica: Zerg Rush é uma estratégia válida (StarCraft)"
        ]
        
        # Loading screen
        with Progress() as progress:
            task = progress.add_task(
                random.choice(loading_tips),
                total=100
            )
            while not progress.finished:
                progress.update(task, advance=1)
                await asyncio.sleep(0.02)
                
        if game_type not in self.games:
            console.print("[red]❌ Mini-game não encontrado![/red]")
            return None
            
        # Executa o mini-game
        success = await self.games[game_type]()
        
        if success:
            reward = self.get_reward(game_type, 100)
            console.print(Panel(
                f"[green]🎁 Recompensa:[/green]\n"
                f"XP: {reward.xp}\n"
                f"Item: {reward.item} ({reward.rarity})\n"
                f"Descrição: {reward.description}",
                title="[gold1]Tesouro Obtido![/gold1]"
            ))
            return reward
            
        return None

# Exemplo de uso:
if __name__ == "__main__":
    games = MiniGames()
    asyncio.run(games.play_game("riddle"))