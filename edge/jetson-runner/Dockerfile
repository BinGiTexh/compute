FROM arm64v8/ubuntu:22.04

# Install required packages
RUN apt-get update && apt-get install -y \
    curl \
    jq \
    git \
    iputils-ping \
    supervisor \
    docker.io \
    libicu70 \
    && rm -rf /var/lib/apt/lists/*

# Create runner user
RUN useradd -m github-runner

# Hardcode runner version and token for testing
ARG RUNNER_VERSION=2.324.0
ARG RUNNER_TOKEN
ARG ORG_NAME="IMAC-community"

# Create a directory for the runner and switch to it
RUN mkdir -p /home/github-runner/actions-runner
WORKDIR /home/github-runner/actions-runner

# Download and install the GitHub runner (following GitHub's instructions but for ARM64)
RUN curl -o actions-runner-linux-arm64-${RUNNER_VERSION}.tar.gz -L \
    https://github.com/actions/runner/releases/download/v${RUNNER_VERSION}/actions-runner-linux-arm64-${RUNNER_VERSION}.tar.gz && \
    tar xzf ./actions-runner-linux-arm64-${RUNNER_VERSION}.tar.gz && \
    rm actions-runner-linux-arm64-${RUNNER_VERSION}.tar.gz && \
    ls -la && \
    chown -R github-runner:github-runner /home/github-runner

# Add github-runner to docker group
RUN usermod -aG docker github-runner

# Copy and set up scripts
COPY scripts/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

COPY scripts/health-check.sh /health-check.sh
RUN chmod +x /health-check.sh

# Switch to github-runner user for execution
USER github-runner

HEALTHCHECK --interval=30s --timeout=10s --retries=3 CMD /health-check.sh

ENTRYPOINT ["/entrypoint.sh"]
