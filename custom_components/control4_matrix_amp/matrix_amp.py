"""Control4 Matrix Amp communication module."""
import asyncio
import logging
import random
import socket
from typing import Optional

_LOGGER = logging.getLogger(__name__)


class Control4MatrixAmp:
    """Class to communicate with Control4 Matrix Amp."""

    def __init__(self, host: str, port: int = 8750):
        """Initialize the Control4 Matrix Amp."""
        self.host = host
        self.port = port
        self._lock = asyncio.Lock()

    async def send_command(self, command: str) -> Optional[str]:
        """Send a UDP command to the matrix amp."""
        try:
            async with self._lock:
                # Generate counter prefix (0s2a + random 2-digit number)
                counter = "0s2a" + str(random.randint(10, 99))
                full_command = counter + " " + command + " \r\n"
                
                _LOGGER.debug("Sending command: %s", full_command)
                
                # Create UDP socket
                loop = asyncio.get_event_loop()
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.settimeout(5.0)
                
                # Send command
                await loop.run_in_executor(
                    None,
                    sock.sendto,
                    bytes(full_command, "utf-8"),
                    (self.host, self.port)
                )
                
                # Receive response
                try:
                    response_bytes = await loop.run_in_executor(
                        None,
                        sock.recv,
                        1024
                    )
                    response = str(response_bytes, "utf-8").strip()
                    _LOGGER.debug("Command sent. Response: %s", response)
                    sock.close()
                    return response
                except socket.timeout:
                    _LOGGER.debug("No response received (timeout)")
                    sock.close()
                    return "OK"  # Assume success if no response
                    
        except Exception as err:
            _LOGGER.error("Error sending command: %s", err)
            return None

    async def set_output_source(self, output: int, input_source: int) -> bool:
        """Route an input to an output."""
        # Control4 Matrix Amp command format: c4.amp.out <output> 0<input>
        # Output should be zero-padded 2 digits, input as hex
        output_str = f"{output:02d}"
        input_hex = f"0{input_source:x}"
        command = f"c4.amp.out {output_str} {input_hex}"
        response = await self.send_command(command)
        return response is not None

    async def set_output_volume(self, output: int, volume: int) -> bool:
        """Set volume for an output (0-100)."""
        # Command format: c4.amp.chvol <output> <volume_hex>
        # Volume formula: int(volume * 100 + 160) converted to hex
        # Since volume is already 0-100, we can use: int(volume + 1.6)
        # But based on examples, volume 0-100 maps to hex values
        # Formula from example: int(float(volume_percent) * 100) + 160
        output_str = f"{output:02d}"
        volume_value = int(volume) + 160  # volume is 0-100
        volume_hex = hex(volume_value)[2:]  # Remove '0x' prefix
        command = f"c4.amp.chvol {output_str} {volume_hex}"
        response = await self.send_command(command)
        return response is not None

    async def get_output_source(self, output: int) -> Optional[int]:
        """Get the current source for an output."""
        # Note: Control4 protocol may not support query commands in the same way
        # This method may need to track state locally
        _LOGGER.debug("get_output_source not supported by Control4 UDP protocol")
        return None

    async def get_output_volume(self, output: int) -> Optional[int]:
        """Get the current volume for an output."""
        # Note: Control4 protocol may not support query commands in the same way
        # This method may need to track state locally
        _LOGGER.debug("get_output_volume not supported by Control4 UDP protocol")
        return None

    async def power_on_output(self, output: int, input_source: int = 1) -> bool:
        """Power on an output with specified input source."""
        # Power on by routing an input to the output
        output_str = f"{output:02d}"
        input_hex = f"0{input_source:x}"
        command = f"c4.amp.out {output_str} {input_hex}"
        response = await self.send_command(command)
        return response is not None

    async def power_off_output(self, output: int) -> bool:
        """Power off an output."""
        # Command format: c4.amp.out <output> 00
        output_str = f"{output:02d}"
        command = f"c4.amp.out {output_str} 00"
        response = await self.send_command(command)
        return response is not None

    async def get_output_state(self, output: int) -> Optional[bool]:
        """Get the power state of an output."""
        # Note: Control4 protocol may not support query commands in the same way
        # This method may need to track state locally
        _LOGGER.debug("get_output_state not supported by Control4 UDP protocol")
        return None
