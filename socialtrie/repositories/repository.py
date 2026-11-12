from typing import Generic, TypeVar

T = TypeVar("T")


class IdGenerator:
    """Monotonic ID generator: never reuses an ID, even for logically deleted records."""

    # Complejidad: O(1)
    def __init__(self) -> None:
        self._next = 1

    # Complejidad: O(1)
    def next_id(self) -> int:
        value = self._next
        self._next += 1
        return value


class Repository(Generic[T]):
    """Dictionary-backed storage (id -> entity). Records are never physically removed."""

    # Complejidad: O(1)
    def __init__(self) -> None:
        self.items: dict[int, T] = {}

    # Complejidad: O(1) promedio
    def add(self, entity: T) -> None:
        self.items[getattr(entity, "id")] = entity

    # Complejidad: O(1) promedio
    def get(self, entity_id: int) -> T | None:
        return self.items.get(entity_id)

    # Complejidad: O(N): devuelve una copia para que listar no modifique el diccionario.
    def all(self) -> list[T]:
        return list(self.items.values())

    # Complejidad: O(1)
    def __len__(self) -> int:
        return len(self.items)
