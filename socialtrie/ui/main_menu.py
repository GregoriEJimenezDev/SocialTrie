from ..services import MetricsService
from .base_menu import BaseMenu, Handler
from .comment_actions import CommentActions
from .input_helpers import input_centered, print_centered
from .post_menu import PostMenu
from .reports_view import MetricsView, SystemStatusView
from .user_menu import UserMenu
from .word_menu import WordMenu


class MainMenu(BaseMenu):
    title = "SOCIALTRIE"
    options = ["Mantenimiento de usuarios (CRUD)", "Mantenimiento de posts (CRUD)", "Buscar post",
               "Comentar en un post (Moderación automática)", "Ver comentarios de un post",
               "Mantenimiento de palabras prohibidas (CRUD)", "Generar métricas",
               "Ver estado del sistema", "Salir"]

    # Complejidad: O(1)
    def __init__(self, users: UserMenu, posts: PostMenu, comments: CommentActions, words: WordMenu,
                 metrics_view: MetricsView, status_view: SystemStatusView,
                 metrics: MetricsService) -> None:
        self._users, self._posts, self._comments, self._words = users, posts, comments, words
        self._metrics_view, self._status_view = metrics_view, status_view
        self._metrics = metrics

    # Complejidad: O(1)
    def handlers(self) -> dict[str, Handler]:
        return {"1": self._users.run, "2": self._posts.run, "3": self._posts.search_by_id,
                "4": self._comments.add_comment, "5": self._comments.view_comments,
                "6": self._words.run, "7": self._metrics_view.show, "8": self._status_view.show,
                "9": self._exit}

    # Complejidad: O(1)
    def _exit(self) -> bool:
        if input_centered("¿Confirma que desea salir? (s/n): ").strip().lower() != "s":
            return False
        self.print_summary()
        return True

    # Complejidad: O(C): recorre los comentarios para calcular el reporte
    def print_summary(self) -> None:
        m = self._metrics.generate()
        print_centered("RESUMEN FINAL")
        print_centered(f"Total de usuarios: {m.total_users}")
        print_centered(f"Total de posts: {m.total_posts}")
        print_centered(f"Total de comentarios: {m.total_comments}")
        print_centered(f"Total de palabras censuradas: {m.total_censored}")
