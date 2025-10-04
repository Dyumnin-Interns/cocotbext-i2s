"""Cocotb testbench for the I2S core."""

from __future__ import annotations

import os
import random

import cocotb
import pytest  # type: ignore
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer
from cocotb_test.simulator import run  # type: ignore
from cocotbext.i2s.driver import I2sMaster, I2sSlave  # type: ignore


# Helper task for generating the main system clock.
async def clock_gen(signal):
    """System Clock Generator."""
    await cocotb.start(Clock(signal, 10, units="ns").start())


# Helper task for resetting the DUT.
async def reset_dut(reset_signal, duration_ns):
    """Resets the DUT."""
    reset_signal.value = 1
    await Timer(duration_ns, units="ns")
    reset_signal.value = 0
    await RisingEdge(reset_signal.parent.i_clk)


@cocotb.test()
async def i2s_test_logic(dut):
    """Main parameterized test logic for I2S verification."""
    # Retrieve parameters from the environment
    data_width = int(os.environ.get("DATA_WIDTH", "24"))
    master_mode = os.environ.get("MASTER_MODE", "true").lower() == "true"

    # Start the system clock.
    await clock_gen(dut.i_clk)

    # Reset the DUT.
    await reset_dut(dut.i_rst, 20)

    # --- Test Data Generation ---
    # Generate 10 random data words for left and right channels.
    left_channel_data = [random.randint(0, (2**data_width) - 1) for _ in range(10)]  # noqa: S311
    right_channel_data = [random.randint(0, (2**data_width) - 1) for _ in range(10)]  # noqa: S311
    interleaved_data = []
    for left_val, right_val in zip(left_channel_data, right_channel_data):
        interleaved_data.extend([left_val, right_val])

    # --- Driver and Monitor Setup ---
    if master_mode:
        # DUT is Master, Testbench is Slave
        tb_driver = I2sSlave(
            dut,
            sclk=dut.o_bclk,
            ws=dut.o_wclk,
            sd=dut.o_sd,
            data_width=data_width,
        )
    else:
        # DUT is Slave, Testbench is Master
        tb_driver = I2sMaster(
            dut,
            sclk=dut.i_bclk,
            ws=dut.i_wclk,
            sd=dut.i_sd,
            data_width=data_width,
        )

    # --- Test Execution ---
    if master_mode:  # Master Mode
        # In master mode, we provide data to the DUT and let it transmit.
        # We then use the testbench's slave driver to receive it.
        for left, right in zip(left_channel_data, right_channel_data):
            # Load left channel data
            dut.i_left_chan_data.value = left
            dut.i_right_chan_data.value = right
            dut.i_valid_data.value = 1
            await RisingEdge(dut.i_clk)
            dut.i_valid_data.value = 0
            await Timer(1, units="us")

        # Wait for transmission to complete and receive the data.
        await Timer(10, units="us")
        received_data = tb_driver.recv()

        # --- Verification ---
        assert received_data == interleaved_data, "Mismatch between transmitted and received data."  # noqa: S101

    else:  # Slave Mode
        # In slave mode, the testbench master drives the data to the DUT.
        await tb_driver.write(interleaved_data)

        # Wait for the DUT to process the data.
        await Timer(10, units="us")

        # In a real scenario, you would read back from DUT internal signals/registers
        # to verify correct reception. This part is DUT-specific.
        dut._log.info("Slave mode test completed. Verification depends on DUT implementation.")


# Pytest runner
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
        module="tests",
        toplevel_lang="vhdl",
        generics={"G_NBITS": data_width},
        extra_env=sim_env,
        testcase="i2s_test_logic",
        # Use GHDL simulator for VHDL files
        simulator="ghdl",
    )
