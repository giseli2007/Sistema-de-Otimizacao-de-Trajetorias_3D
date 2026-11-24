"""Relevo dos tiles do mapa.

Lê os MESMOS tiles "terrarium" que o mapa web exibe (AWS/Mapterhorn), para planejar sobre o que se vê. Busca só os tiles da área; nenhum arquivo de dados é baixado.

Status: implementado.
"""

import io
import math
import urllib.request
from dataclasses import dataclass

from PIL import Image

from calclib.grid import Grid2D
from terreno.base import TerrenoBase
from terreno.grid_terrain import GridTerrain

# Fontes padrão de tiles Terrarium RGB
URLS_TERRARIUM: dict[str, str] = {
    "aws": "https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png",
    "mapterhorn": "https://tiles.mapterhorn.com/{z}/{x}/{y}.webp",
}


@dataclass(frozen=True)
class ConfigFonteTiles:
    """Configuração de uma fonte web de tiles de elevação."""

    url_template: str
    zoom_padrao: int
    tile_size: int = 256


FONTES_PADRAO: dict[str, ConfigFonteTiles] = {
    "aws": ConfigFonteTiles(
        url_template=URLS_TERRARIUM["aws"],
        zoom_padrao=14,
        tile_size=256,
    ),
    "mapterhorn": ConfigFonteTiles(
        url_template=URLS_TERRARIUM["mapterhorn"],
        zoom_padrao=15,
        tile_size=512,
    ),
}


def rgb_para_altitude_terrarium(r: int, g: int, b: int) -> float:
    """Converte um pixel RGB codificado no formato Terrarium para altitude em metros."""
    return (r * 256.0 + g + (b / 256.0)) - 32768.0


def lonlat_para_tile(lon: float, lat: float, zoom: int) -> tuple[int, int]:
    """Converte coordenadas geográficas (lon, lat) para índices de tile Web Mercator (x, y)."""
    n = 2 ** zoom
    x = int(math.floor((lon + 180.0) / 360.0 * n))
    lat_rad = math.radians(lat)
    y = int(
        math.floor(
            (1.0 - math.log(math.tan(lat_rad) + (1.0 / math.cos(lat_rad))) / math.pi)
            / 2.0
            * n
        )
    )
    x = max(0, min(n - 1, x))
    y = max(0, min(n - 1, y))
    return (x, y)


def tile_para_lonlat(x: int, y: int, zoom: int) -> tuple[float, float]:
    """Retorna a coordenada geográfica (lon, lat) do canto superior esquerdo (NW) do tile (x, y)."""
    n = 2 ** zoom
    lon = x / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1.0 - 2.0 * y / n)))
    lat = math.degrees(lat_rad)
    return (lon, lat)


