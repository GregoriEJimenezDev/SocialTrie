from ..builders import CommentBuilder
from ..exceptions import DeletedPostError, EntityNotFoundError, ValidationError
from ..factories import EntityFactory
from ..models import Comment, CommentStatus, PostStatus
from ..moderation import DetectionHistory, Moderator
from ..repositories import Repository
from .post_service import PostService
from .user_service import UserService


class CommentService:
    """Comment rules. Every comment is moderated through the Trie-based Moderator."""

    # Complejidad: O(1)
    def __init__(self, comments: Repository[Comment], post_service: PostService,
                 user_service: UserService, factory: EntityFactory,
                 moderator: Moderator, history: DetectionHistory) -> None:
        self._comments = comments
        self._posts = post_service
        self._users = user_service
        self._factory = factory
        self._moderator = moderator
        self._history = history

    # Complejidad: O(1) promedio
    def get(self, comment_id: int) -> Comment:
        comment = self._comments.get(comment_id)
        if comment is None:
            raise EntityNotFoundError("Comentario inexistente")
        return comment

    # Complejidad: O(N × L)
    def add(self, post_id: int, user_id: int, raw_text: str) -> Comment:
        post = self._posts.get(post_id)
        if post.status is PostStatus.DELETED:
            raise DeletedPostError("No se puede comentar un post eliminado")
        self._users.ensure_active(user_id)
        if not raw_text.strip():
            raise ValidationError("El comentario no puede estar vacío")
        result = self._moderator.moderate(raw_text)
        comment = (CommentBuilder(self._factory.next_comment_id())
                   .with_post(post_id).with_user(user_id).with_raw_text(raw_text)
                   .with_moderation_result(result).build())
        self._comments.add(comment)
        post.comment_ids.append(comment.id)
        post.censorship_count += comment.censorship_count
        self._history.record(result.detected_words)
        return comment

    # Complejidad: O(N × L)
    def edit(self, comment_id: int, raw_text: str) -> Comment:
        comment = self.get(comment_id)
        post = self._posts.get(comment.post_id)
        if post.status is PostStatus.DELETED:
            raise DeletedPostError("No se pueden editar comentarios de un post eliminado")
        if comment.status is CommentStatus.DELETED:
            raise ValidationError("El comentario está eliminado")
        if not raw_text.strip():
            raise ValidationError("El comentario no puede estar vacío")
        result = self._moderator.moderate(raw_text)
        post.censorship_count += result.censorship_count - comment.censorship_count
        comment.raw_text = raw_text
        comment.moderated_text = result.moderated_text
        comment.censorship_count = result.censorship_count
        comment.detected_words = list(result.detected_words)
        comment.status = CommentStatus.EDITED
        self._history.record(result.detected_words)
        return comment

    # Complejidad: O(1) promedio
    def delete(self, comment_id: int) -> Comment:
        comment = self.get(comment_id)
        post = self._posts.get(comment.post_id)
        if post.status is PostStatus.DELETED:
            raise DeletedPostError("No se pueden modificar comentarios de un post eliminado")
        if comment.status is CommentStatus.DELETED:
            raise ValidationError("El comentario ya está eliminado")
        comment.status = CommentStatus.DELETED
        post.censorship_count -= comment.censorship_count
        return comment

    # Complejidad: O(C), C = comentarios del post
    def list_for_post(self, post_id: int) -> list[Comment]:
        post = self._posts.get(post_id)
        return [self.get(cid) for cid in post.comment_ids]
