"""
Abonent model - Abonentlarning pasport ma'lumotlarini saqlash uchun.
"""

from django.db import models
from django.core.validators import MinLengthValidator, RegexValidator


class Abonent(models.Model):
    """
    Abonent modeli - pasport ma'lumotlari va shaxsiy identifikatsiya.
    """
    
    # Jins tanlovlari
    JINS_CHOICES = [
        ('erkak', 'Erkak'),
        ('ayol', 'Ayol'),
    ]
    
    # Asosiy identifikatsiya
    abonent_kod = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        null=True,
        verbose_name="Abonent kodi",
        help_text="Telefon raqami yoki shaxsiy kod (ixtiyoriy)"
    )
    
    # Pasport ma'lumotlari
    pasport_seriya = models.CharField(
        max_length=10,
        verbose_name="Pasport seriyasi",
        help_text="Masalan: AA, AB, AC"
    )
    
    pasport_raqam = models.CharField(
        max_length=20,
        blank=True,
        default="",
        verbose_name="Pasport raqami",
        help_text="7 raqamli pasport raqami (ixtiyoriy)"
    )
    
    # PINFL - Personal Identification Number of Physical Persons (14 raqam) - MAJBURIY
    pinfl = models.CharField(
        max_length=14,
        unique=True,
        verbose_name="PINFL (JShShIR)",
        help_text="14 raqamli shaxsiy identifikatsiya raqami (majburiy)",
        validators=[
            MinLengthValidator(14),
            RegexValidator(
                regex=r'^\d{14}$',
                message="PINFL faqat 14 ta raqamdan iborat bo'lishi kerak"
            )
        ]
    )
    
    # Shaxsiy ma'lumotlar
    ism = models.CharField(
        max_length=100,
        blank=True,
        default="",
        verbose_name="Ism"
    )
    
    familiya = models.CharField(
        max_length=100,
        blank=True,
        default="",
        verbose_name="Familiya"
    )
    
    otasining_ismi = models.CharField(
        max_length=100,
        verbose_name="Otasining ismi",
        blank=True,
        default=""
    )
    
    tugilgan_sana = models.DateField(
        blank=True,
        null=True,
        verbose_name="Tug'ilgan sana"
    )
    
    jins = models.CharField(
        max_length=10,
        choices=JINS_CHOICES,
        blank=True,
        default="",
        verbose_name="Jinsi"
    )
    
    # Rasm - MAJBURIY
    rasm = models.ImageField(
        upload_to='abonent_rasmlar/',
        verbose_name="Rasm",
        help_text="Abonentning rasmi (majburiy)"
    )
    
    # Qo'shimcha ma'lumotlar
    manzil = models.TextField(
        verbose_name="Manzil",
        blank=True,
        default=""
    )
    
    telefon = models.CharField(
        max_length=20,
        verbose_name="Telefon raqami",
        blank=True,
        default=""
    )
    
    # Timestamp fieldlar
    yaratilgan_vaqt = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Yaratilgan vaqt"
    )
    
    yangilangan_vaqt = models.DateTimeField(
        auto_now=True,
        verbose_name="Yangilangan vaqt"
    )
    
    class Meta:
        verbose_name = "Abonent"
        verbose_name_plural = "Abonentlar"
        ordering = ['-id']
    
    def __str__(self):
        return f"{self.familiya} {self.ism} ({self.abonent_kod})"
    
    @property
    def toliq_ism(self):
        """To'liq FIO qaytaradi."""
        parts = [self.familiya, self.ism]
        if self.otasining_ismi:
            parts.append(self.otasining_ismi)
        return " ".join(parts)
    
    @property
    def pasport(self):
        """Pasport seriya va raqamini birlashtiradi."""
        return f"{self.pasport_seriya} {self.pasport_raqam}"


class Inspektor(models.Model):
    """
    Inspektor modeli - inspektorlar uchun autentifikatsiya.
    Django User bilan bog'langan.
    """
    
    user = models.OneToOneField(
        'auth.User',
        on_delete=models.CASCADE,
        verbose_name="Foydalanuvchi",
        related_name='inspektor_profile'
    )
    
    telefon = models.CharField(
        max_length=20,
        verbose_name="Telefon raqami",
        blank=True,
        default=""
    )
    
    hudud = models.CharField(
        max_length=100,
        verbose_name="Hudud",
        help_text="Inspektor ishlaydigan hudud",
        blank=True,
        default=""
    )
    
    lavozim = models.CharField(
        max_length=100,
        verbose_name="Lavozimi",
        blank=True,
        default="Inspektor"
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name="Faol"
    )
    
    yaratilgan_vaqt = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Yaratilgan vaqt"
    )
    
    class Meta:
        verbose_name = "Inspektor"
        verbose_name_plural = "Inspektorlar"
        ordering = ['-id']
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {self.hudud}"
