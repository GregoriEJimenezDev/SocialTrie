from dataclasses import dataclass, field
from .enums import CommentStatus


@dataclass
class Comment:
    id: int
    post_id: int
    user_id: int
    raw_text: str
    moderated_text: str
    censorship_count: int
    detected_words: list[str] = field(default_factory=list)
    status: CommentStatus = CommentStatus.PUBLISHED

    @property
    # Complejidad: O(1)
    def is_active(self) -> bool:
        """True for Publicado/Editado; Eliminado comments are kept only as history."""
        return self.status in (CommentStatus.PUBLISHED, CommentStatus.EDITED)
