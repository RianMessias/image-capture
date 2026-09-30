"""Módulo de compressão de imagens."""

import io
import os
from PIL import Image

FORMATOS_SUPORTADOS = {'.jpg', '.jpeg', '.png', '.webp', '.bmp'}
FORMATOS_SAIDA = ['JPG', 'PNG', 'WebP']


def comprimir_imagem(caminho_origem, tamanho_max_mb, formato_saida, manter_extensao):
    """
    Comprime uma imagem para ficar abaixo do tamanho máximo especificado.

    Args:
        caminho_origem: Path da imagem original
        tamanho_max_mb: Tamanho máximo em MB (float)
        formato_saida: Formato de saída ('JPG', 'PNG', 'WebP')
        manter_extensao: Se True, mantém a extensão original

    Returns:
        dict com: bytes comprimidos, caminho de saída, tamanho original, novo tamanho
    """
    tamanho_max_bytes = tamanho_max_mb * 1024 * 1024
    tamanho_original = os.path.getsize(caminho_origem)

    # Se já está abaixo do tamanho máximo, retorna original
    if tamanho_original <= tamanho_max_bytes:
        with open(caminho_origem, 'rb') as f:
            dados = f.read()
        extensao = os.path.splitext(caminho_origem)[1].lower()
        return {
            'dados': dados,
            'extensao': extensao,
            'tamanho_original': tamanho_original,
            'tamanho_novo': tamanho_original,
            'qualidade': None
        }

    img = Image.open(caminho_origem)

    # Converte para RGB se necessário (JPG não suporta alpha)
    if formato_saida == 'JPG' and img.mode in ('RGBA', 'LA', 'P'):
        img = img.convert('RGB')
    elif img.mode == 'P' and formato_saida in ('PNG', 'WebP'):
        img = img.convert('RGBA')

    # Determina extensão de saída
    if manter_extensao:
        extensao = os.path.splitext(caminho_origem)[1].lower()
        if extensao == '.jpeg':
            extensao = '.jpg'
    else:
        extensao_map = {'JPG': '.jpg', 'PNG': '.png', 'WebP': '.webp'}
        extensao = extensao_map[formato_saida]

    formato_pillow = 'JPEG' if extensao == '.jpg' else formato_saida

    # Busca binária de qualidade para JPG/WebP
    if formato_pillow in ('JPEG', 'WEBP'):
        resultado = _comprimir_com_qualidade(img, formato_pillow, tamanho_max_bytes)
    else:
        resultado = _comprimir_png(img, tamanho_max_bytes)

    return {
        'dados': resultado['dados'],
        'extensao': extensao,
        'tamanho_original': tamanho_original,
        'tamanho_novo': len(resultado['dados']),
        'qualidade': resultado.get('qualidade')
    }


def _comprimir_com_qualidade(img, formato, tamanho_max_bytes):
    """Busca binária de qualidade para formatos com perda (JPEG/WebP)."""
    buffer = io.BytesIO()

    # Tenta qualidade máxima primeiro
    img.save(buffer, format=formato, quality=95)
    if buffer.tell() <= tamanho_max_bytes:
        return {'dados': buffer.getvalue(), 'qualidade': 95}

    # Busca binária entre 10 e 95
    baixo, alto = 10, 95
    melhor_qualidade = baixo
    melhor_dados = None

    while baixo <= alto:
        meio = (baixo + alto) // 2
        buffer = io.BytesIO()
        img.save(buffer, format=formato, quality=meio)
        tamanho = buffer.tell()

        if tamanho <= tamanho_max_bytes:
            melhor_qualidade = meio
            melhor_dados = buffer.getvalue()
            baixo = meio + 1
        else:
            alto = meio - 1

    if melhor_dados is None:
        # Mesmo com qualidade mínima não cabe, redimensiona
        return _redimensionar_para_caber(img, formato, tamanho_max_bytes)

    return {'dados': melhor_dados, 'qualidade': melhor_qualidade}


def _comprimir_png(img, tamanho_max_bytes):
    """Comprime PNG otimizando e se necessário redimensionando."""
    # Tenta otimização lossless primeiro
    buffer = io.BytesIO()
    img.save(buffer, format='PNG', optimize=True)
    if buffer.tell() <= tamanho_max_bytes:
        return {'dados': buffer.getvalue(), 'qualidade': None}

    # Tenta reduzir cores (quantização)
    img_rgb = img.convert('RGB')
    for cores in (256, 128, 64, 32):
        buffer = io.BytesIO()
        img_reduzida = img_rgb.quantize(colors=cores)
        img_reduzida.save(buffer, format='PNG', optimize=True)
        if buffer.tell() <= tamanho_max_bytes:
            return {'dados': buffer.getvalue(), 'qualidade': None}

    # Redimensiona se ainda não couber
    return _redimensionar_para_caber(img, 'PNG', tamanho_max_bytes)


def _redimensionar_para_caber(img, formato, tamanho_max_bytes):
    """Redimensiona progressivamente a imagem até caber no tamanho máximo."""
    largura, altura = img.size
    fator = 0.9

    while largura > 10 and altura > 10:
        nova_largura = int(largura * fator)
        nova_altura = int(altura * fator)
        img_redimensionada = img.resize((nova_largura, nova_altura), Image.LANCZOS)

        buffer = io.BytesIO()
        if formato == 'JPEG':
            img_redimensionada.save(buffer, format=formato, quality=85)
        else:
            img_redimensionada.save(buffer, format=formato, optimize=True)

        if buffer.tell() <= tamanho_max_bytes:
            return {'dados': buffer.getvalue(), 'qualidade': None}

        largura = nova_largura
        altura = nova_altura

    # Último recurso: qualidade mínima
    buffer = io.BytesIO()
    img.save(buffer, format=formato, quality=10)
    return {'dados': buffer.getvalue(), 'qualidade': 10}
