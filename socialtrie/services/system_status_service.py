from dataclasses import dataclass

from ..models import (BannedWord, BannedWordStatus, Comment, CommentStatus, Post,
                      PostStatus, User, UserStatus)
from ..repositories import Repository
from ..trie import Trie


@dataclass
class SystemStatus:
    users: dict[str, int]
    posts: dict[str, int]
    comments: dict[str, int]
    words: dict[str, int]
    trie_empty: bool


class SystemStatusService:
    """Read-only structural snapshot of the system."""

    # Complejidad: O(1)
    def __init__(self, users: Repository[User], posts: Repository[Post],
                 comments: Repository[Comment], words: Repository[BannedWord], trie: Trie) -> None:
        self._users, self._posts = users, posts
        self._comments, self._words = comments, words
        self._trie = trie

    # Complejidad: O(N), N = elementos de la colección
    @staticmethod
    def _count(items, status_enum) -> dict[str, int]:
        counts = {status.value: 0 for status in status_enum}
        for item in items:
            counts[item.status.value] += 1
        return counts

    # Complejidad: O(U + P + C + W)
    def snapshot(self) -> SystemStatus:
        return SystemStatus(
            users=self._count(self._users.all(), UserStatus),
            posts=self._count(self._posts.all(), PostStatus),
            comments=self._count(self._comments.all(), CommentStatus),
            words=self._count(self._words.all(), BannedWordStatus),
            trie_empty=self._trie.is_empty(),
        )
