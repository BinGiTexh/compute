Testing Guide
============

This guide covers testing procedures and practices for the video processing pipeline.

Testing Framework
---------------

Overview
^^^^^^^^
The project uses multiple testing levels:

1. Unit Tests
   - Individual component testing
   - Mock external dependencies
   - Quick feedback loop

2. Integration Tests
   - Component interaction testing
   - Docker container testing
   - System integration

3. System Tests
   - End-to-end testing
   - Performance testing
   - Resource monitoring

Test Organization
--------------

Directory Structure
^^^^^^^^^^^^^^^^
::

    tests/
    ├── unit/              # Unit tests
    │   ├── test_video.py
    │   ├── test_model.py
    │   └── test_export.py
    ├── integration/       # Integration tests
    │   ├── test_pipeline.py
    │   └── test_api.py
    ├── system/            # System tests
    │   ├── test_e2e.py
    │   └── test_performance.py
    └── data/              # Test data
        ├── videos/
        └── models/

Running Tests
-----------

Local Testing
^^^^^^^^^^^
1. Unit Tests::

    pytest tests/unit/

2. Integration Tests::

    pytest tests/integration/

3. System Tests::

    pytest tests/system/

4. All Tests::

    ./run_tests.sh

CI/CD Testing
^^^^^^^^^^^
Tests are automatically run in GitHub Actions:

1. On Pull Requests
2. On Main Branch
3. Nightly Tests

Writing Tests
-----------

Unit Tests
^^^^^^^^^
Example unit test::

    def test_video_processor():
        processor = VideoProcessor(config)
        frame = create_test_frame()
        result = processor.process_frame(frame)
        assert result['detections'] >= 0
        assert 'timestamp' in result

Integration Tests
^^^^^^^^^^^^^^
Example integration test::

    def test_pipeline_flow():
        # Start services
        docker_compose_up()
        
        # Process test video
        result = process_test_video()
        
        # Verify results
        assert result['status'] == 'success'
        assert len(result['frames']) > 0

System Tests
^^^^^^^^^^
Example system test::

    def test_end_to_end():
        # Full pipeline test
        pipeline = Pipeline(config)
        pipeline.process_video('test.mp4')
        
        # Check outputs
        assert os.path.exists('output/results.json')
        assert os.path.exists('output/metrics.csv')

Test Data
---------

Sample Data
^^^^^^^^^^
1. Test Videos
   - Short clips
   - Various formats
   - Different scenarios

2. Model Weights
   - Small test models
   - Mock weights
   - Test configurations

3. Expected Results
   - JSON templates
   - CSV examples
   - Performance baselines

Mocking
------

External Services
^^^^^^^^^^^^^^
Example mock setup::

    @pytest.fixture
    def mock_inference_server():
        with patch('inference_sdk.Client') as mock:
            mock.predict.return_value = {
                'predictions': [
                    {'class': 'fish', 'confidence': 0.9}
                ]
            }
            yield mock

Test Configuration
---------------

pytest Configuration
^^^^^^^^^^^^^^^^
File: pytest.ini::

    [pytest]
    testpaths = tests
    python_files = test_*.py
    markers =
        unit: Unit tests
        integration: Integration tests
        system: System tests

Coverage Configuration
^^^^^^^^^^^^^^^^^^
File: .coveragerc::

    [run]
    source = edge
    omit = tests/*,*/__init__.py

Performance Testing
----------------

Metrics
^^^^^^
1. Processing Speed
   - Frames per second
   - Processing latency
   - Total duration

2. Resource Usage
   - CPU utilization
   - Memory consumption
   - GPU usage

3. Accuracy
   - Detection accuracy
   - False positives
   - Miss rate

Benchmarking
^^^^^^^^^^
Example benchmark test::

    def test_performance():
        start_time = time.time()
        stats = process_benchmark_video()
        duration = time.time() - start_time
        
        assert stats['fps'] >= 25.0
        assert stats['memory_mb'] <= 2048
        assert duration <= 60.0

Continuous Integration
-------------------

GitHub Actions
^^^^^^^^^^^^
1. Test Workflow::

    name: Tests
    on: [push, pull_request]
    jobs:
      test:
        runs-on: ubuntu-latest
        steps:
          - uses: actions/checkout@v2
          - name: Run tests
            run: ./run_tests.sh

2. Coverage Reports
   - Generated after tests
   - Posted to pull requests
   - Stored as artifacts

