"""Veículo.

Parâmetros do veículo: declividade máxima, raio mínimo, velocidade, consumo.

Status: implementado.
"""

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class Vehicle:
    """Representa as restrições físicas e parâmetros operacionais de um veículo.

    Attributes:
        nome: Identificador do perfil do veículo (ex: 'caminhao', '4x4', 'leve').
        declividade_maxima: Inclinação máxima suportada em razão (m/m). Ex: 0.25 equivale a 25%.
        raio_minimo: Raio mínimo de curvatura em metros (m).
        velocidade_base: Velocidade média em terreno plano (m/s).
        consumo_base: Consumo energético/combustível base por metro percorrido em plano (unidades/m).
        fator_subida: Multiplicador de penalidade no consumo ao subir rampas.
        profundidade_vau_max: Lâmina d'água máxima tolerada acima da cota de inundação (m).
    """

    nome: str
    declividade_maxima: float = 0.25       # 25% de inclinação máxima padrão
    raio_minimo: float = 10.0              # 10 metros de raio de giro mínimo
    velocidade_base: float = 10.0          # 10 m/s (~36 km/h)
    consumo_base: float = 1.0              # Custo base unitário por metro
    fator_subida: float = 3.0              # Subir custa mais energia que andar no plano
    profundidade_vau_max: float = 0.0      # 0.0m = não atravessa áreas alagadas

    def __post_init__(self) -> None:
        if self.declividade_maxima <= 0:
            raise ValueError("A declividade máxima deve ser maior que zero.")
        if self.raio_minimo < 0:
            raise ValueError("O raio mínimo não pode ser negativo.")
        if self.velocidade_base <= 0:
            raise ValueError("A velocidade base deve ser maior que zero.")
        if self.consumo_base <= 0:
            raise ValueError("O consumo base deve ser maior que zero.")
        if self.profundidade_vau_max < 0:
            raise ValueError("A profundidade máxima de vau não pode ser negativa.")

    def angulo_curva_maximo(self, passo_metros: float, em_graus: bool = False) -> float:
        """Calcula a deflexão angular máxima permitida para um segmento de comprimento passo_metros."""
        if self.raio_minimo == 0.0:
            return 180.0 if em_graus else math.pi

        # Relação geométrica da corda de um arco de círculo: L = 2 * R * sin(theta / 2)
        razao = passo_metros / (2.0 * self.raio_minimo)
        if razao >= 1.0:
            # Se o passo for maior que o diâmetro de giro, o veículo consegue fazer qualquer curva
            return 180.0 if em_graus else math.pi

        rad = 2.0 * math.asin(razao)
        return math.degrees(rad) if em_graus else rad


# Perfis pré-configurados prontos para uso pela API/servidor
PERFIS_VEICULOS: dict[str, Vehicle] = {
    "padrao": Vehicle(
        nome="padrao",
        declividade_maxima=0.20,  # 20%
        raio_minimo=8.0,
        velocidade_base=11.1,     # ~40 km/h
        consumo_base=1.0,
        fator_subida=3.0,
        profundidade_vau_max=0.0,
    ),
    "4x4": Vehicle(
        nome="4x4",
        declividade_maxima=0.45,  # 45%
        raio_minimo=6.0,
        velocidade_base=8.3,      # ~30 km/h
        consumo_base=1.4,
        fator_subida=2.2,
        profundidade_vau_max=0.5, # Tolera até 50 cm de lâmina d'água
    ),
    "pesado": Vehicle(
        nome="pesado",
        declividade_maxima=0.12,  # 12%
        raio_minimo=15.0,
        velocidade_base=6.9,      # ~25 km/h
        consumo_base=2.5,
        fator_subida=5.0,
        profundidade_vau_max=0.0,
    ),
}