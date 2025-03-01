
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EVA & GUARANI - Backup Quântico Local
Versão: 2.0.0 - Build 2025.02.26

Este módulo realiza backup completo do sistema localmente,
armazenando configurações no MCP (Master Control Program) do cursor.
"""

import os
import sys
import json
import logging
import shutil
import datetime
import zipfile
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/quantum_backup.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("✨quantum-backup✨")

class QuantumBackup:
    """Sistema de backup quântico com integração ao MCP do cursor."""
    
    def __init__(self):
        """Inicializa o sistema de backup."""
        self.timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.backup_dir = Path(f"backup/quantum/backup_{self.timestamp}")
        self.mcp_config_file = Path("cursor/mcp/config_storage.json")
        self.system_dirs = [
            "config", "src", "core", "modules", "scripts",
            "data", "logs", "models", "output",
            "infinity_ai", "ava_mind", "consciousness", "quantum_memory"
        ]
        
    def create_backup_structure(self) -> None:
        """Cria a estrutura de diretórios para o backup."""
        logger.info(f"Criando estrutura de backup em {self.backup_dir}")
        
        # Cria diretório principal de backup
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Cria diretório para o MCP
        mcp_dir = self.backup_dir / "mcp_cursor"
        mcp_dir.mkdir(exist_ok=True)
        
        # Cria diretórios para cada componente do sistema
        for dir_name in self.system_dirs:
            (self.backup_dir / dir_name).mkdir(exist_ok=True)
            
        logger.info("Estrutura de backup criada com sucesso")
    
    def backup_system_files(self) -> None:
        """Realiza backup de todos os arquivos do sistema."""
        logger.info("Iniciando backup dos arquivos do sistema")
        
        for dir_name in self.system_dirs:
            source_dir = Path(dir_name)
            target_dir = self.backup_dir / dir_name
            
            if source_dir.exists():
                logger.info(f"Copiando arquivos de {source_dir} para {target_dir}")
                try:
                    if source_dir.is_dir():
                        shutil.copytree(source_dir, target_dir, dirs_exist_ok=True)
                    else:
                        shutil.copy2(source_dir, target_dir)
                except Exception as e:
                    logger.error(f"Erro ao copiar {source_dir}: {e}")
            else:
                logger.warning(f"Diretório {source_dir} não encontrado, pulando")
    
    def collect_configurations(self) -> Dict[str, Any]:
        """Coleta todas as configurações do sistema."""
        logger.info("Coletando configurações do sistema")
        
        configs = {
            "timestamp": self.timestamp,
            "version": "2.0.0",
            "build": "2025.02.26",
            "system": {},
            "modules": {},
            "quantum": {},
            "security": {}
        }
        
        # Coleta configurações do sistema
        try:
            if Path("config/system.json").exists():
                with open("config/system.json", "r", encoding="utf-8") as f:
                    configs["system"] = json.load(f)
        except Exception as e:
            logger.error(f"Erro ao ler configurações do sistema: {e}")
        
        # Coleta configurações dos módulos
        try:
            modules_dir = Path("modules")
            if modules_dir.exists():
                for module_config in modules_dir.glob("**/config.json"):
                    module_name = module_config.parent.name
                    with open(module_config, "r", encoding="utf-8") as f:
                        configs["modules"][module_name] = json.load(f)
        except Exception as e:
            logger.error(f"Erro ao ler configurações dos módulos: {e}")
        
        # Coleta configurações quânticas
        try:
            if Path("infinity_ai/quantum_config.json").exists():
                with open("infinity_ai/quantum_config.json", "r", encoding="utf-8") as f:
                    configs["quantum"] = json.load(f)
        except Exception as e:
            logger.error(f"Erro ao ler configurações quânticas: {e}")
        
        return configs
    
    def store_in_mcp(self, configs: Dict[str, Any]) -> None:
        """Armazena as configurações no MCP do cursor."""
        logger.info("Armazenando configurações no MCP do cursor")
        
        # Cria diretório do MCP se não existir
        self.mcp_config_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Salva configurações no MCP
        try:
            with open(self.mcp_config_file, "w", encoding="utf-8") as f:
                json.dump(configs, f, indent=2, ensure_ascii=False)
            logger.info(f"Configurações armazenadas com sucesso em {self.mcp_config_file}")
            
            # Cria cópia no diretório de backup
            backup_mcp_file = self.backup_dir / "mcp_cursor/config_storage.json"
            with open(backup_mcp_file, "w", encoding="utf-8") as f:
                json.dump(configs, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Erro ao armazenar configurações no MCP: {e}")
    
    def create_compressed_backup(self) -> None:
        """Cria um arquivo comprimido do backup."""
        logger.info("Criando arquivo comprimido do backup")
        
        zip_file_path = f"backup/quantum_backup_{self.timestamp}.zip"
        try:
            with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, _, files in os.walk(self.backup_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, self.backup_dir.parent)
                        zipf.write(file_path, arcname)
            
            logger.info(f"Backup comprimido criado com sucesso: {zip_file_path}")
        except Exception as e:
            logger.error(f"Erro ao criar arquivo comprimido: {e}")
    
    def generate_documentation(self) -> None:
        """Gera documentação do backup."""
        logger.info("Gerando documentação do backup")
        
        doc_content = f"""
