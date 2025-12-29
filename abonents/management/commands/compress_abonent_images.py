"""
Management command to compress all existing abonent images to 520KB.
"""

from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from abonents.models import Abonent
from abonents.utils import compress_image
import os


class Command(BaseCommand):
    help = 'Compress all existing abonent images to max 520KB'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Only show what would be compressed, without actually compressing',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force compression even for images already under 520KB',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        force = options['force']
        
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS('Starting Abonent Image Compression'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
        
        if dry_run:
            self.stdout.write(self.style.WARNING('\n🔍 DRY RUN MODE - No files will be modified\n'))
        
        # Get all abonents with images
        abonents = Abonent.objects.exclude(rasm='').exclude(rasm__isnull=True)
        total_count = abonents.count()
        
        self.stdout.write(f'\nFound {total_count} abonents with images\n')
        
        compressed_count = 0
        skipped_count = 0
        error_count = 0
        total_saved = 0
        
        for index, abonent in enumerate(abonents, 1):
            try:
                # Get current file size
                if not os.path.exists(abonent.rasm.path):
                    self.stdout.write(
                        self.style.WARNING(
                            f'[{index}/{total_count}] ⚠️  File not found: {abonent.rasm.name}'
                        )
                    )
                    error_count += 1
                    continue
                
                original_size = os.path.getsize(abonent.rasm.path)
                original_size_kb = original_size / 1024
                
                # Check if compression needed
                max_size_kb = 520
                if not force and original_size_kb <= max_size_kb:
                    self.stdout.write(
                        f'[{index}/{total_count}] ⏭️  PINFL {abonent.pinfl}: '
                        f'{original_size_kb:.1f}KB (already under {max_size_kb}KB, skipping)'
                    )
                    skipped_count += 1
                    continue
                
                if dry_run:
                    self.stdout.write(
                        self.style.NOTICE(
                            f'[{index}/{total_count}] 📋 Would compress PINFL {abonent.pinfl}: '
                            f'{original_size_kb:.1f}KB → ~{max_size_kb}KB'
                        )
                    )
                    compressed_count += 1
                    continue
                
                # Compress the image
                self.stdout.write(
                    f'[{index}/{total_count}] 🔄 Compressing PINFL {abonent.pinfl}: '
                    f'{original_size_kb:.1f}KB...',
                    ending=''
                )
                
                # Open and compress
                compressed_file = compress_image(abonent.rasm, max_size_kb=max_size_kb)
                
                # Save compressed image
                compressed_file.seek(0)
                compressed_data = compressed_file.read()
                new_size = len(compressed_data)
                new_size_kb = new_size / 1024
                
                # Save to the same path
                abonent.rasm.save(
                    abonent.rasm.name,
                    ContentFile(compressed_data),
                    save=False  # Don't trigger signals
                )
                abonent.save()
                
                saved_kb = original_size_kb - new_size_kb
                total_saved += saved_kb
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f' ✅ {new_size_kb:.1f}KB (saved {saved_kb:.1f}KB)'
                    )
                )
                compressed_count += 1
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'\n[{index}/{total_count}] ❌ Error with PINFL {abonent.pinfl}: {str(e)}'
                    )
                )
                error_count += 1
        
        # Summary
        self.stdout.write(self.style.SUCCESS('\n' + '=' * 70))
        self.stdout.write(self.style.SUCCESS('Compression Summary'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(f'\n📊 Total abonents:     {total_count}')
        self.stdout.write(self.style.SUCCESS(f'✅ Compressed:         {compressed_count}'))
        self.stdout.write(self.style.WARNING(f'⏭️  Skipped:           {skipped_count}'))
        self.stdout.write(self.style.ERROR(f'❌ Errors:            {error_count}'))
        
        if not dry_run and compressed_count > 0:
            self.stdout.write(self.style.SUCCESS(f'\n💾 Total space saved:  {total_saved:.1f}KB ({total_saved/1024:.1f}MB)'))
        
        self.stdout.write(self.style.SUCCESS('\n✨ Done!\n'))
