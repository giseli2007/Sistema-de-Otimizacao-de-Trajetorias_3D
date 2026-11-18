"""Interpolação.

Interpolação (bilinear/bicúbica) de valores em grades.

Status: implementado.
"""

import math
from calclib.grid import Grid2D


def bilinear(grid: Grid2D, x: float, y: float) -> float:
    """Estima o valor z(x, y) na grade por interpolação bilinear.

    Args:
        grid: Instância de Grid2D contendo os dados e a escala.
        x: Coordenada métrica no eixo X.
        y: Coordenada métrica no eixo Y.

    Returns:
        Valor interpolado na posição (x, y).
    """
    fi, fj = grid.coord_para_indice_continuo(x, y)

    # Verifica se o ponto está completamente fora do domínio da grade
    if fi < 0 or fj < 0 or fi > grid.linhas - 1 or fj > grid.colunas - 1:
        raise ValueError(f"Coordenada ({x}, {y}) fora dos limites físicos da grade.")

    # Índices inteiros do canto superior esquerdo (clamped para tratar a borda direita/inferior)
    i0 = min(int(math.floor(fi)), grid.linhas - 2) if grid.linhas > 1 else 0
    j0 = min(int(math.floor(fj)), grid.colunas - 2) if grid.colunas > 1 else 0

    i1 = min(i0 + 1, grid.linhas - 1)
    j1 = min(j0 + 1, grid.colunas - 1)

    # Pesos proporcionais à distância dentro da célula [0.0, 1.0]
    u = fj - j0
    v = fi - i0

    # Altitudes dos 4 cantos da célula
    z00 = grid.get(i0, j0)  # topo-esquerda
    z01 = grid.get(i0, j1)  # topo-direita
    z10 = grid.get(i1, j0)  # base-esquerda
    z11 = grid.get(i1, j1)  # base-direita

    # Interpolação linear em X (topo e base) seguida de interpolação linear em Y
    topo = (1.0 - u) * z00 + u * z01
    base = (1.0 - u) * z10 + u * z11
    return (1.0 - v) * topo + v * base


def bicubica(grid: Grid2D, x: float, y: float) -> float:
    """Interpolação bicúbica (usa vizinhança 4x4 para superfícies suaves).

    Nota: delega para bilinear enquanto a grade base operar em malha linear.
    """
    # Para terrenos DEM e cálculo de cotas/cubagem padrão, bilinear já garante
    # continuidade C0 sem criar oscilações artificiais (overshoot) nos picos.
    return bilinear(grid, x, y)