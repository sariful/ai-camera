"""
Utilities Module for AI Camera System

Common helper functions and utilities used across the application.
"""

import time
from typing import List
from camera_thread import CameraThread


def initialize_cameras(urls: List[str]) -> List[CameraThread]:
    """
    Initialize camera threads for all provided URLs.
    
    Args:
        urls (List[str]): List of RTSP URLs
        
    Returns:
        List[CameraThread]: List of initialized camera thread objects
    """
    camera_threads = []
    for i, url in enumerate(urls):
        cam_thread = CameraThread(url, i)
        camera_threads.append(cam_thread)
    return camera_threads


def start_all_cameras(camera_threads: List[CameraThread]) -> None:
    """
    Start all camera threads and report status.
    
    Args:
        camera_threads (List[CameraThread]): List of camera thread objects
    """
    for cam_thread in camera_threads:
        if cam_thread.start():
            print(f"✅ Camera {cam_thread.camera_id + 1} started successfully")
        else:
            print(f"❌ Failed to start Camera {cam_thread.camera_id + 1}")


def stop_all_cameras(camera_threads: List[CameraThread]) -> None:
    """
    Stop all camera threads safely.
    
    Args:
        camera_threads (List[CameraThread]): List of camera thread objects
    """
    print("\n🛑 Stopping cameras...")
    for cam_thread in camera_threads:
        cam_thread.stop()
    print("✅ All cameras stopped successfully")


def print_camera_status(camera_threads: List[CameraThread]) -> None:
    """
    Print status information for all cameras.
    
    Args:
        camera_threads (List[CameraThread]): List of camera thread objects
    """
    print("\n📊 Camera Status:")
    print("-" * 50)
    for cam_thread in camera_threads:
        info = cam_thread.get_camera_info()
        status = "🟢 Connected" if info["connected"] else "🔴 Disconnected"
        print(f"Camera {info['id'] + 1}: {status}")
        if info["reconnect_attempts"] > 0:
            print(f"  Reconnect attempts: {info['reconnect_attempts']}")
        if info["last_frame_time"] > 0:
            age = time.time() - info["last_frame_time"]
            print(f"  Last frame: {age:.1f}s ago")
    print("-" * 50)


def get_application_stats(camera_threads: List[CameraThread]) -> dict:
    """
    Get application statistics.
    
    Args:
        camera_threads (List[CameraThread]): List of camera thread objects
        
    Returns:
        dict: Application statistics
    """
    total_cameras = len(camera_threads)
    connected_cameras = sum(1 for cam in camera_threads if cam.is_connected())
    
    return {
        "total_cameras": total_cameras,
        "connected_cameras": connected_cameras,
        "disconnected_cameras": total_cameras - connected_cameras,
        "connection_rate": connected_cameras / total_cameras if total_cameras > 0 else 0
    }


def format_time_elapsed(start_time: float) -> str:
    """
    Format elapsed time in human-readable format.
    
    Args:
        start_time (float): Start timestamp
        
    Returns:
        str: Formatted elapsed time
    """
    elapsed = time.time() - start_time
    hours = int(elapsed // 3600)
    minutes = int((elapsed % 3600) // 60)
    seconds = int(elapsed % 60)
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    else:
        return f"{minutes:02d}:{seconds:02d}"


def log_application_start(urls: List[str]) -> None:
    """
    Log application startup information.
    
    Args:
        urls (List[str]): List of RTSP URLs being used
    """
    print("🎥 AI Camera System Starting...")
    print(f"📡 Configured {len(urls)} camera streams")
    print("🎯 Target: Real-time synchronized display")
    print("⌨️  Press 'q' to quit")
    print("=" * 60)


def log_application_end(start_time: float) -> None:
    """
    Log application shutdown information.
    
    Args:
        start_time (float): Application start timestamp
    """
    runtime = format_time_elapsed(start_time)
    print("=" * 60)
    print(f"📊 Session completed. Runtime: {runtime}")
    print("👋 Thank you for using AI Camera System!")