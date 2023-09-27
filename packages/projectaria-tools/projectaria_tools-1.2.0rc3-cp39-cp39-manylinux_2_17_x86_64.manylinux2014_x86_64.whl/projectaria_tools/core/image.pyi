from __future__ import annotations
import numpy
import typing
__all__ = ['Image3U8', 'ImageF32', 'ImageU64', 'ImageU8', 'ManagedImage3U8', 'ManagedImageF32', 'ManagedImageU64', 'ManagedImageU8', 'debayer']
class Image3U8:
    def __init__(self) -> None:
        ...
    def at(self, x: int, y: int, channel: int = ...) -> int | float | int | int | ...:
        """
        Returns the pixel at (x, y, channel)
        """
    def get_height(self) -> int:
        """
        Returns the number of rows
        """
    def get_width(self) -> int:
        """
        Returns the number of columns
        """
    def to_numpy_array(self) -> numpy.ndarray[numpy.uint8] | numpy.ndarray[numpy.float32] | numpy.ndarray[numpy.uint16] | numpy.ndarray[numpy.uint64] | numpy.ndarray[...]:
        """
        Converts to numpy array
        """
class ImageF32:
    def __init__(self) -> None:
        ...
    def at(self, x: int, y: int, channel: int = ...) -> int | float | int | int | ...:
        """
        Returns the pixel at (x, y, channel)
        """
    def get_height(self) -> int:
        """
        Returns the number of rows
        """
    def get_width(self) -> int:
        """
        Returns the number of columns
        """
    def to_numpy_array(self) -> numpy.ndarray[numpy.uint8] | numpy.ndarray[numpy.float32] | numpy.ndarray[numpy.uint16] | numpy.ndarray[numpy.uint64] | numpy.ndarray[...]:
        """
        Converts to numpy array
        """
class ImageU64:
    def __init__(self) -> None:
        ...
    def at(self, x: int, y: int, channel: int = ...) -> int | float | int | int | ...:
        """
        Returns the pixel at (x, y, channel)
        """
    def get_height(self) -> int:
        """
        Returns the number of rows
        """
    def get_width(self) -> int:
        """
        Returns the number of columns
        """
    def to_numpy_array(self) -> numpy.ndarray[numpy.uint8] | numpy.ndarray[numpy.float32] | numpy.ndarray[numpy.uint16] | numpy.ndarray[numpy.uint64] | numpy.ndarray[...]:
        """
        Converts to numpy array
        """
class ImageU8:
    def __init__(self) -> None:
        ...
    def at(self, x: int, y: int, channel: int = ...) -> int | float | int | int | ...:
        """
        Returns the pixel at (x, y, channel)
        """
    def get_height(self) -> int:
        """
        Returns the number of rows
        """
    def get_width(self) -> int:
        """
        Returns the number of columns
        """
    def to_numpy_array(self) -> numpy.ndarray[numpy.uint8] | numpy.ndarray[numpy.float32] | numpy.ndarray[numpy.uint16] | numpy.ndarray[numpy.uint64] | numpy.ndarray[...]:
        """
        Converts to numpy array
        """
class ManagedImage3U8:
    def __init__(self) -> None:
        ...
    def at(self, x: int, y: int, channel: int = ...) -> int | float | int | int | ...:
        """
        Returns the pixel at (x, y, channel)
        """
    def get_height(self) -> int:
        """
        Returns the number of rows
        """
    def get_width(self) -> int:
        """
        Returns the number of columns
        """
    def to_numpy_array(self) -> numpy.ndarray[numpy.uint8] | numpy.ndarray[numpy.float32] | numpy.ndarray[numpy.uint16] | numpy.ndarray[numpy.uint64] | numpy.ndarray[...]:
        """
        Converts to numpy array
        """
class ManagedImageF32:
    def __init__(self) -> None:
        ...
    def at(self, x: int, y: int, channel: int = ...) -> int | float | int | int | ...:
        """
        Returns the pixel at (x, y, channel)
        """
    def get_height(self) -> int:
        """
        Returns the number of rows
        """
    def get_width(self) -> int:
        """
        Returns the number of columns
        """
    def to_numpy_array(self) -> numpy.ndarray[numpy.uint8] | numpy.ndarray[numpy.float32] | numpy.ndarray[numpy.uint16] | numpy.ndarray[numpy.uint64] | numpy.ndarray[...]:
        """
        Converts to numpy array
        """
class ManagedImageU64:
    def __init__(self) -> None:
        ...
    def at(self, x: int, y: int, channel: int = ...) -> int | float | int | int | ...:
        """
        Returns the pixel at (x, y, channel)
        """
    def get_height(self) -> int:
        """
        Returns the number of rows
        """
    def get_width(self) -> int:
        """
        Returns the number of columns
        """
    def to_numpy_array(self) -> numpy.ndarray[numpy.uint8] | numpy.ndarray[numpy.float32] | numpy.ndarray[numpy.uint16] | numpy.ndarray[numpy.uint64] | numpy.ndarray[...]:
        """
        Converts to numpy array
        """
class ManagedImageU8:
    def __init__(self) -> None:
        ...
    def at(self, x: int, y: int, channel: int = ...) -> int | float | int | int | ...:
        """
        Returns the pixel at (x, y, channel)
        """
    def get_height(self) -> int:
        """
        Returns the number of rows
        """
    def get_width(self) -> int:
        """
        Returns the number of columns
        """
    def to_numpy_array(self) -> numpy.ndarray[numpy.uint8] | numpy.ndarray[numpy.float32] | numpy.ndarray[numpy.uint16] | numpy.ndarray[numpy.uint64] | numpy.ndarray[...]:
        """
        Converts to numpy array
        """
def debayer(arg0: numpy.ndarray[numpy.uint8]) -> numpy.ndarray[numpy.uint8] | numpy.ndarray[numpy.float32] | numpy.ndarray[numpy.uint16] | numpy.ndarray[numpy.uint64] | numpy.ndarray[...]:
    """
    Debayer and also correct color by preset color calibration
    """
