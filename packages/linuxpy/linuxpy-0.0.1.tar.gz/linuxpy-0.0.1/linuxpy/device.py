import logging
import os
import pathlib
from io import IOBase

from .io import IO


PathType = pathlib.Path | str


log = logging.getLogger(__name__)


class ReentrantContextManager:
    def __init__(self):
        self._context_level = 0

    def __enter__(self):
        if not self._context_level:
            self.open()
        self._context_level += 1
        return self

    def __exit__(self, *exc):
        self._context_level -= 1
        if not self._context_level:
            self.close()

    def open(self):
        raise NotImplementedError

    def close(self):
        raise NotImplementedError


def device_number(path: PathType):
    """Retrieves device"""
    num = ""
    for c in str(path)[::-1]:
        if c.isdigit():
            num = c + num
        else:
            break
    return int(num) if num else None


def is_device_file(path: PathType, read_write: bool = True):
    """Check if path is a readable (and, optionally, writable) character device."""
    path = pathlib.Path(path)
    if not path.is_char_device():
        return False
    access = os.R_OK | (os.W_OK if read_write else 0)
    if not os.access(str(path), access):
        return False
    return True


def iter_device_files(
    path: PathType = "/dev", pattern: str = "*"
) -> list[pathlib.Path]:
    path = pathlib.Path(path)
    items = path.glob(pattern)

    return filter(is_device_file, items)


class BaseDevice(ReentrantContextManager):
    def __init__(self, name_or_file, read_write=True, io=IO):
        super().__init__()
        self.controls = None
        self.io = io
        if isinstance(name_or_file, (str, pathlib.Path)):
            filename = pathlib.Path(name_or_file)
            self._read_write = read_write
            self._fobj = None
        elif isinstance(name_or_file, IOBase):
            filename = pathlib.Path(name_or_file.name)
            self._read_write = "+" in name_or_file.mode
            self._fobj = name_or_file
            # this object context manager won't close the file anymore
            self._context_level += 1
            self._init()
        else:
            raise TypeError(
                f"name_or_file must be str or a file-like object, not {name_or_file.__class__.__name__}"
            )
        self.log = log.getChild(filename.stem)
        self.filename = filename
        self.index = device_number(filename)

    def __repr__(self):
        return f"<{type(self).__name__} name={self.filename}, closed={self.closed}>"

    def _init(self):
        raise NotImplementedError

    def open(self):
        if not self._fobj:
            self.log.info("opening %s", self.filename)
            self._fobj = self.io.open(self.filename, self._read_write)
            self._init()
            self.log.info("opened %s", self.filename)

    def close(self):
        if not self.closed:
            self.log.info("closing %s", self.filename)
            self._fobj.close()
            self._fobj = None
            self.log.info("closed %s", self.filename)

    def fileno(self):
        return self._fobj.fileno()

    @property
    def closed(self):
        return self._fobj is None or self._fobj.closed

    @property
    def is_blocking(self):
        return os.get_blocking(self.fileno())
