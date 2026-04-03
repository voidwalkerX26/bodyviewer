#!/usr/bin/env python3
"""
Simple test script to verify the VoxelFit backend works
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_imports():
    """Test that we can import our modules"""
    try:
        from app.main import app
        print("✓ Main app imports successfully")

        from app.api.routes import scan
        print("✓ Scan routes import successfully")

        from app.api.routes import scans
        print("✓ Scans routes import successfully")

        from app.ml.processing import process_scan, get_pose_landmarks
        print("✓ ML processing imports successfully")

        return True
    except Exception as e:
        print(f"✗ Import error: {e}")
        return False

def test_directories():
    """Test that required directories exist or can be created"""
    try:
        from pathlib import Path

        scans_dir = Path("./scans")
        scans_dir.mkdir(exist_ok=True)
        print(f"✓ Scans directory ready: {scans_dir.absolute()}")

        return True
    except Exception as e:
        print(f"✗ Directory error: {e}")
        return False

if __name__ == "__main__":
    print("Testing VoxelFit backend setup...\n")

    success = True
    success &= test_imports()
    success &= test_directories()

    print("\n" + "="*50)
    if success:
        print("✓ All tests passed! Backend is ready to run.")
        print("\nTo start the backend:")
        print("  cd backend")
        print("  uvicorn app.main:app --reload")
        print("\nThen visit: http://localhost:8000/health")
    else:
        print("✗ Some tests failed. Please check the errors above.")
        sys.exit(1)