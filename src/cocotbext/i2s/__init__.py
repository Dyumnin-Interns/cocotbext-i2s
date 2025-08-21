

"""I2S cocotb extension package.

This package provides I2S (Inter-IC Sound) bus models, drivers,
and configuration utilities for use with cocotb-based testbenches.
"""

from .bus import I2sBus
from .driver import I2sDriver
from .config import I2sConfig

__all__ = ["I2sBus", "I2sConfig", "I2sDriver"]
