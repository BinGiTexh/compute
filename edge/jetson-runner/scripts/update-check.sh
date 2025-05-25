#!/bin/bash

# Script to check for GitHub Actions Runner updates
set -e

# Get the latest release version
LATEST_VERSION=$(curl -s https://api.github.com/repos/actions/runner/releases/latest | grep '"tag_name":' | sed -E 's/.*"v([^"]+)".*/\1/')

# Get current version from docker-compose.yml
CURRENT_VERSION=$(grep "RUNNER_VERSION=" docker-compose.yml | head -1 | sed -E 's/.*RUNNER_VERSION=([0-9.]+).*/\1/')

# Compare versions
if [ "$LATEST_VERSION" != "$CURRENT_VERSION" ]; then
  echo "Update available: $CURRENT_VERSION -> $LATEST_VERSION"
  
  # Update the version in docker-compose.yml
  sed -i "s/RUNNER_VERSION=$CURRENT_VERSION/RUNNER_VERSION=$LATEST_VERSION/g" docker-compose.yml
  
  # Rebuild and restart the containers
  docker-compose down
  docker-compose up -d --build
  
  echo "Updated GitHub Runner to version $LATEST_VERSION"
else
  echo "GitHub Runner is up to date (version $CURRENT_VERSION)"
fi
