"""Terrenos sintéticos.

Planos, rampas e colinas para testes e comparações, sem depender de dados reais.

Cada superfície é uma função analítica z = f(x, y) (em metros) com gradiente
exato (f_x, f_y). Isso permite:
  - amostrar o terreno numa Grid2D com qualquer resolução (`amostrar`,
    `amostrar_area`), sempre com o MESMO terreno de fundo;
  - calcular o comprimento "verdadeiro" de uma curva sobre a superfície por
    integral de linha (`comprimento_curva`), para validar as buscas em grade.

Status: implementado.
"""

import math
from collections.abc import Callable
from dataclasses import dataclass
from typing import Protocol

from calclib.grid import Grid2D
from calclib.integrate import trapezio_1d

Ponto2D = tuple[float, float]


class Superficie(Protocol):
    """Contrato mínimo de uma superfície analítica z = f(x, y)."""

    def z(self, x: float, y: float) -> float:
        """Altitude (m) no ponto (x, y)."""
        ...

    def gradiente(self, x: float, y: float) -> tuple[float, float]:
        """Gradiente exato (f_x, f_y) em (x, y), em m/m."""
        ...


@dataclass(frozen=True)
class Rampa:
    """Plano inclinado z = z0 + a*x + b*y (com a = b = 0 vira um plano horizontal).

    Attributes:
        z0: Altitude em (0, 0).
        a: Inclinação na direção x (dz/dx, em m/m).
        b: Inclinação na direção y (dz/dy, em m/m).
    """

    z0: float = 0.0
    a: float = 0.0
    b: float = 0.0

    def z(self, x: float, y: float) -> float:
        return self.z0 + self.a * x + self.b * y

    def gradiente(self, x: float, y: float) -> tuple[float, float]:
        return (self.a, self.b)


@dataclass(frozen=True)
class Colina:
    """Colina gaussiana: z = z_base + altura * exp(-((x-cx)² + (y-cy)²) / (2*sigma²)).

    Attributes:
        cx, cy: Posição do topo (m).
        altura: Altura do topo acima de z_base (m). Negativa vira uma depressão.
        sigma: "Largura" da colina (m); precisa ser > 0.
        z_base: Altitude do terreno longe da colina.
    """

    cx: float = 0.0
    cy: float = 0.0
    altura: float = 10.0
    sigma: float = 10.0
    z_base: float = 0.0

    def __post_init__(self) -> None:
        if self.sigma <= 0:
            raise ValueError("sigma deve ser maior que zero.")

    def _g(self, x: float, y: float) -> float:
        """Parte gaussiana: altura * exp(-r² / (2*sigma²))."""
        r2 = (x - self.cx) ** 2 + (y - self.cy) ** 2
        return self.altura * math.exp(-r2 / (2.0 * self.sigma**2))

    def z(self, x: float, y: float) -> float:
        return self.z_base + self._g(x, y)

    def gradiente(self, x: float, y: float) -> tuple[float, float]:
        # Regra da cadeia: d/dx [exp(-r²/(2σ²))] = exp(...) * (-(x-cx)/σ²)
        g = self._g(x, y)
        s2 = self.sigma**2
        return (-g * (x - self.cx) / s2, -g * (y - self.cy) / s2)


def amostrar(
    superficie: Superficie,
    linhas: int,
    colunas: int,
    dx: float,
    dy: float,
    origem_x: float = 0.0,
    origem_y: float = 0.0,
) -> Grid2D:
    """Amostra a superfície numa Grid2D de `linhas` x `colunas` células-vértice.

    A célula (i, j) fica em x = origem_x + j*dx e y = origem_y + i*dy,
    a mesma convenção de `Grid2D.indice_para_coord`.
    """
    if linhas < 2 or colunas < 2:
        raise ValueError("A grade precisa ter pelo menos 2 linhas e 2 colunas.")

    dados = [
        [superficie.z(origem_x + j * dx, origem_y + i * dy) for j in range(colunas)]
        for i in range(linhas)
    ]
    return Grid2D(dados, dx, dy, origem_x, origem_y)


