"""Tests package for cocotbext-i2s."""
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer


async def reset_dut(dut, duration_ns=100):
    """Reset the DUT."""
    dut.reset.value = 1
    await Timer(duration_ns, units="ns")
    dut.reset.value = 0
    await RisingEdge(dut.clk)


@cocotb.test()
async def test_i2s_transmitter(dut):
    """
    Test I2S transmitter:
    - Feed left/right channel samples
    - Verify WS toggling
    - Verify serial output matches input
    """

    # Start system clock (10 ns period = 100 MHz)
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())

    # Reset
    await reset_dut(dut)

    # Example test vectors (left, right)
    samples = [
        (0xAAAA, 0x5555),
        (0x1234, 0x5678),
    ]

    for left, right in samples:
        # Apply left channel
        dut.data_in.value = left
        dut.valid.value = 1
        await RisingEdge(dut.clk)
        dut.valid.value = 0

        # Wait for DUT to accept
        while not dut.ready.value:
            await RisingEdge(dut.clk)

        # Capture left channel bits
        left_bits = []
        for _ in range(16):
            await RisingEdge(dut.bclk)
            left_bits.append(int(dut.sd.value))

        # Check WS = 0 for left
        assert dut.ws.value == 0, "WS should be LOW during left channel"

        # Reconstruct parallel word
        reconstructed_left = int("".join(str(b) for b in left_bits), 2)
        assert reconstructed_left == left, f"Left mismatch: got {hex(reconstructed_left)}, expected {hex(left)}"

        # Apply right channel
        dut.data_in.value = right
        dut.valid.value = 1
        await RisingEdge(dut.clk)
        dut.valid.value = 0

        while not dut.ready.value:
            await RisingEdge(dut.clk)

        # Capture right channel bits
        right_bits = []
        for _ in range(16):
            await RisingEdge(dut.bclk)
            right_bits.append(int(dut.sd.value))

        # Check WS = 1 for right
        assert dut.ws.value == 1, "WS should be HIGH during right channel"

        reconstructed_right = int("".join(str(b) for b in right_bits), 2)
        assert reconstructed_right == right, f"Right mismatch: got {hex(reconstructed_right)}, expected {hex(right)}"
