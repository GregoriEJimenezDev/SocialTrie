from dataclasses import dataclass
from .enums import BannedWordStatus

@dataclass
class BannedWord:
    id: int
    word: str
    status: BannedWordStatus = BannedWordStatus.ACTIVE
