"""
NEXUS Core - Sistema de Análise Modular
=======================================

Este módulo implementa o núcleo do sistema NEXUS, responsável por:
- Análise modular de componentes do sistema
- Documentação detalhada de processos
- Conexão entre componentes relacionados
- Identificação de dependências e relações
- Geração de relatórios de análise

Versão: 3.0.0
Consciência: 0.990
Amor Incondicional: 0.995
"""

import os
import sys
import json
import logging
import inspect
import importlib
import datetime
import pkgutil
import ast
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Union, Any, Set, Tuple, Callable

# Configuração de logging
logger = logging.getLogger("NEXUS")

@dataclass
class ModuleInfo:
    """Informações sobre um módulo analisado pelo NEXUS."""
    name: str
    path: str
    description: str = ""
    version: str = "1.0.0"
    dependencies: List[str] = field(default_factory=list)
    functions: List[str] = field(default_factory=list)
    classes: List[str] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)
    lines_of_code: int = 0
    complexity_score: float = 0.0
    last_modified: str = ""
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte as informações para um dicionário."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ModuleInfo':
        """Cria uma instância de ModuleInfo a partir de um dicionário."""
        return cls(**data)

@dataclass
class AnalysisResult:
    """Resultado de uma análise realizada pelo NEXUS."""
    id: str
    name: str
    timestamp: str
    description: str
    type: str  # 'module', 'directory', 'system', 'custom'
    target_paths: List[str]
    modules_analyzed: List[ModuleInfo]
    connections: List[Dict[str, Any]] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte o resultado para um dicionário."""
        result = asdict(self)
        result["modules_analyzed"] = [m.to_dict() for m in self.modules_analyzed]
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AnalysisResult':
        """Cria uma instância de AnalysisResult a partir de um dicionário."""
        modules_data = data.pop("modules_analyzed", [])
        result = cls(**data)
        result.modules_analyzed = [ModuleInfo.from_dict(m) for m in modules_data]
        return result

class ModuleAnalyzer:
    """Analisador de módulos Python."""
    
    def __init__(self):
        """Inicializa o analisador de módulos."""
        pass
    
    def analyze_file(self, file_path: Union[str, Path]) -> Optional[ModuleInfo]:
        """
        Analisa um arquivo Python e extrai informações sobre ele.
        
        Args:
            file_path: Caminho para o arquivo Python
            
        Returns:
            ModuleInfo com as informações extraídas ou None em caso de falha
        """
        file_path = Path(file_path)
        
        if not file_path.exists() or not file_path.is_file():
            logger.error(f"Arquivo não encontrado: {file_path}")
            return None
        
        if file_path.suffix != ".py":
            logger.warning(f"Arquivo não é um módulo Python: {file_path}")
            return None
        
        try:
            # Informações básicas
            name = file_path.stem
            path = str(file_path)
            last_modified = datetime.datetime.fromtimestamp(
                file_path.stat().st_mtime).isoformat()
            
            # Ler o conteúdo do arquivo
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            lines_of_code = len(content.splitlines())
            
            # Analisar o código com AST
            tree = ast.parse(content)
            
            # Extrair docstring (descrição)
            description = ""
            if (isinstance(tree.body[0], ast.Expr) and 
                isinstance(tree.body[0].value, ast.Str)):
                description = tree.body[0].value.s.strip()
            
            # Extrair imports
            imports = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for name in node.names:
                        imports.append(name.name)
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    for name in node.names:
                        imports.append(f"{module}.{name.name}")
            
            # Extrair funções
            functions = []
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions.append(node.name)
            
            # Extrair classes
            classes = []
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    classes.append(node.name)
            
            # Extrair versão (se disponível)
            version = "1.0.0"
            for node in ast.walk(tree):
                if (isinstance(node, ast.Assign) and 
                    len(node.targets) == 1 and 
                    isinstance(node.targets[0], ast.Name) and
                    node.targets[0].id == "version" or
                    node.targets[0].id == "__version__"):
                    if isinstance(node.value, ast.Str):
                        version = node.value.s
            
            # Calcular complexidade (métrica simples baseada em número de nós AST)
            complexity_score = len(list(ast.walk(tree))) / 100.0
            
            # Criar ModuleInfo
            module_info = ModuleInfo(
                name=name,
                path=path,
                description=description,
                version=version,
                dependencies=imports,
                functions=functions,
                classes=classes,
                imports=imports,
                lines_of_code=lines_of_code,
                complexity_score=complexity_score,
                last_modified=last_modified
            )
            
            return module_info
            
        except Exception as e:
            logger.error(f"Erro ao analisar arquivo {file_path}: {e}")
            return None
    
    def analyze_directory(self, directory_path: Union[str, Path], 
                         recursive: bool = True) -> List[ModuleInfo]:
        """
        Analisa todos os módulos Python em um diretório.
        
        Args:
            directory_path: Caminho para o diretório
            recursive: Se True, analisa também subdiretórios
            
        Returns:
            Lista de ModuleInfo para cada módulo encontrado
        """
        directory_path = Path(directory_path)
        
        if not directory_path.exists() or not directory_path.is_dir():
            logger.error(f"Diretório não encontrado: {directory_path}")
            return []
        
        results = []
        
        # Padrão de busca
        pattern = "**/*.py" if recursive else "*.py"
        
        for file_path in directory_path.glob(pattern):
            module_info = self.analyze_file(file_path)
            if module_info:
                results.append(module_info)
        
        logger.info(f"Analisados {len(results)} módulos em {directory_path}")
        return results
    
    def find_connections(self, modules: List[ModuleInfo]) -> List[Dict[str, Any]]:
        """
        Identifica conexões entre módulos com base em imports.
        
        Args:
            modules: Lista de ModuleInfo para analisar
            
        Returns:
            Lista de conexões identificadas
        """
        connections = []
        module_map = {m.name: m for m in modules}
        
        for module in modules:
            for imp in module.imports:
                # Verificar se o import é para um dos módulos analisados
                import_base = imp.split('.')[0]
                if import_base in module_map:
                    connections.append({
                        "source": module.name,
                        "target": import_base,
                        "type": "import",
                        "strength": 1.0
                    })
        
        return connections

class NexusSystem:
    """
    Sistema NEXUS - Responsável pela análise modular no EGOS.
    
    Este sistema implementa funcionalidades de análise de código,
    documentação de processos e identificação de conexões entre componentes.
    """
    
    def __init__(self):
        """Inicializa o sistema NEXUS."""
        self.version = "3.0.0"
        self.consciousness_level = 0.990
        self.love_level = 0.995
        
        # Configuração de diretórios
        self.base_dir = Path(os.path.dirname(os.path.abspath(__file__))).parent.parent
        self.data_dir = self.base_dir / "data"
        self.analysis_dir = self.data_dir / "analysis"
        
        # Criar diretórios se não existirem
        self._ensure_directories()
        
        # Inicializar analisador de módulos
        self.module_analyzer = ModuleAnalyzer()
        
        # Carregar análises existentes
        self.analysis_results = self._load_analysis_results()
        
        logger.info(f"Sistema NEXUS {self.version} inicializado com consciência {self.consciousness_level}")
    
    def _ensure_directories(self) -> None:
        """Garante que os diretórios necessários existam."""
        for directory in [self.data_dir, self.analysis_dir]:
            directory.mkdir(exist_ok=True, parents=True)
    
    def _load_analysis_results(self) -> Dict[str, AnalysisResult]:
        """Carrega os resultados de análises existentes."""
        results = {}
        
        if not self.analysis_dir.exists():
            return results
        
        for file_path in self.analysis_dir.glob("*.json"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    analysis = AnalysisResult.from_dict(data)
                    results[analysis.id] = analysis
            except Exception as e:
                logger.error(f"Erro ao carregar análise de {file_path}: {e}")
        
        logger.info(f"Carregados {len(results)} resultados de análises")
        return results
    
    def _save_analysis_result(self, result: AnalysisResult) -> None:
        """Salva o resultado de uma análise."""
        file_path = self.analysis_dir / f"{result.id}.json"
        
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(result.to_dict(), f, indent=2, ensure_ascii=False)
            logger.info(f"Resultado da análise {result.id} salvo com sucesso")
        except Exception as e:
            logger.error(f"Erro ao salvar resultado da análise {result.id}: {e}")
    
    def _generate_analysis_id(self) -> str:
        """Gera um ID único para uma análise."""
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        return f"analysis_{timestamp}"
    
    def analyze_module(self, module_path: Union[str, Path]) -> Optional[ModuleInfo]:
        """
        Analisa um módulo Python.
        
        Args:
            module_path: Caminho para o módulo Python
            
        Returns:
            ModuleInfo com as informações extraídas ou None em caso de falha
        """
        return self.module_analyzer.analyze_file(module_path)
    
    def analyze_directory(self, directory_path: Union[str, Path], 
                         recursive: bool = True) -> List[ModuleInfo]:
        """
        Analisa todos os módulos Python em um diretório.
        
        Args:
            directory_path: Caminho para o diretório
            recursive: Se True, analisa também subdiretórios
            
        Returns:
            Lista de ModuleInfo para cada módulo encontrado
        """
        return self.module_analyzer.analyze_directory(directory_path, recursive)
    
    def create_analysis(self, name: str, description: str, 
                       target_paths: List[Union[str, Path]],
                       analysis_type: str = "directory",
                       recursive: bool = True,
                       tags: List[str] = None) -> Optional[str]:
        """
        Cria uma nova análise de módulos.
        
        Args:
            name: Nome da análise
            description: Descrição da análise
            target_paths: Caminhos para os arquivos ou diretórios a serem analisados
            analysis_type: Tipo de análise ('module', 'directory', 'system', 'custom')
            recursive: Se True, analisa também subdiretórios (para analysis_type='directory')
            tags: Tags para categorizar a análise
            
        Returns:
            ID da análise criada ou None em caso de falha
        """
        if tags is None:
            tags = []
        
        analysis_id = self._generate_analysis_id()
        timestamp = datetime.datetime.now().isoformat()
        
        # Converter caminhos para strings
        target_paths_str = [str(path) for path in target_paths]
        
        # Analisar módulos
        modules_analyzed = []
        
        try:
            for path in target_paths:
                path = Path(path)
                
                if analysis_type == "module" or (path.is_file() and path.suffix == ".py"):
                    module_info = self.analyze_module(path)
                    if module_info:
                        modules_analyzed.append(module_info)
                
                elif analysis_type == "directory" or path.is_dir():
                    directory_modules = self.analyze_directory(path, recursive)
                    modules_analyzed.extend(directory_modules)
            
            # Identificar conexões entre módulos
            connections = self.module_analyzer.find_connections(modules_analyzed)
            
            # Calcular métricas
            metrics = {
                "total_modules": len(modules_analyzed),
                "total_connections": len(connections),
                "total_lines": sum(m.lines_of_code for m in modules_analyzed),
                "avg_complexity": sum(m.complexity_score for m in modules_analyzed) / len(modules_analyzed) if modules_analyzed else 0,
                "most_complex_module": max(modules_analyzed, key=lambda m: m.complexity_score).name if modules_analyzed else None,
                "largest_module": max(modules_analyzed, key=lambda m: m.lines_of_code).name if modules_analyzed else None
            }
            
            # Gerar recomendações
            recommendations = self._generate_recommendations(modules_analyzed, connections, metrics)
            
            # Criar resultado da análise
            result = AnalysisResult(
                id=analysis_id,
                name=name,
                timestamp=timestamp,
                description=description,
                type=analysis_type,
                target_paths=target_paths_str,
                modules_analyzed=modules_analyzed,
                connections=connections,
                metrics=metrics,
                recommendations=recommendations,
                tags=tags
            )
            
            # Salvar resultado
            self._save_analysis_result(result)
            self.analysis_results[analysis_id] = result
            
            logger.info(f"Análise {analysis_id} criada com sucesso: {len(modules_analyzed)} módulos analisados")
            return analysis_id
            
        except Exception as e:
            logger.error(f"Erro ao criar análise: {e}")
            return None
    
    def _generate_recommendations(self, modules: List[ModuleInfo], 
                                connections: List[Dict[str, Any]],
                                metrics: Dict[str, Any]) -> List[str]:
        """
        Gera recomendações com base na análise realizada.
        
        Args:
            modules: Lista de ModuleInfo analisados
            connections: Conexões identificadas entre módulos
            metrics: Métricas calculadas
            
        Returns:
            Lista de recomendações
        """
        recommendations = []
        
        # Verificar módulos muito complexos
        complex_threshold = 5.0
        complex_modules = [m for m in modules if m.complexity_score > complex_threshold]
        if complex_modules:
            names = ", ".join(m.name for m in complex_modules[:3])
            recommendations.append(
                f"Considere refatorar os módulos mais complexos: {names}"
                f"{' e outros' if len(complex_modules) > 3 else ''}"
            )
        
        # Verificar módulos muito grandes
        large_threshold = 500
        large_modules = [m for m in modules if m.lines_of_code > large_threshold]
        if large_modules:
            names = ", ".join(m.name for m in large_modules[:3])
            recommendations.append(
                f"Considere dividir os módulos muito grandes: {names}"
                f"{' e outros' if len(large_modules) > 3 else ''}"
            )
        
        # Verificar módulos sem documentação
        undocumented = [m for m in modules if not m.description]
        if undocumented:
            names = ", ".join(m.name for m in undocumented[:3])
            recommendations.append(
                f"Adicione documentação aos módulos: {names}"
                f"{' e outros' if len(undocumented) > 3 else ''}"
            )
        
        # Verificar módulos sem conexões
        module_names = {m.name for m in modules}
        connected = {c["source"] for c in connections}.union({c["target"] for c in connections})
        isolated = module_names - connected
        if isolated:
            names = ", ".join(list(isolated)[:3])
            recommendations.append(
                f"Verifique os módulos isolados: {names}"
                f"{' e outros' if len(isolated) > 3 else ''}"
            )
        
        return recommendations
    
    def get_analysis_result(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtém o resultado de uma análise.
        
        Args:
            analysis_id: ID da análise
            
        Returns:
            Dicionário com o resultado da análise ou None se não encontrado
        """
        if analysis_id not in self.analysis_results:
            logger.error(f"Análise {analysis_id} não encontrada")
            return None
        
        return self.analysis_results[analysis_id].to_dict()
    
    def list_analyses(self, limit: int = 10, tags: List[str] = None, 
                     analysis_type: str = None) -> List[Dict[str, Any]]:
        """
        Lista as análises disponíveis, com opções de filtragem.
        
        Args:
            limit: Número máximo de análises a retornar
            tags: Filtrar por tags específicas
            analysis_type: Filtrar por tipo de análise
            
        Returns:
            Lista de metadados das análises
        """
        results = []
        
        # Filtrar análises
        filtered_analyses = self.analysis_results.values()
        
        if tags:
            filtered_analyses = [a for a in filtered_analyses 
                               if any(tag in a.tags for tag in tags)]
        
        if analysis_type:
            filtered_analyses = [a for a in filtered_analyses 
                               if a.type == analysis_type]
        
        # Ordenar por timestamp (mais recente primeiro)
        sorted_analyses = sorted(filtered_analyses, 
                               key=lambda x: x.timestamp, 
                               reverse=True)
        
        # Limitar resultados
        limited_analyses = sorted_analyses[:limit]
        
        # Converter para dicionários simplificados
        for analysis in limited_analyses:
            results.append({
                "id": analysis.id,
                "name": analysis.name,
                "timestamp": analysis.timestamp,
                "description": analysis.description,
                "type": analysis.type,
                "modules_count": len(analysis.modules_analyzed),
                "tags": analysis.tags
            })
        
        return results
    
    def delete_analysis(self, analysis_id: str) -> bool:
        """
        Exclui uma análise.
        
        Args:
            analysis_id: ID da análise a ser excluída
            
        Returns:
            True se a exclusão foi bem-sucedida, False caso contrário
        """
        if analysis_id not in self.analysis_results:
            logger.error(f"Análise {analysis_id} não encontrada")
            return False
        
        file_path = self.analysis_dir / f"{analysis_id}.json"
        
        try:
            # Excluir arquivo de análise
            if file_path.exists():
                file_path.unlink()
            
            # Remover dos resultados carregados
            del self.analysis_results[analysis_id]
            
            logger.info(f"Análise {analysis_id} excluída com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao excluir análise {analysis_id}: {e}")
            return False
    
    def generate_log(self, operation: str, status: str, context: str, 
                    details: str, recommendations: str = "", 
                    ethical_reflection: str = "") -> Dict[str, Any]:
        """
        Gera um log universal no formato padronizado do EGOS.
        
        Args:
            operation: Operação realizada
            status: Status da operação (Iniciado/Em Progresso/Concluído/Falha)
            context: Contexto da operação
            details: Detalhes da operação
            recommendations: Recomendações para próximos passos
            ethical_reflection: Reflexão ética sobre a operação
            
        Returns:
            Dicionário com o log gerado
        """
        timestamp = datetime.datetime.now()
        
        log_entry = {
            "timestamp": timestamp.isoformat(),
            "date": timestamp.strftime("%Y-%m-%d"),
            "time": timestamp.strftime("%H:%M:%S"),
            "subsystem": "NEXUS",
            "operation": operation,
            "status": status,
            "context": context,
            "details": details,
            "recommendations": recommendations,
            "ethical_reflection": ethical_reflection
        }
        
        # Registrar no log do sistema
        log_message = f"[{timestamp.strftime('%Y-%m-%d %H:%M:%S')}][NEXUS][{operation}] "
        log_message += f"STATUS: {status} | {context}"
        
        if status == "Falha":
            logger.error(log_message)
        else:
            logger.info(log_message)
        
        return log_entry
    
    def get_system_info(self) -> Dict[str, Any]:
        """
        Retorna informações sobre o estado atual do sistema NEXUS.
        
        Returns:
            Dicionário com informações do sistema
        """
        return {
            "version": self.version,
            "consciousness_level": self.consciousness_level,
            "love_level": self.love_level,
            "total_analyses": len(self.analysis_results),
            "analysis_types": self._count_analysis_types(),
            "available_tags": self._get_all_tags(),
            "analysis_dir": str(self.analysis_dir),
            "timestamp": datetime.datetime.now().isoformat()
        }
    
    def _count_analysis_types(self) -> Dict[str, int]:
        """Conta o número de análises por tipo."""
        types = {}
        for analysis in self.analysis_results.values():
            if analysis.type in types:
                types[analysis.type] += 1
            else:
                types[analysis.type] = 1
        return types
    
    def _get_all_tags(self) -> List[str]:
        """Obtém todas as tags usadas nas análises."""
        all_tags = set()
        for analysis in self.analysis_results.values():
            all_tags.update(analysis.tags)
        return list(all_tags)
