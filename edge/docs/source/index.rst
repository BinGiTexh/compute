Marine Science Video Processing Pipeline
=====================================

A modular video processing pipeline for marine science applications, optimized for edge computing on Jetson devices.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   user_guide/index
   developer_guide/index
   api/index
   examples/index

Features
--------
* Real-time object detection using Roboflow models
* System resource monitoring and performance analysis
* Automated batch processing via GitHub Actions
* Interactive analysis through JupyterLab
* Comprehensive result export (JSON, CSV)
* Docker-based deployment

Quick Start
-----------
1. Clone the repository::

    git clone https://github.com/yourusername/your-repo.git
    cd your-repo

2. Set up your Roboflow API key::

    export ROBOFLOW_API_KEY=your_key_here

3. Run the setup script::

    cd edge
    ./setup.sh

4. Access JupyterLab at http://localhost:8888

Indices and tables
==================
* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
