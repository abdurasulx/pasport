"""
Utility functions for image processing.
"""

import io
import logging
import os
from PIL import Image, ImageOps
from django.core.files.uploadedfile import InMemoryUploadedFile
import numpy as np

logger = logging.getLogger(__name__)


def simple_compress_image(image_field, max_size_kb=520):
    """
    Simple image compression with proper orientation handling.
    
    This function:
    - Applies EXIF orientation (rasmni to'g'ri yo'nalishga keltiradi)
    - Removes EXIF data after applying orientation
    - Preserves aspect ratio (no cropping)
    - Reduces quality/resolution to fit under max_size_kb
    - Keeps the original filename
    
    Args:
        image_field: Django ImageField or UploadedFile
        max_size_kb: Maximum file size in kilobytes (default: 520KB)
    
    Returns:
        InMemoryUploadedFile: Compressed image file
    """
    if not image_field:
        return image_field
    
    max_size_bytes = max_size_kb * 1024
    
    # If already small enough, check if rotation is needed
    try:
        image_field.seek(0)
        temp_img = Image.open(image_field)
        needs_rotation = hasattr(temp_img, '_getexif') and temp_img._getexif() is not None
        
        if image_field.size <= max_size_bytes and not needs_rotation:
            image_field.seek(0)
            return image_field
    except Exception:
        pass
    
    # Open image and apply EXIF orientation
    try:
        image_field.seek(0)
        img = Image.open(image_field)
        
        # KRITIK: EXIF orientation ni qo'llash
        # Bu telefon kamerasidan olingan rasmlarni to'g'ri yo'nalishga keltiradi
        img = ImageOps.exif_transpose(img)
        
        if img is None:
            image_field.seek(0)
            img = Image.open(image_field)
            
    except Exception as e:
        logger.error(f"Failed to open image: {e}")
        return image_field
    
    # RGB normalize
    if img.mode != "RGB":
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
            img = background
        else:
            img = img.convert("RGB")
    
    img = img.copy()  # Clean buffer
    
    output = io.BytesIO()
    
    # Step 1: Compress with quality reduction only
    quality = 90
    while quality >= 40:
        output.seek(0)
        output.truncate()
        
        img.save(
            output,
            "JPEG",
            quality=quality,
            optimize=True,
            exif=b''  # EXIF ni olib tashlash (orientation allaqachon qo'llanilgan)
        )
        
        if output.tell() <= max_size_bytes:
            break
        
        quality -= 5
    
    # Step 2: If still too large, resize
    if output.tell() > max_size_bytes:
        width, height = img.size
        scale = 0.9
        
        while scale >= 0.4:
            output.seek(0)
            output.truncate()
            
            new_size = (
                int(width * scale),
                int(height * scale)
            )
            
            resized = img.resize(new_size, Image.Resampling.LANCZOS)
            resized = resized.copy()
            
            resized.save(
                output,
                "JPEG",
                quality=max(quality, 75),
                optimize=True,
                exif=b''
            )
            
            if output.tell() <= max_size_bytes:
                break
            
            scale -= 0.1
    
    output.seek(0)
    
    # Preserve filename
    name = image_field.name.rsplit("/", 1)[-1]
    if not name.lower().endswith((".jpg", ".jpeg")):
        name = name.rsplit(".", 1)[0] + ".jpg"
    
    return InMemoryUploadedFile(
        output,
        "ImageField",
        name,
        "image/jpeg",
        output.tell(),
        None
    )


def compress_jpeg_no_rotation(input_path, output_path, max_size_kb=520):
    """
    Compress JPEG WITH proper orientation handling.
    
    Args:
        input_path: Path to input image
        output_path: Path to output image
        max_size_kb: Max size in KB
    
    Returns:
        bool: Success
    """
    import subprocess
    import shutil
    
    max_size_bytes = max_size_kb * 1024
    
    # Check if ImageMagick is available
    imagemagick_available = shutil.which('convert') is not None
    
    logger.info(f"ImageMagick check: available={imagemagick_available}")
    
    if imagemagick_available:
        try:
            return _compress_with_imagemagick(input_path, output_path, max_size_kb)
        except Exception as e:
            logger.warning(f"ImageMagick compression failed: {e}, falling back to PIL")
    
    # Fallback to PIL method
    logger.info("Using PIL for compression")
    return _compress_with_pil_fallback(input_path, output_path, max_size_kb)


