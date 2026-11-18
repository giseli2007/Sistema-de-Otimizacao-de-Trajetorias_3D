"""Vetores.

Operações vetoriais 2D/3D: norma, produto escalar, ângulos.

Status: implementado.
"""

import math
from typing import Sequence

Vetor = Sequence[float] # Não cria uma classe nova; apenas dá um apelido de tipo
                        # Para que o editor saiba que u e v podem ser floats ou listas


def subtrair(a: Vetor, b: Vetor) -> tuple[float, ...]:
    """Retorna o vetor deslocamento (a - b), funciona em 2D e 3D."""
    return tuple(ai - bi for ai, bi in zip(a, b)) # zip(u, v) emparelha os elementos pelo índice de elementos correspondentes


def norma(v: Vetor) -> float:
    """Calcula a norma euclidiana (magnitude/comprimento) de um vetor 2D ou 3D."""
    return math.sqrt(sum(c * c for c in v))


def distancia(a: Vetor, b: Vetor) -> float:
    """Calcula a distância euclidiana entre dois pontos 2D ou 3D."""
    return norma(subtrair(a, b))


def produto_escalar(u: Vetor, v: Vetor) -> float:
    """Calcula o produto escalar (dot product) entre dois vetores u e v."""
    return sum(ui * vi for ui, vi in zip(u, v)) # laço for embutido diretamente na função soma


def angulo(u: Vetor, v: Vetor, em_graus: bool = False) -> float:
    """Calcula o ângulo entre dois vetores u e v (em radianos por padrão)."""
    norma_u = norma(u)
    norma_v = norma(v)

    if norma_u == 0.0 or norma_v == 0.0:
        raise ValueError("Não é possível calcular o ângulo com um vetor nulo.")

    # O clamp entre -1.0 e 1.0 evita erro de domínio no math.acos()
    # por imprecisão de ponto flutuante (ex: 1.0000000000000002)
    cos_theta = produto_escalar(u, v) / (norma_u * norma_v)
    cos_theta = max(-1.0, min(1.0, cos_theta))

    rad = math.acos(cos_theta)
    return math.degrees(rad) if em_graus else rad