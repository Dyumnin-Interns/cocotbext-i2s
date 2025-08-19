
"""I2S bus abstraction for cocotb."""

from typing import ClassVar
from cocotb_bus.bus import Bus


class I2sBus(Bus):
    """I2S bus wrapper for cocotb-based simulations."""

    _signals: ClassVar[list[str]] = []

    def __init__(
        self,
        dut,
        prefix,
        *,
        bus_separator: str = "_",
        case_insensitive: bool = False,
        array_idx: int | None = None,
    ) -> None:
        """Initialize the I2S bus wrapper.

        Args:
            dut: The DUT (design under test) instance from cocotb.
            prefix (str): Prefix for signal names in the DUT.
            bus_separator (str, optional): Separator between bus name and
                signal name. Defaults to "_".
            case_insensitive (bool, optional): Whether to ignore case when
                looking up signals. Defaults to False.
            array_idx (int, optional): Index if multiple bus instances exist.
                Defaults to None.
        """
        super().__init__(
            entity=dut,
            name=prefix,
            signals=self._signals,
            bus_separator=bus_separator,
            case_insensitive=case_insensitive,
            array_idx=array_idx,
        )