# EVA & GUARANI - Documentação de Backup Quântico

## Informações Gerais
- **Data e Hora**: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- **Versão do Sistema**: 2.0.0
- **Build**: 2025.02.26
- **ID do Backup**: {self.timestamp}

## Conteúdo do Backup
- Arquivos do sistema
- Configurações do sistema
- Módulos e componentes
- Dados quânticos
- Configurações do MCP do cursor

## Localização
- Diretório principal: {self.backup_dir}
- Arquivo comprimido: backup/quantum_backup_{self.timestamp}.zip
- Configurações MCP: {self.mcp_config_file}

## Componentes Incluídos
{chr(10).join([f"- {dir_name}" for dir_name in self.system_dirs])}

## Instruções de Restauração
1. Descompacte o arquivo backup/quantum_backup_{self.timestamp}.zip
2. Copie os arquivos para seus respectivos diretórios
3. Restaure as configurações do MCP do cursor
4. Execute o script de verificação de integridade

## Observações
- Este backup contém todas as configurações e dados do sistema EVA & GUARANI
- As configurações foram armazenadas no MCP do cursor para acesso rápido
- Recomenda-se manter este backup em local seguro
"""
        
        # Salva a documentação
        doc_file = self.backup_dir / "BACKUP_DOCUMENTATION.md"
        try:
            with open(doc_file, "w", encoding="utf-8") as f:
                f.write(doc_content)
            logger.info(f"Documentação gerada com sucesso: {doc_file}")
        except Exception as e:
            logger.error(f"Erro ao gerar documentação: {e}")
    
    def run_backup(self) -> None:
        """Executa o processo completo de backup."""
        logger.info("Iniciando processo de backup quântico")
        
        try:
            # Cria estrutura de backup
            self.create_backup_structure()
            
            # Realiza backup dos arquivos
            self.backup_system_files()
            
            # Coleta configurações
            configs = self.collect_configurations()
            
            # Armazena no MCP
            self.store_in_mcp(configs)
            
            # Cria arquivo comprimido
            self.create_compressed_backup()
            
            # Gera documentação
            self.generate_documentation()
            
            logger.info("Processo de backup concluído com sucesso")
            print(f"\n✅ Backup quântico concluído com sucesso!")
            print(f"📁 Localização: {self.backup_dir}")
            print(f"📦 Arquivo ZIP: backup/quantum_backup_{self.timestamp}.zip")
            print(f"⚙️ Configurações MCP: {self.mcp_config_file}")
            
        except Exception as e:
            logger.error(f"Erro durante o processo de backup: {e}")
            print(f"\n❌ Erro durante o backup: {e}")

if __name__ == "__main__":
    print("\n🔄 Iniciando backup quântico do sistema EVA & GUARANI...")
    backup = QuantumBackup()
    backup.run_backup()
