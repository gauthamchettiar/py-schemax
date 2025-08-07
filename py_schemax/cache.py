import atexit
import os.path
from typing import Any

import click
import larch.pickle as pickle
from cachebox import cachedmethod


def persistent_cachedmethod(persist_file_path: str, cache: Any, *args, **kwargs):
    if os.path.exists(persist_file_path):
        with open(persist_file_path, "rb") as fd:
            cache = pickle.load(fd)

    def _save_pickle():
        try:
            # Ensure the directory exists before saving
            os.makedirs(os.path.dirname(persist_file_path), exist_ok=True)
            with open(persist_file_path, "wb") as fd:
                pickle.dump(cache, fd)
        except (FileNotFoundError, OSError):
            click.secho(
                "Error saving cache file. Directory may not exist.",
                fg="yellow",
                err=True,
            )
            pass

    atexit.register(_save_pickle)

    return cachedmethod(cache, *args, **kwargs)
