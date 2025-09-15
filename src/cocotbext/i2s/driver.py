"""I2S driver implementation for cocotb."""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable

from .config import I2sConfig, default_config

if TYPE_CHECKING:
    from .bus import I2sBus


class I2sDriver:
    """Driver for interacting with an I2S bus in cocotb testbenches."""

    def __init__(
        self,
        bus: I2sBus,
        config: I2sConfig = default_config,
        name: str | None = None,
    ) -> None:
        """Initialize the I2S driver.

        Args:
            bus: I2S bus instance.
            config (I2sConfig, optional): Configuration object for the bus.
                Defaults to `default_config`.
            name (str, optional): Optional driver name. Defaults to None.
        """
        self.bus = bus
        self.config = config
        self.name = name

    async def write(self, address: int, data: bytes) -> None:
        """Write data to a given address over the I2S bus."""
        raise NotImplementedError("I2S write method not implemented yet.")

    async def read(self, address: int, num_bytes: int) -> bytes:
        """Read data from a given address over the I2S bus."""
        raise NotImplementedError("I2S read method not implemented yet.")

    async def _txrx(self) -> None:
        """Internal transmit/receive coroutine for the I2S driver.

        This method handles low-level TX/RX operations asynchronously.
        """
        raise NotImplementedError("I2S TX/RX coroutine not implemented yet.")

    def add_callback(self, compare_fn: Callable[..., bool]) -> None:
        """Register a callback into the scoreboard.

        Args:
            compare_fn: Function to compare expected vs actual data.
        """
        raise NotImplementedError("Callback mechanism not implemented yet.")
