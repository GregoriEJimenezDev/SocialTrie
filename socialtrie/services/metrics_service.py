from dataclasses import dataclass, field

from ..models import Comment, Post, User
from ..moderation import DetectionHistory
from ..repositories import Repository


@dataclass
class MetricsReport:
    total_users: int
    total_posts: int
    total_comments: int            # todos, incluidos Eliminados (se conservan como historial)
    active_comments: int           # Publicado + Editado
    deleted_comments: int
    moderated_comments: int        # activos con al menos una censura
    moderated_including_deleted: int  # incluye Eliminados (historial)
    total_censored: int            # HISTÓRICO: todas las detecciones registradas
    average_censorship: float      # sobre comentarios activos
    top_words: list[tuple[str, int]] = field(default_factory=list)       # histórico
    user_ranking: list[tuple[str, int]] = field(default_factory=list)    # solo activos
    post_ranking: list[tuple[str, int, int]] = field(default_factory=list)  # (título, id, n)


class MetricsService:
    """Read-only reports. Rankings and average use only Publicado/Editado comments."""

    # Complejidad: O(1)
    def __init__(self, users: Repository[User], posts: Repository[Post],
                 comments: Repository[Comment], history: DetectionHistory) -> None:
        self._users = users
        self._posts = posts
        self._comments = comments
        self._history = history

    # Complejidad: O(C + U log U + P log P + D log D)
    def generate(self) -> MetricsReport:
        everything = self._comments.all()
        active = [c for c in everything if c.is_active]
        per_user: dict[int, int] = {}
        per_post: dict[int, int] = {}
        for c in active:
            per_user[c.user_id] = per_user.get(c.user_id, 0) + 1
            per_post[c.post_id] = per_post.get(c.post_id, 0) + 1
        # Empates: orden alfabético ascendente (nombre / título), luego ID.
        user_ranking = sorted(((self._users.get(uid).name, n) for uid, n in per_user.items()),
                              key=lambda item: (-item[1], item[0].casefold(), item[0]))
        post_ranking = sorted(((self._posts.get(pid).title, pid, n) for pid, n in per_post.items()),
                              key=lambda item: (-item[2], item[0].casefold(), item[1]))
        censored_active = sum(c.censorship_count for c in active)
        return MetricsReport(
            total_users=len(self._users),
            total_posts=len(self._posts),
            total_comments=len(everything),
            active_comments=len(active),
            deleted_comments=len(everything) - len(active),
            moderated_comments=sum(1 for c in active if c.censorship_count > 0),
            moderated_including_deleted=sum(1 for c in everything if c.censorship_count > 0),
            total_censored=self._history.total(),
            average_censorship=censored_active / len(active) if active else 0.0,
            top_words=self._history.ranking(5),
            user_ranking=user_ranking,
            post_ranking=post_ranking,
        )
