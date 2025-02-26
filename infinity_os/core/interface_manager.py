"""
Interface Manager
Sistema de interface com feedback visual e assinatura EVA
"""

import sys
import time
from typing import Optional
from datetime import datetime
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.panel import Panel
from rich.style import Style
from rich.text import Text

class InterfaceManager:
    def __init__(self):
        """Inicializa o gerenciador de interface"""
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
        
    def show_eva_signature(self):
        """Mostra a assinatura EVA"""
        signature = Text(
            "\n~ Com amor, EVA ✨\n"
            f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]",
            style=self.styles["signature"]
        )
        self.console.print(signature)
        
    def create_progress(self, description: str = "Processando") -> Progress:
        """Cria uma barra de progresso estilizada"""
        return Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(complete_style="cyan"),
            TaskProgressColumn(),
            console=self.console
        )
        
    def show_status(self, message: str, style: str = "info"):
        """Mostra mensagem de status com assinatura"""
        text = Text(message, style=self.styles[style])
        panel = Panel(
            text,
            border_style=style
        )
        self.console.print(panel)
        self.show_eva_signature()
        
    def show_error(self, error: str):
        """Mostra mensagem de erro com assinatura"""
        self.show_status(f"❌ Erro: {error}", style="error")
        
    def show_success(self, message: str):
        """Mostra mensagem de sucesso com assinatura"""
        self.show_status(f"✅ {message}", style="success")
        
    def update_progress(self, progress: Progress, task_id: int, advance: int = 1):
        """Atualiza a barra de progresso"""
        progress.update(task_id, advance=advance)
        
    def __enter__(self):
        """Contexto para uso com 'with'"""
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Limpa recursos ao sair do contexto"""
        if self.current_progress:
            self.current_progress.stop()

# Instância global
interface = InterfaceManager() 