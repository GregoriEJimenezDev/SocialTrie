from dataclasses import dataclass, field
from .enums import PostStatus

@dataclass
class Post:
    id: int
    user_id: int
    title: str
    content: str
    status: PostStatus = PostStatus.ACTIVE
    comment_ids: list[int] = field(default_factory=list)
    censorship_count: int = 0
