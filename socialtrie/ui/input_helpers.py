import shutil

from ..exceptions import ValidationError


# Complejidad: O(L), L = longitud del texto a imprimir
def print_centered(message: object = "") -> None:
    """Print each line centered in the current terminal width."""
    width = shutil.get_terminal_size(fallback=(80, 24)).columns
    for line in str(message).splitlines() or [""]:
        print(line.center(width))


# Complejidad: O(1)
def input_centered(prompt: str) -> str:
    """Read input with the prompt centered; the cursor stays right after the prompt."""
    width = shutil.get_terminal_size(fallback=(80, 24)).columns
    return input(" " * max(0, (width - len(prompt)) // 2) + prompt)


# Complejidad: O(K), K = cantidad de opciones
def show_menu(title: str, options: list[str]) -> None:
    print_centered()
    print_centered(title)
    for index, option in enumerate(options, start=1):
        print_centered(f"{index}. {option}")


# Complejidad: O(1)
def show_warning(message: str) -> None:
    print_centered(f"Aviso: {message}")


# Complejidad: O(L)
def read_id(label: str) -> int:
    """Read a positive integer ID ("01" is accepted as 1). Never leaks Python errors."""
    raw = input_centered(label).strip()
    if not (raw.isascii() and raw.isdigit()) or int(raw) <= 0:
        raise ValidationError("Debe ingresar un número entero positivo")
    return int(raw)
