"""

A utilities module for projectaria_tools
"""
from __future__ import annotations
import projectaria_tools.core.sensor_data
from projectaria_tools.core.sensor_data import PixelFrame as _PixelFrame
import numpy as _np
import numpy
__all__ = ['to_image_array']
def to_image_array(pixel_frame: projectaria_tools.core.sensor_data.PixelFrame) -> numpy.ndarray:
    ...
