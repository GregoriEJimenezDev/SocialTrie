from ..exceptions import ValidationError
from ..models import Comment
from ..moderation import ModerationResult


class CommentBuilder:
    """Fluent builder for Comment: with_post().with_user().with_raw_text().with_moderation_result().build()."""

    # Complejidad: O(1)
    def __init__(self, comment_id: int) -> None:
        self._comment_id = comment_id
        self._post_id: int | None = None
        self._user_id: int | None = None
        self._raw_text = ""
        self._result: ModerationResult | None = None

    # Complejidad: O(1)
    def with_post(self, post_id: int) -> "CommentBuilder":
        self._post_id = post_id
        return self

    # Complejidad: O(1)
    def with_user(self, user_id: int) -> "CommentBuilder":
        self._user_id = user_id
        return self

    # Complejidad: O(1)
    def with_raw_text(self, text: str) -> "CommentBuilder":
        self._raw_text = text
        return self

    # Complejidad: O(1)
    def with_moderation_result(self, result: ModerationResult) -> "CommentBuilder":
        self._result = result
        return self

    # Complejidad: O(K), K = palabras detectadas (copia de la lista)
    def build(self) -> Comment:
        if self._post_id is None or self._user_id is None or self._result is None:
            raise ValidationError("Faltan datos obligatorios para crear el comentario")
        return Comment(self._comment_id, self._post_id, self._user_id, self._raw_text,
                       self._result.moderated_text, self._result.censorship_count,
                       list(self._result.detected_words))
