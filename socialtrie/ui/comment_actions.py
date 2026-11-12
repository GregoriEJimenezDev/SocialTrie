from ..exceptions import DomainError
from ..models import CommentStatus, PostStatus
from ..services import CommentService, PostService, UserService
from .formatters import format_comment
from .input_helpers import input_centered, print_centered, read_id, show_warning


class CommentActions:
    """Menu options 4 (comentar con moderación) and 5 (ver comentarios)."""

    # Complejidad: O(1)
    def __init__(self, comments: CommentService, posts: PostService, users: UserService) -> None:
        self._comments = comments
        self._posts = posts
        self._users = users

    # Complejidad: O(N × L)
    def add_comment(self) -> None:
        post_id = read_id("ID del post: ")
        self._posts.ensure_open(post_id)
        user_id = read_id("ID del usuario: ")
        self._users.ensure_active(user_id)
        comment = self._comments.add(post_id, user_id, input_centered("Comentario: "))
        print_centered(f"Comentario #{comment.id}: {comment.moderated_text} | "
                       f"censuras: {comment.censorship_count}")

    # Complejidad: O(C × N × L) en el peor caso (si se re-moderan comentarios)
    def view_comments(self) -> None:
        post = self._posts.get(read_id("ID del post: "))
        comments = self._comments.list_for_post(post.id)
        if not comments:
            print_centered("El post no tiene comentarios")
            return
        read_only = post.status is PostStatus.DELETED
        for comment in comments:
            print_centered(format_comment(comment, self._users.get(comment.user_id).name))
            if read_only or comment.status is CommentStatus.DELETED:
                continue
            self._ask_action(comment.id)
        if read_only:
            print_centered("Post eliminado: solo lectura")

    # Complejidad: O(N × L)
    def _ask_action(self, comment_id: int) -> None:
        action = input_centered("Acción: (e) editar | (x) eliminar | Enter continuar: ").strip().lower()
        try:
            if action == "e":
                self._comments.edit(comment_id, input_centered("Nuevo texto: "))
                print_centered("Comentario editado y re-moderado")
            elif action == "x":
                self._comments.delete(comment_id)
                print_centered("Comentario eliminado lógicamente")
        except DomainError as error:
            show_warning(str(error))
