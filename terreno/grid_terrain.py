"""Terreno em grade.

Terreno baseado em uma grade regular em memória (usa calclib.grid e calclib.interp).

Status: implementado.
"""

import math

from terreno.base import BaseTerrain
from calclib.grid import Grid2D
from calclib.interp import bilinear
from calclib.diff import declividade_celula


class GridTerrain(BaseTerrain):
    RAIO_TERRA = 6371000.0
    LATITUDE_MAXIMA = 89.999999

    def __init__(
        self,
        grid: Grid2D,
        origem_lon: float,
        origem_lat: float,
    ):
        if not isinstance(grid, Grid2D):
            raise TypeError("grid precisa ser uma instância de Grid2D.")

        if not math.isfinite(origem_lon) or not -180 <= origem_lon <= 180:
            raise ValueError("Longitude de origem inválida.")

        if (
            not math.isfinite(origem_lat)
            or not -self.LATITUDE_MAXIMA <= origem_lat <= self.LATITUDE_MAXIMA
        ):
            raise ValueError("Latitude de origem inválida ou próxima dos polos.")

        self.grid = grid
        self.origem_lon = origem_lon
        self.origem_lat = origem_lat

        self.cos_lat = math.cos(math.radians(origem_lat))

        if abs(self.cos_lat) < 1e-10:
            raise ValueError("A origem não pode estar próxima dos polos.")

    def coordenadas_metricas(
        self,
        lon: float,
        lat: float,
    ) -> tuple[float, float]:
        if not math.isfinite(lon) or not -180 <= lon <= 180:
            raise ValueError("Longitude inválida.")

        if (
            not math.isfinite(lat)
            or not -self.LATITUDE_MAXIMA <= lat <= self.LATITUDE_MAXIMA
        ):
            raise ValueError("Latitude inválida ou próxima dos polos.")

        x = self.grid.origem_x + (
            math.radians(lon - self.origem_lon)
            * self.RAIO_TERRA
            * self.cos_lat
        )

        y = self.grid.origem_y + (
            math.radians(lat - self.origem_lat)
            * self.RAIO_TERRA
        )

        return x, y

    def altitude(self, lon: float, lat: float) -> float:
        x, y = self.coordenadas_metricas(lon, lat)
        return bilinear(self.grid, x, y)

    def declividade(self, lon: float, lat: float) -> float:
        x, y = self.coordenadas_metricas(lon, lat)
        i, j = self.grid.coord_para_indice(x, y)

        if not self.grid.dentro_dos_limites(i, j):
            raise ValueError("Coordenada fora dos limites do terreno.")

        return declividade_celula(
            self.grid,
            i,
            j,
            unidade="razao",
        )

    def obter_grade(
        self,
        area: tuple[float, float, float, float],
        resolucao_m: float,
    ) -> Grid2D:

        if not math.isfinite(resolucao_m) or resolucao_m <= 0:
            raise ValueError("A resolução deve ser positiva e finita.")

        if len(area) != 4:
            raise ValueError(

            )

        if not all(math.isfinite(valor) for valor in area):
            raise ValueError("A área possui coordenadas inválidas.")

        lon_min, lat_min, lon_max, lat_max = area

        if (
            lon_min < -180
            or lon_max > 180
            or lat_min < -self.LATITUDE_MAXIMA
            or lat_max > self.LATITUDE_MAXIMA
            or lon_min >= lon_max
            or lat_min >= lat_max
        ):
            raise ValueError("Área geográfica inválida.")

        x_min, y_min = self.coordenadas_metricas(lon_min, lat_min)
        x_max, y_max = self.coordenadas_metricas(lon_max, lat_max)

        colunas = max(2, math.ceil((x_max - x_min) / resolucao_m) + 1)
        linhas = max(2, math.ceil((y_max - y_min) / resolucao_m) + 1)

        dx = (x_max - x_min) / (colunas - 1)
        dy = (y_max - y_min) / (linhas - 1)

        dados = []

        for i in range(linhas):
            linha = []

            for j in range(colunas):
                x = x_min + j * dx
                y = y_min + i * dy

                linha.append(bilinear(self.grid, x, y))

            dados.append(linha)

        return Grid2D(
            dados=dados,
            dx=dx,
            dy=dy,
            origem_x=x_min,
            origem_y=y_min,
        )