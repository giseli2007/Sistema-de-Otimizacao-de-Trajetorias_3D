"""Terrenos sintéticos.

Planos, rampas e colinas para testes e comparações, sem depender de dados reais.

Status: implementado.
"""

import math

from calclib.grid import Grid2D
from terreno.grid_terrain import GridTerrain


def _validar_parametros(
    linhas: int,
    colunas: int,
    dx: float,
    dy: float,
) -> None:

    if not isinstance(linhas, int) or isinstance(linhas, bool) or linhas < 2:
        raise ValueError("O terreno precisa ter pelo menos 2 linhas.")

    if not isinstance(colunas, int) or isinstance(colunas, bool) or colunas < 2:
        raise ValueError("O terreno precisa ter pelo menos 2 colunas.")

    if not math.isfinite(dx) or dx <= 0:
        raise ValueError("A resolução dx deve ser positiva e finita.")

    if not math.isfinite(dy) or dy <= 0:
        raise ValueError("A resolução dy deve ser positiva e finita.")


def _criar_terreno(
    dados: list[list[float]],
    dx: float,
    dy: float,
    origem_lon: float,
    origem_lat: float,
) -> GridTerrain:

    grade = Grid2D(
        dados=dados,
        dx=dx,
        dy=dy,
    )

    return GridTerrain(
        grid=grade,
        origem_lon=origem_lon,
        origem_lat=origem_lat,
    )


def criar_plano(
    linhas: int = 50,
    colunas: int = 50,
    dx: float = 10.0,
    dy: float = 10.0,
    altitude: float = 100.0,
    origem_lon: float = 0.0,
    origem_lat: float = 0.0,
) -> GridTerrain:

    _validar_parametros(linhas, colunas, dx, dy)

    if not math.isfinite(altitude):
        raise ValueError("A altitude deve ser um número finito.")

    dados = [
        [altitude for _ in range(colunas)]
        for _ in range(linhas)
    ]

    return _criar_terreno(
        dados, dx, dy, origem_lon, origem_lat
    )


def criar_rampa(
    linhas: int = 50,
    colunas: int = 50,
    dx: float = 10.0,
    dy: float = 10.0,
    altitude_base: float = 100.0,
    inclinacao: float = 0.10,
    origem_lon: float = 0.0,
    origem_lat: float = 0.0,
) -> GridTerrain:

    _validar_parametros(linhas, colunas, dx, dy)

    if not math.isfinite(altitude_base) or not math.isfinite(inclinacao):
        raise ValueError("A altitude e a inclinação devem ser finitas.")

    dados = []

    for i in range(linhas):
        linha = []

        for j in range(colunas):
            x = j * dx
            altitude = altitude_base + inclinacao * x
            linha.append(altitude)

        dados.append(linha)

    return _criar_terreno(
        dados, dx, dy, origem_lon, origem_lat
    )


def criar_colina(
    linhas: int = 50,
    colunas: int = 50,
    dx: float = 10.0,
    dy: float = 10.0,
    altitude_base: float = 100.0,
    altura: float = 50.0,
    origem_lon: float = 0.0,
    origem_lat: float = 0.0,
) -> GridTerrain:

    _validar_parametros(linhas, colunas, dx, dy)

    if not math.isfinite(altitude_base) or not math.isfinite(altura):
        raise ValueError("A altitude e a altura devem ser finitas.")

    centro_x = (colunas - 1) * dx / 2
    centro_y = (linhas - 1) * dy / 2

    raio = min(centro_x, centro_y) / 2

    dados = []

    for i in range(linhas):
        linha = []

        for j in range(colunas):
            x = j * dx
            y = i * dy

            distancia = math.sqrt(
                (x - centro_x) ** 2 + (y - centro_y) ** 2
            )

            elevacao = altura * math.exp(
                -(distancia ** 2) / (2 * raio ** 2)
            )

            linha.append(altitude_base + elevacao)

        dados.append(linha)

    return _criar_terreno(
        dados, dx, dy, origem_lon, origem_lat
    )


def criar_vale(
    linhas: int = 50,
    colunas: int = 50,
    dx: float = 10.0,
    dy: float = 10.0,
    altitude_base: float = 100.0,
    profundidade: float = 40.0,
    origem_lon: float = 0.0,
    origem_lat: float = 0.0,
) -> GridTerrain:

    if not math.isfinite(profundidade) or profundidade < 0:
        raise ValueError("A profundidade deve ser finita e não negativa.")

    return criar_colina(
        linhas=linhas,
        colunas=colunas,
        dx=dx,
        dy=dy,
        altitude_base=altitude_base,
        altura=-profundidade,
        origem_lon=origem_lon,
        origem_lat=origem_lat,
    )


def criar_montanhoso(
    linhas: int = 50,
    colunas: int = 50,
    dx: float = 10.0,
    dy: float = 10.0,
    altitude_base: float = 100.0,
    amplitude: float = 30.0,
    origem_lon: float = 0.0,
    origem_lat: float = 0.0,
) -> GridTerrain:

    _validar_parametros(linhas, colunas, dx, dy)

    if not math.isfinite(altitude_base) or not math.isfinite(amplitude):
        raise ValueError("A altitude e a amplitude devem ser finitas.")

    dados = []

    for i in range(linhas):
        linha = []

        for j in range(colunas):
            x = j * dx
            y = i * dy

            variacao = (
                math.sin(x / 40) * math.cos(y / 35)
                + 0.5 * math.sin(x / 15)
                + 0.3 * math.cos(y / 20)
            )

            altitude = altitude_base + amplitude * variacao
            linha.append(altitude)

        dados.append(linha)

    return _criar_terreno(
        dados, dx, dy, origem_lon, origem_lat
    )