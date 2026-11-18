"""Grade regular 2D.

Origem, passo e conversão índice <-> coordenada, usada pelo terreno e pelo planejador.

Status: implementado.
"""

from typing import Sequence


class Grid2D:
    """Representa uma malha regular 2D com resolução espacial (dx, dy) em metros."""

    def __init__( # construtor
        self, # primeiro parâmtro de cada método
        dados: Sequence[Sequence[float]],
        dx: float,
        dy: float,
        origem_x: float = 0.0,
        origem_y: float = 0.0,
    ) -> None:
        if not dados or not dados[0]:
            raise ValueError("A matriz de dados da grade não pode ser vazia.")
        if dx <= 0 or dy <= 0:
            raise ValueError("Os passos dx e dy devem ser maiores que zero.")

        # Converte para lista de listas de floats para garantir mutabilidade e tipo uniforme
        self.dados: list[list[float]] = [
            [float(val) for val in linha] for linha in dados
        ]
        self.linhas: int = len(self.dados)
        self.colunas: int = len(self.dados[0])
        self.dx: float = float(dx)
        self.dy: float = float(dy)
        self.origem_x: float = float(origem_x)
        self.origem_y: float = float(origem_y)

    def dentro_dos_limites(self, i: int, j: int) -> bool:
        """Verifica se o índice (i, j) existe dentro da matriz."""
        return 0 <= i < self.linhas and 0 <= j < self.colunas

    def get(self, i: int, j: int) -> float:
        """Retorna o valor (ex: altitude z) na célula (i, j)."""
        if not self.dentro_dos_limites(i, j):
            raise IndexError(f"Índice ({i}, {j}) fora dos limites da grade ({self.linhas}x{self.colunas}).")
        return self.dados[i][j]

    def set(self, i: int, j: int, valor: float) -> None:
        """Atualiza o valor na célula (i, j)."""
        if not self.dentro_dos_limites(i, j):
            raise IndexError(f"Índice ({i}, {j}) fora dos limites da grade ({self.linhas}x{self.colunas}).")
        self.dados[i][j] = float(valor)

    def indice_para_coord(self, i: int, j: int) -> tuple[float, float]:
        """Converte índice discreto (linha i, coluna j) para coordenada métrica (x, y)."""
        x = self.origem_x + j * self.dx
        y = self.origem_y + i * self.dy
        return (x, y)

    def coord_para_indice(self, x: float, y: float) -> tuple[int, int]:
        """Converte coordenada métrica (x, y) para o índice (i, j) mais próximo."""
        j = round((x - self.origem_x) / self.dx)
        i = round((y - self.origem_y) / self.dy)
        return (i, j)

    def coord_para_indice_continuo(self, x: float, y: float) -> tuple[float, float]:
        """Converte (x, y) para índice fracionário (fi, fj) — essencial para interpolação."""
        fj = (x - self.origem_x) / self.dx
        fi = (y - self.origem_y) / self.dy
        return (fi, fj)

    def area_celula(self) -> float:
        """Retorna a área planimétrica (em m²) de uma única célula da grade."""
        return self.dx * self.dy

    def area_total(self) -> float:
        """Retorna a área planimétrica total (em m²) coberta pela grade."""
        return self.linhas * self.colunas * self.area_celula()