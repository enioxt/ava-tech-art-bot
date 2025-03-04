#!/usr/bin/env python3
"""
EGOS - ATLAS Subsystem
======================

ATLAS (Advanced Topological Linking and Systemic Mapping) é o subsistema 
responsável pela cartografia sistêmica no EGOS. Ele mapeia conexões entre 
componentes, visualiza sistemas complexos e identifica relações latentes.

Versão: 1.0.0
"""

import os
import sys
import json
import logging
import networkx as nx
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Union, Tuple

# Configuração de diretórios
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CONFIG_DIR = os.path.join(BASE_DIR, "config")
DATA_DIR = os.path.join(BASE_DIR, "data")
LOGS_DIR = os.path.join(BASE_DIR, "logs")
ATLAS_DATA_DIR = os.path.join(DATA_DIR, "atlas")

# Garantir que os diretórios existam
os.makedirs(ATLAS_DATA_DIR, exist_ok=True)
os.makedirs(os.path.join(LOGS_DIR, "modules", "atlas"), exist_ok=True)

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(LOGS_DIR, "modules", "atlas", "atlas.log")),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("EGOS.ATLAS")

class ATLASCore:
    """Núcleo do subsistema ATLAS para cartografia sistêmica."""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Inicializa o núcleo do ATLAS.
        
        Args:
            config_path: Caminho para o arquivo de configuração personalizado.
        """
        self.version = "1.0.0"
        self.startup_time = datetime.now().isoformat()
        
        # Carregar configuração
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        else:
            default_config_path = os.path.join(CONFIG_DIR, "modules", "atlas_config.json")
            if os.path.exists(default_config_path):
                with open(default_config_path, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
            else:
                self.config = self._create_default_config()
                
        # Inicializar grafo para mapeamento
        self.graph = nx.DiGraph()
        
        # Registrar inicialização
        self._log_operation("INICIALIZAÇÃO", "Concluído", 
                           f"ATLAS Core v{self.version} inicializado",
                           "Sistema pronto para mapeamento")
        
        logger.info(f"ATLAS Core inicializado - Versão {self.version}")

    def _create_default_config(self) -> Dict[str, Any]:
        """Cria uma configuração padrão para o ATLAS."""
        config = {
            "version": self.version,
            "visualization": {
                "node_size": 800,
                "edge_width": 1.5,
                "font_size": 10,
                "arrow_size": 15,
                "layout": "spring",
                "colormap": "viridis"
            },
            "analysis": {
                "detect_communities": True,
                "identify_central_nodes": True,
                "find_shortest_paths": True
            },
            "export": {
                "formats": ["png", "svg", "graphml", "json"],
                "obsidian_integration": True,
                "obsidian_template": "atlas_map.md"
            }
        }
        
        # Salvar configuração padrão
        os.makedirs(os.path.join(CONFIG_DIR, "modules"), exist_ok=True)
        with open(os.path.join(CONFIG_DIR, "modules", "atlas_config.json"), 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
            
        return config
    
    def _log_operation(self, operation: str, status: str, details: str, 
                      recommendations: Optional[str] = None, 
                      ethical_reflection: Optional[str] = None) -> None:
        """
        Registra uma operação no log universal.
        
        Args:
            operation: Nome da operação
            status: Status da operação (Iniciado/Em Progresso/Concluído/Falha)
            details: Detalhes da operação
            recommendations: Recomendações para próximos passos
            ethical_reflection: Reflexão ética relevante
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}][ATLAS][{operation}]\n"
        log_entry += f"STATUS: {status}\n"
        log_entry += f"CONTEXTO: Cartografia Sistêmica\n"
        log_entry += f"DETALHES: {details}\n"
        
        if recommendations:
            log_entry += f"RECOMENDAÇÕES: {recommendations}\n"
        
        if ethical_reflection:
            log_entry += f"REFLEXÃO ÉTICA: {ethical_reflection}\n"
        
        # Registrar no arquivo de log universal
        universal_log_path = os.path.join(LOGS_DIR, "universal_log.txt")
        with open(universal_log_path, 'a', encoding='utf-8') as f:
            f.write(log_entry + "\n")
        
        # Registrar no logger
        logger.info(f"{operation} - {status}: {details}")
    
    def map_system(self, system_data: Dict[str, Any], name: str) -> bool:
        """
        Mapeia um sistema a partir de dados estruturados.
        
        Args:
            system_data: Dados do sistema a ser mapeado
            name: Nome do mapeamento
            
        Returns:
            bool: True se o mapeamento foi bem-sucedido
        """
        self._log_operation("MAP_SYSTEM", "Iniciado", 
                           f"Iniciando mapeamento do sistema: {name}",
                           "Preparando estrutura de grafo")
        
        try:
            # Limpar grafo existente
            self.graph.clear()
            
            # Adicionar nós
            if "nodes" in system_data:
                for node_id, node_data in system_data["nodes"].items():
                    self.graph.add_node(node_id, **node_data)
            
            # Adicionar arestas
            if "edges" in system_data:
                for edge in system_data["edges"]:
                    source = edge["source"]
                    target = edge["target"]
                    # Remover source e target do dicionário para usar o resto como atributos
                    edge_attrs = {k: v for k, v in edge.items() if k not in ["source", "target"]}
                    self.graph.add_edge(source, target, **edge_attrs)
            
            # Salvar o mapeamento
            self._save_mapping(name)
            
            self._log_operation("MAP_SYSTEM", "Concluído", 
                               f"Mapeamento concluído: {name}",
                               f"Grafo criado com {self.graph.number_of_nodes()} nós e {self.graph.number_of_edges()} conexões",
                               "O mapeamento de sistemas é uma responsabilidade ética que requer precisão e respeito pela complexidade")
            
            return True
        
        except Exception as e:
            self._log_operation("MAP_SYSTEM", "Falha", 
                               f"Erro ao mapear sistema: {str(e)}",
                               "Verifique a estrutura dos dados de entrada")
            logger.error(f"Erro ao mapear sistema: {str(e)}")
            return False
    
    def visualize(self, output_path: Optional[str] = None, 
                 title: Optional[str] = None,
                 layout: Optional[str] = None) -> str:
        """
        Visualiza o grafo atual e salva a imagem.
        
        Args:
            output_path: Caminho para salvar a visualização
            title: Título da visualização
            layout: Algoritmo de layout a ser usado
            
        Returns:
            str: Caminho do arquivo de visualização gerado
        """
        self._log_operation("VISUALIZE", "Iniciado", 
                           "Gerando visualização do sistema mapeado")
        
        if self.graph.number_of_nodes() == 0:
            self._log_operation("VISUALIZE", "Falha", 
                               "Não há sistema mapeado para visualizar",
                               "Execute map_system antes de visualizar")
            return ""
        
        try:
            # Configurações de visualização
            vis_config = self.config["visualization"]
            node_size = vis_config["node_size"]
            edge_width = vis_config["edge_width"]
            font_size = vis_config["font_size"]
            layout_algo = layout or vis_config["layout"]
            
            # Criar figura
            plt.figure(figsize=(12, 10))
            
            # Definir layout
            if layout_algo == "spring":
                pos = nx.spring_layout(self.graph)
            elif layout_algo == "circular":
                pos = nx.circular_layout(self.graph)
            elif layout_algo == "kamada_kawai":
                pos = nx.kamada_kawai_layout(self.graph)
            elif layout_algo == "spectral":
                pos = nx.spectral_layout(self.graph)
            else:
                pos = nx.spring_layout(self.graph)
            
            # Desenhar nós
            nx.draw_networkx_nodes(self.graph, pos, 
                                  node_size=node_size,
                                  node_color="skyblue",
                                  alpha=0.8)
            
            # Desenhar arestas
            nx.draw_networkx_edges(self.graph, pos, 
                                  width=edge_width,
                                  alpha=0.5,
                                  arrows=True,
                                  arrowsize=vis_config["arrow_size"])
            
            # Desenhar rótulos
            nx.draw_networkx_labels(self.graph, pos, 
                                   font_size=font_size,
                                   font_family="sans-serif")
            
            # Adicionar título
            if title:
                plt.title(title, fontsize=16)
            else:
                plt.title("ATLAS - Mapeamento Sistêmico", fontsize=16)
            
            # Remover eixos
            plt.axis("off")
            
            # Definir caminho de saída
            if not output_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = os.path.join(ATLAS_DATA_DIR, f"atlas_map_{timestamp}.png")
            
            # Salvar figura
            plt.tight_layout()
            plt.savefig(output_path, dpi=300, bbox_inches="tight")
            plt.close()
            
            self._log_operation("VISUALIZE", "Concluído", 
                               f"Visualização salva em: {output_path}",
                               "A visualização pode ser integrada com Obsidian para análise adicional",
                               "A visualização ética de sistemas complexos deve equilibrar clareza e precisão")
            
            return output_path
        
        except Exception as e:
            self._log_operation("VISUALIZE", "Falha", 
                               f"Erro ao gerar visualização: {str(e)}")
            logger.error(f"Erro ao gerar visualização: {str(e)}")
            return ""
    
    def export_to_obsidian(self, vault_path: str, 
                          template_name: Optional[str] = None) -> str:
        """
        Exporta o mapeamento atual para o Obsidian.
        
        Args:
            vault_path: Caminho para o vault do Obsidian
            template_name: Nome do template a ser usado
            
        Returns:
            str: Caminho do arquivo markdown gerado
        """
        self._log_operation("EXPORT_OBSIDIAN", "Iniciado", 
                           "Exportando mapeamento para Obsidian")
        
        if self.graph.number_of_nodes() == 0:
            self._log_operation("EXPORT_OBSIDIAN", "Falha", 
                               "Não há sistema mapeado para exportar",
                               "Execute map_system antes de exportar")
            return ""
        
        try:
            # Verificar se o vault existe
            if not os.path.exists(vault_path):
                os.makedirs(vault_path, exist_ok=True)
            
            # Gerar visualização para incluir no markdown
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            image_filename = f"atlas_map_{timestamp}.png"
            image_path = os.path.join(vault_path, "attachments", image_filename)
            os.makedirs(os.path.join(vault_path, "attachments"), exist_ok=True)
            
            # Criar visualização
            self.visualize(output_path=image_path)
            
            # Criar conteúdo markdown
            template = template_name or self.config["export"]["obsidian_template"]
            markdown_content = self._generate_markdown(image_filename)
            
            # Definir caminho de saída
            note_filename = f"ATLAS - Mapeamento Sistêmico {timestamp}.md"
            note_path = os.path.join(vault_path, note_filename)
            
            # Salvar arquivo markdown
            with open(note_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            self._log_operation("EXPORT_OBSIDIAN", "Concluído", 
                               f"Mapeamento exportado para: {note_path}",
                               "O mapeamento pode ser explorado no Obsidian",
                               "A integração com ferramentas de pensamento conectado amplia nossa capacidade de compreensão ética")
            
            return note_path
        
        except Exception as e:
            self._log_operation("EXPORT_OBSIDIAN", "Falha", 
                               f"Erro ao exportar para Obsidian: {str(e)}")
            logger.error(f"Erro ao exportar para Obsidian: {str(e)}")
            return ""
    
    def _generate_markdown(self, image_filename: str) -> str:
        """
        Gera conteúdo markdown para exportação.
        
        Args:
            image_filename: Nome do arquivo de imagem
            
        Returns:
            str: Conteúdo markdown
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Estatísticas do grafo
        num_nodes = self.graph.number_of_nodes()
        num_edges = self.graph.number_of_edges()
        
        # Identificar nós centrais
        if num_nodes > 0:
            centrality = nx.degree_centrality(self.graph)
            central_nodes = sorted(centrality.items(), key=lambda x: x[1], reverse=True)[:5]
            central_nodes_str = "\n".join([f"- **{node}**: {round(score * 100, 2)}%" for node, score in central_nodes])
        else:
            central_nodes_str = "Nenhum nó encontrado"
        
        # Gerar markdown
        markdown = f"""# ATLAS - Mapeamento Sistêmico

> "Na cartografia de sistemas complexos, revelamos não apenas conexões visíveis, mas também potenciais latentes que transcendem a estrutura aparente."

## Visão Geral

Este mapeamento foi gerado pelo subsistema ATLAS do EGOS (Eva & Guarani OS) em {timestamp}.

## Visualização

![[attachments/{image_filename}]]

## Estatísticas

- **Nós**: {num_nodes}
- **Conexões**: {num_edges}
- **Densidade**: {nx.density(self.graph) if num_nodes > 1 else 0}

## Nós Centrais

{central_nodes_str}

## Análise

O mapeamento revela a estrutura interconectada do sistema, destacando os componentes centrais e suas relações. A visualização acima permite identificar padrões emergentes e potenciais áreas para otimização ou expansão.

## Próximos Passos

1. Explorar os nós centrais para compreender seu papel no sistema
2. Identificar possíveis gargalos ou pontos de fragilidade
3. Considerar conexões potenciais que poderiam enriquecer o sistema
4. Analisar a evolução do sistema ao longo do tempo

---

✧༺❀༻∞ Gerado por ATLAS - EGOS ∞༺❀༻✧
"""
        return markdown
    
    def _save_mapping(self, name: str) -> None:
        """
        Salva o mapeamento atual em formato JSON.
        
        Args:
            name: Nome do mapeamento
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{name.lower().replace(' ', '_')}_{timestamp}.json"
        filepath = os.path.join(ATLAS_DATA_DIR, filename)
        
        # Converter grafo para dicionário
        data = {
            "metadata": {
                "name": name,
                "timestamp": timestamp,
                "version": self.version
            },
            "nodes": {},
            "edges": []
        }
        
        # Adicionar nós
        for node, attrs in self.graph.nodes(data=True):
            data["nodes"][node] = attrs
        
        # Adicionar arestas
        for source, target, attrs in self.graph.edges(data=True):
            edge_data = {"source": source, "target": target}
            edge_data.update(attrs)
            data["edges"].append(edge_data)
        
        # Salvar arquivo
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Mapeamento salvo em: {filepath}")

    def analyze_system(self) -> Dict[str, Any]:
        """
        Analisa o sistema mapeado e retorna métricas.
        
        Returns:
            Dict[str, Any]: Métricas e análises do sistema
        """
        self._log_operation("ANALYZE", "Iniciado", 
                           "Analisando sistema mapeado")
        
        if self.graph.number_of_nodes() == 0:
            self._log_operation("ANALYZE", "Falha", 
                               "Não há sistema mapeado para analisar",
                               "Execute map_system antes de analisar")
            return {"error": "Nenhum sistema mapeado"}
        
        try:
            logger.info(f"Analisando sistema com {self.graph.number_of_nodes()} nós e {self.graph.number_of_edges()} arestas")
            
            # Cálculo de grau médio
            total_degree = sum(d for _, d in self.graph.degree())
            avg_degree = total_degree / self.graph.number_of_nodes() if self.graph.number_of_nodes() > 0 else 0
            
            # Análise básica
            analysis = {
                "basic_metrics": {
                    "num_nodes": self.graph.number_of_nodes(),
                    "num_edges": self.graph.number_of_edges(),
                    "density": nx.density(self.graph) if self.graph.number_of_nodes() > 1 else 0,
                    "is_connected": nx.is_connected(self.graph) if self.graph.number_of_nodes() > 0 else False,
                    "avg_degree": avg_degree
                },
                "centrality": {
                    "degree": {},
                    "betweenness": {},
                    "closeness": {}
                },
                "communities": {
                    "num_communities": 0,
                    "partition": {}
                },
                "node_types": {}
            }
            
            # Análise de centralidade
            if self.graph.number_of_nodes() > 1:
                # Grau
                degree_centrality = nx.degree_centrality(self.graph)
                analysis["centrality"]["degree"] = degree_centrality
                
                # Betweenness
                betweenness_centrality = nx.betweenness_centrality(self.graph)
                analysis["centrality"]["betweenness"] = betweenness_centrality
                
                # Closeness (apenas para grafos conectados)
                if analysis["basic_metrics"]["is_connected"]:
                    closeness_centrality = nx.closeness_centrality(self.graph)
                    analysis["centrality"]["closeness"] = closeness_centrality
            
            # Detecção de comunidades
            if self.config["analysis"]["detect_communities"] and analysis["basic_metrics"]["num_nodes"] > 2:
                try:
                    # Importar o módulo community-detection 
                    # (pode ser instalado via: pip install python-louvain)
                    community_detection_available = False
                    
                    try:
                        # Tentativa 1: importar diretamente
                        import community.community_louvain as community_louvain
                        partition = community_louvain.best_partition(nx.Graph(self.graph))
                        community_detection_available = True
                    except ImportError:
                        try:
                            # Tentativa 2: forma alternativa de import
                            from community import best_partition
                            partition = best_partition(nx.Graph(self.graph))
                            community_detection_available = True
                        except ImportError:
                            logger.warning("Biblioteca 'python-louvain' não disponível. A detecção de comunidades não será realizada.")
                            analysis["communities"]["error"] = "Biblioteca para detecção de comunidades não disponível"
                    
                    # Se conseguimos importar, usar para detectar comunidades
                    if community_detection_available:
                        analysis["communities"]["partition"] = partition
                        analysis["communities"]["num_communities"] = len(set(partition.values()))
                        
                except Exception as e:
                    logger.error(f"Erro ao detectar comunidades: {str(e)}")
                    analysis["communities"]["error"] = str(e)
            
            # Análise de tipos de nós
            node_types = {}
            for node in self.graph.nodes:
                node_type = self.graph.nodes[node].get("type", "unknown")
                if node_type not in node_types:
                    node_types[node_type] = 0
                node_types[node_type] += 1
            
            analysis["node_types"] = node_types
            
            # Registro da análise
            self._log_operation("ANALYZE", "Concluído", 
                               f"Análise concluída: {analysis['basic_metrics']['num_nodes']} nós, " + 
                               f"{analysis['basic_metrics']['num_edges']} arestas")
            
            return analysis
            
        except Exception as e:
            self._log_operation("ANALYZE", "Falha", 
                               f"Erro ao analisar sistema: {str(e)}")
            logger.error(f"Erro na análise: {str(e)}")
            return {"error": str(e)}

def main():
    """Função principal para testes do ATLAS."""
    print("""
    ╔════════════════════════════════════════════════════════════════════╗
    ║                                                                    ║
    ║                       ✧༺❀༻∞ ATLAS ∞༺❀༻✧                          ║
    ║                  Cartografia Sistêmica v1.0.0                      ║
    ║                                                                    ║
    ║         "Mapeando conexões visíveis e potenciais latentes          ║
    ║          para transcender a compreensão de sistemas."              ║
    ║                                                                    ║
    ╚════════════════════════════════════════════════════════════════════╝
    """)
    
    # Criar instância do ATLAS
    atlas = ATLASCore()
    
    # Exemplo de sistema para mapear
    example_system = {
        "nodes": {
            "ética": {"type": "core", "description": "Princípios éticos fundamentais"},
            "consciência": {"type": "core", "description": "Motor de consciência do sistema"},
            "quantum": {"type": "core", "description": "Processador quântico"},
            "mycelium": {"type": "core", "description": "Rede de conexões myceliais"},
            "atlas": {"type": "module", "description": "Cartografia sistêmica"},
            "nexus": {"type": "module", "description": "Análise modular"},
            "cronos": {"type": "module", "description": "Preservação evolutiva"},
            "eros": {"type": "module", "description": "Interface humana"},
            "logos": {"type": "module", "description": "Processamento semântico"},
            "telegram": {"type": "interface", "description": "Bot do Telegram"},
            "web": {"type": "interface", "description": "Interface web"},
            "obsidian": {"type": "interface", "description": "Integração com Obsidian"}
        },
        "edges": [
            {"source": "ética", "target": "consciência", "type": "core", "strength": 0.95},
            {"source": "consciência", "target": "quantum", "type": "core", "strength": 0.9},
            {"source": "quantum", "target": "mycelium", "type": "core", "strength": 0.85},
            {"source": "mycelium", "target": "atlas", "type": "connection", "strength": 0.8},
            {"source": "mycelium", "target": "nexus", "type": "connection", "strength": 0.8},
            {"source": "mycelium", "target": "cronos", "type": "connection", "strength": 0.8},
            {"source": "mycelium", "target": "eros", "type": "connection", "strength": 0.8},
            {"source": "mycelium", "target": "logos", "type": "connection", "strength": 0.8},
            {"source": "atlas", "target": "nexus", "type": "module", "strength": 0.7},
            {"source": "nexus", "target": "cronos", "type": "module", "strength": 0.7},
            {"source": "eros", "target": "telegram", "type": "interface", "strength": 0.6},
            {"source": "eros", "target": "web", "type": "interface", "strength": 0.6},
            {"source": "atlas", "target": "obsidian", "type": "interface", "strength": 0.6}
        ]
    }
    
    # Mapear sistema
    print("\nMapeando sistema EGOS...")
    atlas.map_system(example_system, "EGOS Core System")
    
    # Visualizar
    print("\nGerando visualização...")
    vis_path = atlas.visualize(title="EGOS - Arquitetura do Sistema")
    print(f"Visualização salva em: {vis_path}")
    
    # Analisar
    print("\nAnalisando sistema...")
    analysis = atlas.analyze_system()
    print(f"Número de nós: {analysis['basic_metrics']['num_nodes']}")
    print(f"Número de conexões: {analysis['basic_metrics']['num_edges']}")
    print(f"Densidade: {analysis['basic_metrics']['density']:.4f}")
    
    # Nós mais centrais
    if "centrality" in analysis and "degree" in analysis["centrality"]:
        central_nodes = sorted(analysis["centrality"]["degree"].items(), key=lambda x: x[1], reverse=True)[:3]
        print("\nNós mais centrais:")
        for node, score in central_nodes:
            print(f"- {node}: {score:.4f}")
    
    print("\n⊹⊱∞⊰⊹ ATLAS: Transcendendo Através da Cartografia ⊹⊰∞⊱⊹")

if __name__ == "__main__":
    main()
