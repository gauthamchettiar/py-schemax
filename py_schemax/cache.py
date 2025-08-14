import atexit
import os.path
from typing import Any

import click
import larch.pickle as pickle
from cachebox import BaseCacheImpl, LRUCache

from py_schemax.config import Config


class Cache:
    def __init__(self, config: Config, cache: BaseCacheImpl | None = None) -> None:
        self.config = config
        self.cache = cache or LRUCache(maxsize=10000)

    def write(self, *args: Any, **kwargs: Any) -> None:
        self.cache.insert(*args, **kwargs)

    def read(self, *args: Any, **kwargs: Any) -> Any:
        return self.cache.get(*args, **kwargs)


class FileHashCache(Cache):
    def __init__(self, config: Config, cache: BaseCacheImpl | None = None) -> None:
        super().__init__(config, cache)

    def write(self, file_path: str, file_hash: str, value: Any) -> None:
        super().write(key=f"{file_path}:{file_hash}", value=value)

    def read(self, file_path: str, file_hash: str) -> Any:
        return super().read(key=f"{file_path}:{file_hash}")


class PersistentFileHashCache(FileHashCache):
    def __init__(
        self,
        config: Config,
        persistent_file_path: str,
        cache: BaseCacheImpl | None = None,
    ) -> None:
        super().__init__(config, cache)
        self.persist_file_path = persistent_file_path
        if os.path.exists(self.persist_file_path):
            with open(self.persist_file_path, "rb") as fd:
                self.cache = pickle.load(fd)

        def __save_pickle() -> None:
            try:
                # Ensure the directory exists before saving
                os.makedirs(os.path.dirname(self.persist_file_path), exist_ok=True)
                with open(self.persist_file_path, "wb") as fd:
                    pickle.dump(self.cache, fd)
            except (FileNotFoundError, OSError):
                click.secho(
                    f"error saving cache to file '{self.persist_file_path}'",
                    fg="yellow",
                    err=True,
                )

        atexit.register(__save_pickle)
