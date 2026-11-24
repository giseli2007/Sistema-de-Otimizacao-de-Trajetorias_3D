"""Terreno em grade.

Terreno baseado em grade regular em memória (usa calclib.grid e calclib.interp).

Status: implementado.
"""

from typing import Sequence

from calclib.diff import declividade_celula
from calclib.grid import Grid2D
from calclib.interp import bilinear
from terreno.base import TerrenoBase, lonlat_para_metros, metros_para_lonlat


class GridTerrain(TerrenoBase):
    """Implementação de TerrenoBase apoiada em uma Grid2D regular em memória."""

    def __init__(
        self,
        grid: Grid2D,
        lon_origem: float,
        lat_origem: float,
    ) -> None:
        """Inicializa o terreno em grade georreferenciada.

        Args:
            grid: Malha regular 2D com altitudes em metros e passos (dx, dy) em metros.
            lon_origem: Longitude (graus) correspondente à origem (x=0, y=0) da grade.
            lat_origem: Latitude (graus) correspondente à origem (x=0, y=0) da grade.
        """
        self.grid = grid
        self.lon_origem = float(lon_origem)
        self.lat_origem = float(lat_origem)

    @classmethod
    def a_partir_de_matriz(
        cls,
        elevacoes: Sequence[Sequence[float]],
        lon_min: float,
        lat_min: float,
        lon_max: float,
        lat_max: float,
    ) -> "GridTerrain":
        """Constrói um GridTerrain calculando automaticamente a escala (dx, dy) em metros
        a partir dos limites geográficos (bounding box) e das dimensões da matriz.
        """
        linhas = len(elevacoes)
        colunas = len(elevacoes[0]) if linhas > 0 else 0
        if linhas < 2 or colunas < 2:
            raise ValueError("A matriz de elevações precisa ter pelo menos 2x2 células.")

        largura_m, altura_m = lonlat_para_metros(lon_max, lat_max, lon_min, lat_min)
        dx = largura_m / (colunas - 1)
        dy = altura_m / (linhas - 1)

        grid = Grid2D(dados=elevacoes, dx=dx, dy=dy, origem_x=0.0, origem_y=0.0)
        return cls(grid=grid, lon_origem=lon_min, lat_origem=lat_min)

    def _lonlat_para_grid_xy(self, lon: float, lat: float) -> tuple[float, float]:
        """Converte (lon, lat) para coordenadas métricas (x, y) relativas à origem da grade."""
        return lonlat_para_metros(lon, lat, self.lon_origem, self.lat_origem)

    def altitude(self, lon: float, lat: float) -> float:
        """Retorna a altitude interpolada (bilinear) na posição (lon, lat)."""
        x, y = self._lonlat_para_grid_xy(lon, lat)
        return bilinear(self.grid, x, y)

    def declividade(self, lon: float, lat: float, unidade: str = "razao") -> float:
        """Retorna a declividade máxima na célula mais próxima de (lon, lat)."""
        x, y = self._lonlat_para_grid_xy(lon, lat)
        i, j = self.grid.coord_para_indice(x, y)
        return declividade_celula(self.grid, i, j, unidade=unidade)

    def grade_area(
        self,
        lon_min: float,
        lat_min: float,
        lon_max: float,
        lat_max: float,
        resolucao_m: float | None = None,
    ) -> Grid2D:
        """Extrai uma sub-grade Grid2D em metros cobrindo a área [lon_min..lon_max, lat_min..lat_max].

        Se resolucao_m for None, mantém a resolução nativa (dx, dy) da grade original.
        A origem (0, 0) da sub-grade retornada corresponde ao canto (lon_min, lat_min).
        """
        largura_m, altura_m = lonlat_para_metros(lon_max, lat_max, lon_min, lat_min)
        if largura_m <= 0 or altura_m <= 0:
            raise ValueError("Os limites máximos devem ser maiores que os limites mínimos.")

        dx = resolucao_m if resolucao_m is not None else self.grid.dx
        dy = resolucao_m if resolucao_m is not None else self.grid.dy

        num_cols = max(2, int(round(largura_m / dx)) + 1)
        num_linhas = max(2, int(round(altura_m / dy)) + 1)

        dados_subgrade: list[list[float]] = []
        for i in range(num_linhas):
            y_local = i * dy
            linha_atual: list[float] = []
            for j in range(num_cols):
                x_local = j * dx
                lon_ponto, lat_ponto = metros_para_lonlat(
                    x_local, y_local, lon_min, lat_min
                )
                z = self.altitude(lon_ponto, lat_ponto)
                linha_atual.append(z)
            dados_subgrade.append(linha_atual)

        return Grid2D(
            dados=dados_subgrade,
            dx=dx,
            dy=dy,
            origem_x=0.0,
            origem_y=0.0,
        )