def _compress_with_imagemagick(input_path, output_path, max_size_kb=520):
    """ImageMagick compression with auto-orient."""
    import subprocess
    
    max_size_bytes = max_size_kb * 1024
    
    # Step 1: Apply orientation and remove EXIF
    quality = 90
    while quality >= 40:
        cmd = [
            'convert',
            input_path,
            '-auto-orient',  # EXIF orientation ni qo'llash
            '-strip',  # Keyin EXIF ni olib tashlash
            '-quality', str(quality),
            output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.error(f"Convert error: {result.stderr}")
            return False
        
        file_size = os.path.getsize(output_path)
        
        if file_size <= max_size_bytes:
            logger.info(f"Compressed: {file_size / 1024:.2f}KB (quality={quality})")
            return True
        
        quality -= 10
    
    # If still too large, resize
    logger.info(f"Quality reduction insufficient, resizing image...")
    
    scale = 0.9
    while scale >= 0.3:
        cmd = [
            'convert',
            input_path,
            '-auto-orient',
            '-resize', f'{int(scale * 100)}%',
            '-strip',
            '-quality', '75',
            output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.error(f"Resize error: {result.stderr}")
            break
        
        file_size = os.path.getsize(output_path)
        
        if file_size <= max_size_bytes:
            logger.info(f"Compressed after resize: {file_size / 1024:.2f}KB (scale={scale:.0%})")
            return True
        
        scale -= 0.1
    
    logger.warning(f"Could not compress to {max_size_kb}KB")
    return False


def _compress_with_pil_fallback(input_path, output_path, max_size_kb=520):
    """PIL fallback compression with proper orientation."""
    max_size_bytes = max_size_kb * 1024
    
    try:
        with Image.open(input_path) as img:
            # KRITIK: EXIF orientation ni qo'llash
            img = ImageOps.exif_transpose(img)
            
            if img is None:
                img = Image.open(input_path)
            
            # Convert to RGB if needed
            if img.mode not in ('RGB', 'L'):
                if img.mode in ('RGBA', 'LA', 'P'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                    img = background.copy()
                else:
                    img = img.convert('RGB')
            else:
                img = img.copy()
        
        # Try quality compression first
        quality = 90
        while quality >= 40:
            temp_output = io.BytesIO()
            img.save(temp_output, 'JPEG', quality=quality, optimize=True, exif=b'')
            
            if temp_output.tell() <= max_size_bytes:
                with open(output_path, 'wb') as f:
                    temp_output.seek(0)
                    f.write(temp_output.read())
                
                logger.info(f"PIL compressed: {temp_output.tell() / 1024:.2f}KB (quality={quality})")
                return True
            
            quality -= 10
        
        # If quality reduction not enough, resize
        scale = 0.9
        while scale >= 0.4:
            new_size = (int(img.width * scale), int(img.height * scale))
            resized = img.resize(new_size, Image.Resampling.LANCZOS)
            
            temp_output = io.BytesIO()
            resized.save(temp_output, 'JPEG', quality=75, optimize=True, exif=b'')
            
            if temp_output.tell() <= max_size_bytes:
                with open(output_path, 'wb') as f:
                    temp_output.seek(0)
                    f.write(temp_output.read())
                
                logger.info(f"PIL compressed after resize: {temp_output.tell() / 1024:.2f}KB (scale={scale:.0%})")
                return True
            
            scale -= 0.1
        
        logger.warning(f"PIL could not compress to {max_size_kb}KB")
        return False
        
    except Exception as e:
        logger.error(f"PIL fallback compression failed: {e}")
        return False


def compress_image(image_field, max_size_kb=520, fix_rotation=False):
    """
    Compress an image to a maximum file size while creating a square crop.
    This ensures profile images display correctly in table views.
    
    Args:
        image_field: Django ImageField or UploadedFile
        max_size_kb: Maximum file size in kilobytes (default: 520KB)
        fix_rotation: Apply additional rotation heuristics (default: False)
    
    Returns:
        InMemoryUploadedFile: Compressed square image file
    """
    if not image_field:
        return image_field
    
    max_size_bytes = max_size_kb * 1024
    
    try:
        img = Image.open(image_field)
        # Apply EXIF orientation first
        img = ImageOps.exif_transpose(img)
        if img is None:
            image_field.seek(0)
            img = Image.open(image_field)
    except Exception:
        return image_field
    
    # Additional rotation heuristics if enabled
    if fix_rotation:
        try:
            width, height = img.size
            if width > height:
                aspect_ratio = width / height
                if 1.2 < aspect_ratio < 2.0:
                    img = img.rotate(-90, expand=True)
                    logger.info(f"Auto-rotated landscape to portrait")
        except Exception:
            pass
    
    # Convert to RGB
    if img.mode in ('RGBA', 'LA', 'P'):
        background = Image.new('RGB', img.size, (255, 255, 255))
        if img.mode == 'P':
            img = img.convert('RGBA')
        background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
        img = background
    elif img.mode != 'RGB':
        img = img.convert('RGB')
    
    # Center crop to square
    width, height = img.size
    if width != height:
        square_size = min(width, height)
        left = (width - square_size) // 2
        top = (height - square_size) // 2
        right = left + square_size
        bottom = top + square_size
        img = img.crop((left, top, right, bottom))
    
    output = io.BytesIO()
    quality = 95
    
    # Compress with progressively lower quality
    while quality > 20:
        output.seek(0)
        output.truncate()
        
        img.save(
            output,
            format='JPEG',
            quality=quality,
            optimize=True,
            progressive=True,
            exif=b''
        )
        
        if output.tell() <= max_size_bytes:
            break
        
        quality -= 5
    
    # If still too large, resize
    if output.tell() > max_size_bytes:
        scale_factor = 0.9
        while output.tell() > max_size_bytes and scale_factor > 0.3:
            output.seek(0)
            output.truncate()
            
            new_width = int(img.width * scale_factor)
            new_height = int(img.height * scale_factor)
            resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            resized_img.save(
                output,
                format='JPEG',
                quality=quality,
                optimize=True,
                progressive=True,
                exif=b''
            )
            
            scale_factor -= 0.1
    
    output.seek(0)
    
    # Preserve original filename
    if hasattr(image_field, 'name') and image_field.name:
        original_name = image_field.name
        new_filename = original_name.split('/')[-1] if '/' in original_name else original_name
    else:
        new_filename = 'image.jpg'
    
    compressed_image = InMemoryUploadedFile(
        output,
        'ImageField',
        new_filename,
        'image/jpeg',
        output.tell(),
        None
    )
    
    return compressed_image