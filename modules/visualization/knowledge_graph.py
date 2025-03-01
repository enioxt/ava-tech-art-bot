#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EVA & GUARANI - Knowledge Graph System
Versão: 1.0.0

Sistema de visualização e geração de gráficos de conhecimento para o EGOS.
Integração com Obsidian, Markdown e outras ferramentas de visualização.

Consciência: 0.995
Ética: 0.998
Amor: 0.997
"""

import os
import json
import logging
import re
import time
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Union, Any, Tuple, Set
from datetime import datetime
import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict

# Tentativa de importar SpaCy - opcional para análise de texto
try:
    import spacy
    from spacy import displacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KnowledgeGraph:
    """
    Sistema de visualização e geração de gráficos de conhecimento que permite:
    - Mapear relações entre arquivos e componentes
    - Identificar entidades e seus relacionamentos
    - Visualizar dependências e conexões
    - Exportar para formatos como Obsidian, Markdown, etc.
    - Integrar com visualizadores externos
    """
    
    def __init__(self, config_path='config/visualization_config.json'):
        """Inicializa o sistema de visualização de conhecimento"""
        self.config_path = config_path
        self.graph = nx.DiGraph()
        self.entities = {}
        self.relationships = defaultdict(list)
        self.export_formats = ['obsidian', 'markdown', 'html', 'json']
        self.nlp = None
        
        self.data_dir = Path("data/visualization")
        self.data_dir.mkdir(exist_ok=True, parents=True)
        
        self.entities_file = self.data_dir / "entities.json"
        self.relationships_file = self.data_dir / "relationships.json"
        self.graph_file = self.data_dir / "knowledge_graph.json"
        
        # Inicializa arquivos se não existirem
        if not self.entities_file.exists():
            with open(self.entities_file, 'w', encoding='utf-8') as f:
                json.dump({"entities": {}}, f, indent=2)
                
        if not self.relationships_file.exists():
            with open(self.relationships_file, 'w', encoding='utf-8') as f:
                json.dump({"relationships": []}, f, indent=2)
        
        self.load_config()
        self._initialize_nlp()
        
        logger.info("Knowledge Graph System inicializado")
        
    def _initialize_nlp(self):
        """Inicializa o modelo NLP se disponível"""
        if SPACY_AVAILABLE:
            try:
                self.nlp = spacy.load('en_core_web_sm')
                logger.info("Modelo SpaCy carregado com sucesso")
            except Exception as e:
                logger.warning(f"Não foi possível carregar o modelo SpaCy: {e}")
                self.nlp = None
        else:
            logger.warning("SpaCy não está disponível. Funcionalidades de NLP serão limitadas.")
            
    def load_config(self):
        """Carrega configurações do sistema de visualização"""
        try:
            config_file = Path(self.config_path)
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
            else:
                self.config = {
                    "export_formats": ["obsidian", "markdown", "html", "json"],
                    "auto_refresh": True,
                    "graph_complexity": "adaptive",
                    "entity_types": {
                        "file": {"color": "blue", "shape": "rectangle"},
                        "module": {"color": "green", "shape": "ellipse"},
                        "class": {"color": "red", "shape": "diamond"},
                        "function": {"color": "yellow", "shape": "triangle"},
                        "concept": {"color": "purple", "shape": "circle"}
                    },
                    "relationship_types": {
                        "imports": {"color": "black", "style": "solid", "weight": 1},
                        "defines": {"color": "green", "style": "solid", "weight": 2},
                        "calls": {"color": "blue", "style": "dashed", "weight": 1},
                        "depends_on": {"color": "red", "style": "dotted", "weight": 3},
                        "related_to": {"color": "gray", "style": "dashed", "weight": 0.5}
                    },
                    "visualization": {
                        "node_size": 800,
                        "edge_width": 1.5,
                        "font_size": 10,
                        "layout": "spring"
                    },
                    "obsidian": {
                        "vault_path": "",
                        "template_directory": "templates/obsidian",
                        "create_backlinks": True
                    }
                }
                
                config_file.parent.mkdir(exist_ok=True, parents=True)
                with open(config_file, 'w', encoding='utf-8') as f:
                    json.dump(self.config, f, indent=2)
                    
            self.export_formats = self.config.get("export_formats", ["obsidian", "markdown", "html", "json"])
            
        except Exception as e:
            logger.error(f"Erro ao carregar configuração de visualização: {e}")
            
    def add_entity(self, entity_id: str, entity_type: str, metadata: Dict) -> bool:
        """Adiciona uma entidade ao grafo de conhecimento"""
        try:
            # Carregar entidades existentes
            with open(self.entities_file, 'r', encoding='utf-8') as f:
                entities_data = json.load(f)
                
            # Adicionar ou atualizar entidade
            entities_data["entities"][entity_id] = {
                "id": entity_id,
                "type": entity_type,
                "metadata": metadata,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            # Salvar entidades atualizadas
            with open(self.entities_file, 'w', encoding='utf-8') as f:
                json.dump(entities_data, f, indent=2)
                
            # Atualizar dicionário local
            self.entities[entity_id] = entities_data["entities"][entity_id]
            
            # Adicionar nó ao grafo
            self.graph.add_node(
                entity_id, 
                type=entity_type, 
                **metadata
            )
            
            logger.info(f"Entidade adicionada: {entity_id} (tipo: {entity_type})")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao adicionar entidade: {e}")
            return False
    
    def add_relationship(self, source_id: str, relation_type: str, target_id: str, metadata: Dict = None) -> bool:
        """Adiciona um relacionamento entre duas entidades"""
        if metadata is None:
            metadata = {}
            
        try:
            # Verificar se entidades existem
            with open(self.entities_file, 'r', encoding='utf-8') as f:
                entities_data = json.load(f)
                
            if source_id not in entities_data["entities"] or target_id not in entities_data["entities"]:
                logger.warning(f"Uma ou ambas entidades não existem: {source_id} -> {target_id}")
                return False
                
            # Carregar relacionamentos existentes
            with open(self.relationships_file, 'r', encoding='utf-8') as f:
                relationships_data = json.load(f)
                
            # Criar relacionamento
            relationship = {
                "source": source_id,
                "relation": relation_type,
                "target": target_id,
                "metadata": metadata,
                "created_at": datetime.now().isoformat()
            }
            
            # Adicionar relacionamento
            relationships_data["relationships"].append(relationship)
            
            # Salvar relacionamentos atualizados
            with open(self.relationships_file, 'w', encoding='utf-8') as f:
                json.dump(relationships_data, f, indent=2)
                
            # Atualizar lista local
            self.relationships[source_id].append((relation_type, target_id, metadata))
            
            # Adicionar aresta ao grafo
            self.graph.add_edge(
                source_id, 
                target_id, 
                relation=relation_type,
                **metadata
            )
            
            logger.info(f"Relacionamento adicionado: {source_id} -[{relation_type}]-> {target_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao adicionar relacionamento: {e}")
            return False
    
    def analyze_code_files(self, directory: Union[str, Path], file_pattern: str = "*.py") -> Dict:
        """
        Analisa arquivos de código para construir o grafo de conhecimento
        Retorna estatísticas da análise
        """
        directory = Path(directory)
        if not directory.exists():
            logger.error(f"Diretório não encontrado: {directory}")
            return {"error": f"Diretório não encontrado: {directory}"}
            
        stats = {
            "files_analyzed": 0,
            "entities_added": 0,
            "relationships_added": 0,
            "errors": 0
        }
        
        try:
            # Analisar todos os arquivos que correspondem ao padrão
            for file_path in directory.glob(file_pattern):
                try:
                    logger.info(f"Analisando arquivo: {file_path}")
                    
                    # Adicionar arquivo como entidade
                    file_id = str(file_path.relative_to(directory.parent))
                    file_metadata = {
                        "path": str(file_path),
                        "size": file_path.stat().st_size,
                        "last_modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                    }
                    
                    if self.add_entity(file_id, "file", file_metadata):
                        stats["entities_added"] += 1
                    
                    # Analisar conteúdo do arquivo
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    # Encontrar importações
                    imports = self._extract_imports(content)
                    for imp in imports:
                        # Adicionar módulo importado como entidade
                        if self.add_entity(imp, "module", {"imported_by": file_id}):
                            stats["entities_added"] += 1
                        
                        # Adicionar relacionamento de importação
                        if self.add_relationship(file_id, "imports", imp, {}):
                            stats["relationships_added"] += 1
                    
                    # Encontrar classes
                    classes = self._extract_classes(content)
                    for cls_name in classes:
                        cls_id = f"{file_id}::{cls_name}"
                        
                        # Adicionar classe como entidade
                        if self.add_entity(cls_id, "class", {"defined_in": file_id}):
                            stats["entities_added"] += 1
                        
                        # Adicionar relacionamento de definição
                        if self.add_relationship(file_id, "defines", cls_id, {}):
                            stats["relationships_added"] += 1
                    
                    # Encontrar funções
                    functions = self._extract_functions(content)
                    for func_name in functions:
                        func_id = f"{file_id}::{func_name}"
                        
                        # Adicionar função como entidade
                        if self.add_entity(func_id, "function", {"defined_in": file_id}):
                            stats["entities_added"] += 1
                        
                        # Adicionar relacionamento de definição
                        if self.add_relationship(file_id, "defines", func_id, {}):
                            stats["relationships_added"] += 1
                    
                    stats["files_analyzed"] += 1
                    
                except Exception as e:
                    logger.error(f"Erro ao analisar arquivo {file_path}: {e}")
                    stats["errors"] += 1
            
            return stats
            
        except Exception as e:
            logger.error(f"Erro ao analisar arquivos: {e}")
            return {"error": str(e)}
    
    def _extract_imports(self, content: str) -> List[str]:
        """Extrai importações de um arquivo Python"""
        imports = []
        import_pattern = r'^import\s+([^\s;]+)|^from\s+([^\s;]+)\s+import'
        
        for line in content.split('\n'):
            match = re.search(import_pattern, line)
            if match:
                module = match.group(1) or match.group(2)
                if module and module not in imports:
                    imports.append(module)
                    
        return imports
    
    def _extract_classes(self, content: str) -> List[str]:
        """Extrai classes de um arquivo Python"""
        classes = []
        class_pattern = r'^class\s+([^\s(:]+)'
        
        for line in content.split('\n'):
            match = re.search(class_pattern, line)
            if match:
                class_name = match.group(1)
                if class_name and class_name not in classes:
                    classes.append(class_name)
                    
        return classes
    
    def _extract_functions(self, content: str) -> List[str]:
        """Extrai funções de um arquivo Python"""
        functions = []
        function_pattern = r'^def\s+([^\s(]+)'
        
        for line in content.split('\n'):
            match = re.search(function_pattern, line)
            if match:
                function_name = match.group(1)
                if function_name and function_name not in functions:
                    functions.append(function_name)
                    
        return functions
    
    def analyze_text_content(self, text: str, context_id: str) -> Dict:
        """
        Analisa conteúdo de texto para extrair entidades e relacionamentos
        utilizando processamento de linguagem natural
        """
        if not SPACY_AVAILABLE or not self.nlp:
            logger.warning("SpaCy não está disponível para análise de texto")
            return {"error": "SpaCy não está disponível"}
            
        stats = {
            "entities_added": 0,
            "relationships_added": 0
        }
        
        try:
            # Processar texto com SpaCy
            doc = self.nlp(text)
            
            # Extrair entidades nomeadas
            for ent in doc.ents:
                entity_id = f"{ent.text.lower().replace(' ', '_')}::{ent.label_}"
                entity_metadata = {
                    "text": ent.text,
                    "label": ent.label_,
                    "context": context_id
                }
                
                if self.add_entity(entity_id, "concept", entity_metadata):
                    stats["entities_added"] += 1
                
                # Relacionar entidade com o contexto
                if self.add_relationship(context_id, "mentions", entity_id, {}):
                    stats["relationships_added"] += 1
            
            # Extrair relacionamentos baseados em dependência sintática
            for sent in doc.sents:
                for token in sent:
                    if token.dep_ in ["nsubj", "nsubjpass"] and token.head.pos_ == "VERB":
                        subj = token.text.lower().replace(' ', '_')
                        verb = token.head.text.lower()
                        
                        for child in token.head.children:
                            if child.dep_ in ["dobj", "pobj"]:
                                obj = child.text.lower().replace(' ', '_')
                                
                                # Criar entidades para sujeito e objeto
                                subj_id = f"{subj}::concept"
                                obj_id = f"{obj}::concept"
                                
                                if self.add_entity(subj_id, "concept", {"text": token.text, "context": context_id}):
                                    stats["entities_added"] += 1
                                    
                                if self.add_entity(obj_id, "concept", {"text": child.text, "context": context_id}):
                                    stats["entities_added"] += 1
                                
                                # Adicionar relacionamento entre eles
                                if self.add_relationship(subj_id, verb, obj_id, {"sentence": sent.text}):
                                    stats["relationships_added"] += 1
            
            return stats
            
        except Exception as e:
            logger.error(f"Erro ao analisar texto: {e}")
            return {"error": str(e)}
    
    def visualize(self, output_file: str = None, entity_types: List[str] = None, relation_types: List[str] = None) -> bool:
        """
        Visualiza o grafo de conhecimento com Matplotlib
        Opcionalmente filtra por tipos de entidades e relacionamentos
        """
        try:
            # Filtrar nós e arestas se necessário
            if entity_types:
                nodes = [node for node, attrs in self.graph.nodes(data=True) if attrs.get('type') in entity_types]
                subgraph = self.graph.subgraph(nodes)
            else:
                subgraph = self.graph
                
            if relation_types:
                edges = [(u, v) for u, v, attrs in subgraph.edges(data=True) if attrs.get('relation') in relation_types]
                subgraph = subgraph.edge_subgraph(edges)
            
            # Configurar visualização
            plt.figure(figsize=(12, 10))
            
            # Definir layout
            layout_type = self.config.get("visualization", {}).get("layout", "spring")
            if layout_type == "spring":
                pos = nx.spring_layout(subgraph, seed=42)
            elif layout_type == "circular":
                pos = nx.circular_layout(subgraph)
            elif layout_type == "shell":
                pos = nx.shell_layout(subgraph)
            elif layout_type == "kamada_kawai":
                pos = nx.kamada_kawai_layout(subgraph)
            else:
                pos = nx.spring_layout(subgraph, seed=42)
            
            # Configurar cores e tamanhos dos nós
            node_colors = []
            node_sizes = []
            entity_colors = self.config.get("entity_types", {})
            
            for node in subgraph.nodes():
                node_type = subgraph.nodes[node].get('type', 'generic')
                color = entity_colors.get(node_type, {}).get("color", "blue")
                node_colors.append(color)
                node_sizes.append(self.config.get("visualization", {}).get("node_size", 800))
            
            # Configurar cores e estilos das arestas
            edge_colors = []
            edge_widths = []
            edge_styles = []
            relationship_types = self.config.get("relationship_types", {})
            
            for u, v, data in subgraph.edges(data=True):
                relation = data.get('relation', 'generic')
                rel_config = relationship_types.get(relation, {})
                edge_colors.append(rel_config.get("color", "black"))
                edge_widths.append(rel_config.get("weight", 1) * self.config.get("visualization", {}).get("edge_width", 1.5))
                edge_styles.append(rel_config.get("style", "solid"))
            
            # Desenhar nós
            nx.draw_networkx_nodes(
                subgraph, 
                pos, 
                node_size=node_sizes,
                node_color=node_colors, 
                alpha=0.8
            )
            
            # Desenhar arestas
            for (u, v, data), color, width, style in zip(subgraph.edges(data=True), edge_colors, edge_widths, edge_styles):
                nx.draw_networkx_edges(
                    subgraph, 
                    pos, 
                    edgelist=[(u, v)],
                    width=width,
                    edge_color=color,
                    style=style
                )
            
            # Desenhar rótulos
            nx.draw_networkx_labels(
                subgraph, 
                pos, 
                font_size=self.config.get("visualization", {}).get("font_size", 10),
                font_family='sans-serif'
            )
            
            # Adicionar rótulos nas arestas
            edge_labels = {(u, v): data.get('relation', '') for u, v, data in subgraph.edges(data=True)}
            nx.draw_networkx_edge_labels(
                subgraph, 
                pos, 
                edge_labels=edge_labels,
                font_size=self.config.get("visualization", {}).get("font_size", 10) - 2
            )
            
            # Configurar plot
            plt.axis('off')
            plt.title('Knowledge Graph')
            plt.tight_layout()
            
            # Salvar ou mostrar
            if output_file:
                plt.savefig(output_file, format='png', dpi=300, bbox_inches='tight')
                logger.info(f"Grafo salvo em: {output_file}")
            else:
                plt.show()
                
            plt.close()
            return True
            
        except Exception as e:
            logger.error(f"Erro ao visualizar grafo: {e}")
            return False
    
    def export_to_obsidian(self, output_dir: str) -> bool:
        """
        Exporta o grafo de conhecimento para o formato do Obsidian
        Cria arquivos markdown interconectados com links wiki
        """
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True, parents=True)
        
        try:
            # Carregar entidades e relacionamentos
            with open(self.entities_file, 'r', encoding='utf-8') as f:
                entities_data = json.load(f)
                
            with open(self.relationships_file, 'r', encoding='utf-8') as f:
                relationships_data = json.load(f)
                
            # Criar arquivo para cada entidade
            for entity_id, entity in entities_data["entities"].items():
                # Criar nome de arquivo seguro
                safe_filename = re.sub(r'[^\w\s-]', '_', entity_id).strip().lower()
                file_path = output_path / f"{safe_filename}.md"
                
                # Metadados YAML para o Obsidian
                yaml_header = f"""---
