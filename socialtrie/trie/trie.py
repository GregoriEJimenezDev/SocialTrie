from .trie_node import TrieNode

class Trie:
    """Trie for exact, case-normalized word lookup."""
    # Complejidad: O(1)
    def __init__(self) -> None:
        self.root = TrieNode()
        self._size = 0

    # Complejidad: O(L)
    def insert(self, word: str) -> None:
        node = self.root
        for char in word:
            node = node.children.setdefault(char, TrieNode())
        if not node.is_end:
            node.is_end = True
            self._size += 1

    # Complejidad: O(L)
    def search(self, word: str) -> bool:
        node = self.root
        for char in word:
            if char not in node.children:
                return False
            node = node.children[char]
        return node.is_end

    # Complejidad: O(L)
    def starts_with(self, prefix: str) -> bool:
        node = self.root
        for char in prefix:
            if char not in node.children:
                return False
            node = node.children[char]
        return True

    # Complejidad: O(L)
    def remove(self, word: str) -> bool:
        # Complejidad: O(L) en el peor caso para recorrer la rama de la palabra.
        def prune(node: TrieNode, index: int) -> tuple[bool, bool]:
            if index == len(word):
                if not node.is_end:
                    return False, False
                node.is_end = False
                return True, not node.children
            char = word[index]
            child = node.children.get(char)
            if child is None:
                return False, False
            removed, prune_child = prune(child, index + 1)
            if prune_child:
                del node.children[char]
            return removed, not node.is_end and not node.children
        removed, _ = prune(self.root, 0)
        if removed:
            self._size -= 1
        return removed

    # Complejidad: O(1)
    def is_empty(self) -> bool:
        return self._size == 0
