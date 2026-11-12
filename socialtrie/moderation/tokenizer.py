from abc import ABC, abstractmethod

class TokenizerStrategy(ABC):
    @abstractmethod
    # Complejidad: O(N)
    def tokenize(self, text: str) -> list[tuple[str, str, str, str]]: ...

class SpaceTokenizer(TokenizerStrategy):
    SIGNS = ".,;:!?()[]{}\"'’"  # incluye apóstrofo recto y curvo

    # Complejidad: O(N)
    def tokenize(self, text: str) -> list[tuple[str, str, str, str]]:
        result = []
        for token in text.split(" "):
            start, end = 0, len(token)
            while start < end and token[start] in self.SIGNS:
                start += 1
            while end > start and token[end - 1] in self.SIGNS:
                end -= 1
            result.append((token[:start], token[start:end], token[end:], token))
        return result
