"""
Utility functions for image processing.
"""

import io
from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile


def compress_image(image_field, max_size_kb=520):
    """
    Compress an image to a maximum file size while maintaining aspect ratio.
    
    Args:
        image_field: Django ImageField or UploadedFile
        max_size_kb: Maximum file size in kilobytes (default: 520KB)
    
    Returns:
        InMemoryUploadedFile: Compressed image file
    """
    if not image_field:
        return image_field
    
    # Maximum size in bytes
    max_size_bytes = max_size_kb * 1024
    
    # Open the image
    try:
        img = Image.open(image_field)
    except Exception:
        # If we can't open it, return original
        return image_field
    
    # Convert RGBA to RGB (for PNG with transparency)
    if img.mode in ('RGBA', 'LA', 'P'):
        background = Image.new('RGB', img.size, (255, 255, 255))
        if img.mode == 'P':
            img = img.convert('RGBA')
        background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
        img = background
    elif img.mode != 'RGB':
        img = img.convert('RGB')
    
    # Get original format
    original_format = image_field.name.split('.')[-1].upper()
    if original_format == 'JPG':
        original_format = 'JPEG'
    
    # Always use JPEG for better compression
    output_format = 'JPEG'
    extension = 'jpg'
    
    # Start with high quality
    quality = 95
    output = io.BytesIO()
    
    # Compress with progressively lower quality until size is acceptable
    while quality > 20:
        output.seek(0)
        output.truncate()
        
        # Save with current quality
        img.save(
            output,
            format=output_format,
            quality=quality,
            optimize=True,
            progressive=True
        )
        
        # Check size
        size = output.tell()
        
        if size <= max_size_bytes:
            break
        
        # Reduce quality for next iteration
        quality -= 5
    
    # If still too large, resize the image
    if output.tell() > max_size_bytes:
        # Calculate new dimensions (reduce by 10% each iteration)
        scale_factor = 0.9
        while output.tell() > max_size_bytes and scale_factor > 0.3:
            output.seek(0)
            output.truncate()
            
            new_width = int(img.width * scale_factor)
            new_height = int(img.height * scale_factor)
            resized_img = img.resize((new_width, new_height), Image.LANCZOS)
            
            resized_img.save(
                output,
                format=output_format,
                quality=quality,
                optimize=True,
                progressive=True
            )
            
            scale_factor -= 0.1
    
    output.seek(0)
    
    # Get the original filename without extension
    original_name = image_field.name.rsplit('.', 1)[0]
    new_filename = f"{original_name.split('/')[-1]}.{extension}"
    
    # Create a new InMemoryUploadedFile
    compressed_image = InMemoryUploadedFile(
        output,
        'ImageField',
        new_filename,
        f'image/{extension}',
        output.tell(),
        None
    )
    
    return compressed_image
