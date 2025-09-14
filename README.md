# AI Camera System

A multi-camera RTSP streaming application with synchronized display and automatic reconnection capabilities.

## Project Structure

```
ai-camera/
├── main.py              # Main application entry point
├── config.py            # Configuration and constants
├── camera_thread.py     # Camera stream management with threading
├── display_manager.py   # Frame processing and display logic
├── utils.py             # Common utilities and helper functions
├── camera.py            # Original monolithic file (backup)
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Features

- **Multi-camera support**: Simultaneously display up to 3 RTSP camera streams
- **Real-time synchronization**: Frame synchronization monitoring and display
- **Automatic reconnection**: Robust error handling with automatic stream reconnection
- **Threaded architecture**: Each camera runs in its own thread for optimal performance
- **Configurable settings**: Easy configuration management through `config.py`
- **Clean shutdown**: Graceful cleanup of all resources

## Modules Overview

### `main.py`
- Application entry point
- Coordinates all modules
- Handles main display loop and cleanup

### `config.py`
- RTSP URLs configuration
- Camera settings (FPS, resolution, buffer size)
- Display settings and constants
- Text overlay settings

### `camera_thread.py`
- `CameraThread` class for individual camera management
- Threading implementation for concurrent stream processing
- Automatic reconnection logic
- Frame capture and resizing

### `display_manager.py`
- `DisplayManager` class for frame processing and display
- Multi-camera frame synchronization
- Combined frame display with overlay information
- Placeholder frames for disconnected cameras

### `utils.py`
- Helper functions for camera initialization
- Status reporting and logging utilities
- Application statistics and monitoring
- Time formatting utilities

## Installation

1. Install required dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables for camera credentials:
```bash
# Copy the example environment file
cp .env.example .env

# Edit the .env file with your actual camera credentials
nano .env  # or use your preferred editor
```

3. Configure your `.env` file with your camera details:
```bash
# RTSP Camera Credentials
RTSP_USERNAME=admin
RTSP_PASSWORD=your_actual_password_here

# RTSP Camera Network Settings  
RTSP_HOST=192.168.0.103
RTSP_PORT=554
```

**Important Security Notes:**
- Never commit `.env` files to version control
- The `.env` file is already included in `.gitignore`
- Use strong, unique passwords for your cameras
- Consider changing default camera passwords

## Usage

Run the application:
```bash
python main.py
```

### Controls
- **'q'**: Quit the application
- **Ctrl+C**: Force shutdown

### Configuration

Edit `config.py` to customize:
- **RTSP URLs**: Update with your camera credentials and addresses
- **Camera settings**: Adjust FPS, resolution, buffer size
- **Display settings**: Modify sync thresholds and window title
- **Reconnection behavior**: Set retry attempts and delays

## Troubleshooting

### Common Issues

1. **Import errors for cv2/numpy**: Install OpenCV and NumPy
```bash
pip install opencv-python numpy
```

2. **Camera connection failures**: 
   - Verify RTSP URLs and credentials
   - Check network connectivity
   - Ensure cameras support the specified resolution/FPS

3. **Performance issues**:
   - Reduce target FPS in configuration
   - Lower frame resolution
   - Check system resources

### Debug Information

The application provides detailed logging:
- Camera connection status
- Reconnection attempts
- Frame synchronization warnings
- Final statistics on shutdown

## Development

### Adding New Features

1. **New camera types**: Extend `CameraThread` class
2. **Additional overlays**: Modify `DisplayManager.add_overlay_info()`
3. **Configuration options**: Add to `config.py` and update relevant modules
4. **Monitoring features**: Extend `utils.py` with new statistics functions

### Code Organization

- Keep configuration in `config.py`
- Add new utilities to `utils.py`
- Camera-specific logic goes in `camera_thread.py`
- Display-related features belong in `display_manager.py`
- Coordinate everything through `main.py`

## License

This project is provided as-is for educational and development purposes.