Installation
============

Prerequisites
------------

Hardware Requirements
^^^^^^^^^^^^^^^^^^^
* NVIDIA Jetson device (or compatible hardware)
* Minimum 4GB RAM
* 20GB available storage
* USB camera or video files for processing

Software Requirements
^^^^^^^^^^^^^^^^^^^
* Ubuntu 20.04 or later
* NVIDIA JetPack 5.0 or later
* Docker and Docker Compose
* NVIDIA Container Runtime
* Python 3.8+
* Git

Step-by-Step Installation
------------------------

1. System Preparation
^^^^^^^^^^^^^^^^^^^
First, ensure your system is up to date::

    sudo apt update
    sudo apt upgrade -y

Install required system packages::

    sudo apt install -y \
        git \
        python3-pip \
        docker.io \
        docker-compose

2. Install NVIDIA Container Runtime
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Follow these steps to install the NVIDIA Container Runtime::

    distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
    curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
    curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
    sudo apt update
    sudo apt install -y nvidia-container-runtime

3. Clone Repository
^^^^^^^^^^^^^^^^
Clone the project repository::

    git clone https://github.com/yourusername/your-repo.git
    cd your-repo

4. Set Up Environment
^^^^^^^^^^^^^^^^^^
Create a .env file with your configuration::

    echo "ROBOFLOW_API_KEY=your_key_here" > .env

5. Run Setup Script
^^^^^^^^^^^^^^^^
Execute the setup script::

    cd edge
    ./setup.sh

The setup script will:
* Build Docker images
* Download required models
* Create test data
* Start required services

Verifying Installation
--------------------

1. Check Services
^^^^^^^^^^^^^^
Verify that all services are running::

    docker compose ps

You should see both the inference server and JupyterLab containers running.

2. Run System Tests
^^^^^^^^^^^^^^^^
Execute the test suite::

    cd tests
    ./run_tests.sh

3. Access JupyterLab
^^^^^^^^^^^^^^^^^
Open a web browser and navigate to::

    http://localhost:8888

Troubleshooting
--------------

Common Issues
^^^^^^^^^^^

1. Docker Permission Issues::

    sudo usermod -aG docker $USER
    # Log out and back in for changes to take effect

2. NVIDIA Runtime Issues::

    # Check NVIDIA runtime installation
    sudo systemctl status nvidia-container-runtime
    # If not running:
    sudo systemctl start nvidia-container-runtime

3. Port Conflicts::

    # Check if ports are in use
    sudo netstat -tulpn | grep -E '8888|9001'
    # Stop conflicting services or modify port configuration

Getting Help
-----------
If you encounter issues not covered here:

1. Check the project's GitHub Issues
2. Join our Discord community
3. Contact support at support@example.com

