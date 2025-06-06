# GitHub Actions Workflows

## Jetson Segmentation Pipeline

This workflow automates the building and testing of the segmentation pipeline on Jetson devices.

### Workflow Details

- **Trigger**: Push to main, Pull requests, Manual dispatch
- **Runner**: Self-hosted Jetson runner
- **Steps**:
  1. Checkout code
  2. Setup Docker Buildx
  3. Build container
  4. Run tests
  5. Upload results
  6. Cleanup

### Requirements

- Self-hosted runner with 'jetson' tag
- NVIDIA Docker runtime
- Sufficient storage for images and artifacts

### Environment Setup

Runner setup instructions are in the main README.md file.
