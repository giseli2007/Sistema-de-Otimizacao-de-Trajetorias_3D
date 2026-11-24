"""Terrenos sintéticos.

Planos, rampas e colinas para testes e comparações, sem depender de dados reais.

Status: implementado.
"""

import math
from typing import Callable

from calclib.diff import declividade_celula
from calclib.grid import Grid2D
from terreno.base import TerrenoBase, lonlat_para_metros, metros_para_lonlat

FuncaoRelevo = Callable[[float, float], float] # Callable é um tipo que representa uma função que recebe dois floats (x, y) e retorna um float (z).


class TerrenoSintetico(TerrenoBase):
    """Terreno definido por uma função analítica z = f(x, y) em metros locais."""

    def __init__(
        self,
        funcao_z: FuncaoRelevo,
        lon_origem: float = -63.90,
        lat_origem: float = -8.76,
    ) -> None:
        """Inicializa um terreno sintético georreferenciado.

        Args:
            funcao_z: Função f(x, y) que recebe metros locais e retorna altitude z (m).
            lon_origem: Longitude de referência para (x=0, y=0).
            lat_origem: Latitude de referência para (x=0, y=0).
        """
        self.funcao_z = funcao_z
        self.lon_origem = float(lon_origem)
        self.lat_origem = float(lat_origem)

    def altitude(self, lon: float, lat: float) -> float:
        """Calcula a altitude exata f(x, y) na coordenada geográfica (lon, lat)."""
        x, y = lonlat_para_metros(lon, lat, self.lon_origem, self.lat_origem)
        return float(self.funcao_z(x, y))

    def declividade(self, lon: float, lat: float, unidade: str = "razao") -> float:
        """Estima a declividade local em (lon, lat) usando diferenças finitas."""
        passo_m = 1.0
        lon_min, lat_min = metros_para_lonlat(-passo_m, -passo_m, lon, lat)
        lon_max, lat_max = metros_para_lonlat(passo_m, passo_m, lon, lat)
        subgrade = self.grade_area(lon_min, lat_min, lon_max, lat_max, resolucao_m=passo_m)
        # O ponto (lon, lat) fica exatamente no centro (1, 1) da grade 3x3
        return declividade_celula(subgrade, 1, 1, unidade=unidade)

    def grade_area(
        self,
        lon_min: float,
        lat_min: float,
        lon_max: float,
        lat_max: float,
        resolucao_m: float | None = None,
    ) -> Grid2D:
        """Gera uma Grid2D regular em metros avaliando f(x, y) em cada nó."""
        largura_m, altura_m = lonlat_para_metros(lon_max, lat_max, lon_min, lat_min)
        if largura_m <= 0 or altura_m <= 0:
            raise ValueError("Os limites máximos devem ser maiores que os limites mínimos.")

        dx = resolucao_m if resolucao_m is not None else 10.0
        dy = dx

        num_cols = max(2, int(round(largura_m / dx)) + 1)
        num_linhas = max(2, int(round(altura_m / dy)) + 1)

        dados: list[list[float]] = []
        for i in range(num_linhas):
            y_local = i * dy
            linha: list[float] = []
            for j in range(num_cols):
                x_local = j * dx
                lon_p, lat_p = metros_para_lonlat(x_local, y_local, lon_min, lat_min)
                linha.append(self.altitude(lon_p, lat_p))
            dados.append(linha)

        return Grid2D(dados=dados, dx=dx, dy=dy, origem_x=0.0, origem_y=0.0)

    # --- Construtores prontos para cenários de teste ---

    @classmethod
    def plano(
        cls,
        cota: float = 100.0,
        lon_origem: float = -63.90,
        lat_origem: float = -8.76,
    ) -> "TerrenoSintetico":
        """Cria um terreno perfeitamente plano na altitude 'cota' (em metros)."""
        return cls(lambda x, y: cota, lon_origem=lon_origem, lat_origem=lat_origem)

    @classmethod
    def rampa(
        cls,
        cota_inicial: float = 50.0,
        declividade_x: float = 0.10,
        declividade_y: float = 0.0,
        lon_origem: float = -63.90,
        lat_origem: float = -8.76,
    ) -> "TerrenoSintetico":
        """Cria um plano inclinado z = z0 + declividade_x * x + declividade_y * y."""
        return cls(
            lambda x, y: cota_inicial + declividade_x * x + declividade_y * y,
            lon_origem=lon_origem,
            lat_origem=lat_origem,
        )

    @classmethod
    def colina_gaussiana(
        cls,
        cota_base: float = 50.0,
        altura_pico: float = 80.0,
        centro_x: float = 250.0,
        centro_y: float = 250.0,
        raio_dispersao: float = 70.0,
        lon_origem: float = -63.90,
        lat_origem: float = -8.76,
    ) -> "TerrenoSintetico":
        """Cria uma colina suave (gaussiana) centrada em (centro_x, centro_y) metros."""
        dois_sigma2 = 2.0 * (raio_dispersao ** 2)

        def _f(x: float, y: float) -> float:
            dist2 = (x - centro_x) ** 2 + (y - centro_y) ** 2
            return cota_base + altura_pico * math.exp(-dist2 / dois_sigma2)

        return cls(_f, lon_origem=lon_origem, lat_origem=lat_origem)