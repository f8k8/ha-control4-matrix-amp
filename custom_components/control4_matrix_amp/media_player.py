"""Support for Control4 Matrix Amp media players."""
import logging
from typing import Any

from homeassistant.components.media_player import (
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    ATTR_INPUT,
    ATTR_OUTPUT,
    CONF_NUM_INPUTS,
    CONF_NUM_OUTPUTS,
    CONF_PORT,
    DEFAULT_NAME,
    DEFAULT_NUM_INPUTS,
    DEFAULT_NUM_OUTPUTS,
    DEFAULT_PORT,
    DOMAIN,
    SERVICE_SELECT_SOURCE,
)
from .matrix_amp import Control4MatrixAmp

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Control4 Matrix Amp media players."""
    host = config_entry.data[CONF_HOST]
    port = config_entry.data.get(CONF_PORT, DEFAULT_PORT)
    name = config_entry.data.get(CONF_NAME, DEFAULT_NAME)
    num_inputs = config_entry.data.get(CONF_NUM_INPUTS, DEFAULT_NUM_INPUTS)
    num_outputs = config_entry.data.get(CONF_NUM_OUTPUTS, DEFAULT_NUM_OUTPUTS)

    # Create one matrix amp connection
    matrix_amp = Control4MatrixAmp(host, port)

    # Create media player entities for each output
    entities = []
    for output in range(1, num_outputs + 1):
        entities.append(
            Control4MatrixAmpMediaPlayer(
                matrix_amp, output, num_inputs, f"{name} Zone {output}", config_entry.entry_id
            )
        )

    async_add_entities(entities)

    # Register custom service
    hass.data.setdefault(DOMAIN, {})
    platform = hass.data[DOMAIN].get("platform")
    if not platform:
        from homeassistant.helpers import entity_platform
        platform = entity_platform.async_get_current_platform()
        hass.data[DOMAIN]["platform"] = platform

        # Register service to select source for output
        platform.async_register_entity_service(
            SERVICE_SELECT_SOURCE,
            {
                ATTR_INPUT: int,
            },
            "async_select_source_to_output",
        )


class Control4MatrixAmpMediaPlayer(MediaPlayerEntity):
    """Representation of a Control4 Matrix Amp output as a media player."""

    _attr_has_entity_name = True
    _attr_should_poll = True

    def __init__(
        self,
        matrix_amp: Control4MatrixAmp,
        output: int,
        num_inputs: int,
        name: str,
        entry_id: str,
    ):
        """Initialize the media player."""
        self._matrix_amp = matrix_amp
        self._output = output
        self._num_inputs = num_inputs
        self._attr_name = name
        self._attr_unique_id = f"{entry_id}_output_{output}"
        
        # State attributes
        self._state = MediaPlayerState.OFF
        self._volume = 0
        self._current_source = None
        self._available = True

        # Supported features
        self._attr_supported_features = (
            MediaPlayerEntityFeature.TURN_ON
            | MediaPlayerEntityFeature.TURN_OFF
            | MediaPlayerEntityFeature.VOLUME_SET
            | MediaPlayerEntityFeature.SELECT_SOURCE
        )

        # Source list (inputs)
        self._attr_source_list = [f"Input {i}" for i in range(1, num_inputs + 1)]

    @property
    def state(self) -> MediaPlayerState:
        """Return the state of the device."""
        return self._state

    @property
    def volume_level(self) -> float | None:
        """Volume level of the media player (0..1)."""
        if self._volume is not None:
            return self._volume / 100.0
        return None

    @property
    def source(self) -> str | None:
        """Return the current input source."""
        if self._current_source is not None:
            return f"Input {self._current_source}"
        return None

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._available

    async def async_update(self) -> None:
        """Update the state of the media player."""
        try:
            # Note: Control4 UDP protocol doesn't support state queries
            # State is tracked locally when commands are sent
            # The device is considered available if we can communicate
            self._available = True
        except Exception as err:
            _LOGGER.error("Error updating output %s: %s", self._output, err)
            self._available = False

    async def async_turn_on(self) -> None:
        """Turn the media player on."""
        # Use current source or default to input 1
        input_source = self._current_source if self._current_source else 1
        await self._matrix_amp.power_on_output(self._output, input_source)
        self._state = MediaPlayerState.ON
        if not self._current_source:
            self._current_source = input_source

    async def async_turn_off(self) -> None:
        """Turn the media player off."""
        await self._matrix_amp.power_off_output(self._output)
        self._state = MediaPlayerState.OFF

    async def async_set_volume_level(self, volume: float) -> None:
        """Set volume level, range 0..1."""
        volume_int = int(volume * 100)
        await self._matrix_amp.set_output_volume(self._output, volume_int)
        self._volume = volume_int

    async def async_select_source(self, source: str) -> None:
        """Select input source."""
        # Extract input number from source name (e.g., "Input 1" -> 1)
        try:
            input_num = int(source.split()[-1])
            await self._matrix_amp.set_output_source(self._output, input_num)
            self._current_source = input_num
        except (ValueError, IndexError) as err:
            _LOGGER.error("Invalid source format: %s, error: %s", source, err)

    async def async_select_source_to_output(self, input: int) -> None:
        """Custom service to select source by input number."""
        if 1 <= input <= self._num_inputs:
            await self._matrix_amp.set_output_source(self._output, input)
            self._current_source = input
        else:
            _LOGGER.error("Invalid input number: %s", input)
