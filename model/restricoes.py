"""Restrições topográficas.

Declividade máxima, trechos proibidos etc., aplicadas ao grafo.

Status: implementado.
"""

from dataclasses import dataclass, field
from typing import Sequence

from calclib.diff import declividade_celula, declividade_entre_pontos
from calclib.grid import Grid2D
from calclib.integrate import Ponto2D, ponto_no_poligono
from calclib.vec import angulo, distancia, subtrair
from model.vehicle import Vehicle


@dataclass(frozen=True)
class RestricoesTopograficas:
    """Agrupa todas as restrições espaciais e ambientais ativas na simulação.

    Attributes:
        cota_inundacao: Nível da água em metros. Pontos abaixo desse nível (descontando
            o vau do veículo) são bloqueados. None desativa a restrição.
        zonas_proibidas: Lista de polígonos [(x, y), ...] onde a passagem é proibida.
        area_permitida: Polígono opcional [(x, y), ...] que delimita a área máxima de busca.
        verificar_declividade_lateral: Se True, bloqueia células cuja inclinação intrínseca
            (gradiente) exceda a declividade máxima do veículo.
    """

    cota_inundacao: float | None = None
    zonas_proibidas: Sequence[Sequence[Ponto2D]] = field(default_factory=list)
    area_permitida: Sequence[Ponto2D] | None = None
    verificar_declividade_lateral: bool = True


def verificar_inundacao(
    altitude: float,
    restricoes: RestricoesTopograficas,
    veiculo: Vehicle,
) -> bool:
    """Retorna True se o ponto NÃO está alagado acima do limite do veículo."""
    if restricoes.cota_inundacao is None:
        return True

    lamina_agua = restricoes.cota_inundacao - altitude
    return lamina_agua <= veiculo.profundidade_vau_max


def verificar_zonas(
    x: float,
    y: float,
    restricoes: RestricoesTopograficas,
) -> bool:
    """Retorna True se (x, y) está dentro da área permitida e fora das zonas proibidas."""
    if restricoes.area_permitida is not None:
        if not ponto_no_poligono(x, y, restricoes.area_permitida):
            return False

    for poligono in restricoes.zonas_proibidas:
        if ponto_no_poligono(x, y, poligono):
            return False

    return True


def no_transitavel(
    grid: Grid2D,
    i: int,
    j: int,
    veiculo: Vehicle,
    restricoes: RestricoesTopograficas,
) -> bool:
    """Verifica se uma célula (i, j) isolada atende a todas as restrições topográficas."""
    if not grid.dentro_dos_limites(i, j):
        return False

    altitude = grid.get(i, j)
    if not verificar_inundacao(altitude, restricoes, veiculo):
        return False

    x, y = grid.indice_para_coord(i, j)
    if not verificar_zonas(x, y, restricoes):
        return False

    if restricoes.verificar_declividade_lateral:
        inc_celula = declividade_celula(grid, i, j, unidade="razao")
        if inc_celula > veiculo.declividade_maxima:
            return False

    return True


def transicao_valida(
    grid: Grid2D,
    origem: tuple[int, int],
    destino: tuple[int, int],
    veiculo: Vehicle,
    restricoes: RestricoesTopograficas,
    anterior: tuple[int, int] | None = None,
) -> bool:
    """Verifica se o veículo pode ir da célula 'origem' (i1, j1) para 'destino' (i2, j2).

    Esta é a função principal a ser chamada pelo A* e pelo Dijkstra ao expandir vizinhos.
    """
    i2, j2 = destino
    if not no_transitavel(grid, i2, j2, veiculo, restricoes):
        return False

    i1, j1 = origem
    x1, y1 = grid.indice_para_coord(i1, j1)
    x2, y2 = grid.indice_para_coord(i2, j2)
    z1 = grid.get(i1, j1)
    z2 = grid.get(i2, j2)

    # Verifica a declividade longitudinal (rampa de subida ou descida) entre origem e destino
    inc_rampa = declividade_entre_pontos(
        (x1, y1, z1),
        (x2, y2, z2),
        unidade="razao",
        usar_modulo=True,
    )
    if inc_rampa > veiculo.declividade_maxima:
        return False

    # Se o planejador informar o nó anterior, verifica também o raio mínimo de curvatura
    if anterior is not None and veiculo.raio_minimo > 0.0:
        i0, j0 = anterior
        x0, y0 = grid.indice_para_coord(i0, j0)

        v_entrada = subtrair((x1, y1), (x0, y0))
        v_saida = subtrair((x2, y2), (x1, y1))

        passo = distancia((x1, y1), (x2, y2))
        if passo > 0.0:
            deflexao = angulo(v_entrada, v_saida, em_graus=False)
            max_deflexao = veiculo.angulo_curva_maximo(passo, em_graus=False)
            if deflexao > max_deflexao:
                return False

    return True