#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EVA & GUARANI - API Principal
Versão: 2.0.0 - Build 2025.02.26

Este módulo implementa a API principal do sistema EVA & GUARANI,
fornecendo endpoints para interação com o sistema.
"""

import os
import sys
import json
import logging
import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List, Union

from fastapi import FastAPI, HTTPException, Depends, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/api.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("✨quantum-api✨")

# Inicialização da API
app = FastAPI(
    title="EVA & GUARANI API",
    description="API Quântica para o Sistema EVA & GUARANI",
    version="2.0.0",
)

# Configuração de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar origens permitidas
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos de dados
class BackupRequest(BaseModel):
    backup_name: Optional[str] = None
    include_models: bool = True
    compress_level: int = 9
    store_in_mcp: bool = True

class BackupResponse(BaseModel):
    success: bool
    message: str
    backup_location: Optional[str] = None
    timestamp: str
    details: Optional[Dict[str, Any]] = None

# Classe para gerenciar backups
class QuantumBackupManager:
    """Gerenciador de backups quânticos via API."""
    
    def __init__(self):
        """Inicializa o gerenciador de backups."""
        self.timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.backup_dir = Path(f"backup/quantum/backup_{self.timestamp}")
        self.mcp_config_file = Path("cursor/mcp/config_storage.json")
        self.system_dirs = [
            "config", "src", "core", "modules", "scripts",
            "data", "logs", "models", "output",
            "infinity_ai", "ava_mind", "consciousness", "quantum_memory"
        ]
    
    def create_backup(self, request: BackupRequest) -> BackupResponse:
        """
        Cria um backup completo do sistema.
        
        Args:
            request: Configurações do backup
            
        Returns:
            Resposta com detalhes do backup
        """
        try:
            logger.info(f"Iniciando backup quântico via API: {request}")
            
            # Personaliza nome do backup se fornecido
            if request.backup_name:
                self.backup_dir = Path(f"backup/quantum/{request.backup_name}_{self.timestamp}")
            
            # Cria estrutura de diretórios
            self.backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Realiza backup dos arquivos do sistema
            self._backup_system_files(include_models=request.include_models)
            
            # Coleta e armazena configurações
            if request.store_in_mcp:
                configs = self._collect_configurations()
                self._store_in_mcp(configs)
            
            # Cria arquivo comprimido
            zip_path = self._create_compressed_backup(compress_level=request.compress_level)
            
            # Gera documentação
            doc_path = self._generate_documentation()
            
            return BackupResponse(
                success=True,
                message="Backup quântico concluído com sucesso",
                backup_location=str(zip_path),
                timestamp=self.timestamp,
                details={
                    "backup_dir": str(self.backup_dir),
                    "mcp_config": str(self.mcp_config_file) if request.store_in_mcp else None,
                    "documentation": str(doc_path),
                    "included_models": request.include_models
                }
            )
            
        except Exception as e:
            logger.error(f"Erro durante o backup: {e}")
            return BackupResponse(
                success=False,
                message=f"Erro durante o backup: {str(e)}",
                timestamp=self.timestamp,
                details={"error": str(e)}
            )
    
    def _backup_system_files(self, include_models: bool = True) -> None:
        """Realiza backup dos arquivos do sistema."""
        logger.info("Copiando arquivos do sistema")
        
        for dir_name in self.system_dirs:
            source_dir = Path(dir_name)
            if not source_dir.exists():
                logger.warning(f"Diretório não encontrado: {source_dir}")
                continue
                
            # Pula diretório de modelos se não solicitado
            if dir_name == "models" and not include_models:
                logger.info("Pulando diretório de modelos conforme solicitado")
                continue
                
            target_dir = self.backup_dir / dir_name
            target_dir.mkdir(parents=True, exist_ok=True)
            
            try:
                # Copia arquivos recursivamente
                for item in source_dir.glob("**/*"):
                    if item.is_file():
                        relative_path = item.relative_to(source_dir)
                        destination = target_dir / relative_path
                        destination.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(item, destination)
            except Exception as e:
                logger.error(f"Erro ao copiar {dir_name}: {e}")
    
    def _collect_configurations(self) -> Dict[str, Any]:
        """Coleta configurações do sistema."""
        logger.info("Coletando configurações do sistema")
        
        configs = {
            "timestamp": self.timestamp,
            "system_info": {
                "version": "2.0.0",
                "build": "2025.02.26",
                "platform": sys.platform,
                "python_version": sys.version
            },
            "directories": {},
            "environment": {}
        }
        
        # Coleta informações sobre diretórios
        for dir_name in self.system_dirs:
            dir_path = Path(dir_name)
            if dir_path.exists():
                file_count = len(list(dir_path.glob("**/*")))
                configs["directories"][dir_name] = {
                    "exists": True,
                    "file_count": file_count,
                    "size_bytes": sum(f.stat().st_size for f in dir_path.glob("**/*") if f.is_file())
                }
            else:
                configs["directories"][dir_name] = {"exists": False}
        
        # Coleta variáveis de ambiente seguras
        safe_env_vars = ["PATH", "PYTHONPATH", "LANG", "USER", "HOME"]
        for var in safe_env_vars:
            if var in os.environ:
                configs["environment"][var] = os.environ[var]
        
        return configs
    
    def _store_in_mcp(self, configs: Dict[str, Any]) -> None:
        """Armazena configurações no MCP do cursor."""
        logger.info(f"Armazenando configurações no MCP: {self.mcp_config_file}")
        
        # Cria diretório do MCP se não existir
        self.mcp_config_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Adiciona metadados ao arquivo de configuração
        mcp_data = {
            "backup_configs": configs,
            "mcp_metadata": {
                "storage_time": datetime.datetime.now().isoformat(),
                "backup_path": str(self.backup_dir),
                "quantum_signature": "0xΦ2E5A1"
            }
        }
        
        # Salva no arquivo MCP
        with open(self.mcp_config_file, "w", encoding="utf-8") as f:
            json.dump(mcp_data, f, indent=2, ensure_ascii=False)
    
    def _create_compressed_backup(self, compress_level: int = 9) -> Path:
        """Cria arquivo comprimido do backup."""
        logger.info(f"Criando arquivo comprimido com nível de compressão {compress_level}")
        
        zip_filename = f"quantum_backup_{self.timestamp}.zip"
        zip_path = Path("backup") / zip_filename
        
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED, compresslevel=compress_level) as zipf:
            for root, _, files in os.walk(self.backup_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, self.backup_dir.parent)
                    zipf.write(file_path, arcname)
        
        return zip_path
    
    def _generate_documentation(self) -> Path:
        """Gera documentação do backup."""
        logger.info("Gerando documentação do backup")
        
        doc_content = f"""# Documentação do Backup Quântico

