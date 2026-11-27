import pytest

from terreno.synthetic import (
    criar_plano,
    criar_rampa,
    criar_colina,
    criar_vale,
    criar_montanhoso
)

from terreno.base import BaseTerrain
from calclib.grid import Grid2D
from model.vehicle import Vehicle
from model.restricoes import (
    RestricoesTopograficas,
    no_transitavel,
    transicao_valida
)


def test_terrenos_sinteticos():
    terrenos = [
        criar_plano(),
        criar_rampa(),
        criar_colina(),
        criar_vale(),
        criar_montanhoso()
    ]

    for terreno in terrenos:
        assert isinstance(terreno, BaseTerrain)
        assert isinstance(terreno.grid, Grid2D)


def test_altitude_plano():
    terreno = criar_plano(altitude=150.0)

    assert terreno.altitude(0.0, 0.0) == 150.0


def test_declividade_plano():
    terreno = criar_plano()

    inclinacao = terreno.declividade(0.0, 0.0)

    assert inclinacao == 0.0


def test_declividade_rampa():
    terreno = criar_rampa(inclinacao=0.10)

    inclinacao = terreno.declividade(0.0, 0.0)

    assert abs(inclinacao - 0.10) < 0.0001


def test_obter_grade():
    terreno = criar_plano()

    grade = terreno.obter_grade(
        (0.0, 0.0, 0.001, 0.001),
        20.0
    )

    assert isinstance(grade, Grid2D)
    assert grade.linhas >= 2
    assert grade.colunas >= 2


def test_restricoes_topograficas():
    terreno = criar_plano()

    veiculo = Vehicle(
        nome="teste",
        raio_minimo=0.0
    )

    restricoes = RestricoesTopograficas()

    grade = terreno.grid

    assert no_transitavel(
        grade,
        10,
        10,
        veiculo,
        restricoes
    )


def test_transicao_valida():
    terreno = criar_plano()

    veiculo = Vehicle(
        nome="teste",
        raio_minimo=0.0
    )

    restricoes = RestricoesTopograficas()

    resultado = transicao_valida(
        terreno.grid,
        (10, 10),
        (10, 11),
        veiculo,
        restricoes
    )

    assert resultado is True


# Testes de validação dos terrenos sintéticos

def test_terreno_rejeita_dimensoes_invalidas():
    with pytest.raises(ValueError):
        criar_plano(linhas=1)

    with pytest.raises(ValueError):
        criar_plano(colunas=1)


def test_terreno_rejeita_resolucao_invalida():
    with pytest.raises(ValueError):
        criar_plano(dx=0)

    with pytest.raises(ValueError):
        criar_plano(dy=-10)


def test_terreno_rejeita_altitude_invalida():
    with pytest.raises(ValueError):
        criar_plano(altitude=float("inf"))

    with pytest.raises(ValueError):
        criar_rampa(inclinacao=float("nan"))


def test_terreno_rejeita_parametros_invalidos_colina():
    with pytest.raises(ValueError):
        criar_colina(altura=float("inf"))


def test_terreno_rejeita_profundidade_invalida_vale():
    with pytest.raises(ValueError):
        criar_vale(profundidade=float("nan"))