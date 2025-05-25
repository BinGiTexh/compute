#!/bin/bash
set -e

cd /home/github-runner/actions-runner

RUNNER_TOKEN=${RUNNER_TOKEN:-$1}
ORG_NAME=${ORG_NAME:-$2}

if [ ! -f ".runner" ]; then
    # Configure the runner if it hasn't been configured
    ./config.sh --unattended \
        --url "https://github.com/${ORG_NAME}" \
        --token "${RUNNER_TOKEN}" \
        --name "$(hostname)" \
        --work "/home/github-runner/data/_work" \
        --labels "self-hosted,Linux,ARM64" \
        --runnergroup "Default" \
        --replace
fi

# Ensure the data directory exists and has correct permissions
mkdir -p /home/github-runner/data/_work

# Start the runner
exec ./run.sh
