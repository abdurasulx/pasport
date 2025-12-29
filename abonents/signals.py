"""
Signal handlers for Abonent model - handles image compression automatically.
"""

from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Abonent
from .utils import compress_image
import logging

logger = logging.getLogger(__name__)


@receiver(pre_save, sender=Abonent)
def compress_abonent_image(sender, instance, **kwargs):
    """
    Compress abonent image before saving.
    
    This signal handler is triggered before an Abonent instance is saved.
    It only compresses the image if a new file is being uploaded.
    """
    # Only process if rasm field has data
    if not instance.rasm:
        return
    
    try:
        # For new instances (no pk yet), always compress
        if not instance.pk:
            logger.info(f"New abonent, compressing image for PINFL: {instance.pinfl}")
            instance.rasm = compress_image(instance.rasm)
            logger.info(f"Image compressed successfully")
            return
        
        # For existing instances, check if image was changed
        try:
            old_instance = Abonent.objects.get(pk=instance.pk)
            
            # Compare the file names to detect if image changed
            old_image_name = old_instance.rasm.name if old_instance.rasm else None
            new_image_name = instance.rasm.name if instance.rasm else None
            
            # If names are different, it's a new upload
            if old_image_name != new_image_name:
                logger.info(f"Image changed for abonent PINFL: {instance.pinfl}")
                logger.info(f"  Old: {old_image_name}")
                logger.info(f"  New: {new_image_name}")
                instance.rasm = compress_image(instance.rasm)
                logger.info(f"Image compressed successfully")
            else:
                logger.debug(f"Image not changed for abonent PINFL: {instance.pinfl}, skipping compression")
                
        except Abonent.DoesNotExist:
            # Old instance doesn't exist (shouldn't happen), compress anyway
            logger.warning(f"Old instance not found for pk={instance.pk}, compressing image")
            instance.rasm = compress_image(instance.rasm)
            
    except Exception as e:
        # Log error but don't break the save
        logger.error(f"Error in compress_abonent_image signal for PINFL {instance.pinfl}: {str(e)}", exc_info=True)
        # Don't raise exception - allow save to continue even if compression fails
