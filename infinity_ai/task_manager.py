"""
AVA Task Manager
Sistema de gerenciamento de tarefas e processos da AVA

Este módulo implementa um sistema de fila inteligente que:
- Gerencia múltiplas tarefas simultaneamente
- Prioriza tarefas baseado em contexto e importância
- Mantém o usuário informado sobre o status de cada processo
- Permite pausar/retomar tarefas sem perder progresso
"""

import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import logging
from collections import deque

logger = logging.getLogger(__name__)

class TaskPriority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

class TaskStatus(Enum):
    PENDING = "⏳ Pendente"
    RUNNING = "▶️ Em Execução"
    PAUSED = "⏸️ Pausado"
    COMPLETED = "✅ Concluído"
    FAILED = "❌ Falhou"

@dataclass
class Task:
    id: str
    name: str
    description: str
    priority: TaskPriority
    created_at: datetime
    status: TaskStatus
    progress: float = 0.0
    error: Optional[str] = None
    context: Dict[str, Any] = None
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "priority": self.priority.name,
            "status": self.status.value,
            "progress": self.progress,
            "created_at": self.created_at.isoformat(),
            "error": self.error,
            "context": self.context
        }
    
    def get_progress_bar(self) -> str:
        filled = int(self.progress * 10)
        return f"[{'█' * filled}{'░' * (10 - filled)}] {self.progress*100:.1f}%"

class TaskManager:
    def __init__(self, max_concurrent: int = 5):
        self.tasks: Dict[str, Task] = {}
        self.queue: deque = deque()
        self.max_concurrent = max_concurrent
        self.running_tasks = 0
        self.total_completed = 0
        self.performance_stats = {
            "avg_completion_time": 0,
            "success_rate": 1.0,
            "total_tasks": 0
        }
    
    async def add_task(self, task: Task) -> str:
        """Adiciona uma nova tarefa à fila"""
        self.tasks[task.id] = task
        self.queue.append(task.id)
        self.performance_stats["total_tasks"] += 1
        
        # Atualiza estatísticas
        await self._update_stats()
        
        # Retorna ID da tarefa para acompanhamento
        return task.id
    
    async def pause_task(self, task_id: str) -> bool:
        """Pausa uma tarefa em execução"""
        if task_id in self.tasks:
            task = self.tasks[task_id]
            if task.status == TaskStatus.RUNNING:
                task.status = TaskStatus.PAUSED
                self.running_tasks -= 1
                return True
        return False
    
    async def resume_task(self, task_id: str) -> bool:
        """Retoma uma tarefa pausada"""
        if task_id in self.tasks:
            task = self.tasks[task_id]
            if task.status == TaskStatus.PAUSED:
                task.status = TaskStatus.RUNNING
                self.running_tasks += 1
                return True
        return False
    
    async def get_task_status(self, task_id: str) -> Optional[Dict]:
        """Retorna status detalhado de uma tarefa"""
        if task_id in self.tasks:
            task = self.tasks[task_id]
            return {
                **task.to_dict(),
                "position_in_queue": self._get_queue_position(task_id),
                "estimated_start": self._estimate_start_time(task_id)
            }
        return None
    
    def get_system_status(self) -> Dict:
        """Retorna status geral do sistema de tarefas"""
        return {
            "running_tasks": self.running_tasks,
            "queue_size": len(self.queue),
            "max_concurrent": self.max_concurrent,
            "total_completed": self.total_completed,
            "performance": self.performance_stats,
            "load": self.running_tasks / self.max_concurrent
        }
    
    async def _update_stats(self):
        """Atualiza estatísticas de performance"""
        completed = [t for t in self.tasks.values() if t.status == TaskStatus.COMPLETED]
        if completed:
            self.performance_stats["success_rate"] = len(completed) / len(self.tasks)
    
    def _get_queue_position(self, task_id: str) -> Optional[int]:
        """Retorna posição de uma tarefa na fila"""
        try:
            return list(self.queue).index(task_id) + 1
        except ValueError:
            return None
    
    def _estimate_start_time(self, task_id: str) -> Optional[str]:
        """Estima tempo de início de uma tarefa"""
        position = self._get_queue_position(task_id)
        if position:
            # Estimativa simples: 2 minutos por tarefa na frente
            minutes = position * 2
            return f"≈ {minutes} minutos"
        return None
    
    def get_task_list(self, status: Optional[TaskStatus] = None) -> List[Dict]:
        """Retorna lista de tarefas filtrada por status"""
        tasks = self.tasks.values()
        if status:
            tasks = [t for t in tasks if t.status == status]
        return [t.to_dict() for t in tasks]
    
    def format_status_report(self) -> str:
        """Gera relatório formatado do estado atual do sistema"""
        stats = self.get_system_status()
        tasks = self.get_task_list()
        
        report = [
            "📊 Status do Sistema de Tarefas",
            f"Executando: {stats['running_tasks']}/{stats['max_concurrent']}",
            f"Na Fila: {stats['queue_size']}",
            f"Completadas: {stats['total_completed']}",
            f"Taxa de Sucesso: {stats['performance']['success_rate']*100:.1f}%",
            "\n🔄 Tarefas Ativas:"
        ]
        
        for task in tasks:
            if task['status'] in [TaskStatus.RUNNING.value, TaskStatus.PAUSED.value]:
                report.append(
                    f"- {task['name']}: {task['status']}\n"
                    f"  {Task(**task).get_progress_bar()}"
                )
        
        return "\n".join(report)

# Exemplo de uso:
"""
manager = TaskManager(max_concurrent=5)

# Criar nova tarefa
task = Task(
    id="task1",
    name="Processar Imagem",
    description="Redimensionar e otimizar imagem",
    priority=TaskPriority.MEDIUM,
    created_at=datetime.now(),
    status=TaskStatus.PENDING
)

# Adicionar à fila
await manager.add_task(task)

# Verificar status
status = await manager.get_task_status("task1")

# Pausar tarefa
await manager.pause_task("task1")

# Retomar tarefa
await manager.resume_task("task1")

# Ver relatório
print(manager.format_status_report())
"""