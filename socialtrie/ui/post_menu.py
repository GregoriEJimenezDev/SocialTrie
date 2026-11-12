from ..services import PostService, UserService
from .base_menu import BaseMenu, Handler
from .formatters import format_post_detail, format_post_row
from .input_helpers import input_centered, print_centered, read_id


class PostMenu(BaseMenu):
    title = "MANTENIMIENTO DE POSTS"
    options = ["Crear post", "Buscar post", "Editar post", "Eliminar post (lógico)",
               "Listar posts", "Volver al menú principal"]

    # Complejidad: O(1)
    def __init__(self, posts: PostService, users: UserService) -> None:
        self._posts = posts
        self._users = users

    # Complejidad: O(1)
    def handlers(self) -> dict[str, Handler]:
        return {"1": self._create, "2": self.search_by_id, "3": self._edit,
                "4": self._delete, "5": self._list, "6": self.back}

    # Complejidad: O(T) promedio
    def _create(self) -> None:
        user_id = read_id("ID del usuario autor: ")
        self._users.ensure_active(user_id)  # se valida el autor antes de pedir más datos
        post = self._posts.create(user_id, input_centered("Título: "), input_centered("Contenido: "))
        print_centered(f"Post creado: ID {post.id}")

    # Complejidad: O(C), C = comentarios del post
    def search_by_id(self) -> None:
        """Used by Posts > Buscar post and by main menu option 3."""
        post = self._posts.get(read_id("ID del post: "))
        author = self._users.get(post.user_id).name
        print_centered(format_post_detail(post, author, self._posts.active_comment_count(post)))

    # Complejidad: O(T) promedio
    def _edit(self) -> None:
        post_id = read_id("ID del post: ")
        self._posts.ensure_open(post_id)
        self._posts.update(post_id, input_centered("Nuevo título: "), input_centered("Nuevo contenido: "))
        print_centered("Post actualizado")

    # Complejidad: O(C)
    def _delete(self) -> None:
        post = self._posts.delete(read_id("ID del post: "))
        print_centered(f"Post #{post.id} eliminado lógicamente")

    # Complejidad: O(P)
    def _list(self) -> None:
        posts = self._posts.list_all()
        for post in posts:
            print_centered(format_post_row(post, self._users.get(post.user_id).name))
        if not posts:
            print_centered("No hay posts registrados")
