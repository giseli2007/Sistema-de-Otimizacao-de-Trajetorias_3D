"""Função de custo.

Custo de percorrer um segmento: distância, declividade, superfície, consumo.

Status: implementado.
"""

from dataclasses import dataclass

from calclib.diff import declividade_entre_pontos
from calclib.grid import Grid2D
from calclib.vec import distancia
from model.vehicle import Vehicle


@dataclass(frozen=True)
class PesosOtimizacao:
    """Pesos para calibrar o objetivo da otimização da trajetória.

    Attributes:
        peso_distancia: Importância da distância/consumo energético base.
        peso_declividade: Penalidade extra para rampas íngremes.
        peso_superficie: Multiplicador do tipo de piso/via (ex: 0.7 para via existente, 1.0 natural).
        peso_cubagem: Custo por m³ de corte/aterro (0.0 se for apenas navegação sem terraplanagem).
        cota_projeto: Altitude alvo (m) usada apenas quando peso_cubagem > 0.
    """

    peso_distancia: float = 1.0
    peso_declividade: float = 1.0
    peso_superficie: float = 1.0
    peso_cubagem: float = 0.0
    cota_projeto: float | None = None


def custo_segmento(
    grid: Grid2D,
    origem: tuple[int, int],
    destino: tuple[int, int],
    veiculo: Vehicle,
    pesos: PesosOtimizacao | None = None,
    fator_superficie: float = 1.0,
) -> float:
    """Calcula o custo total (peso da aresta) para ir da célula 'origem' até 'destino'.

    Garante sempre retorno estritamente positivo (> 0) para preservar a otimalidade
    dos algoritmos Dijkstra e A*.
    """
    if pesos is None:
        pesos = PesosOtimizacao()

    i1, j1 = origem
    i2, j2 = destino

    x1, y1 = grid.indice_para_coord(i1, j1)
    x2, y2 = grid.indice_para_coord(i2, j2)
    z1 = grid.get(i1, j1)
    z2 = grid.get(i2, j2)

    p1 = (x1, y1, z1)
    p2 = (x2, y2, z2)

    # 1. Distância real 3D percorrida no segmento
    dist_3d = distancia(p1, p2)
    if dist_3d == 0.0:
        return 0.0

    # 2. Efeito da declividade (subida vs descida)
    # usar_modulo=False: subida > 0, descida < 0
    inc = declividade_entre_pontos(p1, p2, unidade="razao", usar_modulo=False)

    if inc >= 0.0:
        # Subida: consumo aumenta proporcionalmente à rampa e ao fator_subida do veículo
        fator_rampa = 1.0 + (veiculo.fator_subida * inc * pesos.peso_declividade)
    else:
        # Descida: leve economia de energia, mas travada em no mínimo 0.5 para evitar
        # ciclos negativos ou custos próximos de zero no Dijkstra/A*
        economia = min(0.5, 0.5 * abs(inc) * pesos.peso_declividade)
        fator_rampa = 1.0 - economia

    # 3. Custo base de deslocamento + superfície (mapa base/vias)
    mult_superficie = max(0.1, fator_superficie * pesos.peso_superficie)
    custo_deslocamento = (
        dist_3d
        * veiculo.consumo_base
        * pesos.peso_distancia
        * fator_rampa
        * mult_superficie
    )

    # 4. Custo de cubagem (terraplanagem na célula de destino, se ativado)
    custo_terraplanagem = 0.0
    if pesos.peso_cubagem > 0.0 and pesos.cota_projeto is not None:
        altura_corte_aterro = abs(z2 - pesos.cota_projeto)
        volume_celula = altura_corte_aterro * grid.area_celula()
        custo_terraplanagem = volume_celula * pesos.peso_cubagem

    return custo_deslocamento + custo_terraplanagem


def heuristica_astar(
    grid: Grid2D,
    atual: tuple[int, int],
    objetivo: tuple[int, int],
    veiculo: Vehicle,
    fator_minimo_superficie: float = 0.5,
) -> float:
    """Heurística admissível h(n) para o A*: nunca superestima o custo real restante.

    Usa a distância euclidiana em linha reta multiplicada pelo menor custo unitário
    possível, garantindo que o A* encontre sempre o caminho ótimo global.
    """
    x1, y1 = grid.indice_para_coord(*atual)
    x2, y2 = grid.indice_para_coord(*objetivo)
    z1 = grid.get(*atual)
    z2 = grid.get(*objetivo)

    dist_reta = distancia((x1, y1, z1), (x2, y2, z2))
    # O menor fator possível em custo_segmento é 0.5 (descida máxima) * fator_minimo_superficie
    custo_unitario_minimo = veiculo.consumo_base * 0.5 * fator_minimo_superficie
    return dist_reta * custo_unitario_minimo