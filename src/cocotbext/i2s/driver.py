from .config import default_config
class I2sDriver:

        def __init__(self,bus,config=default_config,name=None):
               self.bus=bus
               self.config=config

        async def write(self,address:int, data:bytes):
                pass

        async def read(self,address:int,numBytes:int):
                pass

        async def _txrx(self) -> None:
                """
                Internal transmit/receive coroutine for the I2S driver.
                
                This method handles low-level TX/RX operations asynchronously.
                
                Returns:
                        None
                """
                pass


        def add_callback(self, compare_fn):
                """Callback into scoreboard."""
                pass

