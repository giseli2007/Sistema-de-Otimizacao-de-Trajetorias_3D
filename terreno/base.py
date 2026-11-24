"""Interface de terreno.

Contrato comum: altitude em (lon, lat), grade de uma área e declividade.

Status: implementado.
"""

import math
from abc import ABC, abstractmethod
from calclib.grid import Grid2D

# Raio médio equatorial da Terra (WGS84 / Web Mercator) em metros
RAIO_TERRA_M: float = 6_378_137.0


def lonlat_para_metros(
    lon: float,
    lat: float,
    lon_origem: float,
    lat_origem: float,
) -> tuple[float, float]: #tuple significa que a função retorna uma tupla de dois valores float
    """Converte coordenadas geográficas (lon, lat) em graus para plano local (x, y) em metros.

    Usa projeção equiretangular local tangente à latitude de origem.
    """
    lat_rad = math.radians(lat_origem)
    dx_rad = math.radians(lon - lon_origem)
    dy_rad = math.radians(lat - lat_origem)

    x = dx_rad * RAIO_TERRA_M * math.cos(lat_rad)
    y = dy_rad * RAIO_TERRA_M
    return (x, y)


def metros_para_lonlat(
    x: float,
    y: float,
    lon_origem: float,
    lat_origem: float,
) -> tuple[float, float]:
    """Converte coordenadas métricas locais (x, y) de volta para (lon, lat) em graus."""
    lat_rad = math.radians(lat_origem)
    cos_lat = math.cos(lat_rad)
    if cos_lat == 0.0:
        raise ValueError("Latitude de origem inválida nos polos (±90°).")

    lon = lon_origem + math.degrees(x / (RAIO_TERRA_M * cos_lat))
    lat = lat_origem + math.degrees(y / RAIO_TERRA_M)
    return (lon, lat)


class TerrenoBase(ABC):
    """Contrato comum (classe abstrata) para qualquer fonte de elevação do sistema."""

    @abstractmethod
    def altitude(self, lon: float, lat: float) -> float:
        """Retorna a altitude z (em metros) na coordenada geográfica (lon, lat)."""
        ...

    @abstractmethod
    def declividade(self, lon: float, lat: float, unidade: str = "razao") -> float:
        """Retorna a declividade máxima na coordenada geográfica (lon, lat)."""
        ...

    @abstractmethod
    def grade_area(
        self,
        lon_min: float,
        lat_min: float,
        lon_max: float,
        lat_max: float,
        resolucao_m: float | None = None,
    ) -> Grid2D:
        """Extrai uma Grid2D regular em metros cobrindo a área geográfica especificada."""
        ...

    def altimetria_rota(
        self,
        pontos_lonlat: list[tuple[float, float]],
    ) -> list[tuple[float, float, float]]:
        """Converte uma sequência de pontos (lon, lat) para (x, y, z) em metros locais."""
        if not pontos_lonlat:
            return []

        lon0, lat0 = pontos_lonlat[0]
        resultado: list[tuple[float, float, float]] = []
        for lon, lat in pontos_lonlat:
            x, y = lonlat_para_metros(lon, lat, lon0, lat0)
            z = self.altitude(lon, lat)
            resultado.append((x, y, z))
        return resultado