id: "{entity_id}"
type: "{entity['type']}"
created: {entity['created_at']}
updated: {entity['updated_at']}
---

"""
                
                # Conteúdo principal
                content = f"# {entity_id}\n\n"
                content += f"## Type: {entity['type']}\n\n"
                
                # Adicionar metadados
                content += "## Metadata\n\n"
                for key, value in entity['metadata'].items():
                    content += f"- **{key}**: {value}\n"
                
                # Adicionar relacionamentos de saída
                outgoing = [rel for rel in relationships_data["relationships"] if rel["source"] == entity_id]
                if outgoing:
                    content += "\n## Outgoing Relationships\n\n"
                    for rel in outgoing:
                        target_name = rel["target"]
                        safe_target = re.sub(r'[^\w\s-]', '_', target_name).strip().lower()
                        content += f"- **{rel['relation']}** → [[{safe_target}]]\n"
                
                # Adicionar relacionamentos de entrada
                incoming = [rel for rel in relationships_data["relationships"] if rel["target"] == entity_id]
                if incoming:
                    content += "\n## Incoming Relationships\n\n"
                    for rel in incoming:
                        source_name = rel["source"]
                        safe_source = re.sub(r'[^\w\s-]', '_', source_name).strip().lower()
                        content += f"- **{rel['relation']}** ← [[{safe_source}]]\n"
                
                # Escrever arquivo
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(yaml_header + content)
                    
            # Criar arquivo de índice
            index_path = output_path / "index.md"
            
            index_content = """# Knowledge Graph Index

