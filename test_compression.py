"""
Test script to verify image compression functionality.
This script tests the compress_image utility function.
"""

import os
import sys
import django

# Setup Django environment
sys.path.insert(0, '/home/banda/Desktop/pasport')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AbonentDataset.settings')
django.setup()

from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
import io

# Import the compression function
from abonents.utils import compress_image

def create_test_image(width=2000, height=2000, quality=95):
    """Create a test image of specified size."""
    img = Image.new('RGB', (width, height), color='red')
    
    # Add some variation to make it more realistic
    from PIL import ImageDraw
    draw = ImageDraw.Draw(img)
    for i in range(0, width, 20):
        draw.line([(i, 0), (i, height)], fill='blue', width=2)
    for i in range(0, height, 20):
        draw.line([(0, i), (width, i)], fill='green', width=2)
    
    # Save to bytes
    img_io = io.BytesIO()
    img.save(img_io, format='JPEG', quality=quality)
    img_io.seek(0)
    
    return img_io

def test_compression():
    """Test image compression."""
    print("=" * 60)
    print("Testing Image Compression to 520KB")
    print("=" * 60)
    
    # Create a large test image
    print("\n1. Creating test image (2000x2000, high quality)...")
    test_image_bytes = create_test_image(2000, 2000, 95)
    original_size = len(test_image_bytes.getvalue())
    print(f"   Original size: {original_size / 1024:.2f} KB")
    
    # Create uploaded file
    test_image_bytes.seek(0)
    uploaded_file = SimpleUploadedFile(
        "test_image.jpg",
        test_image_bytes.read(),
        content_type="image/jpeg"
    )
    
    # Compress the image
    print("\n2. Compressing image to 520KB...")
    compressed_file = compress_image(uploaded_file, max_size_kb=520)
    
    # Check compressed size
    compressed_file.seek(0)
    compressed_data = compressed_file.read()
    compressed_size = len(compressed_data)
    print(f"   Compressed size: {compressed_size / 1024:.2f} KB")
    
    # Calculate reduction
    reduction = ((original_size - compressed_size) / original_size) * 100
    print(f"   Size reduction: {reduction:.1f}%")
    
    # Verify size is under 520KB
    max_size = 520 * 1024
    if compressed_size <= max_size:
        print(f"\n✓ SUCCESS: Image compressed to {compressed_size / 1024:.2f} KB (under 520KB limit)")
    else:
        print(f"\n✗ FAILED: Image size {compressed_size / 1024:.2f} KB exceeds 520KB limit")
    
    # Test with different image sizes
    print("\n" + "=" * 60)
    print("Testing with various image sizes")
    print("=" * 60)
    
    test_cases = [
        (1000, 1000, "Small image (1000x1000)"),
        (3000, 3000, "Large image (3000x3000)"),
        (4000, 3000, "Very large image (4000x3000)"),
    ]
    
    for width, height, description in test_cases:
        print(f"\n{description}:")
        test_img = create_test_image(width, height, 95)
        orig_size = len(test_img.getvalue())
        print(f"  Original: {orig_size / 1024:.2f} KB")
        
        test_img.seek(0)
        uploaded = SimpleUploadedFile(
            f"test_{width}x{height}.jpg",
            test_img.read(),
            content_type="image/jpeg"
        )
        
        compressed = compress_image(uploaded, max_size_kb=520)
        compressed.seek(0)
        comp_size = len(compressed.read())
        print(f"  Compressed: {comp_size / 1024:.2f} KB")
        
        if comp_size <= 520 * 1024:
            print(f"  ✓ Under 520KB limit")
        else:
            print(f"  ✗ Over 520KB limit")
    
    print("\n" + "=" * 60)
    print("Compression test completed!")
    print("=" * 60)

if __name__ == "__main__":
    test_compression()
