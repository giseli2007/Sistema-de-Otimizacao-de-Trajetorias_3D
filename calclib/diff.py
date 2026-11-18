"""Derivadas numéricas.

Diferenças finitas sobre grades: base do gradiente e da declividade do terreno.

Status: implementado.
"""

import math
from calclib.grid import Grid2D
from calclib.vec import norma, distancia


def gradiente(grid: Grid2D, i: int, j: int) -> tuple[float, float]:
    """Calcula o vetor gradiente (dz/dx, dz/dy) na célula (i, j) por diferenças finitas.

    Usa diferenças centrais no interior da grade e diferenças unilaterais nas bordas.
    """
    if not grid.dentro_dos_limites(i, j):
        raise IndexError(f"Índice ({i}, {j}) fora dos limites da grade.")

    # Derivada parcial em X (variação ao longo das colunas j)
    if grid.colunas == 1:
        dz_dx = 0.0
    elif j == 0:
        # Borda esquerda: diferença progressiva
        dz_dx = (grid.get(i, j + 1) - grid.get(i, j)) / grid.dx
    elif j == grid.colunas - 1:
        # Borda direita: diferença regressiva
        dz_dx = (grid.get(i, j) - grid.get(i, j - 1)) / grid.dx
    else:
        # Interior: diferença central
        dz_dx = (grid.get(i, j + 1) - grid.get(i, j - 1)) / (2.0 * grid.dx)

    # Derivada parcial em Y (variação ao longo das linhas i)
    if grid.linhas == 1:
        dz_dy = 0.0
    elif i == 0:
        # Borda superior: diferença progressiva
        dz_dy = (grid.get(i + 1, j) - grid.get(i, j)) / grid.dy
    elif i == grid.linhas - 1:
        # Borda inferior: diferença regressiva
        dz_dy = (grid.get(i, j) - grid.get(i - 1, j)) / grid.dy
    else:
        # Interior: diferença central
        dz_dy = (grid.get(i + 1, j) - grid.get(i - 1, j)) / (2.0 * grid.dy)

    return (dz_dx, dz_dy)


def declividade_celula(grid: Grid2D, i: int, j: int, unidade: str = "razao") -> float:
    """Calcula a declividade máxima (magnitude do gradiente) na célula (i, j).

    Args:
        grid: Grade de elevação.
        i: Índice da linha.
        j: Índice da coluna.
        unidade: 'razao' (m/m), 'porcentagem' (%) ou 'graus' (°).
    """
    g = gradiente(grid, i, j)
    razao = norma(g)  # sqrt((dz/dx)^2 + (dz/dy)^2)
    return _converter_unidade_declividade(razao, unidade)


def declividade_entre_pontos(
    p1: tuple[float, float, float],
    p2: tuple[float, float, float],
    unidade: str = "razao",
    usar_modulo: bool = False,
) -> float:
    """Calcula a declividade direcional entre dois pontos 3D (x, y, z).

    Ideal para o A*/Dijkstra avaliar o esforço de subir ou descer uma aresta.
    """
    dist_planimetrica = distancia(p1[:2], p2[:2])
    if dist_planimetrica == 0.0:
        raise ValueError("Os pontos possuem a mesma coordenada planimétrica (distância zero).")

    dz = p2[2] - p1[2]
    if usar_modulo:
        dz = abs(dz)

    razao = dz / dist_planimetrica
    return _converter_unidade_declividade(razao, unidade)


def _converter_unidade_declividade(razao: float, unidade: str) -> float:
    """Converte a razão adimensional (dz / d_xy) para a unidade desejada."""
    if unidade == "razao":
        return razao
    if unidade == "porcentagem":
        return razao * 100.0
    if unidade == "graus":
        return math.degrees(math.atan(razao))
    raise ValueError(f"Unidade desconhecida: '{unidade}'. Use 'razao', 'porcentagem' ou 'graus'.")