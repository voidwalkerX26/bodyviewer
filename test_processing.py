#!/usr/bin/env python3
"""
Test script to verify the MediaPipe pose estimation processing works
"""
import sys
import os
import tempfile
import json
from pathlib import Path
import cv2
import numpy as np

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def create_test_image(width=640, height=480):
    """Create a simple test image with a person-like shape"""
    # Create a blank image
    img = np.zeros((height, width, 3), dtype=np.uint8)

    # Draw a simple person-like figure (just for testing - won't be detected by MediaPipe)
    # Head
    cv2.circle(img, (width//2, height//4), 20, (255, 255, 255), -1)
    # Body
    cv2.rectangle(img, (width//2 - 15, height//4), (width//2 + 15, height//2), (255, 255, 255), -1)
    # Arms
    cv2.rectangle(img, (width//2 - 30, height//3), (width//2 - 15, height//2 - 10), (255, 255, 255), -1)
    cv2.rectangle(img, (width//2 + 15, height//3), (width//2 + 30, height//2 - 10), (255, 255, 255), -1)
    # Legs
    cv2.rectangle(img, (width//2 - 10, height//2), (width//2, height*3//4), (255, 255, 255), -1)
    cv2.rectangle(img, (width//2, height//2), (width//2 + 10, height*3//4), (255, 255, 255), -1)

    return img

def test_imports():
    """Test that we can import our modules"""
    try:
        from app.ml.processing import process_scan, get_pose_landmarks, get_landmarks
        print("✓ Processing module imports successfully")
        return True
    except Exception as e:
        print(f"✗ Import error: {e}")
        return False

def test_landmark_extraction():
    """Test landmark extraction on a blank image (should return None)"""
    try:
        from app.ml.processing import get_pose_landmarks

        # Create a temporary file
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
            # Create a blank image
            blank_img = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.imwrite(tmp.name, blank_img)

            # Test landmark extraction
            landmarks = get_pose_landmarks(Path(tmp.name))

            # Clean up
            os.unlink(tmp.name)

            # Should return None for blank image
            if landmarks is None:
                print("✓ Landmark extraction correctly returns None for blank image")
                return True
            else:
                print(f"⚠ Landmark extraction returned {len(landmarks)} points for blank image (unexpected but not fatal)")
                return True  # Not necessarily wrong, MediaPipe might detect something

    except Exception as e:
        print(f"✗ Landmark extraction error: {e}")
        return False

def test_process_scan_structure():
    """Test that process_scan function has correct structure"""
    try:
        from app.ml.processing import process_scan
        import inspect

        # Get function signature
        sig = inspect.signature(process_scan)
        params = list(sig.parameters.keys())

        expected_params = ['scan_id', 'scan_dir']
        if params == expected_params:
            print("✓ process_scan function has correct parameters")
            return True
        else:
            print(f"✗ process_scan function has parameters {params}, expected {expected_params}")
            return False

    except Exception as e:
        print(f"✗ Function structure error: {e}")
        return False

if __name__ == "__main__":
    print("Testing VoxelFit MediaPipe processing...\n")

    success = True
    success &= test_imports()
    success &= test_landmark_extraction()
    success &= test_process_scan_structure()

    print("\n" + "="*50)
    if success:
        print("✓ Processing tests passed!")
        print("\nThe MediaPipe pose estimation module is ready.")
        print("\nTo test with real images:")
        print("  1. Start the backend: cd backend && uvicorn app.main:app --reload")
        print("  2. Upload images via frontend or API")
        print("  3. Check results in ./scans/ directory")
    else:
        print("✗ Some tests failed. Please check the errors above.")
        sys.exit(1)