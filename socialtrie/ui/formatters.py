from ..models import BannedWord, Comment, Post, User


# Complejidad: O(1)
def format_user(user: User) -> str:
    return f"ID: {user.id} | Nombre: {user.name} | Estado: {user.status.value}"


# Complejidad: O(1)
def format_post_detail(post: Post, author_name: str, active_comments: int) -> str:
    return (f"ID: {post.id}\n"
            f"Título: {post.title}\n"
            f"Autor: {author_name}\n"
            f"Contenido: {post.content}\n"
            f"Estado: {post.status.value}\n"
            f"Comentarios: {len(post.comment_ids)} (activos: {active_comments})\n"
            f"Censuras: {post.censorship_count}")


# Complejidad: O(1)
def format_post_row(post: Post, author_name: str) -> str:
    return (f"ID: {post.id} | Autor: {author_name} | Título: {post.title} | "
            f"Estado: {post.status.value} | Comentarios: {len(post.comment_ids)}")


# Complejidad: O(1)
def format_comment(comment: Comment, author_name: str) -> str:
    return (f"#{comment.id} {author_name} | {comment.moderated_text} | "
            f"{comment.status.value} | censuras: {comment.censorship_count}")


# Complejidad: O(1)
def format_word(word: BannedWord) -> str:
    return f"ID: {word.id} | Palabra: {word.word} | Estado: {word.status.value}"
