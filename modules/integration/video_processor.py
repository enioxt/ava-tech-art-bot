#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Módulo de Processamento de Vídeos - EVA & GUARANI
-------------------------------------------------
Este módulo gerencia o processamento de vídeos utilizando FFmpeg
e integração com APIs externas para efeitos avançados.

Versão: 1.0.0
"""

import os
import json
import logging
import subprocess
import time
import uuid
from pathlib import Path
from typing import Dict, Any, Optional, Union, List, Tuple
import asyncio
import aiohttp
import shutil

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/video_processor.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("video-processor")

class VideoProcessor:
    """Gerencia o processamento de vídeos utilizando FFmpeg e APIs externas."""
    
    def __init__(self, config_path: str = "config/telegram_config.json"):
        """
        Inicializa o processador de vídeos.
        
        Args:
            config_path: Caminho para o arquivo de configuração
        """
        self.config_path = config_path
        self.config = self._load_config()
        
        # Diretórios para arquivos temporários e processados
        self.temp_dir = Path("temp/videos")
        self.output_dir = Path("data/processed_videos")
        
        # Criar diretórios se não existirem
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Verificar se FFmpeg está instalado
        self.ffmpeg_available = self._check_ffmpeg()
        
        # Estatísticas de uso
        self.stats = {
            "processing_count": 0,
            "total_processing_time": 0,
            "last_processing_time": 0,
            "errors": 0,
            "successful_operations": 0
        }
    
    def _load_config(self) -> Dict[str, Any]:
        """
        Carrega a configuração do arquivo JSON.
        
        Returns:
            Dict: Configurações carregadas
        """
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                logger.warning(f"Arquivo de configuração não encontrado: {self.config_path}")
                return {}
        except Exception as e:
            logger.error(f"Erro ao carregar configuração: {e}")
            return {}
    
    def _check_ffmpeg(self) -> bool:
        """
        Verifica se o FFmpeg está instalado no sistema.
        
        Returns:
            bool: True se FFmpeg estiver disponível, False caso contrário
        """
        try:
            subprocess.run(
                ["ffmpeg", "-version"], 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                check=True
            )
            logger.info("FFmpeg encontrado no sistema.")
            return True
        except (subprocess.SubprocessError, FileNotFoundError):
            logger.warning("FFmpeg não encontrado. Funcionalidades de processamento de vídeo serão limitadas.")
            return False
    
    async def process_video(self, video_path: str, operation: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Processa um vídeo com a operação especificada.
        
        Args:
            video_path: Caminho para o arquivo de vídeo
            operation: Tipo de operação (convert, resize, extract_frames, etc)
            params: Parâmetros adicionais para a operação
        
        Returns:
            Dict: Resultado da operação com caminho do arquivo processado
        """
        if not self.ffmpeg_available:
            return {
                "success": False,
                "error": "FFmpeg não está disponível no sistema",
                "output_path": None
            }
        
        if not os.path.exists(video_path):
            return {
                "success": False,
                "error": f"Arquivo de vídeo não encontrado: {video_path}",
                "output_path": None
            }
        
        if params is None:
            params = {}
        
        start_time = time.time()
        self.stats["processing_count"] += 1
        
        try:
            # Gerar nome único para o arquivo de saída
            output_filename = f"{uuid.uuid4()}_{os.path.basename(video_path)}"
            output_path = str(self.output_dir / output_filename)
            
            # Executar operação específica
            if operation == "convert":
                result = await self._convert_format(video_path, output_path, params)
            elif operation == "resize":
                result = await self._resize_video(video_path, output_path, params)
            elif operation == "extract_frames":
                result = await self._extract_frames(video_path, output_path, params)
            elif operation == "add_watermark":
                result = await self._add_watermark(video_path, output_path, params)
            elif operation == "trim":
                result = await self._trim_video(video_path, output_path, params)
            else:
                result = {
                    "success": False,
                    "error": f"Operação não suportada: {operation}",
                    "output_path": None
                }
            
            # Atualizar estatísticas
            processing_time = time.time() - start_time
            self.stats["last_processing_time"] = processing_time
            self.stats["total_processing_time"] += processing_time
            
            if result["success"]:
                self.stats["successful_operations"] += 1
                # Gerar log de sucesso
                logger.info(f"[PROCESSAMENTO][{operation}] Concluído com sucesso em {processing_time:.2f}s")
                logger.info(f"[PROCESSAMENTO][{operation}] Entrada: {video_path} | Saída: {result['output_path']}")
            else:
                self.stats["errors"] += 1
                # Gerar log de erro
                logger.error(f"[PROCESSAMENTO][{operation}] Falha: {result['error']}")
            
            return result
            
        except Exception as e:
            self.stats["errors"] += 1
            processing_time = time.time() - start_time
            self.stats["last_processing_time"] = processing_time
            self.stats["total_processing_time"] += processing_time
            
            logger.error(f"Erro ao processar vídeo: {e}")
            return {
                "success": False,
                "error": str(e),
                "output_path": None
            }
    
    async def _convert_format(self, input_path: str, output_path: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Converte um vídeo para outro formato.
        
        Args:
            input_path: Caminho do vídeo de entrada
            output_path: Caminho base para o vídeo de saída
            params: Parâmetros adicionais (format, codec, etc)
        
        Returns:
            Dict: Resultado da operação
        """
        target_format = params.get("format", "mp4")
        codec = params.get("codec", "libx264")
        
        # Ajustar extensão do arquivo de saída
        output_path = f"{os.path.splitext(output_path)[0]}.{target_format}"
        
        try:
            cmd = [
                "ffmpeg", "-i", input_path,
                "-c:v", codec,
                "-preset", "medium",
                "-c:a", "aac",
                "-b:a", "128k",
                "-y", output_path
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                return {
                    "success": True,
                    "output_path": output_path,
                    "format": target_format
                }
            else:
                return {
                    "success": False,
                    "error": f"Erro ao converter vídeo: {stderr.decode()}",
                    "output_path": None
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Exceção ao converter vídeo: {str(e)}",
                "output_path": None
            }
    
    async def _resize_video(self, input_path: str, output_path: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Redimensiona um vídeo.
        
        Args:
            input_path: Caminho do vídeo de entrada
            output_path: Caminho para o vídeo de saída
            params: Parâmetros adicionais (width, height, etc)
        
        Returns:
            Dict: Resultado da operação
        """
        width = params.get("width", 640)
        height = params.get("height", 480)
        maintain_aspect_ratio = params.get("maintain_aspect_ratio", True)
        
        try:
            filter_complex = f"scale={width}:{height}"
            if maintain_aspect_ratio:
                filter_complex = f"scale={width}:{height}:force_original_aspect_ratio=decrease"
            
            cmd = [
                "ffmpeg", "-i", input_path,
                "-vf", filter_complex,
                "-c:a", "copy",
                "-y", output_path
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                return {
                    "success": True,
                    "output_path": output_path,
                    "dimensions": f"{width}x{height}"
                }
            else:
                return {
                    "success": False,
                    "error": f"Erro ao redimensionar vídeo: {stderr.decode()}",
                    "output_path": None
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Exceção ao redimensionar vídeo: {str(e)}",
                "output_path": None
            }
    
    async def _extract_frames(self, input_path: str, output_path: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extrai frames de um vídeo.
        
        Args:
            input_path: Caminho do vídeo de entrada
            output_path: Caminho base para os frames extraídos
            params: Parâmetros adicionais (fps, start_time, duration, etc)
        
        Returns:
            Dict: Resultado da operação
        """
        fps = params.get("fps", 1)
        start_time = params.get("start_time", 0)
        duration = params.get("duration", None)
        
        # Criar diretório para os frames
        frames_dir = f"{os.path.splitext(output_path)[0]}_frames"
        os.makedirs(frames_dir, exist_ok=True)
        
        try:
            cmd = ["ffmpeg", "-i", input_path]
            
            if start_time > 0:
                cmd.extend(["-ss", str(start_time)])
            
            if duration:
                cmd.extend(["-t", str(duration)])
            
            cmd.extend([
                "-vf", f"fps={fps}",
                "-y", f"{frames_dir}/frame_%04d.jpg"
            ])
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                # Contar quantos frames foram extraídos
                frame_count = len([f for f in os.listdir(frames_dir) if f.startswith("frame_")])
                
                return {
                    "success": True,
                    "output_path": frames_dir,
                    "frame_count": frame_count,
                    "fps": fps
                }
            else:
                return {
                    "success": False,
                    "error": f"Erro ao extrair frames: {stderr.decode()}",
                    "output_path": None
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Exceção ao extrair frames: {str(e)}",
                "output_path": None
            }
    
    async def _add_watermark(self, input_path: str, output_path: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Adiciona uma marca d'água a um vídeo.
        
        Args:
            input_path: Caminho do vídeo de entrada
            output_path: Caminho para o vídeo de saída
            params: Parâmetros adicionais (watermark_path, position, etc)
        
        Returns:
            Dict: Resultado da operação
        """
        watermark_path = params.get("watermark_path")
        position = params.get("position", "bottomright")
        opacity = params.get("opacity", 0.7)
        
        if not watermark_path or not os.path.exists(watermark_path):
            return {
                "success": False,
                "error": f"Arquivo de marca d'água não encontrado: {watermark_path}",
                "output_path": None
            }
        
        try:
            # Definir posição da marca d'água
            position_map = {
                "topleft": "10:10",
                "topright": "W-w-10:10",
                "bottomleft": "10:H-h-10",
                "bottomright": "W-w-10:H-h-10",
                "center": "(W-w)/2:(H-h)/2"
            }
            pos = position_map.get(position, position_map["bottomright"])
            
            cmd = [
                "ffmpeg", "-i", input_path,
                "-i", watermark_path,
                "-filter_complex", f"overlay={pos}:alpha={opacity}",
                "-codec:a", "copy",
                "-y", output_path
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                return {
                    "success": True,
                    "output_path": output_path,
                    "watermark": os.path.basename(watermark_path)
                }
            else:
                return {
                    "success": False,
                    "error": f"Erro ao adicionar marca d'água: {stderr.decode()}",
                    "output_path": None
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Exceção ao adicionar marca d'água: {str(e)}",
                "output_path": None
            }
    
    async def _trim_video(self, input_path: str, output_path: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Corta um vídeo com base em tempo de início e duração.
        
        Args:
            input_path: Caminho do vídeo de entrada
            output_path: Caminho para o vídeo de saída
            params: Parâmetros adicionais (start_time, duration, etc)
        
        Returns:
            Dict: Resultado da operação
        """
        start_time = params.get("start_time", 0)
        duration = params.get("duration")
        
        try:
            cmd = ["ffmpeg", "-i", input_path, "-ss", str(start_time)]
            
            if duration:
                cmd.extend(["-t", str(duration)])
            
            cmd.extend([
                "-c:v", "copy",
                "-c:a", "copy",
                "-y", output_path
            ])
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                return {
                    "success": True,
                    "output_path": output_path,
                    "start_time": start_time,
                    "duration": duration
                }
            else:
                return {
                    "success": False,
                    "error": f"Erro ao cortar vídeo: {stderr.decode()}",
                    "output_path": None
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Exceção ao cortar vídeo: {str(e)}",
                "output_path": None
            }
    
    async def create_gif_from_video(self, input_path: str, output_path: str | None = None, params: Dict[str, Any] | None = None) -> Dict[str, Any]:
        """
        Cria um GIF a partir de um vídeo.
        
        Args:
            input_path: Caminho do vídeo de entrada
            output_path: Caminho para o GIF de saída (opcional)
            params: Parâmetros adicionais (start_time, duration, fps, width, etc)
        
        Returns:
            Dict: Resultado da operação
        """
        if not self.ffmpeg_available:
            return {
                "success": False,
                "error": "FFmpeg não está disponível no sistema",
                "output_path": None
            }
        
        if not os.path.exists(input_path):
            return {
                "success": False,
                "error": f"Arquivo de vídeo não encontrado: {input_path}",
                "output_path": None
            }
        
        if params is None:
            params = {}
        
        start_time = params.get("start_time", 0)
        duration = params.get("duration")
        fps = params.get("fps", 10)
        width = params.get("width", 320)
        quality = params.get("quality", 90)
        
        # Gerar nome para o arquivo de saída se não fornecido
        if output_path is None:
            output_filename = f"{uuid.uuid4()}_{os.path.splitext(os.path.basename(input_path))[0]}.gif"
            output_path = str(self.output_dir / output_filename)
        
        try:
            # Construir comando para criar o GIF
            filters = [
                f"fps={fps}",
                f"scale={width}:-1:flags=lanczos"
            ]
            
            filter_complex = ",".join(filters)
            
            cmd = ["ffmpeg", "-i", input_path]
            
            if start_time > 0:
                cmd.extend(["-ss", str(start_time)])
            
            if duration:
                cmd.extend(["-t", str(duration)])
            
            cmd.extend([
                "-vf", filter_complex,
                "-y", output_path
            ])
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                return {
                    "success": True,
                    "output_path": output_path,
                    "format": "gif",
                    "fps": fps,
                    "width": width
                }
            else:
                return {
                    "success": False,
                    "error": f"Erro ao criar GIF: {stderr.decode()}",
                    "output_path": None
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Exceção ao criar GIF: {str(e)}",
                "output_path": None
            }
    
    async def concatenate_videos(self, video_paths: List[str], output_path: str = None, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Concatena múltiplos vídeos em um único arquivo.
        
        Args:
            video_paths: Lista de caminhos para os vídeos de entrada
            output_path: Caminho para o vídeo de saída (opcional)
            params: Parâmetros adicionais (codec, bitrate, etc)
        
        Returns:
            Dict: Resultado da operação
        """
        if not self.ffmpeg_available:
            return {
                "success": False,
                "error": "FFmpeg não está disponível no sistema",
                "output_path": None
            }
        
        if not video_paths or len(video_paths) < 2:
            return {
                "success": False,
                "error": "São necessários pelo menos dois vídeos para concatenação",
                "output_path": None
            }
        
        # Verificar se todos os vídeos existem
        for video_path in video_paths:
            if not os.path.exists(video_path):
                return {
                    "success": False,
                    "error": f"Arquivo de vídeo não encontrado: {video_path}",
                    "output_path": None
                }
        
        if params is None:
            params = {}
        
        codec = params.get("codec", "libx264")
        
        # Gerar nome para o arquivo de saída se não fornecido
        if output_path is None:
            output_filename = f"concat_{uuid.uuid4()}.mp4"
            output_path = str(self.output_dir / output_filename)
        
        try:
            # Criar arquivo de lista temporário para o FFmpeg
            list_file = self.temp_dir / f"{uuid.uuid4()}_list.txt"
            
            with open(list_file, "w", encoding="utf-8") as f:
                for video_path in video_paths:
                    f.write(f"file '{os.path.abspath(video_path)}'\n")
            
            # Construir comando para concatenar os vídeos
            cmd = [
                "ffmpeg",
                "-f", "concat",
                "-safe", "0",
                "-i", str(list_file),
                "-c:v", codec,
                "-c:a", "aac",
                "-y", output_path
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            # Remover arquivo de lista temporário
            os.remove(list_file)
            
            if process.returncode == 0:
                return {
                    "success": True,
                    "output_path": output_path,
                    "video_count": len(video_paths)
                }
            else:
                return {
                    "success": False,
                    "error": f"Erro ao concatenar vídeos: {stderr.decode()}",
                    "output_path": None
                }
        except Exception as e:
            # Tentar remover o arquivo de lista temporário em caso de exceção
            if 'list_file' in locals() and os.path.exists(list_file):
                os.remove(list_file)
                
            return {
                "success": False,
                "error": f"Exceção ao concatenar vídeos: {str(e)}",
                "output_path": None
            }
    
    async def add_subtitles(self, input_path: str, subtitle_path: str, output_path: str = None, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Adiciona legendas a um vídeo.
        
        Args:
            input_path: Caminho do vídeo de entrada
            subtitle_path: Caminho para o arquivo de legendas (SRT, ASS, etc)
            output_path: Caminho para o vídeo de saída (opcional)
            params: Parâmetros adicionais (codec, font, etc)
        
        Returns:
            Dict: Resultado da operação
        """
        if not self.ffmpeg_available:
            return {
                "success": False,
                "error": "FFmpeg não está disponível no sistema",
                "output_path": None
            }
        
        if not os.path.exists(input_path):
            return {
                "success": False,
                "error": f"Arquivo de vídeo não encontrado: {input_path}",
                "output_path": None
            }
        
        if not os.path.exists(subtitle_path):
            return {
                "success": False,
                "error": f"Arquivo de legendas não encontrado: {subtitle_path}",
                "output_path": None
            }
        
        if params is None:
            params = {}
        
        # Verificar formato do arquivo de legendas
        subtitle_ext = os.path.splitext(subtitle_path)[1].lower()
        if subtitle_ext not in ['.srt', '.ass', '.ssa', '.vtt']:
            return {
                "success": False,
                "error": f"Formato de legendas não suportado: {subtitle_ext}",
                "output_path": None
            }
        
        # Definir se as legendas serão codificadas no vídeo (hardcoded) ou como stream
        hardcode = params.get("hardcode", False)
        font_size = params.get("font_size", 24)
        font_color = params.get("font_color", "white")
        codec = params.get("codec", "libx264")
        
        # Gerar nome para o arquivo de saída se não fornecido
        if output_path is None:
            output_filename = f"sub_{uuid.uuid4()}_{os.path.basename(input_path)}"
            output_path = str(self.output_dir / output_filename)
        
        try:
            if hardcode:
                # Legendas codificadas no vídeo (permanentes)
                if subtitle_ext == '.srt':
                    cmd = [
                        "ffmpeg", "-i", input_path,
                        "-vf", f"subtitles={subtitle_path}:force_style='FontSize={font_size},PrimaryColour={font_color}'",
                        "-c:v", codec,
                        "-c:a", "copy",
                        "-y", output_path
                    ]
                else:
                    # Para outros formatos, usar filtro ASS
                    cmd = [
                        "ffmpeg", "-i", input_path,
                        "-vf", f"ass={subtitle_path}",
                        "-c:v", codec,
                        "-c:a", "copy",
                        "-y", output_path
                    ]
            else:
                # Legendas como stream (podem ser ativadas/desativadas pelo usuário)
                cmd = [
                    "ffmpeg", "-i", input_path,
                    "-i", subtitle_path,
                    "-c:v", "copy",
                    "-c:a", "copy",
                    "-c:s", "mov_text",
                    "-metadata:s:s:0", f"language={params.get('language', 'por')}",
                    "-y", output_path
                ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                return {
                    "success": True,
                    "output_path": output_path,
                    "subtitle_type": "hardcoded" if hardcode else "stream",
                    "subtitle_format": subtitle_ext[1:]
                }
            else:
                return {
                    "success": False,
                    "error": f"Erro ao adicionar legendas: {stderr.decode()}",
                    "output_path": None
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Exceção ao adicionar legendas: {str(e)}",
                "output_path": None
            }
    
    async def get_video_info(self, video_path: str) -> Dict[str, Any]:
        """
        Obtém informações sobre um arquivo de vídeo.
        
        Args:
            video_path: Caminho para o arquivo de vídeo
        
        Returns:
            Dict: Informações do vídeo (duração, resolução, codec, etc)
        """
        if not self.ffmpeg_available:
            return {
                "success": False,
                "error": "FFmpeg não está disponível no sistema"
            }
        
        if not os.path.exists(video_path):
            return {
                "success": False,
                "error": f"Arquivo de vídeo não encontrado: {video_path}"
            }
        
        try:
            cmd = [
                "ffprobe", "-v", "quiet",
                "-print_format", "json",
                "-show_format", "-show_streams",
                video_path
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                info = json.loads(stdout.decode())
                
                # Extrair informações relevantes
                result = {"success": True}
                
                if "format" in info:
                    result.update({
                        "format": info["format"].get("format_name"),
                        "duration": float(info["format"].get("duration", 0)),
                        "size": int(info["format"].get("size", 0)),
                        "bit_rate": int(info["format"].get("bit_rate", 0))
                    })
                
                video_stream = next((s for s in info.get("streams", []) if s.get("codec_type") == "video"), None)
                if video_stream:
                    result.update({
                        "width": video_stream.get("width"),
                        "height": video_stream.get("height"),
                        "codec": video_stream.get("codec_name"),
                        "fps": eval(video_stream.get("r_frame_rate", "0/1"))
                    })
                
                audio_stream = next((s for s in info.get("streams", []) if s.get("codec_type") == "audio"), None)
                if audio_stream:
                    result.update({
                        "audio_codec": audio_stream.get("codec_name"),
                        "audio_channels": audio_stream.get("channels"),
                        "audio_sample_rate": audio_stream.get("sample_rate")
                    })
                
                return result
            else:
                return {
                    "success": False,
                    "error": f"Erro ao obter informações do vídeo: {stderr.decode()}"
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Exceção ao obter informações do vídeo: {str(e)}"
            }
    
    async def get_stats(self) -> Dict[str, Any]:
        """
        Obtém estatísticas de uso do processador de vídeos.
        
        Returns:
            Dict: Estatísticas de uso
        """
        return {
            "processing_count": self.stats["processing_count"],
            "total_processing_time": self.stats["total_processing_time"],
            "last_processing_time": self.stats["last_processing_time"],
            "errors": self.stats["errors"],
            "successful_operations": self.stats["successful_operations"],
            "ffmpeg_available": self.ffmpeg_available
        }
    
    def cleanup_temp_files(self, older_than_hours: int = 24) -> int:
        """
        Remove arquivos temporários antigos.
        
        Args:
            older_than_hours: Remove arquivos mais antigos que este número de horas
        
        Returns:
            int: Número de arquivos removidos
        """
        cutoff_time = time.time() - (older_than_hours * 3600)
        removed_count = 0
        
        try:
            for item in self.temp_dir.glob("*"):
                if item.is_file() and item.stat().st_mtime < cutoff_time:
                    item.unlink()
                    removed_count += 1
                elif item.is_dir() and item.stat().st_mtime < cutoff_time:
                    shutil.rmtree(item)
                    removed_count += 1
            
            logger.info(f"Limpeza de arquivos temporários: {removed_count} itens removidos")
            return removed_count
        except Exception as e:
            logger.error(f"Erro ao limpar arquivos temporários: {e}")
            return 0

# Função para criar uma instância do processador de vídeos
def create_video_processor() -> VideoProcessor:
    """
    Cria uma instância do processador de vídeos.
    
    Returns:
        VideoProcessor: Instância do processador de vídeos
    """
    return VideoProcessor()

# Instância global para uso no bot
video_processor = create_video_processor()
