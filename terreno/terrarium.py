"""Relevo dos tiles do mapa.

Lê tiles de elevação Terrarium para obter altitudes de terrenos reais.

Status: implementado.
"""

import math
from io import BytesIO
from urllib.error import URLError
from urllib.request import Request, urlopen

from PIL import Image

from terreno.base import BaseTerrain
from calclib.grid import Grid2D


class TerrariumTerrain(BaseTerrain):
    RAIO_TERRA = 6378137.0
    LATITUDE_MAXIMA = 85.05112878

    FONTES = {
        "aws": {
            "url": (
                "https://s3.amazonaws.com/"
                "elevation-tiles-prod/terrarium/"
                "{z}/{x}/{y}.png"
            ),
            "tile_size": 256,
            "maxzoom": 15,
        },
        "mapterhorn": {
            "url": "https://tiles.mapterhorn.com/{z}/{x}/{y}.webp",
            "tile_size": 512,
            "maxzoom": 12,
        },
    }

    def __init__(
        self,
        origem_lon: float,
        origem_lat: float,
        fonte: str = "aws",
        zoom: int = 12,
    ):
        if fonte not in self.FONTES:
            raise ValueError("Fonte de elevação desconhecida.")

        if not math.isfinite(origem_lon) or not -180 <= origem_lon <= 180:
            raise ValueError("Longitude de origem inválida.")

        if (
            not math.isfinite(origem_lat)
            or abs(origem_lat) >= self.LATITUDE_MAXIMA
        ):
            raise ValueError("Latitude de origem inválida ou próxima dos polos.")

        if not isinstance(zoom, int) or isinstance(zoom, bool):
            raise ValueError("O zoom deve ser um número inteiro.")

        configuracao = self.FONTES[fonte]

        if zoom < 0 or zoom > configuracao["maxzoom"]:
            raise ValueError("Zoom fora dos limites da fonte.")

        self.origem_lon = origem_lon
        self.origem_lat = origem_lat
        self.fonte = fonte
        self.zoom = zoom
        self.url_tiles = configuracao["url"]
        self.tamanho_tile = configuracao["tile_size"]
        self.cache: dict[tuple[int, int, int], Image.Image] = {}

    def coordenadas_tile(
        self,
        lon: float,
        lat: float,
    ) -> tuple[int, int, int, float, float]:

        if not math.isfinite(lon) or not -180 <= lon <= 180:
            raise ValueError("Longitude inválida.")

        if not math.isfinite(lat):
            raise ValueError("Latitude inválida.")

        lat = max(
            -self.LATITUDE_MAXIMA,
            min(self.LATITUDE_MAXIMA, lat)
        )

        quantidade = 2 ** self.zoom

        x = (lon + 180.0) / 360.0 * quantidade

        latitude_rad = math.radians(lat)

        y = (
            1.0 - math.asinh(math.tan(latitude_rad)) / math.pi
        ) / 2.0 * quantidade

        x = min(
            max(x, 0.0),
            math.nextafter(float(quantidade), 0.0)
        )

        y = min(
            max(y, 0.0),
            math.nextafter(float(quantidade), 0.0)
        )

        tile_x = int(x)
        tile_y = int(y)

        pixel_x = (x - tile_x) * self.tamanho_tile
        pixel_y = (y - tile_y) * self.tamanho_tile

        return tile_x, tile_y, self.zoom, pixel_x, pixel_y

    def baixar_tile(
        self,
        tile_x: int,
        tile_y: int,
        zoom: int,
    ) -> Image.Image:

        if not isinstance(zoom, int) or isinstance(zoom, bool):
            raise ValueError("O zoom do tile deve ser um número inteiro.")

        if zoom < 0 or zoom > self.FONTES[self.fonte]["maxzoom"]:
            raise ValueError("Zoom do tile fora dos limites da fonte.")

        if (
            not isinstance(tile_x, int)
            or isinstance(tile_x, bool)
            or not isinstance(tile_y, int)
            or isinstance(tile_y, bool)
        ):
            raise ValueError("Os índices do tile devem ser inteiros.")

        quantidade = 2 ** zoom

        if tile_y < 0 or tile_y >= quantidade:
            raise ValueError("Tile fora dos limites geográficos.")

        tile_x = tile_x % quantidade

        chave = (tile_x, tile_y, zoom)

        if chave in self.cache:
            return self.cache[chave]

        url = self.url_tiles.format(
            z=zoom,
            x=tile_x,
            y=tile_y
        )

        try:
            cabecalhos = {
                "User-Agent": "Mozilla/5.0",
                "Accept": "image/webp,image/png,image/*,*/*",
            }

            if self.fonte == "mapterhorn":
                cabecalhos["Referer"] = "https://mapterhorn.com/"

            requisicao = Request(
                url,
                headers=cabecalhos
            )

            with urlopen(requisicao, timeout=20) as resposta:
                conteudo = resposta.read()

            with Image.open(BytesIO(conteudo)) as imagem:
                imagem.load()
                imagem_convertida = imagem.convert("RGB")

        except (URLError, OSError) as erro:
            raise RuntimeError(
                f"Não foi possível baixar ou interpretar o tile: {url}"
            ) from erro

        if (
            imagem_convertida.width != self.tamanho_tile
            or imagem_convertida.height != self.tamanho_tile
        ):
            raise ValueError("O tile possui dimensões inesperadas.")

        self.cache[chave] = imagem_convertida

        return imagem_convertida

    def altitude(self, lon: float, lat: float) -> float:
        """Retorna a altitude, em metros, de uma coordenada geográfica."""

        tile_x, tile_y, zoom, pixel_x, pixel_y = self.coordenadas_tile(
            lon, lat
        )

        imagem = self.baixar_tile(tile_x, tile_y, zoom)

        x = min(int(pixel_x), imagem.width - 1)
        y = min(int(pixel_y), imagem.height - 1)

        r, g, b = imagem.getpixel((x, y))

        return (r * 256) + g + (b / 256) - 32768

    def coordenadas_metricas(
        self,
        lon: float,
        lat: float,
    ) -> tuple[float, float]:
        """Converte longitude e latitude para metros em uma projeção local."""

        if not math.isfinite(lon) or not -180 <= lon <= 180:
            raise ValueError("Longitude inválida.")

        if (
            not math.isfinite(lat)
            or not -self.LATITUDE_MAXIMA <= lat <= self.LATITUDE_MAXIMA
        ):
            raise ValueError("Latitude inválida.")

        x = (
            math.radians(lon - self.origem_lon)
            * self.RAIO_TERRA
            * math.cos(math.radians(self.origem_lat))
        )

        y = (
            math.radians(lat - self.origem_lat)
            * self.RAIO_TERRA
        )

        return x, y

    def declividade(self, lon: float, lat: float) -> float:
        """Calcula a declividade aproximada por diferenças finitas de 10 metros."""

        if not math.isfinite(lon) or not -180 <= lon <= 180:
            raise ValueError("Longitude inválida.")

        if (
            not math.isfinite(lat)
            or not -self.LATITUDE_MAXIMA <= lat <= self.LATITUDE_MAXIMA
        ):
            raise ValueError("Latitude inválida.")

        distancia_amostra = 10.0

        cos_lat = math.cos(math.radians(lat))

        if abs(cos_lat) < 1e-10:
            raise ValueError(
                "Não é possível calcular a declividade próximo aos polos."
            )

        lon_delta = math.degrees(
            distancia_amostra / (self.RAIO_TERRA * cos_lat)
        )

        lon_direita = (lon + lon_delta + 180.0) % 360.0 - 180.0
        lon_esquerda = (lon - lon_delta + 180.0) % 360.0 - 180.0

        altitude_direita = self.altitude(lon_direita, lat)
        altitude_esquerda = self.altitude(lon_esquerda, lat)

        lat_delta = math.degrees(
            distancia_amostra / self.RAIO_TERRA
        )

        lat_norte = min(
            self.LATITUDE_MAXIMA,
            lat + lat_delta
        )

        lat_sul = max(
            -self.LATITUDE_MAXIMA,
            lat - lat_delta
        )

        altitude_norte = self.altitude(lon, lat_norte)
        altitude_sul = self.altitude(lon, lat_sul)

        distancia_norte_sul = (
            math.radians(lat_norte - lat_sul) * self.RAIO_TERRA
        )

        if distancia_norte_sul <= 0:
            raise ValueError(
                "Não há distância suficiente para calcular a declividade."
            )

        dz_dx = (
            altitude_direita - altitude_esquerda
        ) / (2.0 * distancia_amostra)

        dz_dy = (
            altitude_norte - altitude_sul
        ) / distancia_norte_sul

        return math.sqrt(dz_dx ** 2 + dz_dy ** 2)

    def obter_grade(
        self,
        area: tuple[float, float, float, float],
        resolucao_m: float,
    ) -> Grid2D:
        """Busca altitudes de uma região e retorna uma grade métrica."""

        if not math.isfinite(resolucao_m) or resolucao_m <= 0:
            raise ValueError("A resolução deve ser positiva e finita.")

        if len(area) != 4:
            raise ValueError(
                "A área deve conter lon_min, lat_min, lon_max e lat_max."
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
            raise ValueError("Área geográfica inválida ou fora dos limites.")

        x_min, y_min = self.coordenadas_metricas(
            lon_min,
            lat_min
        )

        x_max, y_max = self.coordenadas_metricas(
            lon_max,
            lat_max
        )

        colunas = max(
            2,
            math.ceil((x_max - x_min) / resolucao_m) + 1
        )

        linhas = max(
            2,
            math.ceil((y_max - y_min) / resolucao_m) + 1
        )

        dx = (x_max - x_min) / (colunas - 1)
        dy = (y_max - y_min) / (linhas - 1)

        dados = []

        cos_origem = math.cos(math.radians(self.origem_lat))

        for i in range(linhas):
            linha = []

            y = y_min + i * dy

            lat = self.origem_lat + math.degrees(
                y / self.RAIO_TERRA
            )

            for j in range(colunas):
                x = x_min + j * dx

                lon = self.origem_lon + math.degrees(
                    x / (self.RAIO_TERRA * cos_origem)
                )

                linha.append(self.altitude(lon, lat))

            dados.append(linha)

        return Grid2D(
            dados=dados,
            dx=dx,
            dy=dy,
            origem_x=x_min,
            origem_y=y_min,
        )