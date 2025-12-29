import logging
from pathlib import Path
from PIL import Image

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from abonents.utils import compress_image

samples = [
    'media/abonent_rasmlar/3388.jpg',
    'media/abonent_rasmlar/3390_6JAxrRt_wIH3Izu.jpg',
]

for p in samples:
    path = Path(p)
    if not path.exists():
        logger.error(f"Sample not found: {p}")
        continue

    with open(path, 'rb') as f:
        try:
            compressed = compress_image(f, max_size_kb=520)
        except Exception as e:
            logger.exception(f"compress_image failed for {p}: {e}")
            continue

    if hasattr(compressed, 'file'):
        compressed.file.seek(0)
        out_path = Path('/tmp') / f"fixed_{path.name}"
        with open(out_path, 'wb') as out:
            out.write(compressed.file.read())
        logger.info(f"Wrote fixed image: {out_path} (size={out_path.stat().st_size})")
    else:
        logger.warning(f"compress_image returned non-file for {p}")

print('done')
