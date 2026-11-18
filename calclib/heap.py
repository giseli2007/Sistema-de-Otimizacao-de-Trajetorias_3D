"""Fila de prioridade.

Heap usado por Dijkstra e A*.

Status: implementado.
"""

import heapq
from typing import Generic, TypeVar

T = TypeVar("T")


class MinHeap(Generic[T]):
    """Fila de prioridade mínima (Min-Heap) segura contra empates de prioridade."""

    def __init__(self) -> None:
        self._heap: list[tuple[float, int, T]] = []
        self._contador: int = 0

    def push(self, prioridade: float, item: T) -> None:
        """Insere um item na fila associado a um custo/prioridade numérico."""
        # O contador evita que o Python compare 'item' diretamente quando houver
        # empate na prioridade, além de manter a ordem de chegada (FIFO).
        entrada = (float(prioridade), self._contador, item)
        heapq.heappush(self._heap, entrada)
        self._contador += 1

    def pop(self) -> tuple[float, T]:
        """Remove e retorna (prioridade, item) de menor prioridade."""
        if self.vazio():
            raise IndexError("Não é possível remover de uma MinHeap vazia.")
        prioridade, _, item = heapq.heappop(self._heap)
        return (prioridade, item)

    def peek(self) -> tuple[float, T]:
        """Consulta (prioridade, item) do topo sem remover da fila."""
        if self.vazio():
            raise IndexError("A MinHeap está vazia.")
        prioridade, _, item = self._heap[0]
        return (prioridade, item)

    def vazio(self) -> bool:
        """Retorna True se não houver elementos na fila."""
        return len(self._heap) == 0

    def __len__(self) -> int:
        """Permite usar len(heap) diretamente em Python."""
        return len(self._heap)