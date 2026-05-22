"""Caché en memoria para respuestas repetidas (por proceso)."""

class MemoryCache:
    """
    Diccionario simple clave -> respuesta.

    Se pierde al reiniciar el servidor. Cumple el requisito de determinismo
    dentro de la misma sesion.
    """

    def __init__(self) -> None:
        self._store: dict[str, str] = {}

    def get(self, key: str) -> str | None:
        return self._store.get(key)

    def set(self, key: str, value: str) -> None:
        self._store[key] = value
