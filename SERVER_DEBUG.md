# Server Log Qo'llanma

## Serverda Xatolarni Aniqlash

### 1. Django Log Faylini Ko'rish

```bash
# SSH orqali serverga kiring, keyin:
tail -f /home/banda/Desktop/pasport/logs/django.log

# Yoki gunicorn loglarini ko'rish:
journalctl -u gunicorn -f
```

### 2. Qidirilishi Kerak Bo'lgan Xato Belgilari

Log faylda quyidagilarni qidiring:
- `Error compressing image` - Siqish jarayonida xato
- `Detected new upload` - Yangi rasm yuklangani aniqlandi
- `Compressing image` - Siqish boshlandi
- `Traceback` - Python xatolari

### 3. Agar Pillow O'rnatilmagan Bo'lsa

```bash
# SSH orqali serverda:
source /path/to/venv/bin/activate
pip install Pillow>=10.0
sudo systemctl restart gunicorn
```

### 4. Agar File Permission Muammosi Bo'lsa

```bash
# Media papkaga ruxsat bering:
sudo chown -R www-data:www-data /path/to/media/
sudo chmod -R 755 /path/to/media/
```

## Tez Yechim (Compression O'chirish)

Agar compressed versiya juda muammolar keltirayotgan bo'lsa, vaqtinchalik o'chirish mumkin:

### Oddiy versiya (compression yo'q):

`models.py` da `save()` metodini o'zgartiring:

```python
def save(self, *args, **kwargs):
    """Simple save without compression - temporary fix."""
    super().save(*args, **kwargs)
```

Keyin normal save ishlaydi va compression muammosini keyinroq hal qilish mumkin.
