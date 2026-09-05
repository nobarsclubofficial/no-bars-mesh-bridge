# No Bars Mesh Bridge

No Bars Mesh Bridge is the No Bars Club infrastructure fork of PE1HVH's MeshCore Bridge.

## Project goals

- Preserve the proven MeshCore cross-frequency bridge engine
- Add No Bars Club branding and deployment guidance
- Add a public, read-only network status layer for NoBarsClub.com
- Keep administrative controls private
- Add optional Discord and MQTT integrations without coupling them to the core forwarding path
- Keep the fork easy to sync with upstream fixes

## Architecture direction

### Core bridge
Two MeshCore devices connected to one Linux host forward selected channels through the existing bridge engine.

### Private admin surface
The existing dashboard remains the place for bridge configuration, device state, logs and operational controls. This surface should not be exposed publicly without authentication and a reverse proxy.

### Public status surface
A separate read-only status endpoint will expose only safe operational metadata such as:

- bridge online or offline
- uptime
- device connection health
- aggregate forwarded message counts
- last bridge activity time

It will not expose private channel names, secrets, message bodies or administrator controls.

### Integrations
Future optional adapters may publish selected operational events to Discord or MQTT. These adapters should fail independently so they never interrupt LoRa-to-LoRa forwarding.

## Licensing and attribution

This repository is based on `pe1hvh/meshcore-bridge` and retains the upstream MIT license and copyright notice. No Bars Club modifications are maintained in this fork.

## Development

NBC-specific work begins on the `nbc-foundation` branch. The `main` branch should remain stable and changes should reach it through reviewed pull requests.
