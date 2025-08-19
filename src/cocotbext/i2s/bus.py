"""Bus creator."""
import cocotb
from cocotb_bus import Bus
from typing import ClassVar


class I2sBus(Bus):
    """Custom I2S bus creator for cocotb, handling protocol-specific edge cases.

    Examples of customizations:
        1. Multiple names for the same signal (e.g., RDY vs not_busy).
        2. Relationships between signals that need validation (e.g., byte_enable == width_of(data)/8).
        3. Different signal sets depending on version/profile.
    """

    _signals: ClassVar[list[str]] = []
def __init__(self, dut, prefix, *, bus_separator="_", case_insensitive=False, array_idx=None):
   
        """
        Initialize the I2S bus wrapper.

        Args:
            dut: The DUT (design under test) instance from cocotb.
            prefix (str): Prefix for signal names in the DUT.
            bus_separator (str, optional): Separator between bus name and signal name. Defaults to "_".
            case_insensitive (bool, optional): Whether to ignore case when looking up signals. Defaults to False.
            array_idx (int, optional): Index if multiple bus instances exist. Defaults to None.
        """
        super().__init__(entity=dut,
                         name=prefix,
                         signals=self._signals,
                         optional_signals=[],
                         bus_separator=bus_separator,
                         case_insensitive=case_insensitive,
                         array_idx=array_idx)