class TerrariumTerrain(TerrenoBase):
    """Lê tiles Terrarium (AWS ou Mapterhorn) sob demanda em memória e expõe TerrenoBase."""

    def __init__(
        self,
        fonte: str = "aws",
        zoom: int | None = None,
        url_template: str | None = None,
        timeout: float = 10.0,
    ) -> None:
        if fonte in FONTES_PADRAO:
            cfg = FONTES_PADRAO[fonte]
            self.url_template = url_template or cfg.url_template
            self.zoom = zoom if zoom is not None else cfg.zoom_padrao
        else:
            if url_template is None:
                raise ValueError(
                    f"Fonte '{fonte}' desconhecida. Use 'aws', 'mapterhorn' ou informe 'url_template'."
                )
            self.url_template = url_template
            self.zoom = zoom if zoom is not None else 14

        self.timeout = timeout
        # Cache em memória: {(z, x, y): matriz_altitudes_sul_para_norte}
        self._cache_tiles: dict[tuple[int, int, int], list[list[float]]] = {}

    def _baixar_tile(self, x: int, y: int) -> list[list[float]]:
        """Busca um único tile em memória, decodifica RGB -> metros e armazena no cache."""
        chave = (self.zoom, x, y)
        if chave in self._cache_tiles:
            return self._cache_tiles[chave]

        url = self.url_template.format(z=self.zoom, x=x, y=y)
        req = urllib.request.Request(url, headers={"User-Agent": "SistemaOtimizacao3D/1.0"})

        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            bytes_imagem = resp.read()

        with Image.open(io.BytesIO(bytes_imagem)) as img:
            img_rgb = img.convert("RGB")
            largura, altura = img_rgb.size
            pixels = img_rgb.load()

            # Lê as linhas da imagem de baixo para cima (Sul -> Norte)
            # para alinhar com o sistema de coordenadas do GridTerrain (i=0 no Sul)
            matriz: list[list[float]] = []
            for py in range(altura - 1, -1, -1):
                linha: list[float] = []
                for px in range(largura):
                    r, g, b = pixels[px, py]
                    linha.append(rgb_para_altitude_terrarium(r, g, b))
                matriz.append(linha)

        self._cache_tiles[chave] = matriz
        return matriz

    def _montar_grid_terrain_area(
        self,
        lon_min: float,
        lat_min: float,
        lon_max: float,
        lat_max: float,
    ) -> GridTerrain:
        """Costura os tiles necessários para cobrir a bounding box em um único GridTerrain."""
        # Em Web Mercator, Y cresce para o Sul (lat_max -> y_min, lat_min -> y_max)
        tx_min, ty_min = lonlat_para_tile(lon_min, lat_max, self.zoom)
        tx_max, ty_max = lonlat_para_tile(lon_max, lat_min, self.zoom)

        # Limites geográficos exatos do mosaico de tiles baixados
        mosaico_lon_min, mosaico_lat_max = tile_para_lonlat(tx_min, ty_min, self.zoom)
        mosaico_lon_max, mosaico_lat_min = tile_para_lonlat(tx_max + 1, ty_max + 1, self.zoom)

        # Costura os tiles de Sul (ty_max) para Norte (ty_min) e Oeste (tx_min) para Leste (tx_max)
        matriz_completa: list[list[float]] = []
        for ty in range(ty_max, ty_min - 1, -1):
            tiles_da_faixa = [self._baixar_tile(tx, ty) for tx in range(tx_min, tx_max + 1)]
            altura_tile = len(tiles_da_faixa[0])
            for linha_idx in range(altura_tile):
                linha_costurada: list[float] = []
                for tile in tiles_da_faixa:
                    linha_costurada.extend(tile[linha_idx])
                matriz_completa.append(linha_costurada)

        return GridTerrain.a_partir_de_matriz(
            elevacoes=matriz_completa,
            lon_min=mosaico_lon_min,
            lat_min=mosaico_lat_min,
            lon_max=mosaico_lon_max,
            lat_max=mosaico_lat_max,
        )

    def altitude(self, lon: float, lat: float) -> float:
        """Retorna a altitude (em metros) do ponto (lon, lat) a partir do tile correspondente."""
        tx, ty = lonlat_para_tile(lon, lat, self.zoom)
        tile_matriz = self._baixar_tile(tx, ty)

        lon_oeste, lat_norte = tile_para_lonlat(tx, ty, self.zoom)
        lon_leste, lat_sul = tile_para_lonlat(tx + 1, ty + 1, self.zoom)

        gt = GridTerrain.a_partir_de_matriz(
            elevacoes=tile_matriz,
            lon_min=lon_oeste,
            lat_min=lat_sul,
            lon_max=lon_leste,
            lat_max=lat_norte,
        )
        return gt.altitude(lon, lat)

    def declividade(self, lon: float, lat: float, unidade: str = "razao") -> float:
        """Retorna a declividade na coordenada (lon, lat) a partir do tile correspondente."""
        tx, ty = lonlat_para_tile(lon, lat, self.zoom)
        tile_matriz = self._baixar_tile(tx, ty)

        lon_oeste, lat_norte = tile_para_lonlat(tx, ty, self.zoom)
        lon_leste, lat_sul = tile_para_lonlat(tx + 1, ty + 1, self.zoom)

        gt = GridTerrain.a_partir_de_matriz(
            elevacoes=tile_matriz,
            lon_min=lon_oeste,
            lat_min=lat_sul,
            lon_max=lon_leste,
            lat_max=lat_norte,
        )
        return gt.declividade(lon, lat, unidade=unidade)

    def grade_area(
        self,
        lon_min: float,
        lat_min: float,
        lon_max: float,
        lat_max: float,
        resolucao_m: float | None = None,
    ) -> Grid2D:
        """Baixa apenas os tiles da área, costura o mosaico e extrai a Grid2D em metros."""
        mosaico = self._montar_grid_terrain_area(lon_min, lat_min, lon_max, lat_max)
        return mosaico.grade_area(
            lon_min=lon_min,
            lat_min=lat_min,
            lon_max=lon_max,
            lat_max=lat_max,
            resolucao_m=resolucao_m,
        )