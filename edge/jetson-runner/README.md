# Dynamic GitHub Runner Configuration for Edge Devices

This directory contains the configuration for a self-hosted GitHub Actions runner designed for edge devices, particularly Jetson devices. The setup includes dynamic runner naming based on system specifications.

## Features

- Dynamic runner naming based on system specifications
- Containerized runner using Docker Compose
- Automatic detection of:
  - Device model name
  - System architecture
  - Available RAM
- Portable configuration suitable for various edge devices

## Directory Structure

```
.
├── docker-compose.yml
└── data/
    └── generate_runner_name.sh
```

## Configuration Files

### docker-compose.yml
Contains the Docker Compose configuration for the GitHub runner with dynamic naming support.

### generate_runner_name.sh
Script that automatically generates the runner name based on system specifications:
- Reads device model from /proc/device-tree/model (falls back to hostname)
- Detects system architecture using uname
- Calculates available RAM

## Setup Instructions

1. Clone this repository
2. Set required environment variables:
   ```bash
   export RUNNER_TOKEN=<your-github-runner-token>
   export ORG_NAME=<your-github-org-name>
   ```
3. Start the runner:
   ```bash
   docker compose up -d
   ```

## Runner Naming Convention

The runner will be automatically named following the pattern:
`<Device Model> (<Architecture>, <RAM>GB)`

Example: "Jetson AGX Orin (aarch64, 61GB)"

## Important Notes

- The runner token should be kept secure and not committed to version control
- The data directory is mounted into the container for persistent runner configuration
- Docker socket is mounted to allow Docker operations within workflows

