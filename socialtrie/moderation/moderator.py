from abc import ABC, abstractmethod
from .tokenizer import TokenizerStrategy, SpaceTokenizer
from .moderation_result import ModerationResult
from ..trie import Trie

class CensorStrategy(ABC):
    @abstractmethod
    # Complejidad: O(1)
    def censor(self, prefix: str, core: str, suffix: str) -> str: ...

class AsteriskCensor(CensorStrategy):
    # Complejidad: O(1)
    def censor(self, prefix: str, core: str, suffix: str) -> str:
        return prefix + "*****" + suffix

class Moderator:
    # Complejidad: O(1)
    def __init__(self, trie: Trie, tokenizer: TokenizerStrategy | None = None,
                 censor: CensorStrategy | None = None) -> None:
        self.trie = trie
        self.tokenizer = tokenizer or SpaceTokenizer()
        self.censor = censor or AsteriskCensor()

    # Complejidad: O(N × L)
    def moderate(self, text: str) -> ModerationResult:
        output, detected = [], []
        for prefix, core, suffix, original in self.tokenizer.tokenize(text):
            normalized = core.lower().strip()
            # Consultar el Trie explícitamente por cada token; los núcleos vacíos no se censuran.
            found = self.trie.search(normalized)
            if normalized and found:
                output.append(self.censor.censor(prefix, core, suffix))
                detected.append(normalized)
            else:
                output.append(original)
        return ModerationResult(" ".join(output), len(detected), detected)
