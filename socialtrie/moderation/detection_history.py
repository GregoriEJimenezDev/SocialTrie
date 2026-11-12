from collections import Counter


class DetectionHistory:
    """Historical count of detected banned words (independent of the word's current status)."""

    # Complejidad: O(1)
    def __init__(self) -> None:
        self._counts: Counter[str] = Counter()
        self._total = 0

    # Complejidad: O(K), K = palabras detectadas en el comentario
    def record(self, words: list[str]) -> None:
        self._counts.update(words)
        self._total += len(words)

    # Complejidad: O(1)
    def total(self) -> int:
        return self._total

    # Complejidad: O(D log D), D = palabras distintas detectadas. Desempate alfabético ascendente.
    def ranking(self, limit: int = 5) -> list[tuple[str, int]]:
        return sorted(self._counts.items(), key=lambda item: (-item[1], item[0]))[:limit]
