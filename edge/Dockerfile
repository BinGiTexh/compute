# Use the specified base image with NVIDIA support
FROM dustynv/jupyterlab:r35.4.1

# Install Python packages
RUN pip install --no-cache-dir \
    roboflow \
    ultralytics \
    jupyterhub

# Create workspace directory
RUN mkdir -p /workspace
WORKDIR /workspace

# Set environment variable placeholder (will be overridden at runtime)
ENV ROBOFLOW_API_KEY=""

# Configure JupyterLab
ENV JUPYTER_ENABLE_LAB=yes
ENV JUPYTER_TOKEN=""
ENV NOTEBOOK_DIR=/workspace

# Expose JupyterLab port
EXPOSE 8888

# Start JupyterLab
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root", "--notebook-dir=/workspace"]
