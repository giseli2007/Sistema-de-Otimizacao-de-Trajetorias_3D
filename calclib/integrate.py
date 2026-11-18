"""Integração numérica.

Ex.: custo acumulado ao longo de um caminho.

Status: implementado.
"""

from typing import Sequence
from calclib.grid import Grid2D
from calclib.vec import distancia

Ponto2D = tuple[float, float]
Ponto3D = tuple[float, float, float]


def trapezio_1d(valores_f: Sequence[float], passos_ds: Sequence[float]) -> float:
    """Integra numericamente uma função f(s) ao longo de segmentos de comprimento ds.

    Usa a Regra do Trapézio composta: soma de ((f_i + f_{i+1}) / 2) * ds_i.
    Ideal para calcular o custo energético/operacional acumulado de um trajeto.
    """
    if len(valores_f) < 2:
        return 0.0
    if len(passos_ds) != len(valores_f) - 1:
        raise ValueError(
            "O número de passos (ds) deve ser exatamente len(valores_f) - 1."
        )

    total = 0.0
    for i in range(len(passos_ds)):
        media_altura = 0.5 * (valores_f[i] + valores_f[i + 1])
        total += media_altura * passos_ds[i]
    return total


def comprimento_caminho(pontos: Sequence[Sequence[float]], usar_3d: bool = True) -> float:
    """Calcula o comprimento total acumulado de uma trajetória (planimétrico 2D ou real 3D)."""
    if len(pontos) < 2:
        return 0.0

    total = 0.0
    for i in range(len(pontos) - 1):
        p1 = pontos[i] if usar_3d else pontos[i][:2]
        p2 = pontos[i + 1] if usar_3d else pontos[i + 1][:2]
        total += distancia(p1, p2)
    return total


def area_poligono(vertices_xy: Sequence[Ponto2D]) -> float:
    """Calcula a área planimétrica (em m²) de um polígono fechado pela Fórmula de Shoelace.

    Args:
        vertices_xy: Sequência ordenada de vértices (x, y) em metros.
    """
    n = len(vertices_xy)
    if n < 3:
        return 0.0

    soma = 0.0
    for i in range(n):
        x1, y1 = vertices_xy[i]
        x2, y2 = vertices_xy[(i + 1) % n]  # O '% n' fecha o último vértice com o primeiro
        soma += (x1 * y2) - (x2 * y1)

    return 0.5 * abs(soma)


def ponto_no_poligono(x: float, y: float, vertices_xy: Sequence[Ponto2D]) -> bool:
    """Verifica se o ponto (x, y) está dentro do polígono (algoritmo Ray Casting)."""
    n = len(vertices_xy)
    if n < 3:
        return False

    dentro = False
    j = n - 1
    for i in range(n):
        xi, yi = vertices_xy[i]
        xj, yj = vertices_xy[j]

        cruza_y = (yi > y) != (yj > y)
        if cruza_y:
            x_intersecao = (xj - xi) * (y - yi) / (yj - yi) + xi
            if x < x_intersecao:
                dentro = not dentro
        j = i

    return dentro


def cubagem_grade(
    grid: Grid2D,
    cota_projeto: float,
    poligono_xy: Sequence[Ponto2D] | None = None,
) -> tuple[float, float]:
    """Calcula os volumes de corte e aterro (em m³) em relação a uma cota de projeto.

    Args:
        grid: Grade de elevação com escala métrica (dx, dy).
        cota_projeto: Altitude alvo (em metros) para nivelamento do terreno.
        poligono_xy: Polígono opcional (em metros) para restringir a área da cubagem.

    Returns:
        Tupla (volume_corte, volume_aterro) em metros cúbicos (m³).
    """
    area_cel = grid.area_celula()
    vol_corte = 0.0
    vol_aterro = 0.0

    for i in range(grid.linhas):
        for j in range(grid.colunas):
            if poligono_xy is not None:
                x, y = grid.indice_para_coord(i, j)
                if not ponto_no_poligono(x, y, poligono_xy):
                    continue

            z_terreno = grid.get(i, j)
            diferenca = z_terreno - cota_projeto

            if diferenca > 0.0:
                # Terreno mais alto que o projeto -> precisa escavar (corte)
                vol_corte += diferenca * area_cel
            elif diferenca < 0.0:
                # Terreno mais baixo que o projeto -> precisa preencher (aterro)
                vol_aterro += abs(diferenca) * area_cel

    return (vol_corte, vol_aterro)