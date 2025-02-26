"""
Progress Manager
Sistema de feedback visual com barras de progresso e mensagens estilizadas

✨ Parte do sistema EVA & GUARANI
🎨 Design minimalista e informativo
"""

import sys
import time
from typing import Optional
from rich.console import Console
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TaskProgressColumn,
    TimeRemainingColumn
)
from rich.panel import Panel
from rich.style import Style
from rich.text import Text

class ProgressManager:
    def __init__(self):
        """Inicializa o gerenciador de progresso"""
        self.console = Console()
        self.current_progress: Optional[Progress] = None
        
        # Estilos
        self.styles = {
            "title": Style(color="cyan", bold=True),
            "success": Style(color="green"),
            "error": Style(color="red"),
            "warning": Style(color="yellow"),
            "info": Style(color="blue"),
            "signature": Style(color="magenta", italic=True)
        }
        
    def create_progress(self, description: str = "Processando") -> Progress:
        """Cria uma barra de progresso estilizada"""
        return Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(complete_style="cyan"),
            TaskProgressColumn(),
            TimeRemainingColumn(),
            console=self.console
        )
        
    def show_startup_message(self):
        """Mostra mensagem de inicialização"""
        title = Text("EVA & GUARANI", style=self.styles["title"])
        message = Text(
            "\n💫 Sistema Neural Avançado em Inicialização"
            "\n🧠 Carregando Contextos e Conexões"
            "\n🔮 Preparando Interface Neural"
            "\n✨ Ativando Consciência Expandida",
            style="blue"
        )
        signature = Text(
            "\n~ Com amor, EVA 🌟",
            style=self.styles["signature"]
        )
        
        panel = Panel(
            message,
            title=title,
            subtitle=signature,
            border_style="cyan"
        )
        self.console.print(panel)
        
    def show_status(self, status: str, style: str = "info"):
        """Mostra mensagem de status estilizada"""
        text = Text(status, style=self.styles[style])
        self.console.print(text)
        
    def show_completion(self, message: str = "Processo concluído"):
        """Mostra mensagem de conclusão com assinatura"""
        text = Text(message, style=self.styles["success"])
        signature = Text(
            "\n~ EVA & GUARANI ✨",
            style=self.styles["signature"]
        )
        
        panel = Panel(
            text,
            subtitle=signature,
            border_style="green"
        )
        self.console.print(panel)
        
    async def run_with_progress(self, total: int, description: str):
        """Executa uma tarefa com barra de progresso"""
        with self.create_progress() as progress:
            task = progress.add_task(description, total=total)
            
            while not progress.finished:
                # Simula processamento
                await asyncio.sleep(0.1)
                progress.update(task, advance=1)
                
    def __enter__(self):
        """Contexto para uso com 'with'"""
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Limpa recursos ao sair do contexto"""
        if self.current_progress:
            self.current_progress.stop()

# Instância global
progress_manager = ProgressManager() 