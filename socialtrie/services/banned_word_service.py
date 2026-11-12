from ..exceptions import DuplicateBannedWordError, EntityNotFoundError, ValidationError
from ..factories import EntityFactory
from ..models import BannedWord, BannedWordStatus
from ..repositories import Repository
from ..trie import Trie


class BannedWordService:
    """Keeps the banned_words dict and the Trie synchronized (Trie = only Activa words)."""

    # Complejidad: O(1)
    def __init__(self, words: Repository[BannedWord], trie: Trie, factory: EntityFactory) -> None:
        self._words = words
        self._trie = trie
        self._factory = factory
        # Índice texto -> id solo para detectar duplicados activos. NO se usa para moderar.
        self._active_index: dict[str, int] = {}

    # Complejidad: O(1) promedio
    def get(self, word_id: int) -> BannedWord:
        word = self._words.get(word_id)
        if word is None:
            raise EntityNotFoundError("Palabra inexistente")
        return word

    # Complejidad: O(L)
    @staticmethod
    def _normalize(text: str) -> str:
        normalized = text.lower().strip()
        if not normalized:
            raise ValidationError("La palabra es obligatoria")
        return normalized

    # Complejidad: O(L)
    def add(self, text: str) -> BannedWord:
        normalized = self._normalize(text)
        if normalized in self._active_index:
            raise DuplicateBannedWordError("La palabra ya existe y está activa")
        word = self._factory.create_word(normalized)
        self._words.add(word)
        self._trie.insert(normalized)
        self._active_index[normalized] = word.id
        return word

    # Complejidad: O(L)
    def edit(self, word_id: int, text: str) -> BannedWord:
        word = self.get(word_id)
        normalized = self._normalize(text)
        owner = self._active_index.get(normalized)
        if owner is not None and owner != word_id:
            raise DuplicateBannedWordError("La palabra ya existe y está activa")
        if word.status is BannedWordStatus.ACTIVE:
            self._trie.remove(word.word)
            del self._active_index[word.word]
            self._trie.insert(normalized)
            self._active_index[normalized] = word_id
        word.word = normalized
        return word

    # Complejidad: O(L)
    def set_active(self, word_id: int, active: bool) -> BannedWord:
        word = self.get(word_id)
        target = BannedWordStatus.ACTIVE if active else BannedWordStatus.INACTIVE
        if word.status is target:
            raise ValidationError(f"La palabra ya está {target.value}")
        if active:
            if word.word in self._active_index:
                raise DuplicateBannedWordError("Ya existe otra palabra activa con ese texto")
            self._trie.insert(word.word)
            self._active_index[word.word] = word_id
        else:
            self._trie.remove(word.word)
            del self._active_index[word.word]
        word.status = target
        return word

    # Complejidad: O(W)
    def list_all(self) -> list[BannedWord]:
        return self._words.all()
