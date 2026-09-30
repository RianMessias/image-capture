# Capturador de Imagens

Aplicativo desktop para compressão de imagens em lote, com interface gráfica simples.

## Funcionalidades

- Seleção múltipla de imagens ou pastas completas
- Definição de tamanho máximo de saída (ex: reduzir de 20MB para no máximo 16MB)
- Escolha de formato de saída: JPG, PNG ou WebP
- Opção de manter extensão original
- Salva em subpasta nomeada automaticamente (ex: `comprimido_2026-09-30_14-30`)
- Barra de progresso e status em tempo real

## Formatos aceitos

- JPG/JPEG
- PNG
- WebP
- BMP

## Instalação

```bash
pip install -r requirements.txt
```

## Uso

```bash
python main.py
```

## Como funciona

1. Adicione imagens ou pastas
2. Escolha a pasta de destino
3. Defina o tamanho máximo desejado em MB
4. Escolha o formato de saída (ou marque "Manter extensão original")
5. Clique em Comprimir

As imagens comprimidas serão salvas em uma subpasta dentro do destino escolhido.
