import pytest
from PIL import Image

from terreno.terrarium import TerrariumTerrain


def test_conversao_altitude():
    terreno = TerrariumTerrain(
        origem_lon=0.0,
        origem_lat=0.0
    )

    imagem = Image.new("RGB", (256, 256), (128, 0, 0))

    terreno.baixar_tile = lambda x, y, z: imagem

    altitude = terreno.altitude(0.0, 0.0)

    assert altitude == 0.0


def test_coordenadas_tile():
    terreno = TerrariumTerrain(
        origem_lon=0.0,
        origem_lat=0.0,
        zoom=1
    )

    tile_x, tile_y, zoom, pixel_x, pixel_y = (
        terreno.coordenadas_tile(0.0, 0.0)
    )

    assert tile_x == 1
    assert tile_y == 1
    assert zoom == 1
    assert pixel_x == 0.0
    assert pixel_y == 0.0


def test_obter_grade(monkeypatch):
    terreno = TerrariumTerrain(
        origem_lon=0.0,
        origem_lat=0.0
    )

    monkeypatch.setattr(
        terreno,
        "altitude",
        lambda lon, lat: 100.0
    )

    grade = terreno.obter_grade(
        (0.0, 0.0, 0.001, 0.001),
        20.0
    )

    assert grade.linhas >= 2
    assert grade.colunas >= 2

    for linha in grade.dados:
        for altitude in linha:
            assert altitude == 100.0


def test_fonte_invalida():
    with pytest.raises(ValueError):
        TerrariumTerrain(
            origem_lon=0.0,
            origem_lat=0.0,
            fonte="invalida"
        )


def test_zoom_invalido():
    with pytest.raises(ValueError):
        TerrariumTerrain(
            origem_lon=0.0,
            origem_lat=0.0,
            zoom=20
        )