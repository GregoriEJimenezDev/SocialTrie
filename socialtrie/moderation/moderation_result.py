from dataclasses import dataclass, field

@dataclass
class ModerationResult:
    moderated_text: str
    censorship_count: int
    detected_words: list[str] = field(default_factory=list)
