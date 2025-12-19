#!/usr/bin/env python3
"""Test video generation without GUI"""
import sys
import os
sys.path.insert(0, '/Users/polo/Code/Repo/Cartoonizer/source')

from PIL import Image
import numpy as np

# Create a simple test image
print("Creating test image...")
test_img = Image.new('RGB', (256, 256), color='blue')
# Add a simple pattern
pixels = np.array(test_img)
for i in range(256):
    for j in range(256):
        pixels[i, j] = [100 + i % 155, 100 + j % 155, 200]
test_img = Image.fromarray(pixels.astype('uint8'))

# Import the infer_video function
print("Importing cartoonizer...")
from cartoonizer import infer_video

# Test video generation
print("\nTesting video generation...")
print("=" * 50)
try:
    video_path, status_msg = infer_video(test_img, duration=2)
    print(f"Status: {status_msg}")
    print(f"Video path: {video_path}")
    
    if video_path and os.path.exists(video_path):
        size = os.path.getsize(video_path)
        print(f"✓ Video file created successfully: {size} bytes")
    else:
        print("✗ Video file was not created")
except Exception as e:
    print(f"✗ Error: {str(e)}")
    import traceback
    traceback.print_exc()

print("=" * 50)
