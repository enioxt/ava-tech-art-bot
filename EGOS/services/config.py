"""
Módulo de configuração para gerenciamento seguro de credenciais - EVA & GUARANI
-------------------------------------------------------------------------------
Este módulo gerencia as chaves de API e outras configurações de serviços externos,
priorizando a segurança e ocultação das credenciais.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional

class ConfigManager:
    """
    Gerencia configurações e credenciais do sistema EVA & GUARANI.
    Prioriza a segurança das chaves de API e outras credenciais sensíveis.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Inicializa o gerenciador de configuração.
        
        Args:
            config_path: Caminho para o arquivo de configuração. Se None, 
                         usa o padrão dentro do diretório EGOS.
        """
        if config_path is None:
            # Diretório padrão para configurações
            egos_dir = Path(__file__).parent.parent
            self.config_path = egos_dir / "config" / "api_keys.json"
        else:
            self.config_path = Path(config_path)
            
        # Criar diretório de configuração se não existir
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Configurações iniciais
        self.config = self._load_config()
        
        # Chave da Perplexity - prioriza variável de ambiente, depois arquivo
        perplexity_key = os.environ.get("PERPLEXITY_API_KEY")
        if perplexity_key:
            self.set_key("perplexity", perplexity_key)
        
    def _load_config(self) -> Dict[str, Any]:
        """
        Carrega configurações do arquivo se existir.
        
        Returns:
            Dicionário com configurações
        """
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print(f"Erro ao carregar arquivo de configuração: {self.config_path}")
                return {"api_keys": {}}
        else:
            return {"api_keys": {}}
    
    def _save_config(self) -> None:
        """Salva as configurações no arquivo."""
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def get_key(self, service: str) -> Optional[str]:
        """
        Obtém a chave API para um serviço específico.
        
        Args:
            service: Nome do serviço (ex: 'perplexity', 'openai')
            
        Returns:
            Chave API ou None se não encontrada
        """
        # Primeiro tenta obter da variável de ambiente
        env_key = os.environ.get(f"{service.upper()}_API_KEY")
        if env_key:
            return env_key
            
        # Se não encontrar no ambiente, busca no arquivo de configuração
        return self.config.get("api_keys", {}).get(service)
    
    def set_key(self, service: str, api_key: str) -> None:
        """
        Define a chave API para um serviço.
        
        Args:
            service: Nome do serviço (ex: 'perplexity', 'openai')
            api_key: Chave API para armazenar
        """
        if "api_keys" not in self.config:
            self.config["api_keys"] = {}
            
        self.config["api_keys"][service] = api_key
        self._save_config()
        
    def clear_key(self, service: str) -> None:
        """
        Remove a chave API de um serviço.
        
        Args:
            service: Nome do serviço (ex: 'perplexity', 'openai')
        """
        if service in self.config.get("api_keys", {}):
            del self.config["api_keys"][service]
            self._save_config()
            
    def is_configured(self, service: str) -> bool:
        """
        Verifica se o serviço está configurado com uma chave API.
        
        Args:
            service: Nome do serviço (ex: 'perplexity', 'openai')
            
        Returns:
            True se o serviço tem uma chave API configurada
        """
        # Verifica ambiente primeiro
        env_key = os.environ.get(f"{service.upper()}_API_KEY")
        if env_key:
            return True
            
        # Depois verifica o arquivo
        return service in self.config.get("api_keys", {})


# Instância global do gerenciador de configuração
config_manager = ConfigManager()

# Exemplo de uso:
if __name__ == "__main__":
    # Este trecho só é executado se o arquivo for executado diretamente
    
    # Configurar API key da Perplexity (apenas exemplo)
    sample_key = "pplx-sample-key-for-testing"
    config_manager.set_key("perplexity", sample_key)
    
    # Verificar se está configurado
    if config_manager.is_configured("perplexity"):
        print("Perplexity API está configurada.")
    else:
        print("Perplexity API NÃO está configurada.") 