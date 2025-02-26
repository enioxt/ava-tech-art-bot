"""
🎮 EVA & GUARANI - Game Manager
Sistema de gerenciamento de jogos para Telegram
"""

import random
from typing import Dict, Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from .mini_games import MiniGames, GameReward

class GameManager:
    def __init__(self):
        self.mini_games = MiniGames()
        self.active_games: Dict[int, str] = {}
        self.scores: Dict[int, int] = {}
        
    def get_game_menu(self) -> InlineKeyboardMarkup:
        """Menu de jogos estilo arcade"""
        keyboard = [
            [
                InlineKeyboardButton("🗡️ Enigma de Zelda", callback_data="game_riddle"),
                InlineKeyboardButton("⏰ Memória Chrono", callback_data="game_memory")
            ],
            [
                InlineKeyboardButton("🎵 Padrões Portal", callback_data="game_pattern"),
                InlineKeyboardButton("❓ Quiz Final Fantasy", callback_data="game_quiz")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
        
    async def handle_game_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Manipula callbacks dos jogos"""
        query = update.callback_query
        await query.answer()
        
        if not query.data.startswith("game_"):
            return
            
        game_type = query.data.replace("game_", "")
        user_id = update.effective_user.id
        
        # Inicia o jogo
        self.active_games[user_id] = game_type
        await self._start_game(update, context, game_type)
        
    async def _start_game(self, update: Update, context: ContextTypes.DEFAULT_TYPE, game_type: str) -> None:
        """Inicia um mini-game"""
        intros = {
            "riddle": "🏰 Bem-vindo ao Templo do Tempo!\nResolva o enigma para provar seu valor...",
            "memory": "⚔️ O Julgamento do Tempo começou!\nMostre sua memória digna de um herói...",
            "pattern": "🧩 Os padrões do Portal se revelam!\nDecore a sequência para avançar...",
            "quiz": "📚 O Grimório dos Games se abre!\nProve seu conhecimento ancestral..."
        }
        
        await update.effective_message.reply_text(intros.get(game_type, "Que comecem os jogos!"))
        
        # Inicia o jogo
        reward = await self.mini_games.play_game(game_type)
        
        if reward:
            await self._handle_victory(update, context, reward)
        else:
            await self._handle_defeat(update, context)
            
    async def _handle_victory(self, update: Update, context: ContextTypes.DEFAULT_TYPE, reward: GameReward) -> None:
        """Celebra vitória estilo Final Fantasy"""
        victory_text = (
            f"🎉 VITÓRIA! 🎉\n\n"
            f"XP: +{reward.xp}\n"
            f"Item: {reward.item} ({reward.rarity})\n"
            f"Descrição: {reward.description}\n\n"
            f"Como diria Kratos: 'Os deuses do Olimpo te abandonaram, agora sua vitória está completa!'"
        )
        
        user_id = update.effective_user.id
        self.scores[user_id] = self.scores.get(user_id, 0) + reward.xp
        
        await update.effective_message.reply_text(victory_text)
        await self._show_play_again(update, context)
        
    async def _handle_defeat(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Mensagem de derrota estilo Dark Souls"""
        defeat_texts = [
            "💀 YOU DIED 💀\nComo diria Solaire: 'O sol brilhará novamente!'",
            "❌ GAME OVER ❌\nLembra do Mario: 'Wahoo! Try again!'",
            "😢 DERROTA 😢\nComo diz o Yasuo: 'A morte é como o vento...'",
            "💔 FALHOU 💔\nMas como diz Minecraft: 'Respawn?'"
        ]
        
        await update.effective_message.reply_text(random.choice(defeat_texts))
        await self._show_play_again(update, context)
        
    async def _show_play_again(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Oferece jogar novamente"""
        keyboard = [
            [
                InlineKeyboardButton("🔄 Jogar Novamente", callback_data="game_again"),
                InlineKeyboardButton("🎮 Outros Jogos", callback_data="game_menu")
            ]
        ]
        await update.effective_message.reply_text(
            "O que deseja fazer?",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

# Exemplo de uso no bot:
"""
game_manager = GameManager()

async def games_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎮 Escolha seu mini-game:",
        reply_markup=game_manager.get_game_menu()
    )
""" 