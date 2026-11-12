from ..exceptions import DeletedPostError, EntityNotFoundError, ValidationError
from ..factories import EntityFactory
from ..models import Comment, Post, PostStatus
from ..repositories import Repository
from .user_service import UserService


class PostService:
    """Post business rules. Deleting a post is logical (status Eliminado)."""

    # Complejidad: O(1)
    def __init__(self, posts: Repository[Post], comments: Repository[Comment],
                 user_service: UserService, factory: EntityFactory) -> None:
        self._posts = posts
        self._comments = comments
        self._users = user_service
        self._factory = factory

    # Complejidad: O(1) promedio
    def get(self, post_id: int) -> Post:
        post = self._posts.get(post_id)
        if post is None:
            raise EntityNotFoundError("Post inexistente")
        return post

    # Complejidad: O(1) promedio
    def ensure_open(self, post_id: int) -> Post:
        post = self.get(post_id)
        if post.status is PostStatus.DELETED:
            raise DeletedPostError("El post está eliminado")
        return post

    # Complejidad: O(T), T = longitud de título y contenido
    @staticmethod
    def _clean_text(title: str, content: str) -> tuple[str, str]:
        title, content = title.strip(), content.strip()
        if not title or not content:
            raise ValidationError("Título y contenido son obligatorios")
        return title, content

    # Complejidad: O(T) promedio
    def create(self, user_id: int, title: str, content: str) -> Post:
        self._users.ensure_active(user_id)
        title, content = self._clean_text(title, content)
        post = self._factory.create_post(user_id, title, content)
        self._posts.add(post)
        return post

    # Complejidad: O(T) promedio. No permite cambiar ID ni autor.
    def update(self, post_id: int, title: str, content: str) -> Post:
        post = self.ensure_open(post_id)
        post.title, post.content = self._clean_text(title, content)
        return post

    # Complejidad: O(C), C = comentarios del post
    def delete(self, post_id: int) -> Post:
        post = self.get(post_id)
        if post.status is PostStatus.DELETED:
            raise ValidationError("El post ya está eliminado")
        if self.active_comment_count(post) > 0:
            raise ValidationError("Solo se elimina un post sin comentarios Publicado/Editado")
        post.status = PostStatus.DELETED
        return post

    # Complejidad: O(C)
    def active_comment_count(self, post: Post) -> int:
        return sum(1 for cid in post.comment_ids
                   if (c := self._comments.get(cid)) is not None and c.is_active)

    # Complejidad: O(P)
    def list_all(self) -> list[Post]:
        return self._posts.all()
