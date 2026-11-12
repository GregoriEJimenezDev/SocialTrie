"""Run with: python main.py"""
from socialtrie.factories import EntityFactory
from socialtrie.moderation import DetectionHistory, Moderator
from socialtrie.repositories import Repository
from socialtrie.services import (BannedWordService, CommentService, MetricsService, PostService,
                                 SystemStatusService, UserService)
from socialtrie.trie import Trie
from socialtrie.ui import MainMenu
from socialtrie.ui.comment_actions import CommentActions
from socialtrie.ui.input_helpers import input_centered, print_centered
from socialtrie.ui.post_menu import PostMenu
from socialtrie.ui.reports_view import MetricsView, SystemStatusView
from socialtrie.ui.user_menu import UserMenu
from socialtrie.ui.word_menu import WordMenu


# Complejidad: O(1)
def build_app() -> MainMenu:
    """Composition root: the only place where concrete dependencies are wired (DIP)."""
    users, posts, comments, banned_words = (Repository() for _ in range(4))  # dicts base
    banned_trie = Trie()
    factory, history = EntityFactory(), DetectionHistory()
    moderator = Moderator(banned_trie)

    user_service = UserService(users, posts, factory)
    post_service = PostService(posts, comments, user_service, factory)
    comment_service = CommentService(comments, post_service, user_service, factory, moderator, history)
    word_service = BannedWordService(banned_words, banned_trie, factory)
    metrics = MetricsService(users, posts, comments, history)
    status = SystemStatusService(users, posts, comments, banned_words, banned_trie)

    return MainMenu(UserMenu(user_service), PostMenu(post_service, user_service),
                    CommentActions(comment_service, post_service, user_service),
                    WordMenu(word_service), MetricsView(metrics), SystemStatusView(status), metrics)


# Complejidad: O(1) por interacción
def main() -> None:
    app = build_app()
    try:
        app.run()
    except (EOFError, KeyboardInterrupt):
        print_centered("\nEntrada finalizada. Cerrando SocialTrie.")
        app.print_summary()
        return
    # Pausa final para que la ventana no se cierre antes de leer el resumen.
    try:
        input_centered("Presione Enter para cerrar...")
    except (EOFError, KeyboardInterrupt):
        pass


if __name__ == "__main__":
    main()
