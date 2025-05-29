Development Setup
===============

This guide helps developers set up their environment for contributing to the project.

Prerequisites
-----------

System Requirements
^^^^^^^^^^^^^^^^
- NVIDIA Jetson device or compatible hardware
- Ubuntu 20.04 or later
- Git
- Docker and Docker Compose
- Python 3.8+

Development Tools
^^^^^^^^^^^^^^
- Visual Studio Code or PyCharm
- Git client
- Docker Desktop
- NVIDIA Container Toolkit

Environment Setup
--------------

1. Clone Repository
   ::

    git clone https://github.com/yourusername/your-repo.git
    cd your-repo

2. Install Dependencies
   ::

    # System packages
    sudo apt update
    sudo apt install -y \
        python3-pip \
        python3-venv \
        docker.io \
        docker-compose

    # Python packages
    pip install -r edge/requirements-dev.txt

3. Configure Environment
   ::

    # Create .env file
    echo "ROBOFLOW_API_KEY=your_key_here" > .env

    # Set up pre-commit hooks
    pre-commit install

Development Workflow
-----------------

1. Create Feature Branch
   ::

    git checkout -b feature/your-feature-name

2. Set Up Development Environment
   ::

    # Start services
    docker compose up -d

    # Run tests
    cd edge/tests
    ./run_tests.sh

3. Make Changes
   - Write code
   - Add tests
   - Update documentation

4. Submit Changes
   ::

    # Format code
    black edge/

    # Run linters
    flake8 edge/
    mypy edge/

    # Run tests
    pytest edge/tests/

Code Style
---------

Python Guidelines
^^^^^^^^^^^^^^
- Follow PEP 8
- Use type hints
- Write docstrings

Documentation
^^^^^^^^^^^
- Update RST files
- Include examples
- Add API docs

Testing
^^^^^^
- Write unit tests
- Add integration tests
- Include benchmarks

Development Tools
--------------

IDE Setup
^^^^^^^^
1. VS Code
   - Python extension
   - Docker extension
   - Remote development

2. PyCharm
   - Professional edition
   - Docker integration
   - Remote interpreter

Debugging
^^^^^^^^
1. Local Development
   - Python debugger
   - Docker logs
   - System monitoring

2. Remote Debugging
   - Remote interpreter
   - Port forwarding
   - Log collection

Best Practices
------------

Code Quality
^^^^^^^^^^
- Write tests first
- Review changes
- Document features

Git Workflow
^^^^^^^^^^
- Small commits
- Clear messages
- Regular updates

Documentation
^^^^^^^^^^^
- Keep updated
- Include examples
- Add comments

