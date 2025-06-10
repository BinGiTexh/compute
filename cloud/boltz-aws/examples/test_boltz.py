#!/usr/bin/env python3
"""
Simple test script for Boltz to verify the installation is working correctly.
"""

import os
import sys
import time
import argparse

def test_boltz_import():
    """Test importing the Boltz package"""
    print("Testing Boltz import...")
    try:
        import boltz
        print(f"✅ Successfully imported Boltz version: {boltz.__version__}")
        return True
    except ImportError as e:
        print(f"❌ Failed to import Boltz: {e}")
        return False

def test_gpu_availability():
    """Test if PyTorch can access the GPU"""
    print("\nTesting GPU availability...")
    try:
        import torch
        if torch.cuda.is_available():
            device_count = torch.cuda.device_count()
            device_name = torch.cuda.get_device_name(0) if device_count > 0 else "N/A"
            print(f"✅ GPU is available: {device_count} device(s) detected")
            print(f"   Device name: {device_name}")
            print(f"   CUDA version: {torch.version.cuda}")
            return True
        else:
            print("❌ GPU is not available. Boltz will run in CPU mode (slower).")
            return False
    except Exception as e:
        print(f"❌ Error checking GPU: {e}")
        return False

def test_simple_prediction():
    """Test a simple prediction with Boltz if possible"""
    print("\nTesting simple Boltz functionality...")
    try:
        import boltz
        
        # Check if we can access the model class
        print("Checking model availability...")
        if hasattr(boltz, 'predict'):
            print("✅ Boltz prediction functionality is available")
            
            # Note: We don't actually run a prediction here as it would require input files
            # and could be resource-intensive. This just verifies the API is accessible.
            print("ℹ️ To run an actual prediction, use the example below")
            return True
        else:
            print("❓ Boltz prediction API structure is different than expected")
            print("ℹ️ Please refer to the Boltz documentation for usage examples")
            return False
    except Exception as e:
        print(f"❌ Error testing Boltz functionality: {e}")
        return False

def print_usage_example():
    """Print an example of how to use Boltz"""
    print("\n" + "="*60)
    print("EXAMPLE USAGE:")
    print("="*60)
    print("""
# Create a YAML input file for Boltz
cat > input.yaml << EOF
molecules:
  - name: protein
    sequence: MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG
  - name: ligand
    sequence: PEPTIDE
properties:
  - type: structure
  - type: affinity
EOF

# Run Boltz prediction
boltz predict input.yaml
""")
    print("="*60)

def main():
    """Main test function"""
    print("="*60)
    print("BOLTZ CONTAINER TEST")
    print("="*60)
    
    # Run tests
    import_success = test_boltz_import()
    gpu_success = test_gpu_availability()
    func_success = test_simple_prediction() if import_success else False
    
    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY:")
    print("="*60)
    print(f"Boltz Import: {'✅ PASS' if import_success else '❌ FAIL'}")
    print(f"GPU Available: {'✅ PASS' if gpu_success else '❌ FAIL'}")
    print(f"Functionality Check: {'✅ PASS' if func_success else '❌ FAIL'}")
    print("="*60)
    
    # Print usage example
    print_usage_example()
    
    # Return success status
    return 0 if import_success else 1

if __name__ == "__main__":
    sys.exit(main())

