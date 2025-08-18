# i2s COCOTB VIP for i2s protocol
I2S Protocol

# install
`pip3 install cocotbext_i2s`

#Usage

```
from cocotbext.i2s import I2sBus,I2sDriver,I2sConfig

....
class Env:
   def __init__(self,dut):
	i2s_bus = I2sBus(from_prefix='...',dut=....)
	i2s_config = I2sConfig()
	i2s_config.<key>=<value>
	i2s_driver = i2sDriver(i2s_bus, i2s_config)
   async def xyz(self):
 	i2s_driver.write(address,byteArray)
 	rv =i2s_driver.read(address,numbytes)
	assert rv=byteArray, "Data mismatch at %X"%(address)

