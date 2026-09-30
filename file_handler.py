"""Módulo para seleção e varredura de arquivos."""

import os
from tkinter import filedialog

FORMATOS_IMAGEM = {'.jpg', '.jpeg', '.png', '.webp', '.bmp'}


def selecionar_arquivos():
    """Abre diálogo para selecionar múltiplos arquivos de imagem."""
    arquivos = filedialog.askopenfilenames(
        title="Selecionar Imagens",
        filetypes=[
            ("Imagens", "*.jpg *.jpeg *.png *.webp *.bmp"),
            ("Todos os arquivos", "*.*")
        ]
    )
    return list(arquivos) if arquivos else []


def selecionar_pasta():
    """Abre diálogo para selecionar uma pasta e retorna todas as imagens dela."""
    pasta = filedialog.askdirectory(title="Selecionar Pasta com Imagens")
    if not pasta:
        return []
    return varrer_pasta(pasta)


def varrer_pasta(pasta):
    """Varre recursivamente uma pasta por imagens suportadas."""
    imagens = []
    for raiz, _, arquivos in os.walk(pasta):
        for arquivo in arquivos:
            caminho_completo = os.path.join(raiz, arquivo)
            extensao = os.path.splitext(arquivo)[1].lower()
            if extensao in FORMATOS_IMAGEM:
                imagens.append(caminho_completo)
    return sorted(imagens)


def selecionar_destino():
    """Abre diálogo para selecionar pasta de destino."""
    pasta = filedialog.askdirectory(title="Selecionar Pasta de Destino")
    return pasta if pasta else None
