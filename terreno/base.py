"""Interface de terreno.

Contrato comum: altitude em (lon, lat), grade de uma área e declividade.

Status: implementado.
"""

from abc import ABC, abstractmethod

from calclib.grid import Grid2D


class BaseTerrain(ABC):

    @abstractmethod
    def altitude(self, lon: float, lat: float) -> float:
        raise NotImplementedError

    @abstractmethod
    def obter_grade(
        self,
        area: tuple[float, float, float, float],
        resolucao_m: float,
    ) -> Grid2D:
        raise NotImplementedError

    @abstractmethod
    def declividade(self, lon: float, lat: float) -> float:
        raise NotImplementedError