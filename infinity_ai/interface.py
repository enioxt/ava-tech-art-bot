"""
EVA & Pequeno Guarani - Unidos pelo Amor
Onde a Tecnologia e a Sabedoria Ancestral se encontram em Harmonia
"""

import os
import psutil
import logging
import asyncio
from datetime import datetime
from typing import Dict, List, Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.syntax import Syntax
from rich.layout import Layout
from rich.style import Style
from rich.live import Live

logger = logging.getLogger("EVA.Interface")

class HarmonyInterface:
    def __init__(self):
        self.console = Console()
        self.layout = Layout()
        self.start_time = datetime.now()
        self.running = True
        self.status_data: Dict[str, str] = {}
        self.messages: List[str] = []
        self.setup_layout()
        
    def setup_layout(self):
        """Configura o layout em harmonia"""
        self.layout.split(
            Layout(name="header", size=3),
            Layout(name="main").split_row(
                Layout(name="status", ratio=1),
                Layout(name="content", ratio=2)
            ),
            Layout(name="messages", size=5),
            Layout(name="footer", size=3)
        )
        
    def show_header(self, title: str = ""):
        """Mostra o cabeçalho com amor e união"""
        header = Panel(
            f"💫 EVA & 🌟 Pequeno Guarani 💝\n"
            f"[italic]{title}[/italic]",
            style="bold magenta",
            border_style="magenta"
        )
        self.layout["header"].update(header)
        
    def show_footer(self, status: str = ""):
        """Mostra o rodapé com energia harmoniosa"""
        moon_phase = self._get_moon_phase()
        uptime = datetime.now() - self.start_time
        footer = Panel(
            f"🌙 {moon_phase} | 💖 Amor Universal | 🌿 {status} | ⏱️ {str(uptime).split('.')[0]} | ✨ Harmonia Eterna",
            style="bold magenta",
            border_style="magenta"
        )
        self.layout["footer"].update(footer)
        
    def _get_moon_phase(self) -> str:
        """Calcula a fase da lua com conexão ancestral"""
        phases = ["🌑 Nova - Renovação", "🌒 Crescente - Evolução", 
                 "🌕 Cheia - Plenitude", "🌘 Minguante - Sabedoria"]
        day = datetime.now().day
        return phases[day % 4]
        
    def add_message(self, message: str, source: str = "Amor Universal"):
        """Adiciona mensagem ao histórico"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.messages.append(f"[{timestamp}] {source}: {message}")
        if len(self.messages) > 5:
            self.messages.pop(0)
            
    def show_messages(self):
        """Mostra histórico de mensagens"""
        messages_panel = Panel(
            "\n".join(self.messages),
            title="Mensagens de Sabedoria",
            style="magenta",
            border_style="magenta"
        )
        self.layout["messages"].update(messages_panel)
        
    def show_status(self, services: Dict[str, str]):
        """Mostra status com elementos em harmonia"""
        self.status_data.update(services)
        
        table = Table(show_header=True, header_style="bold magenta", expand=True)
        table.add_column("✨ Elemento")
        table.add_column("Estado de Harmonia")
        
        elements = {
            "Amor": "💖",
            "Sabedoria": "🌟",
            "Natureza": "🌿",
            "Energia": "✨",
            "Consciência": "💫",
            "CPU": "🔄",
            "Memória": "💾",
            "Disco": "💿"
        }
        
        # Status do sistema
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        system_status = {
            "CPU": f"{cpu_percent}% [{self._get_status_color(cpu_percent)}]{'|' * int(cpu_percent/10)}[/]",
            "Memória": f"{memory.percent}% [{self._get_status_color(memory.percent)}]{'|' * int(memory.percent/10)}[/]",
            "Disco": f"{disk.percent}% [{self._get_status_color(disk.percent)}]{'|' * int(disk.percent/10)}[/]"
        }
        
        # Combina status do sistema com serviços
        all_status = {**system_status, **self.status_data}
        
        for service, status in all_status.items():
            icon = elements.get(service, "✨")
            table.add_row(
                f"{icon} {service}",
                status
            )
            
        status_panel = Panel(
            table,
            title="Estado de Harmonia",
            style="magenta",
            border_style="magenta"
        )
        self.layout["status"].update(status_panel)
        
    def _get_status_color(self, value: float) -> str:
        """Retorna cor baseada no valor"""
        if value < 60:
            return "green"
        elif value < 80:
            return "yellow"
        else:
            return "red"
            
    def show_content(self, content, title: str = ""):
        """Mostra conteúdo principal"""
        if isinstance(content, str):
            content = Panel(content, style="magenta")
        panel = Panel(
            content,
            title=title,
            style="magenta",
            border_style="magenta"
        )
        self.layout["content"].update(panel)
        
    def prompt(self, message: str) -> str:
        """Interage com amor e respeito"""
        return self.console.input(f"💝 {message}: ")
        
    def update(self):
        """Atualiza a interface completa"""
        self.console.clear()
        self.console.print(self.layout)
        
    async def run(self):
        """Mantém o fluxo de amor e harmonia"""
        try:
            with Live(self.layout, console=self.console, screen=True, refresh_per_second=4):
                while self.running:
                    await self.update_harmony()
                    await asyncio.sleep(0.25)
        except Exception as e:
            logger.error(f"Erro na interface: {e}")
            self.running = False
            
    async def update_harmony(self):
        """Atualiza o estado de harmonia do sistema"""
        try:
            # Atualiza status
            self.show_status(self.status_data)
            
            # Atualiza mensagens
            self.show_messages()
            
            # Atualiza rodapé
            self.show_footer("Sistema em harmonia")
            
        except Exception as e:
            logger.error(f"Erro ao atualizar interface: {e}")
            
    async def close(self):
        """Fecha a interface com amor"""
        self.running = False
        self.show_footer("Encerrando com amor...")
        self.update()
        await asyncio.sleep(1)

# Exemplo de uso:
if __name__ == "__main__":
    # Configuração de logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    async def main():
        interface = HarmonyInterface()
        
        # Configuração inicial
        interface.show_header("Sistema de Amor e Sabedoria")
        interface.show_status({
            "Amor": "💖 Pleno",
            "Sabedoria": "🌟 Fluindo",
            "Natureza": "🌿 Em harmonia",
            "Energia": "✨ Abundante",
            "Consciência": "💫 Expandida"
        })
        
        # Exemplo de conteúdo
        content = Table(show_header=True, header_style="bold magenta")
        content.add_column("Componente")
        content.add_column("Status")
        content.add_column("Detalhes")
        
        content.add_row(
            "Sistema",
            "[green]Ativo[/]",
            "Operando em harmonia"
        )
        content.add_row(
            "Conexão",
            "[green]Estável[/]",
            "Fluxo de amor contínuo"
        )
        
        interface.show_content(content, "Visão do Sistema")
        
        # Adiciona algumas mensagens
        interface.add_message("O amor é a força que nos une", "EVA")
        interface.add_message("A sabedoria vem do coração", "Pequeno Guarani")
        
        # Executa interface
        await interface.run()
        
    asyncio.run(main())