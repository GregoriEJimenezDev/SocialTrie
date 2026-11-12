from ..exceptions import EntityNotFoundError, InactiveUserError, ValidationError
from ..factories import EntityFactory
from ..models import Post, PostStatus, User, UserStatus
from ..repositories import Repository


class UserService:
    """User business rules. Users are never deleted physically (only Activo/Inactivo)."""

    # Complejidad: O(1)
    def __init__(self, users: Repository[User], posts: Repository[Post], factory: EntityFactory) -> None:
        self._users = users
        self._posts = posts
        self._factory = factory
        self._names: set[str] = set()  # índice de nombres únicos (no se usa en moderación)

    # Complejidad: O(1) promedio
    def get(self, user_id: int) -> User:
        user = self._users.get(user_id)
        if user is None:
            raise EntityNotFoundError("Usuario inexistente")
        return user

    # Complejidad: O(1) promedio
    def ensure_active(self, user_id: int) -> User:
        user = self.get(user_id)
        if user.status is UserStatus.INACTIVE:
            raise InactiveUserError("El usuario está inactivo")
        return user

    # Complejidad: O(M), M = longitud del nombre
    @staticmethod
    def _clean_name(name: str) -> str:
        clean = name.strip()
        if not clean:
            raise ValidationError("El nombre de usuario es obligatorio")
        return clean

    # Complejidad: O(M) promedio
    def create(self, name: str) -> User:
        clean = self._clean_name(name)
        if clean.casefold() in self._names:
            raise ValidationError("El nombre de usuario ya existe")
        user = self._factory.create_user(clean)
        self._users.add(user)
        self._names.add(clean.casefold())
        return user

    # Complejidad: O(M) promedio
    def rename(self, user_id: int, name: str) -> User:
        user = self.get(user_id)
        clean = self._clean_name(name)
        old_key, new_key = user.name.casefold(), clean.casefold()
        if new_key != old_key and new_key in self._names:
            raise ValidationError("El nombre de usuario ya existe")
        self._names.discard(old_key)
        self._names.add(new_key)
        user.name = clean
        return user

    # Complejidad: O(P), P = posts del sistema (solo al inactivar)
    def has_active_posts(self, user_id: int) -> bool:
        return any(p.user_id == user_id and p.status is PostStatus.ACTIVE
                   for p in self._posts.all())

    # Complejidad: O(P) al inactivar; O(1) promedio al activar
    def set_active(self, user_id: int, active: bool) -> User:
        # Regla del documento: no se da de baja a un usuario con posts activos. Como el menú no
        # elimina usuarios (nunca hay eliminación física), inactivar es su única "baja" y se protege.
        user = self.get(user_id)
        target = UserStatus.ACTIVE if active else UserStatus.INACTIVE
        if user.status is target:
            raise ValidationError(f"El usuario ya está {target.value}")
        if not active and self.has_active_posts(user_id):
            raise ValidationError("No se puede inactivar: el usuario tiene posts activos")
        user.status = target
        return user

    # Complejidad: O(U)
    def list_all(self) -> list[User]:
        return self._users.all()
