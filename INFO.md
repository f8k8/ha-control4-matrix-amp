# Control4 Matrix Amp Integration

This integration allows you to control a Control4 Matrix Amp (C4-16AMP3-B) from Home Assistant.

## What does this integration do?

- Creates a media player entity for each output zone on your matrix amp
- Allows you to control power, volume, and source selection for each zone
- Provides a custom service for routing inputs to outputs
- Supports control through the Home Assistant UI and REST API

## Features

### Zone Control
Each output (zone) of your matrix amp appears as a separate media player entity in Home Assistant. You can:
- Turn zones on/off
- Adjust volume levels
- Select input sources
- Monitor current state and settings

### Multi-zone Management
Perfect for whole-home audio setups where you want to:
- Control different music in each room
- Sync multiple zones to the same source (party mode)
- Create automations based on time, presence, or other sensors
- Adjust volumes automatically based on time of day

### Integration with Home Assistant
- Full REST API support for external control
- Works with automations and scripts
- Compatible with voice assistants (Alexa, Google Home) through Home Assistant
- Lovelace UI cards for easy control

## Quick Start

1. Install the integration through HACS or manually
2. Restart Home Assistant
3. Go to Settings → Devices & Services
4. Click "Add Integration" and search for "Control4 Matrix Amp"
5. Enter your device's IP address and configuration
6. Start controlling your zones!

## Need Help?

Check out the [full documentation](https://github.com/f8k8/ha-control4-matrix-amp) including:
- Detailed setup instructions
- Automation examples
- Lovelace card configurations
- REST API usage examples
- Troubleshooting guide

## Contributing

Found a bug or want to contribute? Visit our [GitHub repository](https://github.com/f8k8/ha-control4-matrix-amp) to open issues or submit pull requests.
