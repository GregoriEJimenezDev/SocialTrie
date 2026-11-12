from ..models import User, Post, BannedWord
from ..repositories import IdGenerator


class EntityFactory:
    """Creates entities with an auto-generated, sequential and non-reusable ID."""

    # Complejidad: O(1)
    def __init__(self) -> None:
        self._user_ids = IdGenerator()
        self._post_ids = IdGenerator()
        self._comment_ids = IdGenerator()
        self._word_ids = IdGenerator()

    # Complejidad: O(1)
    def create_user(self, name: str) -> User:
        return User(self._user_ids.next_id(), name)

    # Complejidad: O(1)
    def create_post(self, user_id: int, title: str, content: str) -> Post:
        return Post(self._post_ids.next_id(), user_id, title, content)

    # Complejidad: O(1)
    def create_word(self, word: str) -> BannedWord:
        return BannedWord(self._word_ids.next_id(), word)

    # Complejidad: O(1). El Comment lo arma CommentBuilder; la fábrica solo entrega el ID.
    def next_comment_id(self) -> int:
        return self._comment_ids.next_id()
