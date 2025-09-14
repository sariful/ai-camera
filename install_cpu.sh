#!/bin/bash
# Install CPU-only PyTorch libraries for AI Camera without GPU

echo "🔧 Installing AI Camera dependencies (CPU-only)..."

# Uninstall any existing GPU versions
echo "🗑️  Removing any existing GPU versions..."
pip uninstall -y torch torchvision torchaudio

# Install CPU-only PyTorch first
echo "🔄 Installing CPU-only PyTorch..."
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Install other requirements
echo "📦 Installing other dependencies..."
pip install opencv-python>=4.5.0
pip install numpy>=1.19.0
pip install python-dotenv>=0.19.0
pip install ultralytics>=8.0.0
pip install pillow>=8.3.0

echo "✅ Installation complete! Your AI Camera is now configured for CPU-only operation."
echo "ℹ️  Note: Performance will be slower than with GPU, but it will work on any system."