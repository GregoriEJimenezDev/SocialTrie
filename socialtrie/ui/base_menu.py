from abc import ABC, abstractmethod
from typing import Callable

from ..exceptions import DomainError
from .input_helpers import input_centered, show_menu, show_warning

Handler = Callable[[], "bool | None"]


class BaseMenu(ABC):
    """Template for console menus. A handler returning True leaves the menu."""

    title: str = ""
    options: list[str] = []

    @abstractmethod
    # Complejidad: O(1)
    def handlers(self) -> dict[str, Handler]: ...

    # Complejidad: O(1)
    def back(self) -> bool:
        return True

    # Complejidad: O(1) por iteración del menú
    def run(self) -> None:
        actions = self.handlers()
        while True:
            show_menu(self.title, self.options)
            choice = input_centered("Opción: ").strip()
            action = actions.get(choice)
            if action is None:
                show_warning("Opción inválida")
                continue
            try:
                if action():
                    return
            except DomainError as error:
                show_warning(str(error))
