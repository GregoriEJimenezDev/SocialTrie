from enum import Enum

class UserStatus(Enum):
    ACTIVE = "Activo"
    INACTIVE = "Inactivo"

class PostStatus(Enum):
    ACTIVE = "Activo"
    DELETED = "Eliminado"

class CommentStatus(Enum):
    PUBLISHED = "Publicado"
    EDITED = "Editado"
    DELETED = "Eliminado"

class BannedWordStatus(Enum):
    ACTIVE = "Activa"
    INACTIVE = "Inactiva"