def amostrar_area(
    superficie: Superficie,
    largura: float,
    altura: float,
    passo: float,
    origem_x: float = 0.0,
    origem_y: float = 0.0,
) -> Grid2D:
    """Amostra a área [origem_x, origem_x + largura] x [origem_y, origem_y + altura].

    Pensada para estudos de convergência: a área é a mesma e só o `passo` muda.
    `largura` e `altura` precisam ser múltiplos inteiros do passo.
    """
    if passo <= 0:
        raise ValueError("O passo deve ser maior que zero.")

    n_colunas = largura / passo
    n_linhas = altura / passo
    if abs(n_colunas - round(n_colunas)) > 1e-9 or abs(n_linhas - round(n_linhas)) > 1e-9:
        raise ValueError("largura e altura devem ser múltiplos inteiros do passo.")

    return amostrar(
        superficie,
        linhas=round(n_linhas) + 1,
        colunas=round(n_colunas) + 1,
        dx=passo,
        dy=passo,
        origem_x=origem_x,
        origem_y=origem_y,
    )


def comprimento_curva(
    superficie: Superficie,
    curva: Callable[[float], Ponto2D],
    derivada: Callable[[float], Ponto2D],
    t0: float = 0.0,
    t1: float = 1.0,
    n: int = 10_000,
) -> float:
    """Comprimento sobre a superfície da curva (x(t), y(t)) levada para z = f(x, y).

    Integral de linha (regra da cadeia em z(t) = f(x(t), y(t))):

        L = ∫ sqrt( x'² + y'² + (f_x·x' + f_y·y')² ) dt,  t de t0 a t1

    calculada pela regra do trapézio composta com `n` subintervalos.

    Args:
        curva: t -> (x, y), a projeção da curva no plano.
        derivada: t -> (x', y'), derivada da curva em relação a t.
    """
    if n < 1:
        raise ValueError("n deve ser pelo menos 1.")

    dt = (t1 - t0) / n
    valores = []
    for k in range(n + 1):
        t = t0 + k * dt
        x, y = curva(t)
        dxdt, dydt = derivada(t)
        fx, fy = superficie.gradiente(x, y)
        dzdt = fx * dxdt + fy * dydt
        valores.append(math.sqrt(dxdt**2 + dydt**2 + dzdt**2))

    return trapezio_1d(valores, [dt] * n)


def comprimento_reta(
    superficie: Superficie,
    inicio: Ponto2D,
    fim: Ponto2D,
    n: int = 10_000,
) -> float:
    """Comprimento sobre a superfície da reta em planta entre `inicio` e `fim`."""
    vx = fim[0] - inicio[0]
    vy = fim[1] - inicio[1]
    return comprimento_curva(
        superficie,
        curva=lambda t: (inicio[0] + t * vx, inicio[1] + t * vy),
        derivada=lambda t: (vx, vy),
        n=n,
    )


def comprimento_exato_reta_rampa(rampa: Rampa, inicio: Ponto2D, fim: Ponto2D) -> float:
    """Comprimento exato (fórmula fechada) da reta em planta sobre uma Rampa.

    Numa rampa o gradiente é constante, então a derivada direcional ao longo da
    reta, ∇f·u, também é, e a integral vira um produto:

        L = |AB|_planta * sqrt(1 + (∇f·u)²),  u = vetor unitário de A para B
    """
    vx = fim[0] - inicio[0]
    vy = fim[1] - inicio[1]
    d_planta = math.hypot(vx, vy)
    if d_planta == 0.0:
        return 0.0

    ux, uy = vx / d_planta, vy / d_planta
    inclinacao = rampa.a * ux + rampa.b * uy
    return d_planta * math.sqrt(1.0 + inclinacao**2)