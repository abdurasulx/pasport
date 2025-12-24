"""
Abonent serializers - API uchun ma'lumotlarni serializatsiya qilish.
"""

from rest_framework import serializers
from .models import Abonent


class AbonentSerializer(serializers.ModelSerializer):
    """
    Abonent uchun to'liq serializer - CRUD operatsiyalar uchun.
    """
    toliq_ism = serializers.ReadOnlyField()
    pasport = serializers.ReadOnlyField()
    
    class Meta:
        model = Abonent
        fields = [
            'id',
            'abonent_kod',
            'pasport_seriya',
            'pasport_raqam',
            'pasport',  # computed field
            'pinfl',
            'ism',
            'familiya',
            'otasining_ismi',
            'toliq_ism',  # computed field
            'tugilgan_sana',
            'jins',
            'rasm',
            'manzil',
            'telefon',
            'yaratilgan_vaqt',
            'yangilangan_vaqt',
        ]
        read_only_fields = ['id', 'yaratilgan_vaqt', 'yangilangan_vaqt']


class AbonentListSerializer(serializers.ModelSerializer):
    """
    Abonent uchun list serializer - optimized for list view.
    """
    toliq_ism = serializers.ReadOnlyField()
    
    class Meta:
        model = Abonent
        fields = [
            'id',
            'abonent_kod',
            'pinfl',
            'toliq_ism',
            'jins',
            'telefon',
            'rasm',
            'yaratilgan_vaqt',
        ]


class AbonentCreateSerializer(serializers.ModelSerializer):
    """
    Yangi abonent yaratish uchun serializer.
    Majburiy: pasport_seriya, pinfl, rasm
    Ixtiyoriy: qolgan barchasi
    """
    # Majburiy maydonlar
    pinfl = serializers.CharField(max_length=14, required=True)
    rasm = serializers.ImageField(required=True)
    pasport_seriya = serializers.CharField(max_length=10, required=True)
    
    # Ixtiyoriy maydonlar
    abonent_kod = serializers.CharField(max_length=50, required=False, allow_blank=True, allow_null=True)
    pasport_raqam = serializers.CharField(max_length=20, required=False, allow_blank=True)
    ism = serializers.CharField(max_length=100, required=False, allow_blank=True)
    familiya = serializers.CharField(max_length=100, required=False, allow_blank=True)
    tugilgan_sana = serializers.DateField(required=False, allow_null=True)
    jins = serializers.ChoiceField(choices=[('erkak', 'Erkak'), ('ayol', 'Ayol')], required=False, allow_blank=True)
    
    class Meta:
        model = Abonent
        fields = [
            'abonent_kod',
            'pasport_seriya',
            'pasport_raqam',
            'pinfl',
            'ism',
            'familiya',
            'otasining_ismi',
            'tugilgan_sana',
            'jins',
            'rasm',
            'manzil',
            'telefon',
        ]
    
    def validate_pinfl(self, value):
        """PINFL validatsiyasi - majburiy."""
        if not value:
            raise serializers.ValidationError("PINFL kiritish majburiy")
        if not value.isdigit():
            raise serializers.ValidationError("PINFL faqat raqamlardan iborat bo'lishi kerak")
        if len(value) != 14:
            raise serializers.ValidationError("PINFL 14 ta raqamdan iborat bo'lishi kerak")
        return value


class PinflResponseSerializer(serializers.Serializer):
    """
    PINFL qaytarish uchun serializer.
    """
    pinfl = serializers.CharField(max_length=14)
