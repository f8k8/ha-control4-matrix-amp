"""Control4 Matrix Amp communication module."""
import asyncio
import logging
from typing import Optional

_LOGGER = logging.getLogger(__name__)


class Control4MatrixAmp:
    """Class to communicate with Control4 Matrix Amp."""

    def __init__(self, host: str, port: int = 4999):
        """Initialize the Control4 Matrix Amp."""
        self.host = host
        self.port = port
        self._reader: Optional[asyncio.StreamReader] = None
        self._writer: Optional[asyncio.StreamWriter] = None
        self._lock = asyncio.Lock()
        self._connected = False

    async def connect(self) -> bool:
        """Connect to the matrix amp."""
        try:
            async with self._lock:
                if self._connected:
                    return True

                self._reader, self._writer = await asyncio.wait_for(
                    asyncio.open_connection(self.host, self.port),
                    timeout=10.0,
                )
                self._connected = True
                _LOGGER.info("Connected to Control4 Matrix Amp at %s:%s", self.host, self.port)
                return True
        except asyncio.TimeoutError:
            _LOGGER.error("Timeout connecting to Control4 Matrix Amp")
            return False
        except Exception as err:
            _LOGGER.error("Error connecting to Control4 Matrix Amp: %s", err)
            return False

    async def disconnect(self):
        """Disconnect from the matrix amp."""
        async with self._lock:
            if self._writer:
                try:
                    self._writer.close()
                    await self._writer.wait_closed()
                except Exception as err:
                    _LOGGER.error("Error disconnecting: %s", err)
                finally:
                    self._writer = None
                    self._reader = None
                    self._connected = False

    async def send_command(self, command: str) -> Optional[str]:
        """Send a command to the matrix amp."""
        if not self._connected:
            if not await self.connect():
                return None

        try:
            async with self._lock:
                # Send command with proper termination
                self._writer.write(f"{command}\r\n".encode())
                await self._writer.drain()

                # Read response with timeout
                response = await asyncio.wait_for(
                    self._reader.readline(),
                    timeout=5.0,
                )
                return response.decode().strip()
        except asyncio.TimeoutError:
            _LOGGER.error("Timeout waiting for response")
            await self.disconnect()
            return None
        except Exception as err:
            _LOGGER.error("Error sending command: %s", err)
            await self.disconnect()
            return None

    async def set_output_source(self, output: int, input_source: int) -> bool:
        """Route an input to an output."""
        # Control4 Matrix Amp command format: ROUTE <output> <input>
        command = f"ROUTE {output} {input_source}"
        response = await self.send_command(command)
        return response is not None and "OK" in response

    async def set_output_volume(self, output: int, volume: int) -> bool:
        """Set volume for an output (0-100)."""
        # Command format: SETVOL <output> <volume>
        command = f"SETVOL {output} {volume}"
        response = await self.send_command(command)
        return response is not None and "OK" in response

    async def get_output_source(self, output: int) -> Optional[int]:
        """Get the current source for an output."""
        # Command format: GETROUTE <output>
        command = f"GETROUTE {output}"
        response = await self.send_command(command)
        if response and "SOURCE" in response:
            try:
                # Expected response format: "SOURCE <input>"
                return int(response.split()[1])
            except (IndexError, ValueError):
                _LOGGER.error("Invalid response format: %s", response)
        return None

    async def get_output_volume(self, output: int) -> Optional[int]:
        """Get the current volume for an output."""
        # Command format: GETVOL <output>
        command = f"GETVOL {output}"
        response = await self.send_command(command)
        if response and "VOLUME" in response:
            try:
                # Expected response format: "VOLUME <level>"
                return int(response.split()[1])
            except (IndexError, ValueError):
                _LOGGER.error("Invalid response format: %s", response)
        return None

    async def power_on_output(self, output: int) -> bool:
        """Power on an output."""
        command = f"POWERON {output}"
        response = await self.send_command(command)
        return response is not None and "OK" in response

    async def power_off_output(self, output: int) -> bool:
        """Power off an output."""
        command = f"POWEROFF {output}"
        response = await self.send_command(command)
        return response is not None and "OK" in response

    async def get_output_state(self, output: int) -> Optional[bool]:
        """Get the power state of an output."""
        command = f"GETPOWER {output}"
        response = await self.send_command(command)
        if response:
            if "ON" in response:
                return True
            elif "OFF" in response:
                return False
        return None
