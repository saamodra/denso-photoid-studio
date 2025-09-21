#!/usr/bin/env python3
"""
Simple camera test script to debug camera detection issues
"""
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.camera_manager import CameraManager

def main():
    print("Camera Detection Test")
    print("====================")

    try:
        camera_manager = CameraManager()
        print(f"Camera manager initialized")

        # Run debug detection
        camera_manager.debug_camera_detection()

        # Get cameras
        cameras = camera_manager.get_available_cameras()

        if cameras:
            print(f"\n✅ SUCCESS: Found {len(cameras)} camera(s)")
            for i, cam in enumerate(cameras):
                print(f"  {i}: {cam['name']} - {cam['resolution']}")
        else:
            print(f"\n❌ FAILED: No cameras detected")
            print("\nTroubleshooting tips:")
            print("1. Make sure a camera is connected")
            print("2. Check if camera is being used by another application")
            print("3. Try disconnecting and reconnecting the camera")
            print("4. On macOS, check System Preferences > Security & Privacy > Camera")

    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
