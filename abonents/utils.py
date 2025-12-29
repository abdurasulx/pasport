"""
Utility functions for image processing.
"""

import io
import logging
from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile
import numpy as np

logger = logging.getLogger(__name__)


def compress_image(image_field, max_size_kb=520, fix_rotation=False):
    """
    Compress an image to a maximum file size while creating a square crop.
    This ensures profile images display correctly in table views.
    
    Args:
        image_field: Django ImageField or UploadedFile
        max_size_kb: Maximum file size in kilobytes (default: 520KB)
    
    Returns:
        InMemoryUploadedFile: Compressed square image file
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
    
    
    # Rotation heuristics are optional and controlled by the fix_rotation flag.
    if fix_rotation:
        # Fix EXIF rotation (images from phones often come rotated)
        try:
            from PIL import ImageOps
            rotated_img = ImageOps.exif_transpose(img)
            if rotated_img is not None:
                img = rotated_img
        except Exception:
            pass

        # Auto-rotate landscape images to portrait if they appear to be portrait photos
        try:
            width, height = img.size
            if width > height:
                aspect_ratio = width / height
                if 1.2 < aspect_ratio < 2.0:
                    img = img.rotate(-90, expand=True)
                    logger.info(f"Auto-rotated landscape image ({width}x{height}) to portrait → ({img.height}x{img.width})")
        except Exception:
            pass

        # OpenCV face-detection heuristic fallback (optional)
        try:
            import cv2

            def pil_to_cv(img_pil):
                arr = np.array(img_pil.convert('RGB'))
                return cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)

            try:
                face_cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
                face_cascade = cv2.CascadeClassifier(face_cascade_path)

                cv_img = pil_to_cv(img)
                best_rotation = 0
                best_faces = 0

                for k, angle in enumerate((0, 90, 180, 270)):
                    if k == 0:
                        test_img = cv_img
                    else:
                        # rotate 90*k degrees clockwise equivalently
                        test_img = np.ascontiguousarray(np.rot90(cv_img, 4 - k))

                    gray = cv2.cvtColor(test_img, cv2.COLOR_BGR2GRAY)
                    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
                    if len(faces) > best_faces:
                        best_faces = len(faces)
                        best_rotation = angle

                if best_faces > 0 and best_rotation != 0:
                    if best_rotation == 90:
                        img = img.rotate(-90, expand=True)
                    elif best_rotation == 180:
                        img = img.rotate(180, expand=True)
                    elif best_rotation == 270:
                        img = img.rotate(90, expand=True)

                    logger.info(f"OpenCV face-heuristic rotated image by {best_rotation}° (faces={best_faces})")
            except Exception:
                pass
        except Exception:
            pass
    
    # Convert RGBA to RGB (for PNG with transparency)
    if img.mode in ('RGBA', 'LA', 'P'):
        background = Image.new('RGB', img.size, (255, 255, 255))
        if img.mode == 'P':
            img = img.convert('RGBA')
        background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
        img = background
    elif img.mode != 'RGB':
        img = img.convert('RGB')
    
    # Center crop to square aspect ratio to prevent distortion when displayed
    width, height = img.size
    if width != height:
        # Determine the size of the square (use the smaller dimension)
        square_size = min(width, height)
        
        # Calculate cropping coordinates (center crop)
        left = (width - square_size) // 2
        top = (height - square_size) // 2
        right = left + square_size
        bottom = top + square_size
        
        # Crop to square
        img = img.crop((left, top, right, bottom))
    
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
