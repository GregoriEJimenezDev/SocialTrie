from ..services import MetricsService, SystemStatusService
from .input_helpers import print_centered


class MetricsView:
    """Menu option 7: prints the metrics report."""

    # Complejidad: O(1)
    def __init__(self, metrics: MetricsService) -> None:
        self._metrics = metrics

    # Complejidad: O(C + U log U + P log P)
    def show(self) -> None:
        m = self._metrics.generate()
        print_centered(f"Total de usuarios: {m.total_users}")
        print_centered(f"Total de posts: {m.total_posts}")
        print_centered(f"Total de comentarios: {m.total_comments} "
                       f"(activos: {m.active_comments}, eliminados: {m.deleted_comments})")
        print_centered(f"Total de comentarios moderados: {m.moderated_comments} activos "
                       f"({m.moderated_including_deleted} contando eliminados)")
        print_centered(f"Palabras censuradas globalmente (histórico): {m.total_censored}")
        print_centered(f"Promedio de censuras por comentario activo: {m.average_censorship:.2f}")
        print_centered("Top 5 palabras más detectadas (histórico):")
        for position, (word, count) in enumerate(m.top_words, start=1):
            print_centered(f"{position}. {word} ({count})")
        if not m.top_words:
            print_centered("(sin datos)")
        if m.user_ranking:
            name, count = m.user_ranking[0]
            tie = len(m.user_ranking) > 1 and m.user_ranking[1][1] == count
            print_centered(f"Usuario con más comentarios: {name} ({count})"
                           + (" — empate resuelto alfabéticamente" if tie else ""))
        else:
            print_centered("Usuario con más comentarios: (sin datos)")
        if m.post_ranking:
            title, post_id, count = m.post_ranking[0]
            tie = len(m.post_ranking) > 1 and m.post_ranking[1][2] == count
            print_centered(f'Post con más comentarios: "{title}" (ID {post_id}, {count} comentario(s))'
                           + (" — empate resuelto alfabéticamente" if tie else ""))
        else:
            print_centered("Post con más comentarios: (sin datos)")


class SystemStatusView:
    """Menu option 8: prints the structural state of the system."""

    # Complejidad: O(1)
    def __init__(self, status: SystemStatusService) -> None:
        self._status = status

    # Complejidad: O(U + P + C + W)
    def show(self) -> None:
        s = self._status.snapshot()
        print_centered("ESTADO DEL SISTEMA")
        print_centered(f"Usuarios: Activos {s.users['Activo']} / Inactivos {s.users['Inactivo']}")
        print_centered(f"Posts: Activos {s.posts['Activo']} / Eliminados {s.posts['Eliminado']}")
        print_centered("Comentarios: " + ", ".join(f"{k} {v}" for k, v in s.comments.items()))
        print_centered(f"Palabras prohibidas: Activas {s.words['Activa']} / Inactivas {s.words['Inactiva']}")
        print_centered("Trie vacío: " + ("Sí" if s.trie_empty else "No"))
