import os
import json
import random
import logging
import time
from datetime import datetime
from pathlib import Path

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("mycelium.deploy")

class MyceliumDeployer:
    """
    Classe responsável pelo deployment de sites na rede Mycelium.
    Gerencia a distribuição de conteúdo através dos nós da rede.
    """
    
    def __init__(self, config_path=None):
        """Inicializa o deployer com configurações opcionais"""
        self.sites = {}
        self.deployment_history = []
        self.start_time = datetime.now()
        
        # Carregar configuração
        if config_path:
            self.load_config(config_path)
        else:
            self.config = {
                "max_sites": 50,
                "replication_factor": 3,
                "health_check_interval": 300,  # segundos
                "auto_healing": True,
                "quantum_optimization": True
            }
        
        logger.info(f"MyceliumDeployer inicializado com {self.config['max_sites']} sites máximos")
    
    def load_config(self, config_path):
        """Carrega configuração de um arquivo JSON"""
        try:
            with open(config_path, 'r') as f:
                self.config = json.load(f)
            logger.info(f"Configuração carregada de {config_path}")
        except Exception as e:
            logger.error(f"Erro ao carregar configuração: {e}")
            self.config = {
                "max_sites": 50,
                "replication_factor": 3,
                "health_check_interval": 300,
                "auto_healing": True,
                "quantum_optimization": True
            }
    
    def deploy_site(self, site_id, content_path, metadata=None):
        """
        Realiza o deployment de um site na rede Mycelium
        
        Args:
            site_id: Identificador único do site
            content_path: Caminho para os arquivos do site
            metadata: Metadados adicionais do site
        
        Returns:
            dict: Informações sobre o deployment
        """
        if len(self.sites) >= self.config["max_sites"]:
            return {"error": "Limite máximo de sites atingido"}
        
        if site_id in self.sites:
            return {"error": f"Site {site_id} já existe"}
        
        # Verificar se o caminho existe
        if not os.path.exists(content_path):
            return {"error": f"Caminho {content_path} não encontrado"}
        
        # Simular processamento de deployment
        processing_time = random.uniform(1.0, 5.0)
        time.sleep(processing_time)
        
        # Criar registro do site
        deployment_info = {
            "site_id": site_id,
            "content_path": content_path,
            "deployed_at": datetime.now().isoformat(),
            "status": "active",
            "replicas": self.config["replication_factor"],
            "metadata": metadata or {},
            "health": 100.0,
            "deployment_time": processing_time
        }
        
        self.sites[site_id] = deployment_info
        self.deployment_history.append({
            "action": "deploy",
            "site_id": site_id,
            "timestamp": datetime.now().isoformat()
        })
        
        logger.info(f"Site {site_id} implantado com sucesso em {processing_time:.2f}s")
        return {
            "success": True,
            "site_id": site_id,
            "deployment_info": deployment_info
        }
    
    def update_site(self, site_id, content_path=None, metadata=None):
        """Atualiza um site existente"""
        if site_id not in self.sites:
            return {"error": f"Site {site_id} não encontrado"}
        
        # Simular processamento de atualização
        processing_time = random.uniform(0.5, 3.0)
        time.sleep(processing_time)
        
        # Atualizar informações do site
        if content_path:
            self.sites[site_id]["content_path"] = content_path
        
        if metadata:
            self.sites[site_id]["metadata"].update(metadata)
        
        self.sites[site_id]["updated_at"] = datetime.now().isoformat()
        
        self.deployment_history.append({
            "action": "update",
            "site_id": site_id,
            "timestamp": datetime.now().isoformat()
        })
        
        logger.info(f"Site {site_id} atualizado com sucesso em {processing_time:.2f}s")
        return {
            "success": True,
            "site_id": site_id,
            "update_info": {
                "processing_time": processing_time,
                "updated_at": self.sites[site_id]["updated_at"]
            }
        }
    
    def undeploy_site(self, site_id):
        """Remove um site da rede"""
        if site_id not in self.sites:
            return {"error": f"Site {site_id} não encontrado"}
        
        # Simular processamento de remoção
        processing_time = random.uniform(0.5, 2.0)
        time.sleep(processing_time)
        
        site_info = self.sites.pop(site_id)
        
        self.deployment_history.append({
            "action": "undeploy",
            "site_id": site_id,
            "timestamp": datetime.now().isoformat()
        })
        
        logger.info(f"Site {site_id} removido com sucesso em {processing_time:.2f}s")
        return {
            "success": True,
            "site_id": site_id,
            "undeploy_info": {
                "processing_time": processing_time,
                "was_active": site_info["status"] == "active"
            }
        }
    
    def get_site_status(self, site_id):
        """Retorna o status de um site específico"""
        if site_id not in self.sites:
            return {"error": f"Site {site_id} não encontrado"}
        
        # Atualizar saúde do site com pequena variação aleatória
        self.sites[site_id]["health"] = max(0.0, min(100.0, 
            self.sites[site_id]["health"] + random.uniform(-2.0, 1.0)))
        
        # Atualizar status baseado na saúde
        if self.sites[site_id]["health"] < 50:
            self.sites[site_id]["status"] = "degraded"
        elif self.sites[site_id]["health"] < 20:
            self.sites[site_id]["status"] = "critical"
        else:
            self.sites[site_id]["status"] = "active"
        
        return {
            "site_id": site_id,
            "status": self.sites[site_id]["status"],
            "health": self.sites[site_id]["health"],
            "last_checked": datetime.now().isoformat()
        }
    
    def get_all_sites(self):
        """Retorna informações sobre todos os sites implantados"""
        return {
            "total_sites": len(self.sites),
            "active_sites": sum(1 for s in self.sites.values() if s["status"] == "active"),
            "sites": self.sites
        }
    
    def run_health_check(self):
        """Executa verificação de saúde em todos os sites"""
        results = {
            "timestamp": datetime.now().isoformat(),
            "sites_checked": len(self.sites),
            "healthy_sites": 0,
            "degraded_sites": 0,
            "critical_sites": 0,
            "site_statuses": {}
        }
        
        for site_id in self.sites:
            status = self.get_site_status(site_id)
            results["site_statuses"][site_id] = status
            
            if status["status"] == "active":
                results["healthy_sites"] += 1
            elif status["status"] == "degraded":
                results["degraded_sites"] += 1
            elif status["status"] == "critical":
                results["critical_sites"] += 1
                
            # Auto-healing para sites críticos
            if self.config["auto_healing"] and status["status"] == "critical":
                logger.info(f"Iniciando auto-healing para site {site_id}")
                self.sites[site_id]["health"] = random.uniform(60.0, 80.0)
                self.sites[site_id]["status"] = "active"
                self.sites[site_id]["last_healed"] = datetime.now().isoformat()
        
        logger.info(f"Verificação de saúde concluída: {results['healthy_sites']} saudáveis, "
                   f"{results['degraded_sites']} degradados, {results['critical_sites']} críticos")
        return results
    
    def get_deployment_history(self):
        """Retorna o histórico de deployments"""
        return {
            "total_actions": len(self.deployment_history),
            "history": self.deployment_history
        }
    
    def get_uptime(self):
        """Retorna o tempo de atividade do deployer"""
        return (datetime.now() - self.start_time).total_seconds()

# Função para teste do módulo
if __name__ == "__main__":
    deployer = MyceliumDeployer()
    
    # Testar deployment
    test_site = deployer.deploy_site(
        "test-site-1", 
        "./content/test-site", 
        {"description": "Site de teste", "owner": "admin"}
    )
    print(json.dumps(test_site, indent=2))
    
    # Testar verificação de saúde
    health_results = deployer.run_health_check()
    print(json.dumps(health_results, indent=2))
    
    # Testar atualização
    update_result = deployer.update_site(
        "test-site-1", 
        metadata={"updated": True, "version": "1.1"}
    )
    print(json.dumps(update_result, indent=2))
    
    # Testar remoção
    undeploy_result = deployer.undeploy_site("test-site-1")
    print(json.dumps(undeploy_result, indent=2))

# EVA & GUARANI | Sistema Quântico
