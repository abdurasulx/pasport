"""
Abonent serializers - API uchun ma'lumotlarni serializatsiya qilish.
"""

from rest_framework import serializers
from .models import Abonent, Tuman, Mahalla


class AbonentSerializer(serializers.ModelSerializer):
    """
    Abonent uchun to'liq serializer - CRUD operatsiyalar uchun.
    """
    tuman_nomi = serializers.CharField(source='tuman.nomi', read_only=True)
    mahalla_nomi = serializers.CharField(source='mahalla.nomi', read_only=True)
    
    class Meta:
        model = Abonent
        fields = [
            'id',
            'abonent_kod',
            'pinfl',
            'rasm',
            'tuman',
            'tuman_nomi',
            'mahalla',
            'mahalla_nomi',
            'yaratilgan_vaqt',
            'yangilangan_vaqt',
        ]
        read_only_fields = ['id', 'yaratilgan_vaqt', 'yangilangan_vaqt']


class AbonentListSerializer(serializers.ModelSerializer):
    """
    Abonent uchun list serializer - optimized for list view.
    """
    tuman_nomi = serializers.CharField(source='tuman.nomi', read_only=True)
    mahalla_nomi = serializers.CharField(source='mahalla.nomi', read_only=True)
    
    class Meta:
        model = Abonent
        fields = [
            'id',
            'pinfl',
            'tuman_nomi',
            'mahalla_nomi',
            'rasm',
            'yaratilgan_vaqt',
        ]


class AbonentCreateSerializer(serializers.ModelSerializer):
    """
    Abonent yaratish uchun serializer.
    """
    class Meta:
        model = Abonent
        fields = [
            'abonent_kod',
            'pinfl',
            'rasm',
            'tuman',
            'mahalla',
        ]
    
    def validate_pinfl(self, value):
        if not value:
            raise serializers.ValidationError("JSHIR kiritish majburiy")
        if not value.isdigit():
            raise serializers.ValidationError("JSHIR faqat raqamlardan iborat bo'lishi kerak")
        if len(value) != 14:
            raise serializers.ValidationError("JSHIR 14 ta raqamdan iborat bo'lishi kerak")
        return value


class PinflResponseSerializer(serializers.Serializer):
    """
    PINFL qaytarish uchun serializer.
    """
    pinfl = serializers.CharField(max_length=14)
    mavjud = serializers.BooleanField()
    abonent_id = serializers.IntegerField(required=False, allow_null=True)
