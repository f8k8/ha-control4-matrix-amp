"""Control4 Matrix Amp communication module."""
import asyncio
import logging
import random
import socket
from typing import Optional

_LOGGER = logging.getLogger(__name__)

# Control4 protocol constants
COUNTER_PREFIX = "0s2a"  # Control4 packet counter prefix
COMMAND_TERMINATOR = " \r\n"  # Control4 command terminator (space + CRLF)
VOLUME_OFFSET = 160  # Volume offset required by Control4 protocol


class Control4MatrixAmp:
    """Class to communicate with Control4 Matrix Amp."""

    def __init__(self, host: str, port: int = 8750):
        """Initialize the Control4 Matrix Amp."""
        self.host = host
        self.port = port
        self._lock = asyncio.Lock()

    async def send_command(self, command: str) -> Optional[str]:
        """Send a UDP command to the matrix amp.
        
        Note: Creates a new UDP socket for each command. This is intentional as:
        1. UDP is connectionless, so there's no persistent connection to maintain
        2. Creating UDP sockets is lightweight compared to TCP
        3. Ensures clean state for each command
        4. Avoids issues with socket timeout/error states
        """
        sock = None
        try:
            async with self._lock:
                # Generate counter prefix for packet identification
                counter = COUNTER_PREFIX + str(random.randint(10, 99))
                full_command = counter + " " + command + COMMAND_TERMINATOR
                
                _LOGGER.debug("Sending command: %s", full_command)
                
                # Create UDP socket for this command
                loop = asyncio.get_event_loop()
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.setblocking(False)
                
                # Send command
                await loop.sock_sendto(
                    sock,
                    bytes(full_command, "utf-8"),
                    (self.host, self.port)
                )
                
                # Receive response with timeout
                try:
                    response_bytes = await asyncio.wait_for(
                        loop.sock_recv(sock, 1024),
                        timeout=2.0
                    )
                    response = str(response_bytes, "utf-8").strip()
                    _LOGGER.debug("Command sent. Response: %s", response)
                    return response
                except asyncio.TimeoutError:
                    _LOGGER.debug("No response received (timeout)")
                    # UDP protocol may not always send responses, return None to indicate unknown status
                    return None
                    
        except Exception as err:
            _LOGGER.error("Error sending command: %s", err)
            return None
        finally:
            if sock:
                sock.close()

    def _validate_input_source(self, input_source: int) -> bool:
        """Validate input source is in valid range.
        
        Args:
            input_source: Input source number to validate
            
        Returns:
            True if valid, False otherwise
            
        Note: Input values must be 1-15 to fit in single hex digit format (e.g., '01', '0f').
        """
        if not 1 <= input_source <= 15:
            _LOGGER.error("Input source must be between 1 and 15, got %d", input_source)
            return False
        return True

    async def set_output_source(self, output: int, input_source: int) -> bool:
        """Route an input to an output.
        
        Args:
            output: Output number (1-16)
            input_source: Input source number (1-15)
        """
        if not self._validate_input_source(input_source):
            return False
            
        output_str = f"{output:02d}"
        input_hex = f"0{input_source:x}"
        command = f"c4.amp.out {output_str} {input_hex}"
        response = await self.send_command(command)
        return response is not None

    async def set_output_volume(self, output: int, volume: int) -> bool:
        """Set volume for an output (0-100).
        
        Args:
            output: Output number (1-16)
            volume: Volume level 0-100
            
        The Control4 protocol expects volume as: (volume + VOLUME_OFFSET) in hexadecimal.
        For example: volume 50 -> (50 + 160) = 210 = 0xd2
        """
        output_str = f"{output:02d}"
        volume_value = int(volume) + VOLUME_OFFSET
        volume_hex = hex(volume_value)[2:]
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
        """Power on an output with specified input source.
        
        Args:
            output: Output number (1-16)
            input_source: Input source number (1-15), defaults to 1
        
        Power on is achieved by routing an input to the output.
        """
        if not self._validate_input_source(input_source):
            return False
            
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