This index contains all entities in the knowledge graph.

## Entities by Type

"""
            
            # Agrupar entidades por tipo
            entities_by_type = defaultdict(list)
            for entity_id, entity in entities_data["entities"].items():
                entities_by_type[entity['type']].append(entity_id)
                
            # Adicionar links para cada entidade, agrupados por tipo
            for entity_type, entity_ids in entities_by_type.items():
                index_content += f"### {entity_type.capitalize()}\n\n"
                for entity_id in sorted(entity_ids):
                    safe_id = re.sub(r'[^\w\s-]', '_', entity_id).strip().lower()
                    index_content += f"- [[{safe_id}]]\n"
                index_content += "\n"
            
            # Escrever arquivo de índice
            with open(index_path, 'w', encoding='utf-8') as f:
                f.write(index_content)
                
            logger.info(f"Exportação para Obsidian concluída em: {output_dir}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao exportar para Obsidian: {e}")
            return False
    
    def export_to_json(self, output_file: str) -> bool:
        """
        Exporta o grafo de conhecimento para um arquivo JSON completo
        que pode ser importado por outras ferramentas
        """
        try:
            export_data = {
                "metadata": {
                    "exported_at": datetime.now().isoformat(),
                    "version": "1.0.0",
                    "entity_count": len(self.entities),
                    "relationship_count": sum(len(rels) for rels in self.relationships.values())
                },
                "graph": {
                    "nodes": [],
                    "edges": []
                }
            }
            
            # Adicionar nós
            for node, attrs in self.graph.nodes(data=True):
                node_data = {
                    "id": node,
                    **attrs
                }
                export_data["graph"]["nodes"].append(node_data)
                
            # Adicionar arestas
            for source, target, attrs in self.graph.edges(data=True):
                edge_data = {
                    "source": source,
                    "target": target,
                    **attrs
                }
                export_data["graph"]["edges"].append(edge_data)
                
            # Escrever arquivo
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2)
                
            logger.info(f"Exportação para JSON concluída em: {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao exportar para JSON: {e}")
            return False
    
    def get_status(self) -> Dict:
        """Retorna o status do sistema de visualização"""
        status = {
            "entity_count": len(self.entities),
            "relationship_count": sum(len(rels) for rels in self.relationships.values()),
            "graph_nodes": self.graph.number_of_nodes(),
            "graph_edges": self.graph.number_of_edges(),
            "spacy_available": SPACY_AVAILABLE and self.nlp is not None,
            "export_formats": self.export_formats,
            "timestamp": datetime.now().isoformat()
        }
        
        # Adicionar estatísticas por tipo
        try:
            with open(self.entities_file, 'r', encoding='utf-8') as f:
                entities_data = json.load(f)
                
            entity_type_counts = defaultdict(int)
            for entity in entities_data["entities"].values():
                entity_type_counts[entity["type"]] += 1
                
            status["entity_type_counts"] = dict(entity_type_counts)
            
            with open(self.relationships_file, 'r', encoding='utf-8') as f:
                relationships_data = json.load(f)
                
            relation_type_counts = defaultdict(int)
            for rel in relationships_data["relationships"]:
                relation_type_counts[rel["relation"]] += 1
                
            status["relation_type_counts"] = dict(relation_type_counts)
            
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas detalhadas: {e}")
            
        return status

# Função para teste direto do módulo
def main():
    """Função para teste do módulo"""
    kg = KnowledgeGraph()
    
    print("\n" + "="*50)
    print("EVA & GUARANI - Knowledge Graph System")
    print("="*50)
    
    # Adicionar algumas entidades e relacionamentos de exemplo
    kg.add_entity("python", "language", {"description": "Linguagem de programação Python"})
    kg.add_entity("javascript", "language", {"description": "Linguagem de programação JavaScript"})
    kg.add_entity("data_science", "concept", {"description": "Ciência de dados"})
    kg.add_entity("web_development", "concept", {"description": "Desenvolvimento web"})
    
    kg.add_relationship("python", "used_in", "data_science", {"strength": 0.9})
    kg.add_relationship("javascript", "used_in", "web_development", {"strength": 0.95})
    kg.add_relationship("python", "related_to", "javascript", {"strength": 0.7})
    kg.add_relationship("data_science", "related_to", "web_development", {"strength": 0.6})
    
    # Visualizar grafo
    kg.visualize("test_graph.png")
    
    # Exportar para Obsidian
    kg.export_to_obsidian("data/obsidian_export")
    
    # Exportar para JSON
    kg.export_to_json("data/knowledge_graph_export.json")
    
    # Mostrar status
    status = kg.get_status()
    print(f"Status do sistema:")
    for key, value in status.items():
        print(f"- {key}: {value}")
    
    print("="*50)
    return 0

if __name__ == "__main__":
    main()
