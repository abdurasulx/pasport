"""
Abonent model - Abonentlarning pasport ma'lumotlarini saqlash uchun.
"""

from django.db import models
from django.core.validators import MinLengthValidator, RegexValidator


class Tuman(models.Model):
    """
    Tuman (District) modeli - hududiy tashkilot.
    """
    nomi = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Tuman nomi"
    )
    yaratilgan_vaqt = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Yaratilgan vaqt"
    )
    
    class Meta:
        verbose_name = "Tuman"
        verbose_name_plural = "Tumanlar"
        ordering = ['nomi']
    
    def __str__(self):
        return self.nomi


class Mahalla(models.Model):
    """
    Mahalla (Neighborhood) modeli - tumanga bog'langan.
    """
    nomi = models.CharField(
        max_length=150,
        verbose_name="Mahalla nomi"
    )
    tuman = models.ForeignKey(
        Tuman,
        on_delete=models.CASCADE,
        related_name='mahallalar',
        verbose_name="Tuman"
    )
    yaratilgan_vaqt = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Yaratilgan vaqt"
    )
    
    class Meta:
        verbose_name = "Mahalla"
        verbose_name_plural = "Mahallalar"
        ordering = ['tuman', 'nomi']
        unique_together = ['tuman', 'nomi']
    
    def __str__(self):
        return f"{self.nomi} ({self.tuman.nomi})"


class Abonent(models.Model):
    """
    Abonent modeli - JSHIR va rasm bilan ro'yxatdan o'tkazish.
    """
    
    # Abonent kodi (ixtiyoriy)
    abonent_kod = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        null=True,
        verbose_name="Abonent kodi",
        help_text="Telefon raqami yoki shaxsiy kod (ixtiyoriy)"
    )
    
    # PINFL - MAJBURIY
    pinfl = models.CharField(
        max_length=14,
        unique=True,
        verbose_name="JSHIR",
        help_text="14 raqamli shaxsiy identifikatsiya raqami",
        validators=[
            MinLengthValidator(14),
            RegexValidator(
                regex=r'^\d{14}$',
                message="JSHIR faqat 14 ta raqamdan iborat bo'lishi kerak"
            )
        ]
    )
    
    # Rasm - MAJBURIY
    rasm = models.ImageField(
        upload_to='abonent_rasmlar/',
        verbose_name="Rasm",
        help_text="Abonentning rasmi"
    )
    
    # Hudud ma'lumotlari - MAJBURIY
    tuman = models.ForeignKey(
        Tuman,
        on_delete=models.PROTECT,
        related_name='abonentlar',
        verbose_name="Tuman"
    )
    
    mahalla = models.ForeignKey(
        Mahalla,
        on_delete=models.PROTECT,
        related_name='abonentlar',
        verbose_name="Mahalla"
    )
    
    # Kim kiritgani - Yangi qo'shilgan
    inspektor = models.ForeignKey(
        'Inspektor',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='added_abonents',
        verbose_name="Kiritgan inspektor"
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
        return f"{self.pinfl} ({self.mahalla.nomi})"


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
    
    # Hudud ma'lumotlari
    tuman = models.ForeignKey(
        Tuman,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='inspektorlar',
        verbose_name="Tuman"
    )
    
    mahallalar = models.ManyToManyField(
        Mahalla,
        blank=True,
        related_name='inspektorlar',
        verbose_name="Mahallalar"
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
        tuman_nomi = self.tuman.nomi if self.tuman else "Tuman yo'q"
        return f"{self.user.get_full_name() or self.user.username} - {tuman_nomi}"
