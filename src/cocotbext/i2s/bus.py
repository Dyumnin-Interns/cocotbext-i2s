"""I2S bus definition for cocotb."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cocotb.handle import SimHandleBase


class I2sBus:
    """Abstraction of the I2S bus for cocotb."""

    def __init__(self, dut: SimHandleBase, name: str = "i2s") -> None:
        """Initialize the I2S bus.

        Args:
            dut (SimHandleBase): The device under test handle from cocotb.
            name (str, optional): Name of the bus instance. Defaults to "i2s".
        """
        self.dut = dut
        self.name = name

        # Example: attach bus signals if they exist
        self.sck = getattr(dut, f"{name}_sck", None)
        self.ws = getattr(dut, f"{name}_ws", None)
        self.sd = getattr(dut, f"{name}_sd", None)

