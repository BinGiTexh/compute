#!/bin/bash

# Device-specific health check script
# Usage: ./health-check.sh [device-type]

# Default thresholds
MEMORY_THRESHOLD=80
CPU_THRESHOLD=90
GPU_THRESHOLD=85
DISK_THRESHOLD=90

# Load device-specific configuration
load_device_config() {
    DEVICE_TYPE=$1
    if [ -f "devices/$DEVICE_TYPE/device_config.json" ]; then
        echo "Loading configuration for $DEVICE_TYPE"
        # In a real implementation, parse the JSON file and set thresholds
    else
        echo "Warning: No device-specific configuration found. Using defaults."
    fi
}

# Check memory usage
check_memory() {
    MEM_USAGE=$(free | grep Mem | awk '{print ($3/$2) * 100}' | cut -d. -f1)
    if [ $MEM_USAGE -gt $MEMORY_THRESHOLD ]; then
        echo "WARNING: High memory usage: $MEM_USAGE%"
        return 1
    fi
    echo "Memory usage: $MEM_USAGE% (OK)"
    return 0
}

# Check CPU usage
check_cpu() {
    CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print int($2)}')
    if [ $CPU_USAGE -gt $CPU_THRESHOLD ]; then
        echo "WARNING: High CPU usage: $CPU_USAGE%"
        return 1
    fi
    echo "CPU usage: $CPU_USAGE% (OK)"
    return 0
}

# Check GPU if available
check_gpu() {
    if command -v nvidia-smi &> /dev/null; then
        GPU_USAGE=$(nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits)
        if [ $GPU_USAGE -gt $GPU_THRESHOLD ]; then
            echo "WARNING: High GPU usage: $GPU_USAGE%"
            return 1
        fi
        echo "GPU usage: $GPU_USAGE% (OK)"
        return 0
    else
        echo "No GPU detected"
        return 0
    fi
}

# Check disk space
check_disk() {
    DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | cut -d% -f1)
    if [ $DISK_USAGE -gt $DISK_THRESHOLD ]; then
        echo "WARNING: High disk usage: $DISK_USAGE%"
        return 1
    fi
    echo "Disk usage: $DISK_USAGE% (OK)"
    return 0
}

# Check temperature (for supported devices)
check_temperature() {
    if [ -f /sys/class/thermal/thermal_zone0/temp ]; then
        TEMP=$(cat /sys/class/thermal/thermal_zone0/temp)
        TEMP=$((TEMP/1000))
        if [ $TEMP -gt 80 ]; then
            echo "WARNING: High temperature: $TEMP°C"
            return 1
        fi
        echo "Temperature: $TEMP°C (OK)"
        return 0
    else
        echo "Temperature monitoring not available"
        return 0
    fi
}

# Main execution
main() {
    DEVICE_TYPE=${1:-"jetson-agx-orin"}  # Default to AGX Orin if no device specified
    load_device_config $DEVICE_TYPE

    echo "Running health check for $DEVICE_TYPE..."
    echo "----------------------------------------"

    ERRORS=0
    check_memory || ((ERRORS++))
    check_cpu || ((ERRORS++))
    check_gpu || ((ERRORS++))
    check_disk || ((ERRORS++))
    check_temperature || ((ERRORS++))

    echo "----------------------------------------"
    if [ $ERRORS -gt 0 ]; then
        echo "Health check completed with $ERRORS warnings"
        exit 1
    else
        echo "All checks passed successfully"
        exit 0
    fi
}

main "$@"
