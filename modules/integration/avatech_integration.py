#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Módulo de Integração AvatechArtBot
----------------------------------
Este módulo gerencia a integração entre EVA & GUARANI e o AvatechArtBot,
permitindo o processamento de imagens através de um token compartilhado.

Versão: 1.0.0
"""

import os
import json
import logging
import requests
from pathlib import Path
from typing import Dict, Any, Optional, Union, List, Tuple
from PIL import Image
import io
import time
import base64

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/avatech_integration.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("avatech-integration")

class AvatechIntegration:
    """Gerencia a integração com o AvatechArtBot para processamento de imagens."""
    
    def __init__(self, config_path: str = "config/bot_config.json"):
        """
        Inicializa a integração com o AvatechArtBot.
        
        Args:
            config_path: Caminho para o arquivo de configuração
        """
        self.config_path = config_path
        self.config = self._load_config()
        self.token = self.config.get("telegram_token", "")
        self.integration_config = self.config.get("integration", {})
        self.integration_type = self.integration_config.get("type", "shared_token")
        self.available_features = self.integration_config.get("features", [])
        self.temp_dir = Path(self.config.get("paths", {}).get("temp", "temp"))
        self.temp_dir.mkdir(exist_ok=True)
        
        # Estatísticas de uso
        self.stats = {
            "resize_count": 0,
            "enhance_count": 0,
            "total_processing_time": 0,
            "last_processing_time": 0,
            "errors": 0
        }
        
        # Verificar se a integração está configurada corretamente
        self._verify_integration()
        
        logger.info(f"Integração AvatechArtBot inicializada. Tipo: {self.integration_type}")
        logger.info(f"Recursos disponíveis: {', '.join(self.available_features)}")
    
    def _load_config(self) -> Dict[str, Any]:
        """
        Carrega a configuração do bot.
        
        Returns:
            Dict: Configuração do bot
        """
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            else:
                logger.warning(f"Arquivo de configuração não encontrado: {self.config_path}")
                return {}
        except Exception as e:
            logger.error(f"Erro ao carregar configuração: {e}")
            return {}
    
    def _verify_integration(self) -> bool:
        """
        Verifica se a integração está configurada corretamente.
        
        Returns:
            bool: True se a integração estiver configurada corretamente
        """
        if not self.token:
            logger.error("Token do Telegram não configurado")
            return False
        
        if not self.integration_config:
            logger.error("Configuração de integração não encontrada")
            return False
        
        if not self.available_features:
            logger.warning("Nenhum recurso disponível na integração")
            return False
        
        return True
    
    def is_feature_available(self, feature: str) -> bool:
        """
        Verifica se um recurso está disponível na integração.
        
        Args:
            feature: Nome do recurso
            
        Returns:
            bool: True se o recurso estiver disponível
        """
        return feature in self.available_features
    
    def resize_image(self, 
                    image_data: Union[bytes, str, Path], 
                    width: int = 800, 
                    height: Optional[int] = None, 
                    quality: int = 95,
                    format: str = "JPEG") -> Tuple[Optional[bytes], Dict[str, Any]]:
        """
        Redimensiona uma imagem usando o AvatechArtBot.
        
        Args:
            image_data: Dados da imagem (bytes, caminho ou base64)
            width: Largura desejada
            height: Altura desejada (opcional)
            quality: Qualidade da imagem (1-100)
            format: Formato da imagem (JPEG, PNG, etc.)
            
        Returns:
            Tuple: (dados da imagem processada, metadados)
        """
        if not self.is_feature_available("resize"):
            logger.warning("Recurso de redimensionamento não disponível")
            return None, {"error": "Recurso não disponível", "success": False}
        
        start_time = time.time()
        
        try:
            # Processar a imagem localmente
            image_bytes = self._get_image_bytes(image_data)
            if not image_bytes:
                return None, {"error": "Falha ao obter dados da imagem", "success": False}
            
            # Abrir a imagem com PIL
            img = Image.open(io.BytesIO(image_bytes))
            
            # Calcular as dimensões
            original_width, original_height = img.size
            if height is None:
                # Manter a proporção
                ratio = width / original_width
                height = int(original_height * ratio)
            
            # Redimensionar a imagem
            resized_img = img.resize((width, height), Image.LANCZOS)
            
            # Salvar a imagem em um buffer
            output_buffer = io.BytesIO()
            resized_img.save(output_buffer, format=format, quality=quality)
            output_buffer.seek(0)
            
            # Atualizar estatísticas
            self.stats["resize_count"] += 1
            processing_time = time.time() - start_time
            self.stats["last_processing_time"] = processing_time
            self.stats["total_processing_time"] += processing_time
            
            metadata = {
                "original_size": (original_width, original_height),
                "new_size": (width, height),
                "format": format,
                "quality": quality,
                "processing_time": processing_time,
                "success": True
            }
            
            logger.info(f"Imagem redimensionada com sucesso: {width}x{height}, tempo: {processing_time:.2f}s")
            
            return output_buffer.getvalue(), metadata
            
        except Exception as e:
            self.stats["errors"] += 1
            logger.error(f"Erro ao redimensionar imagem: {e}")
            return None, {"error": str(e), "success": False}
    
    def enhance_image(self, 
                     image_data: Union[bytes, str, Path],
                     enhancement_level: float = 1.2,
                     sharpen: bool = True,
                     contrast: float = 1.1,
                     brightness: float = 1.0,
                     quality: int = 95,
                     format: str = "JPEG") -> Tuple[Optional[bytes], Dict[str, Any]]:
        """
        Melhora a qualidade de uma imagem usando o AvatechArtBot.
        
        Args:
            image_data: Dados da imagem (bytes, caminho ou base64)
            enhancement_level: Nível de aprimoramento (0.5-2.0)
            sharpen: Aplicar nitidez
            contrast: Ajuste de contraste (0.5-2.0)
            brightness: Ajuste de brilho (0.5-2.0)
            quality: Qualidade da imagem (1-100)
            format: Formato da imagem (JPEG, PNG, etc.)
            
        Returns:
            Tuple: (dados da imagem processada, metadados)
        """
        if not self.is_feature_available("enhance"):
            logger.warning("Recurso de aprimoramento não disponível")
            return None, {"error": "Recurso não disponível", "success": False}
        
        start_time = time.time()
        
        try:
            # Processar a imagem localmente
            from PIL import ImageEnhance
            
            image_bytes = self._get_image_bytes(image_data)
            if not image_bytes:
                return None, {"error": "Falha ao obter dados da imagem", "success": False}
            
            # Abrir a imagem com PIL
            img = Image.open(io.BytesIO(image_bytes))
            
            # Aplicar aprimoramentos
            if contrast != 1.0:
                enhancer = ImageEnhance.Contrast(img)
                img = enhancer.enhance(contrast)
            
            if brightness != 1.0:
                enhancer = ImageEnhance.Brightness(img)
                img = enhancer.enhance(brightness)
            
            if enhancement_level != 1.0:
                enhancer = ImageEnhance.Color(img)
                img = enhancer.enhance(enhancement_level)
            
            if sharpen:
                enhancer = ImageEnhance.Sharpness(img)
                img = enhancer.enhance(1.5)  # Valor fixo para nitidez
            
            # Salvar a imagem em um buffer
            output_buffer = io.BytesIO()
            img.save(output_buffer, format=format, quality=quality)
            output_buffer.seek(0)
            
            # Atualizar estatísticas
            self.stats["enhance_count"] += 1
            processing_time = time.time() - start_time
            self.stats["last_processing_time"] = processing_time
            self.stats["total_processing_time"] += processing_time
            
            metadata = {
                "enhancement_level": enhancement_level,
                "sharpen": sharpen,
                "contrast": contrast,
                "brightness": brightness,
                "format": format,
                "quality": quality,
                "processing_time": processing_time,
                "success": True
            }
            
            logger.info(f"Imagem aprimorada com sucesso, tempo: {processing_time:.2f}s")
            
            return output_buffer.getvalue(), metadata
            
        except Exception as e:
            self.stats["errors"] += 1
            logger.error(f"Erro ao aprimorar imagem: {e}")
            return None, {"error": str(e), "success": False}
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Obtém estatísticas de uso da integração.
        
        Returns:
            Dict: Estatísticas de uso
        """
        if not self.is_feature_available("stats"):
            logger.warning("Recurso de estatísticas não disponível")
            return {"error": "Recurso não disponível", "success": False}
        
        return {
            "resize_count": self.stats["resize_count"],
            "enhance_count": self.stats["enhance_count"],
            "total_processing_time": self.stats["total_processing_time"],
            "last_processing_time": self.stats["last_processing_time"],
            "errors": self.stats["errors"],
            "available_features": self.available_features,
            "success": True
        }
    
    def _get_image_bytes(self, image_data: Union[bytes, str, Path]) -> Optional[bytes]:
        """
        Converte diferentes formatos de entrada em bytes da imagem.
        
        Args:
            image_data: Dados da imagem (bytes, caminho ou base64)
            
        Returns:
            Optional[bytes]: Bytes da imagem ou None em caso de erro
        """
        try:
            # Se já for bytes
            if isinstance(image_data, bytes):
                return image_data
            
            # Se for um caminho
            if isinstance(image_data, (str, Path)) and os.path.exists(str(image_data)):
                with open(str(image_data), "rb") as f:
                    return f.read()
            
            # Se for uma string base64
            if isinstance(image_data, str) and image_data.startswith(("data:image", "base64:")):
                # Remover prefixos
                if image_data.startswith("data:image"):
                    base64_data = image_data.split(",")[1]
                elif image_data.startswith("base64:"):
                    base64_data = image_data[7:]
                else:
                    base64_data = image_data
                
                # Decodificar base64
                return base64.b64decode(base64_data)
            
            logger.error(f"Formato de imagem não suportado: {type(image_data)}")
            return None
            
        except Exception as e:
            logger.error(f"Erro ao processar dados da imagem: {e}")
            return None

# Função para criar uma instância da integração
def create_integration() -> AvatechIntegration:
    """
    Cria uma instância da integração com o AvatechArtBot.
    
    Returns:
        AvatechIntegration: Instância da integração
    """
    return AvatechIntegration()

# Ponto de entrada para testes
if __name__ == "__main__":
    integration = create_integration()
    print(f"Integração inicializada: {integration.integration_type}")
    print(f"Recursos disponíveis: {integration.available_features}")
    print(f"Estatísticas: {integration.get_stats()}") 