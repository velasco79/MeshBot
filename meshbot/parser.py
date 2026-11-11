"""Parser de comandos com gatilho '/' do MeshBot."""


def parse_command(text: str | None) -> tuple[str, list[str]] | None:
    """'/nome arg1 arg2' -> ('nome', ['arg1', 'arg2']); None se não é comando.

    Nome sempre minúsculo. Texto que não começa com '/' não é comando.
    """
    if not text:
        return None
    stripped = text.strip()
    if not stripped.startswith("/"):
        return None
    parts = stripped[1:].split()
    if not parts:
        return None
    return parts[0].lower(), parts[1:]
