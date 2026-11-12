class TrieNode:
    """One node in a manually implemented trie."""
    # Complejidad: O(1)
    def __init__(self) -> None:
        self.children: dict[str, TrieNode] = {}
        self.is_end: bool = False
