
















# Rover Operations - Tele-operation & Supervised Autonomy Platform

![Rover Operations Architecture](docs/images/architecture-overview.png)

## Overview

**Rover Operations** is a production-quality monorepo implementing an end-to-end MVP for tele-operation and supervised autonomy of heavy machines. The platform provides live video feeds, drive controls, safety features (E-stop, geofencing), telemetry streaming, session recording, and policy enforcement.

### Key Features
- **Live Video**: Simulated video feed via WebRTC
- **Drive Controls**: WASD/joystick control with speed cap
- **Safety Systems**:
  - Virtual E-stop with immediate effect
  - Dead-man switch for operator control
  - Geofencing to block restricted areas
- **Telemetry**: Real-time sensor data streaming (GPS, IMU, etc.)
- **Session Recording**: Record and replay operations
- **Policy Engine**: Enforce speed limits, access controls

## Getting Started

### Prerequisites
- Docker & Docker Compose
- Make utility
- Node.js 20+
- Go 1.22+
- Python 3.11+

### Quick Start

```bash
# Bring up the development environment
make dev-up

# Run simulation service (Python)
make run-sim

# Start edge agent with hello-tractor driver (Go)
make run-edge

# Launch operator console (Next.js)
make run-web
```

## System Architecture

![System Components](docs/images/component-diagram.png)

### Core Services
- **Control Broker**: Session management, authZ, policy gates, E-stop fanout
- **Signaling Server**: WebRTC signaling with Pion library
- **Telemetry Service**: Ingest -> NATS -> ClickHouse pipeline
- **Policy Engine**: Geofences, speed limits, role/time windows
- **Replay Service**: Session recording and playback

### Edge Components
- **Edge Agent**: Device driver management, WebRTC data channel, policy enforcement
- **Hello Tractor Driver**: Simulated tractor implementing DCM (Drive, Sensors)

## Safety Features

![Safety Diagram](docs/images/safety-overview.png)

1. **E-stop System**:
   - Enforced at agent level with hard stop
   - Mirrored in control-broker for system-wide effect
2. **Dead-man Switch**: Operator must maintain periodic keepalive to hold control
3. **Geofencing**: Blocks commands that would cross restricted polygons
4. **Speed Caps**: Policy-engine enforced limits with tamper-evident logging

## Development Workflow

### Common Makefile Targets

```bash
# Help message
make help

# Development environment management
make dev-up      # Start all services
make dev-down    # Stop and remove containers
make dev-logs    # View service logs

# Service-specific targets
make build-sim   # Build simulation service
make run-sim     # Run tractor simulation
make build-edge  # Build edge agent
make run-edge    # Start edge agent with driver
make build-web   # Build web console
make run-web     # Launch operator console

# Testing and quality
make test        # Run all tests
make lint        # Lint codebase
```

### Demo Flow

1. Create geofence in policy engine
2. Start tractor simulation: `make run-sim`
3. Take control from web console
4. Drive with WASD controls
5. Test geofencing boundary
6. Activate E-stop and observe immediate stop
7. Stop session and view replay

## Documentation

- [Architecture Overview](docs/architecture.md)
- [Safety Systems](docs/safety.md)
- [Operator Training](docs/operators.md)
- [Compliance & Auditing](docs/compliance.md)

## Contributing

Please see our [Contribution Guidelines](docs/CONTRIBUTING.md) for details on:

- Code style and conventions
- Testing requirements
- Pull request process
- Issue templates

## License

This project is licensed under the Apache 2.0 license - see the [LICENSE](LICENSE) file for details.

## Project Status

![Project Board](https://img.shields.io/badge/Project-Backlog%2C%20In%20Progress%2C%20Review%2C%20Done-blue)

### Roadmap Issues
- MVP: Hello Tractor E2E ✅
- Hardening: TURN & NAT traversal 🚧
- Add hardware E-stop GPIO support 📝
- Add ClickHouse retention policies 📝

## Screenshots

![Operator Console](docs/images/console-screenshot.png)
*Web console showing live video feed, controls, and telemetry HUD*














