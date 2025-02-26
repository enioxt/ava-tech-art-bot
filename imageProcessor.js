import sharp from 'sharp';
import { CONFIG } from '../config/config.js';
import fs from 'fs/promises';
import path from 'path';

/**
 * Processa uma imagem redimensionando-a para as dimensões especificadas
 * @param {string} inputPath - Caminho do arquivo de entrada
 * @param {number|null} width - Largura desejada (null para manter proporção)
 * @param {number|null} height - Altura desejada (null para manter proporção)
 * @returns {Promise<string>} - Caminho do arquivo processado
 */
export async function processImage(inputPath, width, height) {
  try {
    // Verificar se o arquivo existe
    await fs.access(inputPath);

    // Obter informações da imagem
    const metadata = await sharp(inputPath).metadata();
    
    // Configurar opções de redimensionamento
    const resizeOptions = {
      width: width || undefined,
      height: height || undefined,
      fit: sharp.fit.inside,
      withoutEnlargement: true
    };

    // Determinar formato de saída baseado no original
    const outputFormat = {
      format: metadata.format === 'png' ? 'png' : 'jpeg',
      options: metadata.format === 'png' ? {
        compressionLevel: 9,
        palette: true
      } : {
        quality: 90,
        mozjpeg: true
      }
    };

    // Gerar nome do arquivo de saída
    const outputPath = path.join(
      CONFIG.BOT.TEMP_DIR,
      `processed_${path.basename(inputPath)}.${outputFormat.format}`
    );

    // Processar imagem com otimizações
    await sharp(inputPath)
      .resize(resizeOptions)
      [outputFormat.format](outputFormat.options)
      .toFile(outputPath);

    return outputPath;
  } catch (error) {
    console.error('Erro ao processar imagem:', error);
    throw new Error('Falha ao processar imagem');
  }
}

/**
 * Verifica se um arquivo é uma imagem válida
 * @param {string} filePath - Caminho do arquivo
 * @returns {Promise<boolean>} - true se for uma imagem válida
 */
export async function isValidImage(filePath) {
  try {
    const metadata = await sharp(filePath).metadata();
    return CONFIG.BOT.ALLOWED_FORMATS.includes(`image/${metadata.format}`);
  } catch {
    return false;
  }
}

/**
 * Obtém as dimensões de uma imagem
 * @param {string} filePath - Caminho do arquivo
 * @returns {Promise<{width: number, height: number}>} - Dimensões da imagem
 */
export async function getImageDimensions(filePath) {
  const metadata = await sharp(filePath).metadata();
  return {
    width: metadata.width,
    height: metadata.height
  };
}

/**
 * Otimiza uma imagem para web
 * @param {string} inputPath - Caminho do arquivo de entrada
 * @returns {Promise<string>} - Caminho do arquivo otimizado
 */
export async function optimizeForWeb(inputPath) {
  const metadata = await sharp(inputPath).metadata();
  const outputPath = path.join(
    CONFIG.BOT.TEMP_DIR,
    `web_${path.basename(inputPath)}`
  );

  await sharp(inputPath)
    .resize({
      width: 1920,
      height: 1920,
      fit: sharp.fit.inside,
      withoutEnlargement: true
    })
    .jpeg({
      quality: 85,
      mozjpeg: true,
      chromaSubsampling: '4:2:0'
    })
    .toFile(outputPath);

  return outputPath;
}

/**
 * Adiciona marca d'água a uma imagem
 * @param {string} inputPath - Caminho do arquivo de entrada
 * @param {string} watermarkText - Texto da marca d'água
 * @returns {Promise<string>} - Caminho do arquivo com marca d'água
 */
export async function addWatermark(inputPath, watermarkText) {
  const outputPath = path.join(
    CONFIG.BOT.TEMP_DIR,
    `watermark_${path.basename(inputPath)}`
  );

  const { width, height } = await getImageDimensions(inputPath);
  const svgBuffer = Buffer.from(`
    <svg width="${width}" height="${height}">
      <style>
        .title { fill: rgba(255, 255, 255, 0.5); font-size: 24px; font-family: sans-serif; }
      </style>
      <text x="50%" y="50%" text-anchor="middle" class="title">${watermarkText}</text>
    </svg>
  `);

  await sharp(inputPath)
    .composite([{
      input: svgBuffer,
      top: 0,
      left: 0
    }])
    .toFile(outputPath);

  return outputPath;
}

/**
 * Converte uma imagem para um formato específico
 * @param {string} inputPath - Caminho do arquivo de entrada
 * @param {string} format - Formato desejado ('jpeg', 'png', 'webp')
 * @returns {Promise<string>} - Caminho do arquivo convertido
 */
export async function convertFormat(inputPath, format) {
  if (!['jpeg', 'png', 'webp'].includes(format)) {
    throw new Error('Formato não suportado');
  }

  const outputPath = path.join(
    CONFIG.BOT.TEMP_DIR,
    `converted_${path.basename(inputPath)}.${format}`
  );

  await sharp(inputPath)
    [format]({
      quality: 90,
      ...(format === 'png' && { compressionLevel: 9 }),
      ...(format === 'webp' && { lossless: true })
    })
    .toFile(outputPath);

  return outputPath;
}
