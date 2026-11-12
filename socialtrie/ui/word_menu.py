from ..services import BannedWordService
from .base_menu import BaseMenu, Handler
from .formatters import format_word
from .input_helpers import input_centered, print_centered, read_id


class WordMenu(BaseMenu):
    title = "MANTENIMIENTO DE PALABRAS PROHIBIDAS"
    options = ["Agregar palabra prohibida", "Editar palabra prohibida", "Desactivar palabra prohibida",
               "Activar palabra prohibida", "Listar palabras prohibidas", "Volver al menú principal"]

    # Complejidad: O(1)
    def __init__(self, words: BannedWordService) -> None:
        self._words = words

    # Complejidad: O(1)
    def handlers(self) -> dict[str, Handler]:
        return {"1": self._add, "2": self._edit, "3": lambda: self._set_active(False),
                "4": lambda: self._set_active(True), "5": self._list, "6": self.back}

    # Complejidad: O(L)
    def _add(self) -> None:
        word = self._words.add(input_centered("Palabra: "))
        print_centered(f"Palabra creada: ID {word.id} — {word.word}")

    # Complejidad: O(L)
    def _edit(self) -> None:
        word_id = read_id("ID de palabra: ")
        self._words.get(word_id)
        word = self._words.edit(word_id, input_centered("Nueva palabra: "))
        print_centered(f"Palabra actualizada: {format_word(word)}")

    # Complejidad: O(L)
    def _set_active(self, active: bool) -> None:
        word = self._words.set_active(read_id("ID de palabra: "), active)
        print_centered(f"Palabra #{word.id} ahora está {word.status.value}")

    # Complejidad: O(W)
    def _list(self) -> None:
        words = self._words.list_all()
        for word in words:
            print_centered(format_word(word))
        if not words:
            print_centered("No hay palabras prohibidas registradas")
