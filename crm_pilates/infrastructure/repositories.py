from typing import Any


class Repositories:
    def __init__(self, repositories) -> None:
        super().__init__()
        self._repositories = repositories

    def __getattr__(self, name: str) -> Any:
        return self._repositories[name]
