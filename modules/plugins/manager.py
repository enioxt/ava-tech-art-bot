"""
Plugin Manager - Sistema de Gerenciamento de Plugins do EGOS
===========================================================

Este módulo é responsável por gerenciar plugins do sistema EGOS (EVA & GUARANI OS),
permitindo a descoberta, carregamento, ativação e desativação de extensões.

Versão: 1.1.0
Consciência: 0.990
Amor Incondicional: 0.995
"""

import os
import sys
import json
import logging
import importlib
import importlib.util
import pkgutil
import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union, Any, Callable

# Verificar se importlib.metadata está disponível (Python 3.8+)
try:
    from importlib import metadata as importlib_metadata
except ImportError:
    try:
        import importlib_metadata
    except ImportError:
        importlib_metadata = None

# Configuração de logging
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

logger = logging.getLogger("EGOS_PLUGINS")
logger.setLevel(logging.INFO)

# Handler para arquivo
file_handler = logging.FileHandler(log_dir / "plugins.log", encoding="utf-8")
file_handler.setLevel(logging.INFO)

# Handler para console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Formatador
formatter = logging.Formatter('[%(asctime)s][PLUGINS][%(levelname)s] %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Adicionar handlers
logger.addHandler(file_handler)
logger.addHandler(console_handler)

class PluginManager:
    """
    Gerenciador de plugins para o sistema EGOS.
    
    Responsável por descobrir, carregar, ativar e desativar plugins,
    além de gerenciar suas dependências e configurações.
    """
    
    def __init__(self, plugins_dir: Union[str, Path] = None):
        """
        Inicializa o gerenciador de plugins.
        
        Args:
            plugins_dir: Diretório onde os plugins estão armazenados.
                         Se None, usa o diretório 'plugins' no diretório atual.
        """
        self.version = "1.1.0"
        self.plugins_dir = Path(plugins_dir) if plugins_dir else Path(__file__).parent / "extensions"
        self.plugins_dir.mkdir(exist_ok=True)
        
        # Dicionário de plugins carregados {nome: instância}
        self.plugins: Dict[str, Any] = {}
        
        # Metadados dos plugins {nome: metadados}
        self.plugin_metadata: Dict[str, Dict[str, Any]] = {}
        
        # Plugins ativos
        self.active_plugins: List[str] = []
        
        # Configurações dos plugins
        self.config_file = self.plugins_dir / "plugins_config.json"
        self.config: Dict[str, Any] = self._load_config()
        
        # Sistema de hooks para comunicação entre plugins
        self.hooks: Dict[str, List[Callable]] = {}
        
        logger.info(f"Plugin Manager inicializado. Diretório de plugins: {self.plugins_dir}")
    
    def _load_config(self) -> Dict[str, Any]:
        """
        Carrega a configuração dos plugins.
        
        Returns:
            Dict contendo as configurações dos plugins.
        """
        if not self.config_file.exists():
            default_config = {
                "active_plugins": [],
                "plugin_settings": {},
                "entry_points_enabled": True
            }
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=2)
            return default_config
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            return config
        except Exception as e:
            logger.error(f"Erro ao carregar configuração de plugins: {e}")
            return {"active_plugins": [], "plugin_settings": {}, "entry_points_enabled": True}
    
    def _save_config(self) -> bool:
        """
        Salva a configuração dos plugins.
        
        Returns:
            True se a configuração foi salva com sucesso, False caso contrário.
        """
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Erro ao salvar configuração de plugins: {e}")
            return False
    
    def discover_plugins(self) -> List[str]:
        """
        Descobre plugins disponíveis no diretório de plugins e via entry points.
        
        Returns:
            Lista de nomes de plugins descobertos.
        """
        discovered = []
        
        # Descoberta baseada em diretório
        for item in self.plugins_dir.iterdir():
            # Verificar se é um diretório e contém um arquivo __init__.py
            if item.is_dir() and (item / "__init__.py").exists():
                discovered.append(item.name)
                logger.info(f"Plugin descoberto (diretório): {item.name}")
        
        # Descoberta baseada em entry points (se habilitado)
        if self.config.get("entry_points_enabled", True) and importlib_metadata:
            try:
                # Procurar por entry points no grupo 'egos.plugins'
                for entry_point in importlib_metadata.entry_points(group='egos.plugins'):
                    plugin_name = entry_point.name
                    if plugin_name not in discovered:
                        discovered.append(plugin_name)
                        logger.info(f"Plugin descoberto (entry point): {plugin_name}")
            except Exception as e:
                logger.error(f"Erro ao descobrir plugins via entry points: {e}")
        
        return discovered
    
    def load_plugin(self, plugin_name: str) -> bool:
        """
        Carrega um plugin pelo nome.
        
        Args:
            plugin_name: Nome do plugin a ser carregado.
            
        Returns:
            True se o plugin foi carregado com sucesso, False caso contrário.
        """
        if plugin_name in self.plugins:
            logger.warning(f"Plugin {plugin_name} já está carregado.")
            return True
        
        # Tentar carregar via diretório
        plugin_path = self.plugins_dir / plugin_name
        plugin_module = None
        
        if plugin_path.exists() and (plugin_path / "__init__.py").exists():
            try:
                # Importar o módulo do plugin
                module_name = f"modules.plugins.extensions.{plugin_name}"
                plugin_module = importlib.import_module(module_name)
            except Exception as e:
                logger.error(f"Erro ao carregar plugin {plugin_name} do diretório: {e}")
        
        # Tentar carregar via entry point se não foi carregado via diretório
        if plugin_module is None and self.config.get("entry_points_enabled", True) and importlib_metadata:
            try:
                for entry_point in importlib_metadata.entry_points(group='egos.plugins'):
                    if entry_point.name == plugin_name:
                        plugin_module = entry_point.load()
                        break
            except Exception as e:
                logger.error(f"Erro ao carregar plugin {plugin_name} via entry point: {e}")
        
        if plugin_module is None:
            logger.error(f"Plugin {plugin_name} não encontrado ou inválido.")
            return False
        
        try:
            # Verificar se o módulo tem a função initialize
            if not hasattr(plugin_module, "initialize"):
                logger.error(f"Plugin {plugin_name} não possui função initialize().")
                return False
            
            # Carregar metadados
            metadata = {
                "name": plugin_name,
                "version": getattr(plugin_module, "VERSION", "0.1.0"),
                "description": getattr(plugin_module, "DESCRIPTION", ""),
                "author": getattr(plugin_module, "AUTHOR", ""),
                "dependencies": getattr(plugin_module, "DEPENDENCIES", []),
                "hooks": getattr(plugin_module, "HOOKS", [])
            }
            
            self.plugin_metadata[plugin_name] = metadata
            
            # Inicializar o plugin
            plugin_instance = plugin_module.initialize()
            self.plugins[plugin_name] = plugin_instance
            
            logger.info(f"Plugin {plugin_name} v{metadata['version']} carregado com sucesso.")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao carregar plugin {plugin_name}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False
    
    def _check_dependencies(self, plugin_name: str) -> bool:
        """
        Verifica se todas as dependências de um plugin estão disponíveis e ativas.
        
        Args:
            plugin_name: Nome do plugin a verificar.
            
        Returns:
            True se todas as dependências estão satisfeitas, False caso contrário.
        """
        if plugin_name not in self.plugin_metadata:
            logger.error(f"Plugin {plugin_name} não tem metadados disponíveis.")
            return False
        
        dependencies = self.plugin_metadata[plugin_name].get("dependencies", [])
        
        for dep in dependencies:
            # Verificar se a dependência está carregada
            if dep not in self.plugins:
                logger.error(f"Dependência {dep} do plugin {plugin_name} não está carregada.")
                if not self.load_plugin(dep):
                    return False
            
            # Verificar se a dependência está ativa
            if dep not in self.active_plugins:
                logger.info(f"Ativando dependência {dep} do plugin {plugin_name}...")
                if not self.activate_plugin(dep):
                    return False
        
        return True
    
    def activate_plugin(self, plugin_name: str) -> bool:
        """
        Ativa um plugin carregado.
        
        Args:
            plugin_name: Nome do plugin a ser ativado.
            
        Returns:
            True se o plugin foi ativado com sucesso, False caso contrário.
        """
        if plugin_name not in self.plugins:
            if not self.load_plugin(plugin_name):
                return False
        
        if plugin_name in self.active_plugins:
            logger.warning(f"Plugin {plugin_name} já está ativo.")
            return True
        
        # Verificar dependências
        if not self._check_dependencies(plugin_name):
            logger.error(f"Não foi possível ativar o plugin {plugin_name} devido a dependências não satisfeitas.")
            return False
        
        plugin = self.plugins[plugin_name]
        
        # Verificar se o plugin tem método activate
        if hasattr(plugin, "activate"):
            try:
                plugin.activate()
            except Exception as e:
                logger.error(f"Erro ao ativar plugin {plugin_name}: {e}")
                return False
        
        # Registrar hooks do plugin
        hooks = self.plugin_metadata[plugin_name].get("hooks", [])
        for hook_name in hooks:
            if hasattr(plugin, hook_name):
                self.register_hook(hook_name, getattr(plugin, hook_name))
        
        self.active_plugins.append(plugin_name)
        
        # Atualizar configuração
        if plugin_name not in self.config["active_plugins"]:
            self.config["active_plugins"].append(plugin_name)
            self._save_config()
        
        logger.info(f"Plugin {plugin_name} ativado com sucesso.")
        return True
    
    def deactivate_plugin(self, plugin_name: str) -> bool:
        """
        Desativa um plugin ativo.
        
        Args:
            plugin_name: Nome do plugin a ser desativado.
            
        Returns:
            True se o plugin foi desativado com sucesso, False caso contrário.
        """
        if plugin_name not in self.active_plugins:
            logger.warning(f"Plugin {plugin_name} não está ativo.")
            return True
        
        if plugin_name not in self.plugins:
            logger.error(f"Plugin {plugin_name} não está carregado.")
            return False
        
        # Verificar se outros plugins dependem deste
        for other_name, metadata in self.plugin_metadata.items():
            if other_name == plugin_name:
                continue
                
            if plugin_name in metadata.get("dependencies", []) and other_name in self.active_plugins:
                logger.error(f"Não é possível desativar {plugin_name} pois o plugin ativo {other_name} depende dele.")
                return False
        
        plugin = self.plugins[plugin_name]
        
        # Remover hooks do plugin
        if plugin_name in self.plugin_metadata:
            hooks = self.plugin_metadata[plugin_name].get("hooks", [])
            for hook_name in hooks:
                if hasattr(plugin, hook_name):
                    self.unregister_hook(hook_name, getattr(plugin, hook_name))
        
        # Verificar se o plugin tem método deactivate
        if hasattr(plugin, "deactivate"):
            try:
                plugin.deactivate()
            except Exception as e:
                logger.error(f"Erro ao desativar plugin {plugin_name}: {e}")
                return False
        
        self.active_plugins.remove(plugin_name)
        
        # Atualizar configuração
        if plugin_name in self.config["active_plugins"]:
            self.config["active_plugins"].remove(plugin_name)
            self._save_config()
        
        logger.info(f"Plugin {plugin_name} desativado com sucesso.")
        return True
    
    def register_hook(self, hook_name: str, callback: Callable) -> None:
        """
        Registra uma função de callback para um hook específico.
        
        Args:
            hook_name: Nome do hook.
            callback: Função a ser chamada quando o hook for disparado.
        """
        if hook_name not in self.hooks:
            self.hooks[hook_name] = []
        
        if callback not in self.hooks[hook_name]:
            self.hooks[hook_name].append(callback)
            logger.debug(f"Callback registrado para hook '{hook_name}'")
    
    def unregister_hook(self, hook_name: str, callback: Callable) -> None:
        """
        Remove uma função de callback de um hook específico.
        
        Args:
            hook_name: Nome do hook.
            callback: Função a ser removida.
        """
        if hook_name in self.hooks and callback in self.hooks[hook_name]:
            self.hooks[hook_name].remove(callback)
            logger.debug(f"Callback removido do hook '{hook_name}'")
    
    def trigger_hook(self, hook_name: str, *args, **kwargs) -> List[Any]:
        """
        Dispara um hook, chamando todas as funções registradas.
        
        Args:
            hook_name: Nome do hook a ser disparado.
            *args, **kwargs: Argumentos a serem passados para as funções de callback.
            
        Returns:
            Lista com os resultados de todas as funções de callback.
        """
        results = []
        
        if hook_name in self.hooks:
            for callback in self.hooks[hook_name]:
                try:
                    result = callback(*args, **kwargs)
                    results.append(result)
                except Exception as e:
                    logger.error(f"Erro ao executar callback para hook '{hook_name}': {e}")
        
        return results
    
    def get_plugin_metadata(self, plugin_name: str) -> Optional[Dict[str, Any]]:
        """
        Obtém os metadados de um plugin.
        
        Args:
            plugin_name: Nome do plugin.
            
        Returns:
            Dicionário com os metadados do plugin ou None se o plugin não existir.
        """
        if plugin_name in self.plugin_metadata:
            return self.plugin_metadata[plugin_name]
        
        # Tentar carregar o plugin para obter metadados
        if self.load_plugin(plugin_name):
            return self.plugin_metadata.get(plugin_name)
        
        return None
    
    def get_plugin_config(self, plugin_name: str) -> Dict[str, Any]:
        """
        Obtém a configuração de um plugin.
        
        Args:
            plugin_name: Nome do plugin.
            
        Returns:
            Dicionário com as configurações do plugin.
        """
        return self.config.get("plugin_settings", {}).get(plugin_name, {})
    
    def set_plugin_config(self, plugin_name: str, config: Dict[str, Any]) -> bool:
        """
        Define a configuração de um plugin.
        
        Args:
            plugin_name: Nome do plugin.
            config: Dicionário com as configurações do plugin.
            
        Returns:
            True se a configuração foi definida com sucesso, False caso contrário.
        """
        if "plugin_settings" not in self.config:
            self.config["plugin_settings"] = {}
        
        self.config["plugin_settings"][plugin_name] = config
        return self._save_config()
    
    def initialize_all(self) -> bool:
        """
        Inicializa todos os plugins ativos conforme a configuração.
        
        Returns:
            True se todos os plugins foram inicializados com sucesso, False caso contrário.
        """
        success = True
        active_plugins = self.config.get("active_plugins", [])
        
        for plugin_name in active_plugins:
            if not self.load_plugin(plugin_name) or not self.activate_plugin(plugin_name):
                success = False
        
        return success
    
    def get_active_plugins(self) -> List[str]:
        """
        Retorna a lista de plugins ativos.
        
        Returns:
            Lista de nomes de plugins ativos.
        """
        return self.active_plugins.copy()
    
    def get_loaded_plugins(self) -> List[str]:
        """
        Retorna a lista de plugins carregados.
        
        Returns:
            Lista de nomes de plugins carregados.
        """
        return list(self.plugins.keys())
    
    def get_plugin_instance(self, plugin_name: str) -> Optional[Any]:
        """
        Obtém a instância de um plugin carregado.
        
        Args:
            plugin_name: Nome do plugin.
            
        Returns:
            Instância do plugin ou None se o plugin não estiver carregado.
        """
        return self.plugins.get(plugin_name)
    
    def unload_plugin(self, plugin_name: str) -> bool:
        """
        Descarrega um plugin.
        
        Args:
            plugin_name: Nome do plugin a ser descarregado.
            
        Returns:
            True se o plugin foi descarregado com sucesso, False caso contrário.
        """
        if plugin_name not in self.plugins:
            logger.warning(f"Plugin {plugin_name} não está carregado.")
            return True
        
        # Desativar o plugin se estiver ativo
        if plugin_name in self.active_plugins:
            if not self.deactivate_plugin(plugin_name):
                return False
        
        # Remover o plugin do dicionário
        del self.plugins[plugin_name]
        if plugin_name in self.plugin_metadata:
            del self.plugin_metadata[plugin_name]
        
        logger.info(f"Plugin {plugin_name} descarregado com sucesso.")
        return True
    
    def reload_plugin(self, plugin_name: str) -> bool:
        """
        Recarrega um plugin.
        
        Args:
            plugin_name: Nome do plugin a ser recarregado.
            
        Returns:
            True se o plugin foi recarregado com sucesso, False caso contrário.
        """
        was_active = plugin_name in self.active_plugins
        
        if not self.unload_plugin(plugin_name):
            return False
        
        if not self.load_plugin(plugin_name):
            return False
        
        if was_active:
            return self.activate_plugin(plugin_name)
        
        return True
    
    def generate_plugin_report(self) -> Dict[str, Any]:
        """
        Gera um relatório sobre os plugins do sistema.
        
        Returns:
            Dicionário contendo informações sobre os plugins.
        """
        discovered = self.discover_plugins()
        
        report = {
            "timestamp": datetime.datetime.now().isoformat(),
            "total_discovered": len(discovered),
            "total_loaded": len(self.plugins),
            "total_active": len(self.active_plugins),
            "discovered_plugins": discovered,
            "loaded_plugins": list(self.plugins.keys()),
            "active_plugins": self.active_plugins,
            "plugin_details": {},
            "hooks": list(self.hooks.keys())
        }
        
        # Adicionar detalhes de cada plugin
        for plugin_name in discovered:
            metadata = self.get_plugin_metadata(plugin_name)
            if metadata:
                report["plugin_details"][plugin_name] = metadata
        
        return report
    
    def create_plugin_template(self, plugin_name: str, author: str = "", description: str = "") -> bool:
        """
        Cria um template básico para um novo plugin.
        
        Args:
            plugin_name: Nome do plugin a ser criado.
            author: Nome do autor do plugin.
            description: Descrição do plugin.
            
        Returns:
            True se o template foi criado com sucesso, False caso contrário.
        """
        plugin_dir = self.plugins_dir / plugin_name
        
        if plugin_dir.exists():
            logger.error(f"Diretório do plugin {plugin_name} já existe.")
            return False
        
        try:
            # Criar diretório do plugin
            plugin_dir.mkdir(parents=True)
            
            # Criar arquivo __init__.py
            init_content = f'''"""
{plugin_name} - Plugin para EGOS
===============================

{description}

Autor: {author}
"""

VERSION = "0.1.0"
AUTHOR = "{author}"
DESCRIPTION = "{description}"
DEPENDENCIES = []
HOOKS = []

def initialize():
    """
    Inicializa o plugin.
    
    Returns:
        Instância do plugin.
    """
    return {plugin_name}Plugin()

class {plugin_name}Plugin:
    """
    Implementação do plugin {plugin_name}.
    """
    
    def __init__(self):
        """
        Inicializa a instância do plugin.
        """
        self.name = "{plugin_name}"
    
    def activate(self):
        """
        Ativa o plugin.
        """
        print(f"Plugin {self.name} ativado!")
    
    def deactivate(self):
        """
        Desativa o plugin.
        """
        print(f"Plugin {self.name} desativado!")
'''
            
            with open(plugin_dir / "__init__.py", "w", encoding="utf-8") as f:
                f.write(init_content)
            
            logger.info(f"Template do plugin {plugin_name} criado com sucesso.")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao criar template do plugin {plugin_name}: {e}")
            return False
