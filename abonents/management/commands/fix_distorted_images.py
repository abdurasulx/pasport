"""
Management command to re-compress all abonent images to square format.
This fixes distorted images by applying center-crop to square.
"""

from django.core.management.base import BaseCommand
from abonents.models import Abonent
from abonents.utils import compress_image
from django.core.files.base import ContentFile


class Command(BaseCommand):
    help = 'Re-compress all abonent images to square format to fix distortion'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Only show what would be done, without actually processing images',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']

        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('Re-compressing Abonent Images to Square Format'))
        self.stdout.write(self.style.SUCCESS('=' * 60))

        if dry_run:
            self.stdout.write(self.style.WARNING('\n🔍 DRY RUN MODE - No changes will be made\n'))

        # Get all abonents with images
        abonents = Abonent.objects.exclude(rasm='').exclude(rasm__isnull=True)
        total_count = abonents.count()

        if total_count == 0:
            self.stdout.write(self.style.WARNING('No abonent images found.'))
            return

        self.stdout.write(f'\nFound {total_count} abonent(s) with images\n')

        processed_count = 0
        error_count = 0

        for index, abonent in enumerate(abonents, 1):
            try:
                if not abonent.rasm:
                    continue

                # Get current file size
                try:
                    current_size = abonent.rasm.size
                except Exception:
                    current_size = 0

                if dry_run:
                    self.stdout.write(
                        f'[{index}/{total_count}] 📋 Would re-compress PINFL {abonent.pinfl}: '
                        f'{current_size / 1024:.2f} KB'
                    )
                    processed_count += 1
                    continue

                # Re-compress the image (will apply square crop)
                self.stdout.write(
                    f'[{index}/{total_count}] 🔄 Re-compressing PINFL {abonent.pinfl}: '
                    f'{current_size / 1024:.2f} KB -> ',
                    ending=''
                )

                # Open and re-compress
                compressed_file = compress_image(abonent.rasm, max_size_kb=520)

                # Save re-compressed image
                compressed_file.seek(0)
                compressed_data = compressed_file.read()
                new_size = len(compressed_data)

                # Get the original filename
                original_filename = abonent.rasm.name.split('/')[-1]

                # Save with the same filename (will overwrite)
                abonent.rasm.save(
                    original_filename,
                    ContentFile(compressed_data),
                    save=True
                )

                self.stdout.write(self.style.SUCCESS(f'{new_size / 1024:.2f} KB ✓'))

                processed_count += 1

            except Exception as e:
                error_count += 1
                self.stdout.write(
                    self.style.ERROR(f'\n✗ Error processing PINFL {abonent.pinfl}: {str(e)}')
                )
                continue

        # Summary
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write(self.style.SUCCESS('Re-compression Summary'))
        self.stdout.write('=' * 60)
        self.stdout.write(self.style.SUCCESS(f'✅ Total images:       {total_count}'))
        self.stdout.write(self.style.SUCCESS(f'✅ Re-compressed:      {processed_count}'))
        self.stdout.write(self.style.ERROR(f'❌ Errors:             {error_count}'))

        if not dry_run and processed_count > 0:
            self.stdout.write(
                self.style.SUCCESS(f'\n🎉 Successfully re-compressed {processed_count} image(s) to square format!')
            )
