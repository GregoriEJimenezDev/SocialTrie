from ..services import UserService
from .base_menu import BaseMenu, Handler
from .formatters import format_user
from .input_helpers import input_centered, print_centered, read_id


class UserMenu(BaseMenu):
    title = "MANTENIMIENTO DE USUARIOS"
    options = ["Crear usuario", "Buscar usuario", "Editar usuario", "Inactivar usuario",
               "Activar usuario", "Listar usuarios", "Volver al menú principal"]

    # Complejidad: O(1)
    def __init__(self, users: UserService) -> None:
        self._users = users

    # Complejidad: O(1)
    def handlers(self) -> dict[str, Handler]:
        return {"1": self._create, "2": self._search, "3": self._edit,
                "4": lambda: self._set_active(False), "5": lambda: self._set_active(True),
                "6": self._list, "7": self.back}

    # Complejidad: O(M) promedio
    def _create(self) -> None:
        user = self._users.create(input_centered("Nombre de usuario: "))
        print_centered(f"Usuario creado: ID {user.id} — {user.name}")

    # Complejidad: O(1) promedio
    def _search(self) -> None:
        print_centered(format_user(self._users.get(read_id("ID de usuario: "))))

    # Complejidad: O(M) promedio
    def _edit(self) -> None:
        user_id = read_id("ID de usuario: ")
        self._users.get(user_id)
        user = self._users.rename(user_id, input_centered("Nuevo nombre: "))
        print_centered(f"Usuario actualizado: {format_user(user)}")

    # Complejidad: O(1) promedio
    def _set_active(self, active: bool) -> None:
        user = self._users.set_active(read_id("ID de usuario: "), active)
        print_centered(f"Usuario #{user.id} ahora está {user.status.value}")

    # Complejidad: O(U)
    def _list(self) -> None:
        users = self._users.list_all()
        for user in users:
            print_centered(format_user(user))
        if not users:
            print_centered("No hay usuarios registrados")
