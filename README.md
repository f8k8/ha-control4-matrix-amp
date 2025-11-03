# Control4 Matrix Amp Home Assistant Integration

A Home Assistant custom component for controlling the Control4 Matrix Amp (C4-16AMP3-B).

## Features

- **Multi-zone Control**: Control up to 16 outputs (zones) independently
- **Input Routing**: Route any of the 6 inputs to any output
- **Volume Control**: Adjust volume for each zone individually
- **Power Management**: Turn zones on/off independently
- **UI Configuration**: Easy setup through Home Assistant UI
- **REST API Support**: Full control through Home Assistant's REST API
- **Media Player Integration**: Each zone appears as a media player entity

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Go to "Integrations"
3. Click the three dots in the top right corner
4. Select "Custom repositories"
5. Add this repository URL: `https://github.com/f8k8/ha-control4-matrix-amp`
6. Select category "Integration"
7. Click "Add"
8. Find "Control4 Matrix Amp" in the integration list and install it
9. Restart Home Assistant

### Manual Installation

1. Copy the `custom_components/control4_matrix_amp` directory to your Home Assistant's `custom_components` directory
2. Restart Home Assistant

## Configuration

### UI Configuration (Recommended)

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for "Control4 Matrix Amp"
4. Enter the following information:
   - **Host IP Address**: The IP address of your Control4 Matrix Amp
   - **Port**: The port number (default: 8750)
   - **Name**: A friendly name for your amp (default: "Control4 Matrix Amp")
   - **Number of Inputs**: Number of audio inputs (default: 6, max: 16)
   - **Number of Outputs**: Number of zones/outputs (default: 16, max: 16)
5. Click **Submit**

### YAML Configuration (Legacy)

While UI configuration is recommended, you can also configure via YAML:

```yaml
# Not required - use UI configuration instead
```

## Usage

### Controlling Zones

Each output (zone) appears as a media player entity:
- `media_player.control4_matrix_amp_zone_1`
- `media_player.control4_matrix_amp_zone_2`
- etc.

### Basic Operations

**Turn Zone On/Off:**
```yaml
service: media_player.turn_on
target:
  entity_id: media_player.control4_matrix_amp_zone_1
```

**Set Volume:**
```yaml
service: media_player.volume_set
target:
  entity_id: media_player.control4_matrix_amp_zone_1
data:
  volume_level: 0.5  # 0.0 to 1.0
```

**Select Input Source:**
```yaml
service: media_player.select_source
target:
  entity_id: media_player.control4_matrix_amp_zone_1
data:
  source: "Input 3"
```

### Custom Service

**Route Input to Output:**
```yaml
service: control4_matrix_amp.select_source
target:
  entity_id: media_player.control4_matrix_amp_zone_1
data:
  input: 3  # Input number 1-16
```

### REST API Examples

**Get Zone State:**
```bash
curl -X GET \
  -H "Authorization: Bearer YOUR_LONG_LIVED_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  http://YOUR_HA_IP:8123/api/states/media_player.control4_matrix_amp_zone_1
```

**Turn On Zone:**
```bash
curl -X POST \
  -H "Authorization: Bearer YOUR_LONG_LIVED_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"entity_id": "media_player.control4_matrix_amp_zone_1"}' \
  http://YOUR_HA_IP:8123/api/services/media_player/turn_on
```

**Set Volume:**
```bash
curl -X POST \
  -H "Authorization: Bearer YOUR_LONG_LIVED_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"entity_id": "media_player.control4_matrix_amp_zone_1", "volume_level": 0.5}' \
  http://YOUR_HA_IP:8123/api/services/media_player/volume_set
```

**Select Input Source:**
```bash
curl -X POST \
  -H "Authorization: Bearer YOUR_LONG_LIVED_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"entity_id": "media_player.control4_matrix_amp_zone_1", "input": 3}' \
  http://YOUR_HA_IP:8123/api/services/control4_matrix_amp/select_source
```

## Automation Examples

### Turn on zone and set source when motion detected
```yaml
automation:
  - alias: "Living Room Audio On Motion"
    trigger:
      - platform: state
        entity_id: binary_sensor.living_room_motion
        to: "on"
    action:
      - service: media_player.turn_on
        target:
          entity_id: media_player.control4_matrix_amp_zone_1
      - service: media_player.select_source
        target:
          entity_id: media_player.control4_matrix_amp_zone_1
        data:
          source: "Input 1"
      - service: media_player.volume_set
        target:
          entity_id: media_player.control4_matrix_amp_zone_1
        data:
          volume_level: 0.3
```

### Multi-zone party mode
```yaml
automation:
  - alias: "Party Mode"
    trigger:
      - platform: state
        entity_id: input_boolean.party_mode
        to: "on"
    action:
      - service: media_player.turn_on
        target:
          entity_id:
            - media_player.control4_matrix_amp_zone_1
            - media_player.control4_matrix_amp_zone_2
            - media_player.control4_matrix_amp_zone_3
      - service: control4_matrix_amp.select_source
        target:
          entity_id:
            - media_player.control4_matrix_amp_zone_1
            - media_player.control4_matrix_amp_zone_2
            - media_player.control4_matrix_amp_zone_3
        data:
          input: 1  # Same source for all zones
```

## Lovelace UI Card Example

```yaml
type: entities
title: Control4 Matrix Amp
entities:
  - entity: media_player.control4_matrix_amp_zone_1
    name: Living Room
    type: custom:mini-media-player
  - entity: media_player.control4_matrix_amp_zone_2
    name: Kitchen
    type: custom:mini-media-player
  - entity: media_player.control4_matrix_amp_zone_3
    name: Bedroom
    type: custom:mini-media-player
```

## Troubleshooting

### Connection Issues

1. **Verify IP and Port**: Ensure the Control4 Matrix Amp is accessible at the configured IP address and port
2. **Network Connectivity**: Check that Home Assistant can reach the device on your network
3. **Firewall**: Ensure no firewall is blocking UDP traffic on port 8750 (or your configured port)

### Check Logs

Enable debug logging in your `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.control4_matrix_amp: debug
```

## Technical Details

### Communication Protocol

The integration communicates with the Control4 Matrix Amp over UDP using the Control4 protocol:

- **c4.amp.out \<output\> 0\<input\>**: Route an input to an output (power on)
- **c4.amp.out \<output\> 00**: Power off an output
- **c4.amp.chvol \<output\> \<volume_hex\>**: Set volume (hex value)

Commands are prefixed with a counter (0s2a + random 2-digit number) for packet identification.

Note: The Control4 UDP protocol is primarily command-based and does not support state queries. The integration tracks state locally.

### Device Compatibility

This integration is designed for the Control4 Matrix Amp model C4-16AMP3-B but may work with similar Control4 matrix amplifiers.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.

## Support

For issues, questions, or feature requests, please open an issue on [GitHub](https://github.com/f8k8/ha-control4-matrix-amp/issues).