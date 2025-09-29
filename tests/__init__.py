"""Tests package for cocotbext-i2s."""
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer

from cocotbext.i2s.driver import I2sMaster, I2sSlave  # type: ignore

import random
import os
import pytest
from cocotb_test.simulator import run


# Helper task for generating the main system clock
async def clock_gen(signal):
    """System Clock Generator."""
    await cocotb.start(Clock(signal, 10, units="ns").start())


# Helper task for resetting the DUT
async def reset_dut(reset_signal, duration_ns):
    """Resets the DUT."""
    reset_signal.value = 1
    await Timer(duration_ns, units="ns")
    reset_signal.value = 0
    reset_signal._log.info("Reset complete")


# Main cocotb test logic
@cocotb.test()
async def i2s_test_logic(dut):
    """Main parameterized test function for I2S verification."""
    # Get parameters from environment variables set by the pytest runner
    data_width = int(os.getenv("DATA_WIDTH", "24"))
    master_mode = os.getenv("MASTER_MODE", "true").lower() == "true"

    # Start the system clock
    await clock_gen(dut.i_clk)

    # Reset the DUT
    await reset_dut(dut.i_rst, 20)

    # --- Test Data Generation ---
    # Generate 10 random data words for left and right channels
    test_data_left = [random.getrandbits(data_width) for _ in range(10)]
    test_data_right = [random.getrandbits(data_width) for _ in range(10)]
    # We interleave them for transmission, similar to how I2S works
    interleaved_data = [val for pair in zip(test_data_left, test_data_right) for val in pair]

    # --- Verification Component Initialization ---
    if master_mode:
        dut._log.info("Configuring test for DUT as MASTER.")
        # DUT is Master, so testbench needs a Slave to receive data
        i2s_peripheral = I2sSlave(
            dut,
            sclk=dut.o_bclk,
            ws=dut.o_wclk,
            sd=dut.o_sd,
            data_width=data_width,
        )
    else:
        dut._log.info("Configuring test for DUT as SLAVE.")
        # DUT is Slave, so testbench needs a Master to provide clocks and data
        i2s_peripheral = I2sMaster(
            dut,
            sclk=dut.i_bclk,
            ws=dut.i_wclk,
            sd=dut.i_sd,
            data_width=data_width,
        )

    # --- DUT Configuration ---
    dut.i_enable.value = 1
    dut.i_mode.value = 0 if master_mode else 1  # 0 for Master, 1 for Slave

    # --- Test Execution ---
    await RisingEdge(dut.i_clk)

    if master_mode:
        # DUT is Master, we need to provide it with data to transmit
        for i in range(len(test_data_left)):
            dut.i_data.value = test_data_left[i]
            dut.i_valid_data.value = 1
            await RisingEdge(dut.i_clk)
            dut.i_valid_data.value = 0
            await Timer(1, units="us")

            dut.i_data.value = test_data_right[i]
            dut.i_valid_data.value = 1
            await RisingEdge(dut.i_clk)
            dut.i_valid_data.value = 0
            await Timer(1, units="us")

        # Now, receive the data using our I2S Slave driver
        received_data = []
        for _ in range(len(interleaved_data)):
            data_word = await i2s_peripheral.recv_word()
            received_data.append(data_word)

        dut._log.info(f"Original interleaved data: {interleaved_data}")
        dut._log.info(f"Data received by slave:    {received_data}")

        # --- Verification ---
        assert received_data == interleaved_data, "Mismatch between transmitted and received data"  # noqa: S101

    else:  # Slave Mode
        # DUT is Slave, so our testbench Master sends data to it
        await i2s_peripheral.write(interleaved_data)
        await Timer(10, units="us")
        dut._log.warning("Slave receive check relies on waveform analysis as DUT has no output path for received data.")

    await Timer(50, units="us")
    dut._log.info("Test finished successfully.")


# --- Pytest Test Runner ---
# This function is discovered by pytest. It runs the simulation and passes parameters.
@pytest.mark.parametrize("data_width", [24, 32])
@pytest.mark.parametrize("master_mode", [True, False])
def test_i2s_runner(data_width, master_mode):
    """Pytest wrapper to run the cocotb test."""
    # Define VHDL sources
    vhdl_sources = [os.path.join(os.path.dirname(__file__), "..", "src", "i2s_simple.vhd")]

    # Pass parameters to cocotb via environment variables
    sim_env = {
        "DATA_WIDTH": str(data_width),
        "MASTER_MODE": "true" if master_mode else "false",
    }

    run(
        vhdl_sources=vhdl_sources,
        toplevel="i2s_simple",
        module="test_i2s",  # Name of this python file
        toplevel_lang="vhdl",
        generics={"G_NBITS": data_width},
        extra_env=sim_env,
        testcase="i2s_test_logic",  # Name of the cocotb test function to run
    )

