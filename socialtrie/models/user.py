from dataclasses import dataclass
from .enums import UserStatus

@dataclass
class User:
    id: int
    name: str
    status: UserStatus = UserStatus.ACTIVE
