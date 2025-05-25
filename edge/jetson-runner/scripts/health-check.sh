#!/bin/bash

# Check if the runner process is running
if pgrep -f "./run.sh" > /dev/null; then
    exit 0
else
    exit 1
fi