## Informações Gerais
- **Data e Hora**: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- **Versão do Sistema**: 2.0.0
- **Build**: 2025.02.26
- **Localização**: {self.backup_dir}

## Conteúdo do Backup
- Arquivos de configuração
- Código-fonte
- Módulos do sistema
- Logs e dados
- Componentes de IA

## Instruções de Restauração
1. Extraia o arquivo ZIP para um diretório temporário
2. Execute o script de restauração: `python restore.py --source={self.backup_dir}`
3. Verifique os logs para confirmar a restauração
4. Execute o script de verificação de integridade

## Observações
- Este backup contém todas as configurações e dados do sistema EVA & GUARANI
- As configurações foram armazenadas no MCP do cursor para acesso rápido
- Recomenda-se manter este backup em local seguro
"""
        
        # Salva a documentação
        doc_file = self.backup_dir / "BACKUP_DOCUMENTATION.md"
        with open(doc_file, "w", encoding="utf-8") as f:
            f.write(doc_content)
        
        return doc_file

# Endpoints da API
@app.get("/")
async def root():
    """Endpoint raiz da API."""
    return {
        "name": "EVA & GUARANI API",
        "version": "2.0.0",
        "status": "online",
        "timestamp": datetime.datetime.now().isoformat()
    }

@app.post("/backup", response_model=BackupResponse)
async def create_backup(
    request: BackupRequest,
    background_tasks: BackgroundTasks
):
    """
    Cria um backup completo do sistema.
    
    - **backup_name**: Nome personalizado para o backup (opcional)
    - **include_models**: Se deve incluir modelos de IA (padrão: True)
    - **compress_level**: Nível de compressão do arquivo ZIP (1-9)
    - **store_in_mcp**: Se deve armazenar configurações no MCP (padrão: True)
    """
    logger.info(f"Solicitação de backup recebida: {request}")
    
    # Cria instância do gerenciador de backup
    backup_manager = QuantumBackupManager()
    
    # Executa backup
    response = backup_manager.create_backup(request)
    
    if response.success:
        return response
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=response.message
        )

@app.get("/backup/status")
async def backup_status():
    """Verifica o status dos backups existentes."""
    backup_dir = Path("backup/quantum")
    
    if not backup_dir.exists():
        return {
            "status": "no_backups",
            "message": "Nenhum backup encontrado"
        }
    
    backups = []
    for item in backup_dir.glob("*"):
        if item.is_dir() and "backup_" in item.name:
            try:
                doc_file = item / "BACKUP_DOCUMENTATION.md"
                has_doc = doc_file.exists()
                
                backups.append({
                    "name": item.name,
                    "created_at": datetime.datetime.fromtimestamp(item.stat().st_ctime).isoformat(),
                    "size_bytes": sum(f.stat().st_size for f in item.glob("**/*") if f.is_file()),
                    "has_documentation": has_doc
                })
            except Exception as e:
                logger.error(f"Erro ao processar backup {item.name}: {e}")
    
    return {
        "status": "success",
        "count": len(backups),
        "backups": sorted(backups, key=lambda x: x["created_at"], reverse=True)
    }

if __name__ == "__main__":
    import uvicorn
    print("\n🚀 Iniciando API Quântica do Sistema EVA & GUARANI...")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
