#!/usr/bin/env python3
"""
Main Application File for AI Camera System

Coordinates all modules and handles the main application loop for synchronized multi-camera display.
"""

import time
from config import RTSP_URLS
from camera_thread import CameraThread
from display_manager import DisplayManager
from utils import (
    initialize_cameras, 
    start_all_cameras, 
    stop_all_cameras, 
    log_application_start, 
    log_application_end,
    get_application_stats
)


def main():
    """
    Main application entry point.
    
    Initializes cameras, starts display loop, and handles cleanup.
    """
    start_time = time.time()
    
    # Log startup information
    log_application_start(RTSP_URLS)
    
    # Initialize components
    camera_threads = initialize_cameras(RTSP_URLS)
    display_manager = DisplayManager()
    
    try:
        # Start all cameras
        start_all_cameras(camera_threads)
        
        # Main display loop
        print("🎬 Starting main display loop...")
        while True:
            # Process one frame cycle
            if not display_manager.process_frame_cycle(camera_threads):
                break  # User pressed 'q' to quit
                
    except KeyboardInterrupt:
        print("\n⚠️ Received interrupt signal...")
        
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        
    finally:
        # Clean shutdown
        display_manager.cleanup()
        stop_all_cameras(camera_threads)
        
        # Show final statistics
        stats = get_application_stats(camera_threads)
        print(f"\n📊 Final Statistics:")
        print(f"   Connected cameras: {stats['connected_cameras']}/{stats['total_cameras']}")
        print(f"   Connection rate: {stats['connection_rate']:.1%}")
        
        # Log application end
        log_application_end(start_time)


if __name__ == "__main__":
    main()