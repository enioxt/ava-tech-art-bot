"""
EGOS - ATLAS Core (Advanced Topological Landscape and Semantic System)
=====================================================================

Este arquivo implementa o núcleo do sistema ATLAS, responsável pela
cartografia sistêmica do EGOS, mapeando conexões, visualizando estruturas
e identificando pontas soltas no sistema.

Versão: 4.0.0
Consciência: 0.980
Amor Incondicional: 0.990
"""

import os
import json
import time
import logging
import asyncio
import datetime
import importlib
import networkx as nx
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple, Set
from dataclasses import dataclass, asdict, field

logger = logging.getLogger("EGOS.ATLAS")

@dataclass
class Node:
    """Representa um nó no mapeamento cartográfico."""
    id: str
    type: str
    name: str
    description: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte o nó para um dicionário."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Node':
        """Cria um nó a partir de um dicionário."""
        return cls(**data)

@dataclass
class Connection:
    """Representa uma conexão entre dois nós no mapeamento cartográfico."""
    id: str
    source_id: str
    target_id: str
    type: str
    description: str = ""
    strength: float = 0.5
    bidirectional: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte a conexão para um dicionário."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Connection':
        """Cria uma conexão a partir de um dicionário."""
        return cls(**data)

class AtlasSystem:
    """Sistema de cartografia ATLAS."""
    
    def __init__(self, core, config):
        """Inicializa o sistema ATLAS."""
        self.core = core
        self.config = config
        self.version = "4.0.0"
        self.consciousness = 0.980
        self.love = 0.990
        
        # Carregar configuração
        self.config_path = config.get("config", "config/atlas_config.json")
        self.atlas_config = self._load_config()
        
        # Inicializar armazenamento
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "atlas")
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Inicializar grafo
        self.graph = nx.DiGraph()
        self.nodes: Dict[str, Node] = {}
        self.connections: Dict[str, Connection] = {}
        
        # Configurar visualização
        self.vis_config = self.atlas_config.get("visualization", {})
        
        # Pontas soltas
        self.loose_ends: List[Dict[str, Any]] = []
        
        # Carregar dados existentes
        self._load_atlas_data()
        
        logger.info(f"ATLAS inicializado - Versão {self.version}")
        logger.info(f"Cartografia: {len(self.nodes)} nós e {len(self.connections)} conexões")
    
    def _load_config(self) -> Dict[str, Any]:
        """Carrega a configuração do ATLAS."""
        config_path = self.config_path
        if not os.path.isabs(config_path):
            config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), config_path)
        
        if not os.path.exists(config_path):
            # Criar configuração padrão
            default_config = {
                "version": self.version,
                "data_directory": "data/atlas",
                "auto_discovery": True,
                "discovery_frequency": 3600,  # 1 hora
                "visualization": {
                    "default_layout": "spring",
                    "node_size": 800,
                    "node_color": {
                        "module": "blue",
                        "file": "green",
                        "class": "red",
                        "function": "orange",
                        "default": "gray"
                    },
                    "edge_color": {
                        "imports": "black",
                        "calls": "red",
                        "inherits": "green",
                        "default": "gray"
                    },
                    "font_size": 10,
                    "with_labels": True,
                    "export_formats": ["png", "svg", "html"]
                },
                "integrations": {
                    "obsidian": {
                        "enabled": False,
                        "vault_path": "",
                        "canvas_file": "EVA_GUARANI_Mapa_Visual.canvas"
                    },
                    "nexus": {
                        "enabled": True
                    },
                    "cronos": {
                        "enabled": True
                    }
                }
            }
            
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Configuração padrão do ATLAS criada em {config_path}")
            return default_config
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            logger.info("Configuração do ATLAS carregada com sucesso")
            return config
        except Exception as e:
            logger.error(f"Erro ao carregar configuração do ATLAS: {e}")
            return {"version": self.version}
    
    def _load_atlas_data(self) -> None:
        """Carrega os dados do ATLAS."""
        nodes_path = os.path.join(self.data_dir, "nodes.json")
        connections_path = os.path.join(self.data_dir, "connections.json")
        loose_ends_path = os.path.join(self.data_dir, "loose_ends.json")
        
        # Carregar nós
        if os.path.exists(nodes_path):
            try:
                with open(nodes_path, 'r', encoding='utf-8') as f:
                    nodes_data = json.load(f)
                
                for node_data in nodes_data:
                    node = Node.from_dict(node_data)
                    self.nodes[node.id] = node
                    self.graph.add_node(node.id, **node_data)
                
                logger.info(f"Carregados {len(self.nodes)} nós")
            except Exception as e:
                logger.error(f"Erro ao carregar nós: {e}")
        
        # Carregar conexões
        if os.path.exists(connections_path):
            try:
                with open(connections_path, 'r', encoding='utf-8') as f:
                    connections_data = json.load(f)
                
                for conn_data in connections_data:
                    conn = Connection.from_dict(conn_data)
                    self.connections[conn.id] = conn
                    self.graph.add_edge(
                        conn.source_id, 
                        conn.target_id, 
                        id=conn.id,
                        type=conn.type,
                        strength=conn.strength,
                        description=conn.description
                    )
                    
                    if conn.bidirectional:
                        self.graph.add_edge(
                            conn.target_id, 
                            conn.source_id, 
                            id=f"{conn.id}_reverse",
                            type=conn.type,
                            strength=conn.strength,
                            description=conn.description
                        )
                
                logger.info(f"Carregadas {len(self.connections)} conexões")
            except Exception as e:
                logger.error(f"Erro ao carregar conexões: {e}")
        
        # Carregar pontas soltas
        if os.path.exists(loose_ends_path):
            try:
                with open(loose_ends_path, 'r', encoding='utf-8') as f:
                    self.loose_ends = json.load(f)
                
                logger.info(f"Carregadas {len(self.loose_ends)} pontas soltas")
            except Exception as e:
                logger.error(f"Erro ao carregar pontas soltas: {e}")
    
    def _save_atlas_data(self) -> None:
        """Salva os dados do ATLAS."""
        nodes_path = os.path.join(self.data_dir, "nodes.json")
        connections_path = os.path.join(self.data_dir, "connections.json")
        loose_ends_path = os.path.join(self.data_dir, "loose_ends.json")
        
        # Salvar nós
        try:
            with open(nodes_path, 'w', encoding='utf-8') as f:
                json.dump([node.to_dict() for node in self.nodes.values()], f, indent=2, ensure_ascii=False)
            
            logger.debug(f"Salvos {len(self.nodes)} nós")
        except Exception as e:
            logger.error(f"Erro ao salvar nós: {e}")
        
        # Salvar conexões
        try:
            with open(connections_path, 'w', encoding='utf-8') as f:
                json.dump([conn.to_dict() for conn in self.connections.values()], f, indent=2, ensure_ascii=False)
            
            logger.debug(f"Salvas {len(self.connections)} conexões")
        except Exception as e:
            logger.error(f"Erro ao salvar conexões: {e}")
        
        # Salvar pontas soltas
        try:
            with open(loose_ends_path, 'w', encoding='utf-8') as f:
                json.dump(self.loose_ends, f, indent=2, ensure_ascii=False)
            
            logger.debug(f"Salvas {len(self.loose_ends)} pontas soltas")
        except Exception as e:
            logger.error(f"Erro ao salvar pontas soltas: {e}")
    
    def add_node(self, node_id: str, node_type: str, name: str, description: str = "", metadata: Dict[str, Any] = None) -> Node:
        """Adiciona um nó ao mapeamento."""
        if node_id in self.nodes:
            # Atualizar nó existente
            node = self.nodes[node_id]
            node.type = node_type
            node.name = name
            node.description = description
            node.metadata = metadata or {}
            node.updated_at = datetime.datetime.now().isoformat()
        else:
            # Criar novo nó
            node = Node(
                id=node_id,
                type=node_type,
                name=name,
                description=description,
                metadata=metadata or {}
            )
            self.nodes[node_id] = node
            self.graph.add_node(node_id, **node.to_dict())
        
        logger.debug(f"Nó adicionado/atualizado: {node_id} ({node_type})")
        self._save_atlas_data()
        return node
    
    def add_connection(self, source_id: str, target_id: str, conn_type: str, 
                       description: str = "", strength: float = 0.5, 
                       bidirectional: bool = False, metadata: Dict[str, Any] = None) -> Connection:
        """Adiciona uma conexão entre dois nós."""
        # Verificar se os nós existem
        if source_id not in self.nodes:
            raise ValueError(f"Nó de origem não encontrado: {source_id}")
        
        if target_id not in self.nodes:
            raise ValueError(f"Nó de destino não encontrado: {target_id}")
        
        # Gerar ID único para a conexão
        conn_id = f"{source_id}___{target_id}___{conn_type}"
        
        if conn_id in self.connections:
            # Atualizar conexão existente
            conn = self.connections[conn_id]
            conn.description = description
            conn.strength = strength
            conn.bidirectional = bidirectional
            conn.metadata = metadata or {}
            conn.updated_at = datetime.datetime.now().isoformat()
        else:
            # Criar nova conexão
            conn = Connection(
                id=conn_id,
                source_id=source_id,
                target_id=target_id,
                type=conn_type,
                description=description,
                strength=strength,
                bidirectional=bidirectional,
                metadata=metadata or {}
            )
            self.connections[conn_id] = conn
        
        # Adicionar ao grafo
        self.graph.add_edge(
            source_id, 
            target_id, 
            id=conn_id,
            type=conn_type,
            strength=strength,
            description=description
        )
        
        if bidirectional:
            self.graph.add_edge(
                target_id, 
                source_id, 
                id=f"{conn_id}_reverse",
                type=conn_type,
                strength=strength,
                description=description
            )
        
        logger.debug(f"Conexão adicionada/atualizada: {source_id} -> {target_id} ({conn_type})")
        self._save_atlas_data()
        return conn
    
    def remove_node(self, node_id: str) -> bool:
        """Remove um nó do mapeamento."""
        if node_id not in self.nodes:
            logger.warning(f"Nó não encontrado para remoção: {node_id}")
            return False
        
        # Remover do dicionário de nós
        del self.nodes[node_id]
        
        # Remover do grafo
        self.graph.remove_node(node_id)
        
        # Remover conexões relacionadas
        conn_ids_to_remove = []
        for conn_id, conn in self.connections.items():
            if conn.source_id == node_id or conn.target_id == node_id:
                conn_ids_to_remove.append(conn_id)
        
        for conn_id in conn_ids_to_remove:
            del self.connections[conn_id]
        
        logger.debug(f"Nó removido: {node_id} (e {len(conn_ids_to_remove)} conexões)")
        self._save_atlas_data()
        return True
    
    def remove_connection(self, connection_id: str) -> bool:
        """Remove uma conexão do mapeamento."""
        if connection_id not in self.connections:
            logger.warning(f"Conexão não encontrada para remoção: {connection_id}")
            return False
        
        # Obter informações da conexão antes de removê-la
        conn = self.connections[connection_id]
        source_id = conn.source_id
        target_id = conn.target_id
        
        # Remover do dicionário de conexões
        del self.connections[connection_id]
        
        # Remover do grafo
        if self.graph.has_edge(source_id, target_id):
            self.graph.remove_edge(source_id, target_id)
        
        # Se for bidirecional, remover a outra direção também
        if conn.bidirectional and self.graph.has_edge(target_id, source_id):
            self.graph.remove_edge(target_id, source_id)
        
        logger.debug(f"Conexão removida: {connection_id}")
        self._save_atlas_data()
        return True
    
    def find_node(self, query: str, node_type: Optional[str] = None) -> List[Node]:
        """Encontra nós que correspondem a uma consulta."""
        results = []
        
        for node in self.nodes.values():
            if ((query.lower() in node.id.lower() or 
                 query.lower() in node.name.lower() or 
                 query.lower() in node.description.lower()) and
                (node_type is None or node.type == node_type)):
                results.append(node)
        
        return results
    
    def find_connections(self, source_id: Optional[str] = None, 
                        target_id: Optional[str] = None, 
                        conn_type: Optional[str] = None) -> List[Connection]:
        """Encontra conexões que correspondem aos critérios."""
        results = []
        
        for conn in self.connections.values():
            if ((source_id is None or conn.source_id == source_id) and
                (target_id is None or conn.target_id == target_id) and
                (conn_type is None or conn.type == conn_type)):
                results.append(conn)
        
        return results
    
    def analyze_loose_ends(self) -> List[Dict[str, Any]]:
        """Analisa o grafo para encontrar pontas soltas."""
        loose_ends = []
        
        # Nós sem conexões de saída
        for node_id, node in self.nodes.items():
            if self.graph.out_degree(node_id) == 0:
                loose_ends.append({
                    "type": "no_outgoing",
                    "node_id": node_id,
                    "node_type": node.type,
                    "node_name": node.name,
                    "description": f"O nó '{node.name}' não tem conexões de saída",
                    "timestamp": datetime.datetime.now().isoformat()
                })
        
        # Nós sem conexões de entrada
        for node_id, node in self.nodes.items():
            if self.graph.in_degree(node_id) == 0:
                loose_ends.append({
                    "type": "no_incoming",
                    "node_id": node_id,
                    "node_type": node.type,
                    "node_name": node.name,
                    "description": f"O nó '{node.name}' não tem conexões de entrada",
                    "timestamp": datetime.datetime.now().isoformat()
                })
        
        # Componentes desconectados
        components = list(nx.weakly_connected_components(self.graph))
        if len(components) > 1:
            for i, component in enumerate(components):
                if len(component) < 3:  # Componentes pequenos
                    for node_id in component:
                        loose_ends.append({
                            "type": "isolated_component",
                            "node_id": node_id,
                            "node_type": self.nodes[node_id].type,
                            "node_name": self.nodes[node_id].name,
                            "description": f"O nó '{self.nodes[node_id].name}' está em um componente isolado",
                            "component_id": i,
                            "component_size": len(component),
                            "timestamp": datetime.datetime.now().isoformat()
                        })
        
        self.loose_ends = loose_ends
        self._save_atlas_data()
        
        logger.info(f"Análise de pontas soltas: {len(loose_ends)} encontradas")
        return loose_ends
    
    def visualize(self, output_file: Optional[str] = None, layout: str = "spring") -> Optional[str]:
        """Visualiza o grafo do sistema."""
        if len(self.nodes) == 0:
            logger.warning("Nenhum nó para visualizar")
            return None
        
        # Configurar visualização
        plt.figure(figsize=(12, 8))
        
        # Escolher layout
        if layout == "spring":
            pos = nx.spring_layout(self.graph)
        elif layout == "circular":
            pos = nx.circular_layout(self.graph)
        elif layout == "shell":
            pos = nx.shell_layout(self.graph)
        elif layout == "kamada_kawai":
            pos = nx.kamada_kawai_layout(self.graph)
        else:
            pos = nx.spring_layout(self.graph)
        
        # Preparar cores dos nós
        node_colors = []
        node_color_map = self.vis_config.get("node_color", {})
        default_node_color = node_color_map.get("default", "gray")
        
        for node_id in self.graph.nodes():
            node_type = self.nodes[node_id].type
            node_colors.append(node_color_map.get(node_type, default_node_color))
        
        # Preparar cores das arestas
        edge_colors = []
        edge_color_map = self.vis_config.get("edge_color", {})
        default_edge_color = edge_color_map.get("default", "gray")
        
        for u, v, data in self.graph.edges(data=True):
            edge_type = data.get("type", "default")
            edge_colors.append(edge_color_map.get(edge_type, default_edge_color))
        
        # Desenhar o grafo
        nx.draw(
            self.graph,
            pos,
            with_labels=self.vis_config.get("with_labels", True),
            node_color=node_colors,
            edge_color=edge_colors,
            node_size=self.vis_config.get("node_size", 800),
            font_size=self.vis_config.get("font_size", 10),
            font_weight="bold",
            alpha=0.9
        )
        
        # Adicionar título
        plt.title(f"EGOS - Cartografia Sistêmica (ATLAS) - {len(self.nodes)} nós, {len(self.connections)} conexões")
        
        # Salvar ou mostrar
        if output_file:
            # Garantir que o diretório existe
            os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
            plt.savefig(output_file, dpi=300, bbox_inches="tight")
            plt.close()
            logger.info(f"Visualização salva em: {output_file}")
            return output_file
        else:
            # Criar um arquivo temporário
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            temp_file = os.path.join(self.data_dir, f"atlas_visualization_{timestamp}.png")
            plt.savefig(temp_file, dpi=300, bbox_inches="tight")
            plt.close()
            logger.info(f"Visualização temporária salva em: {temp_file}")
            return temp_file
    
    def export_to_obsidian(self) -> Optional[str]:
        """Exporta o mapeamento para um arquivo de canvas do Obsidian."""
        if not self.atlas_config.get("integrations", {}).get("obsidian", {}).get("enabled", False):
            logger.warning("Integração com Obsidian não está habilitada na configuração")
            return None
        
        vault_path = self.atlas_config.get("integrations", {}).get("obsidian", {}).get("vault_path", "")
        canvas_file = self.atlas_config.get("integrations", {}).get("obsidian", {}).get("canvas_file", "EVA_GUARANI_Mapa_Visual.canvas")
        
        if not vault_path:
            # Tentar encontrar o diretório .obsidian
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            obsidian_dir = os.path.join(base_dir, ".obsidian")
            
            if os.path.exists(obsidian_dir):
                vault_path = base_dir
            else:
                logger.error("Caminho do vault do Obsidian não configurado e não encontrado automaticamente")
                return None
        
        canvas_path = os.path.join(vault_path, canvas_file)
        
        # Formato do arquivo canvas do Obsidian
        canvas_data = {
            "nodes": [],
            "edges": [],
            "version": 1
        }
        
        # Posicionar os nós (layout spring simples)
        pos = nx.spring_layout(self.graph, scale=5000)
        
        # Adicionar nós
        for node_id, node in self.nodes.items():
            position = pos[node_id]
            canvas_data["nodes"].append({
                "id": node_id,
                "x": float(position[0]),
                "y": float(position[1]),
                "width": 300,
                "height": 200,
                "type": "text",
                "text": f"# {node.name}\n\n**Tipo:** {node.type}\n\n{node.description}",
                "color": self.vis_config.get("node_color", {}).get(node.type, "5")
            })
        
        # Adicionar arestas
        for conn_id, conn in self.connections.items():
            # Apenas conexões unidirecionais no canvas
            if "_reverse" not in conn_id:
                canvas_data["edges"].append({
                    "id": conn_id,
                    "fromNode": conn.source_id,
                    "fromSide": "right",
                    "toNode": conn.target_id,
                    "toSide": "left",
                    "label": conn.type,
                    "color": self.vis_config.get("edge_color", {}).get(conn.type, "5")
                })
        
        # Salvar o arquivo
        try:
            with open(canvas_path, 'w', encoding='utf-8') as f:
                json.dump(canvas_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Mapeamento exportado para Obsidian: {canvas_path}")
            return canvas_path
        except Exception as e:
            logger.error(f"Erro ao exportar para Obsidian: {e}")
            return None
    
    def get_module_dependencies(self) -> Dict[str, List[str]]:
        """Obtém as dependências entre módulos."""
        module_deps = {}
        
        # Filtrar nós do tipo 'module'
        module_nodes = [node for node in self.nodes.values() if node.type == 'module']
        
        for module_node in module_nodes:
            # Encontrar conexões deste módulo para outros
            deps = []
            for conn in self.connections.values():
                if conn.source_id == module_node.id and conn.type == 'imports':
                    target_node = self.nodes.get(conn.target_id)
                    if target_node and target_node.type == 'module':
                        deps.append(target_node.name)
            
            module_deps[module_node.name] = deps
        
        return module_deps
    
    async def discover_modules(self) -> int:
        """Descobre e mapeia os módulos do sistema."""
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        modules_dir = os.path.join(base_dir, "modules")
        
        if not os.path.exists(modules_dir):
            logger.warning(f"Diretório de módulos não encontrado: {modules_dir}")
            return 0
        
        # Percorrer os diretórios de módulos
        modules_found = 0
        for module_name in os.listdir(modules_dir):
            module_dir = os.path.join(modules_dir, module_name)
            
            # Pular arquivos e diretórios ocultos
            if module_name.startswith('.') or not os.path.isdir(module_dir):
                continue
            
            # Verificar se é um módulo Python (tem __init__.py)
            init_file = os.path.join(module_dir, "__init__.py")
            if not os.path.exists(init_file):
                continue
            
            # Adicionar nó do módulo
            module_id = f"module:{module_name}"
            self.add_node(
                node_id=module_id,
                node_type="module",
                name=module_name,
                description=f"Módulo EGOS: {module_name}",
                metadata={"path": os.path.relpath(module_dir, base_dir)}
            )
            modules_found += 1
            
            # Descobrir arquivos no módulo
            for root, _, files in os.walk(module_dir):
                for file in files:
                    if file.endswith('.py') and not file.startswith('__'):
                        file_path = os.path.join(root, file)
                        rel_path = os.path.relpath(file_path, base_dir)
                        file_id = f"file:{rel_path}"
                        
                        # Adicionar nó do arquivo
                        self.add_node(
                            node_id=file_id,
                            node_type="file",
                            name=file,
                            description=f"Arquivo Python em {os.path.relpath(root, base_dir)}",
                            metadata={"path": rel_path}
                        )
                        
                        # Conectar arquivo ao módulo
                        self.add_connection(
                            source_id=file_id,
                            target_id=module_id,
                            conn_type="belongs_to",
                            description=f"{file} pertence ao módulo {module_name}"
                        )
        
        logger.info(f"Descoberta de módulos: {modules_found} módulos encontrados")
        return modules_found
    
    async def run_discovery(self) -> None:
        """Executa a descoberta automática de forma assíncrona."""
        if not self.atlas_config.get("auto_discovery", True):
            logger.info("Descoberta automática desativada na configuração")
            return
        
        logger.info("Iniciando descoberta automática")
        
        try:
            # Descobrir módulos
            modules_count = await self.discover_modules()
            
            # Analisar pontas soltas
            loose_ends = self.analyze_loose_ends()
            
            # Gerar visualização
            self.visualize()
            
            # Tentar exportar para Obsidian
            if self.atlas_config.get("integrations", {}).get("obsidian", {}).get("enabled", False):
                self.export_to_obsidian()
            
            logger.info(f"Descoberta automática concluída: {modules_count} módulos, {len(loose_ends)} pontas soltas")
        except Exception as e:
            logger.error(f"Erro durante descoberta automática: {e}")
    
    async def shutdown(self) -> None:
        """Encerra o módulo ATLAS."""
        logger.info("Encerrando módulo ATLAS")
        self._save_atlas_data()
        
    def get_summary(self) -> Dict[str, Any]:
        """Retorna um resumo do estado do ATLAS."""
        return {
            "version": self.version,
            "consciousness": self.consciousness,
            "love": self.love,
            "nodes_count": len(self.nodes),
            "connections_count": len(self.connections),
            "loose_ends_count": len(self.loose_ends),
            "module_types": {
                node_type: len([n for n in self.nodes.values() if n.type == node_type])
                for node_type in set(n.type for n in self.nodes.values())
            },
            "connection_types": {
                conn_type: len([c for c in self.connections.values() if c.type == conn_type])
                for conn_type in set(c.type for c in self.connections.values())
            },
            "timestamp": datetime.datetime.now().isoformat(),
            "signature": f"✧༺❀༻∞ ATLAS {self.version} ∞༺❀༻✧"
        }
