"""
Abonent views - API endpointlar uchun viewlar.
"""

from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404
from django.db.models import ProtectedError
from rest_framework import viewsets, status, filters
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.pagination import PageNumberPagination

from .models import Abonent
from .serializers import (
    AbonentSerializer,
    AbonentListSerializer,
    AbonentCreateSerializer,
    PinflResponseSerializer,
)


class AbonentPagination(PageNumberPagination):
    """
    Abonentlar uchun pagination - 20 ta element per page.
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class AbonentViewSet(viewsets.ModelViewSet):
    """
    Abonent CRUD ViewSet.
    
    Endpoints:
    - GET /api/abonents/ - List all abonents (paginated)
    - POST /api/abonents/ - Create new abonent
    - GET /api/abonents/{id}/ - Retrieve abonent
    - PUT /api/abonents/{id}/ - Update abonent
    - PATCH /api/abonents/{id}/ - Partial update
    - DELETE /api/abonents/{id}/ - Delete abonent
    
    Query params:
    - search: Search by abonent_kod, pinfl, ism, familiya
    - ordering: Order by field (default: -id)
    - page: Page number
    - page_size: Items per page (max 100)
    """
    queryset = Abonent.objects.all()
    pagination_class = AbonentPagination
    parser_classes = [MultiPartParser, FormParser]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['abonent_kod', 'pinfl']
    ordering_fields = ['id', 'yaratilgan_vaqt']
    ordering = ['-id']
    
    def get_serializer_class(self):
        """Action ga qarab serializer tanlash."""
        if self.action == 'list':
            return AbonentListSerializer
        elif self.action == 'create':
            return AbonentCreateSerializer
        return AbonentSerializer


@api_view(['POST'])
def add_data(request):
    """
    POST /api/add-data/
    
    Yangi abonent qo'shish - multipart/form-data bilan.
    
    Request body (form-data):
    - abonent_kod: string (ixtiyoriy)
    - pinfl: string (majburiy, 14 raqam)
    - rasm: file (majburiy, image)
    - tuman: integer (majburiy, tuman ID)
    - mahalla: integer (majburiy, mahalla ID)
    
    Response:
    - 201: Created successfully with abonent data
    - 400: Validation error
    """
    serializer = AbonentCreateSerializer(data=request.data)
    
    if serializer.is_valid():
        abonent = serializer.save()
        response_serializer = AbonentSerializer(abonent)
        return Response(
            {
                'success': True,
                'message': "Abonent muvaffaqiyatli qo'shildi",
                'data': response_serializer.data
            },
            status=status.HTTP_201_CREATED
        )
    
    return Response(
        {
            'success': False,
            'message': "Xatolik yuz berdi",
            'errors': serializer.errors
        },
        status=status.HTTP_400_BAD_REQUEST
    )




def get_pinfl(request, abonent_kod):
    """
    GET /api/get-pinfl/<abonent_kod>/
    
    Berilgan abonent_kod bo'yicha PINFL va rasm URL ni qaytaradi.
    
    Response:
    - 200: {"pinfl": "12345678901234", "rasm_url": "/media/..."}
    - 404: Abonent topilmadi
    """
    from django.http import JsonResponse
    
    try:
        abonent = Abonent.objects.get(abonent_kod=abonent_kod)
        rasm_url = request.build_absolute_uri(abonent.rasm.url) if abonent.rasm else None
        return JsonResponse({
            'pinfl': abonent.pinfl,
            'rasm_url': rasm_url
        })
    except Abonent.DoesNotExist:
        return JsonResponse({
            'error': "Abonent topilmadi",
            'abonent_kod': abonent_kod
        }, status=404)


@api_view(['GET'])
def get_rasm(request, abonent_kod):
    """
    GET /api/get-rasm/<abonent_kod>/
    
    Berilgan abonent_kod bo'yicha rasmni qaytaradi (image file).
    
    Response:
    - 200: Image file (content-type based on image type)
    - 404: Abonent yoki rasm topilmadi
    """
    try:
        abonent = Abonent.objects.get(abonent_kod=abonent_kod)
        
        if not abonent.rasm:
            raise Http404("Rasm topilmadi")
        
        # Rasmni FileResponse sifatida qaytarish
        return FileResponse(
            abonent.rasm.open('rb'),
            content_type='image/jpeg'  # Fayl turiga qarab o'zgaradi
        )
    except Abonent.DoesNotExist:
        raise Http404("Abonent topilmadi")


# =============================================================================
# INSPECTOR FRONTEND VIEWS
# =============================================================================

# =============================================================================
# INSPECTOR FRONTEND VIEWS
# =============================================================================

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from django.http import HttpResponseForbidden
from django import forms
from .models import Abonent, Mahalla
import functools


def admin_required(view_func):
    """Decorator for views that require admin/staff access."""
    @functools.wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('inspector-login')
        if not request.user.is_staff:
            messages.error(request, "Bu sahifaga kirish huquqingiz yo'q!")
            return redirect('inspector-dashboard')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def inspector_required(view_func):
    """Decorator for views that require inspector access."""
    @functools.wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('inspector-login')
        # If user is staff/admin, they shouldn't be here (according to strict separation logic)
        # OR we can allow admins to view inspector pages as inspectors?
        # Requirement: "admin faqat bitta user bo'lihsi kerak. inspektor hech qachon admin sahifaga admin hech qachon inspektor sahifasiga kira olmasligi kerak"
        if request.user.is_staff:
            messages.error(request, "Admin inspektor sahifasiga kira olmaydi!")
            return redirect('custom-admin-dashboard')
            
        if not hasattr(request.user, 'inspektor_profile'):
            messages.error(request, "Siz inspektor emassiz!")
            return redirect('inspector-login')
            
        return view_func(request, *args, **kwargs)
    return _wrapped_view


class AbonentForm(forms.ModelForm):
    """Abonent form for inspector frontend - simplified."""
    
    mahalla = forms.ModelChoiceField(
        queryset=Mahalla.objects.none(),
        required=True,
        label="Mahalla",
        empty_label="Mahallani tanlang"
    )
    
    class Meta:
        model = Abonent
        fields = ['pinfl', 'rasm', 'mahalla']
    
    def __init__(self, *args, inspektor=None, **kwargs):
        super().__init__(*args, **kwargs)
        if inspektor and inspektor.tuman:
            self.fields['mahalla'].queryset = inspektor.mahallalar.all()
        elif self.instance and self.instance.pk and self.instance.mahalla:
            self.fields['mahalla'].queryset = Mahalla.objects.filter(
                pk=self.instance.mahalla.pk
            )


def inspector_login(request):
    """Inspector login view."""
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('custom-admin-dashboard')
        return redirect('inspector-dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f"Xush kelibsiz, {user.get_full_name() or user.username}!")
            # Staff users go to admin panel, inspectors go to inspector dashboard
            if user.is_staff:
                return redirect('custom-admin-dashboard')
            else:
                # Check if user has inspector profile
                if not hasattr(user, 'inspektor_profile'):
                    logout(request)
                    messages.error(request, "Siz inspektor emassiz!")
                    return redirect('inspector-login')
                return redirect('inspector-dashboard')
        else:
            messages.error(request, "Login yoki parol noto'g'ri!")
    
    return render(request, 'inspector/login.html')


def inspector_logout(request):
    """Inspector logout view."""
    logout(request)
    messages.info(request, "Tizimdan chiqdingiz.")
    return redirect('inspector-login')


@inspector_required
def inspector_dashboard(request):
    """Inspector dashboard - stats and recent abonents (inspector's own only)."""
    today = timezone.now().date()
    inspektor = request.user.inspektor_profile
    
    # Filter by inspector
    my_abonents = Abonent.objects.filter(inspektor=inspektor)
    
    context = {
        'today': today,
        'total_abonents': my_abonents.count(),
        'today_added': my_abonents.filter(yaratilgan_vaqt__date=today).count(),
        'recent_abonents': my_abonents.order_by('-yaratilgan_vaqt')[:5],
    }
    return render(request, 'inspector/dashboard.html', context)


@inspector_required
def inspector_abonent_list(request):
    """Abonent list with search and pagination (inspector's own only)."""
    search_query = request.GET.get('q', '')
    inspektor = request.user.inspektor_profile
    
    # Filter by inspector
    abonents = Abonent.objects.filter(inspektor=inspektor)
    
    if search_query:
        abonents = abonents.filter(
            Q(abonent_kod__icontains=search_query) |
            Q(pinfl__icontains=search_query) |
            Q(mahalla__nomi__icontains=search_query)
        )
    
    paginator = Paginator(abonents, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'abonents': page_obj,
        'page_obj': page_obj,
        'search_query': search_query,
    }
    return render(request, 'inspector/abonent_list.html', context)


@inspector_required
def inspector_abonent_add(request):
    """Add new abonent with inspector's tuman/mahalla."""
    inspektor = request.user.inspektor_profile
    
    if request.method == 'POST':
        form = AbonentForm(request.POST, request.FILES, inspektor=inspektor)
        if form.is_valid():
            abonent = form.save(commit=False)
            # Auto-set tuman from inspector
            if inspektor.tuman:
                abonent.tuman = inspektor.tuman
            # Set owner
            abonent.inspektor = inspektor
            abonent.save()
            messages.success(request, f"Abonent '{abonent.pinfl}' muvaffaqiyatli qo'shildi!")
            return redirect('inspector-abonent-list')
    else:
        form = AbonentForm(inspektor=inspektor)
    
    return render(request, 'inspector/abonent_form.html', {'form': form, 'inspektor': inspektor})


@inspector_required
def inspector_abonent_edit(request, pk):
    """Edit existing abonent (inspector's own only)."""
    # Verify ownership
    inspektor = request.user.inspektor_profile
    abonent = get_object_or_404(Abonent, pk=pk, inspektor=inspektor)
    
    if request.method == 'POST':
        form = AbonentForm(request.POST, request.FILES, instance=abonent, inspektor=inspektor)
        if form.is_valid():
            abonent = form.save(commit=False)
            # Ensure tuman is set from inspector if not already set
            if inspektor.tuman and not abonent.tuman:
                abonent.tuman = inspektor.tuman
            abonent.save()
            messages.success(request, f"Abonent '{abonent.pinfl}' yangilandi!")
            return redirect('inspector-abonent-list')
    else:
        form = AbonentForm(instance=abonent, inspektor=inspektor)
    
    return render(request, 'inspector/abonent_form.html', {'form': form, 'inspektor': inspektor})


@inspector_required
def inspector_abonent_delete(request, pk):
    """Delete abonent confirmation (inspector's own only)."""
    # Verify ownership
    inspektor = request.user.inspektor_profile
    abonent = get_object_or_404(Abonent, pk=pk, inspektor=inspektor)
    
    if request.method == 'POST':
        pinfl = abonent.pinfl
        abonent.delete()
        messages.success(request, f"Abonent '{pinfl}' o'chirildi!")
        return redirect('inspector-abonent-list')
    
    return render(request, 'inspector/abonent_delete.html', {'abonent': abonent})


# =============================================================================
# CUSTOM ADMIN VIEWS
# =============================================================================

from .models import Tuman, Mahalla, Inspektor
from django.contrib.auth.models import User


# Dashboard
@admin_required
def custom_admin_dashboard(request):
    """Custom admin dashboard."""
    context = {
        'tumanlar_soni': Tuman.objects.count(),
        'mahallalar_soni': Mahalla.objects.count(),
        'inspektorlar_soni': Inspektor.objects.count(),
        'abonentlar_soni': Abonent.objects.count(),
        'recent_tumanlar': Tuman.objects.all()[:5],
        'recent_inspektorlar': Inspektor.objects.all()[:5],
    }
    return render(request, 'admin_custom/dashboard.html', context)


# Tuman Forms
class TumanForm(forms.ModelForm):
    class Meta:
        model = Tuman
        fields = ['nomi']


class MahallaForm(forms.ModelForm):
    class Meta:
        model = Mahalla
        fields = ['tuman', 'nomi']


# Tuman CRUD
@admin_required
def admin_tuman_list(request):
    tumanlar = Tuman.objects.all()
    return render(request, 'admin_custom/tuman_list.html', {'tumanlar': tumanlar})


@admin_required
def admin_tuman_add(request):
    if request.method == 'POST':
        form = TumanForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Tuman muvaffaqiyatli qo'shildi!")
            return redirect('admin-tuman-list')
    else:
        form = TumanForm()
    return render(request, 'admin_custom/tuman_form.html', {'form': form})


@admin_required
def admin_tuman_edit(request, pk):
    tuman = get_object_or_404(Tuman, pk=pk)
    if request.method == 'POST':
        form = TumanForm(request.POST, instance=tuman)
        if form.is_valid():
            form.save()
            messages.success(request, "Tuman muvaffaqiyatli yangilandi!")
            return redirect('admin-tuman-list')
    else:
        form = TumanForm(instance=tuman)
    return render(request, 'admin_custom/tuman_form.html', {'form': form})


@admin_required
def admin_tuman_delete(request, pk):
    tuman = get_object_or_404(Tuman, pk=pk)
    if request.method == 'POST':
        try:
            tuman.delete()
            messages.success(request, "Tuman o'chirildi!")
        except ProtectedError:
            messages.error(request, f"'{tuman.nomi}' tumanini o'chirib bo'lmaydi - unga bog'langan mahallalar yoki abonentlar mavjud!")
        return redirect('admin-tuman-list')
    return render(request, 'admin_custom/tuman_delete.html', {'tuman': tuman})


# Mahalla CRUD
@admin_required
def admin_mahalla_list(request):
    mahallalar = Mahalla.objects.select_related('tuman').all()
    return render(request, 'admin_custom/mahalla_list.html', {'mahallalar': mahallalar})


@admin_required
def admin_mahalla_add(request):
    if request.method == 'POST':
        form = MahallaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Mahalla muvaffaqiyatli qo'shildi!")
            return redirect('admin-mahalla-list')
    else:
        form = MahallaForm()
    return render(request, 'admin_custom/mahalla_form.html', {
        'form': form,
        'tumanlar': Tuman.objects.all()
    })


@admin_required
def admin_mahalla_edit(request, pk):
    mahalla = get_object_or_404(Mahalla, pk=pk)
    if request.method == 'POST':
        form = MahallaForm(request.POST, instance=mahalla)
        if form.is_valid():
            form.save()
            messages.success(request, "Mahalla muvaffaqiyatli yangilandi!")
            return redirect('admin-mahalla-list')
    else:
        form = MahallaForm(instance=mahalla)
    return render(request, 'admin_custom/mahalla_form.html', {
        'form': form,
        'tumanlar': Tuman.objects.all()
    })


@admin_required
def admin_mahalla_delete(request, pk):
    mahalla = get_object_or_404(Mahalla, pk=pk)
    if request.method == 'POST':
        try:
            mahalla.delete()
            messages.success(request, "Mahalla o'chirildi!")
        except ProtectedError:
            messages.error(request, f"'{mahalla.nomi}' mahallasini o'chirib bo'lmaydi - unga bog'langan abonentlar mavjud!")
        return redirect('admin-mahalla-list')
    return render(request, 'admin_custom/mahalla_delete.html', {'mahalla': mahalla})


# Inspektor CRUD
@admin_required
def admin_inspektor_list(request):
    inspektorlar = Inspektor.objects.select_related('user', 'tuman').prefetch_related('mahallalar').all()
    return render(request, 'admin_custom/inspektor_list.html', {'inspektorlar': inspektorlar})


@admin_required
def admin_inspektor_add(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        
        # Check if username exists
        if User.objects.filter(username=username).exists():
            return render(request, 'admin_custom/inspektor_form.html', {
                'error': "Bu username allaqachon mavjud!",
                'tumanlar': Tuman.objects.all(),
                'mahallalar': Mahalla.objects.select_related('tuman').all(),
            })
        
        # Create user
        user = User.objects.create_user(
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        
        # Create inspektor
        inspektor = Inspektor.objects.create(
            user=user,
            tuman_id=request.POST.get('tuman') or None,
            telefon=request.POST.get('telefon', ''),
            lavozim=request.POST.get('lavozim', 'Inspektor'),
            is_active='is_active' in request.POST
        )
        
        # Add mahallalar
        mahalla_ids = request.POST.getlist('mahallalar')
        if mahalla_ids:
            inspektor.mahallalar.set(mahalla_ids)
        
        messages.success(request, "Inspektor muvaffaqiyatli qo'shildi!")
        return redirect('admin-inspektor-list')
    
    return render(request, 'admin_custom/inspektor_form.html', {
        'tumanlar': Tuman.objects.all(),
        'mahallalar': Mahalla.objects.select_related('tuman').all(),
    })


@admin_required
def admin_inspektor_edit(request, pk):
    inspektor = get_object_or_404(Inspektor, pk=pk)
    
    if request.method == 'POST':
        # Check password update
        new_password = request.POST.get('new_password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()
        
        if new_password or confirm_password:
            if new_password != confirm_password:
                return render(request, 'admin_custom/inspektor_form.html', {
                    'inspektor': inspektor,
                    'tumanlar': Tuman.objects.all(),
                    'mahallalar': Mahalla.objects.select_related('tuman').all(),
                    'error': "Parollar mos kelmadi!"
                })
            if len(new_password) < 4:
                return render(request, 'admin_custom/inspektor_form.html', {
                    'inspektor': inspektor,
                    'tumanlar': Tuman.objects.all(),
                    'mahallalar': Mahalla.objects.select_related('tuman').all(),
                    'error': "Parol kamida 4 ta belgidan iborat bo'lishi kerak!"
                })
        
        # Update user info
        inspektor.user.first_name = request.POST.get('first_name', '')
        inspektor.user.last_name = request.POST.get('last_name', '')
        
        # Update password if provided
        if new_password:
            inspektor.user.set_password(new_password)
        
        inspektor.user.save()
        
        # Update inspektor
        inspektor.tuman_id = request.POST.get('tuman') or None
        inspektor.telefon = request.POST.get('telefon', '')
        inspektor.lavozim = request.POST.get('lavozim', 'Inspektor')
        inspektor.is_active = 'is_active' in request.POST
        inspektor.save()
        
        # Update mahallalar
        mahalla_ids = request.POST.getlist('mahallalar')
        inspektor.mahallalar.set(mahalla_ids)
        
        if new_password:
            messages.success(request, "Inspektor va parol muvaffaqiyatli yangilandi!")
        else:
            messages.success(request, "Inspektor muvaffaqiyatli yangilandi!")
        return redirect('admin-inspektor-list')
    
    return render(request, 'admin_custom/inspektor_form.html', {
        'inspektor': inspektor,
        'tumanlar': Tuman.objects.all(),
        'mahallalar': Mahalla.objects.select_related('tuman').all(),
    })


@admin_required
def admin_inspektor_delete(request, pk):
    inspektor = get_object_or_404(Inspektor, pk=pk)
    if request.method == 'POST':
        user = inspektor.user
        inspektor.delete()
        user.delete()
        messages.success(request, "Inspektor o'chirildi!")
        return redirect('admin-inspektor-list')
    return render(request, 'admin_custom/inspektor_delete.html', {'inspektor': inspektor})


# =============================================================================
# ADMIN ABONENT CRUD
# =============================================================================

@admin_required
def admin_abonent_list(request):
    """Admin panel abonent list with search and pagination."""
    search_query = request.GET.get('q', '')
    inspektor_id = request.GET.get('inspektor')
    tuman_id = request.GET.get('tuman')
    mahalla_id = request.GET.get('mahalla')
    
    abonentlar = Abonent.objects.select_related('tuman', 'mahalla', 'inspektor', 'inspektor__user').all()
    
    if search_query:
        abonentlar = abonentlar.filter(
            Q(pinfl__icontains=search_query) |
            Q(mahalla__nomi__icontains=search_query)
        )
        
    if inspektor_id:
        try:
            inspektor_id = int(inspektor_id)
            abonentlar = abonentlar.filter(inspektor_id=inspektor_id)
        except (ValueError, TypeError):
            pass

    if tuman_id:
        try:
            tuman_id = int(tuman_id)
            abonentlar = abonentlar.filter(tuman_id=tuman_id)
        except (ValueError, TypeError):
            pass

    if mahalla_id:
        try:
            mahalla_id = int(mahalla_id)
            abonentlar = abonentlar.filter(mahalla_id=mahalla_id)
        except (ValueError, TypeError):
            pass
    
    paginator = Paginator(abonentlar, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Get all inspectors for filter
    inspektorlar = Inspektor.objects.select_related('user').all()
    tumanlar = Tuman.objects.all()
    
    # Filter mahallas based on selected tuman if any
    if tuman_id:
        mahallalar = Mahalla.objects.filter(tuman_id=tuman_id)
    else:
        mahallalar = Mahalla.objects.select_related('tuman').all()
    
    return render(request, 'admin_custom/abonent_list.html', {
        'abonentlar': page_obj,
        'page_obj': page_obj,
        'search_query': search_query,
        'inspektorlar': inspektorlar,
        'selected_inspektor': inspektor_id,
        'tumanlar': tumanlar,
        'selected_tuman': tuman_id,
        'mahallalar': mahallalar,
        'selected_mahalla': mahalla_id,
    })


@admin_required
def admin_abonent_add(request):
    """Admin panel add abonent."""
    from django.db import IntegrityError
    
    if request.method == 'POST':
        pinfl = request.POST.get('pinfl')
        tuman_id = request.POST.get('tuman')
        mahalla_id = request.POST.get('mahalla')
        inspektor_id = request.POST.get('inspektor') or None
        abonent_kod = request.POST.get('abonent_kod', '').strip() or None
        rasm = request.FILES.get('rasm')
        
        if not all([pinfl, tuman_id, mahalla_id, rasm]):
            return render(request, 'admin_custom/abonent_form.html', {
                'error': "Barcha maydonlarni to'ldiring!",
                'tumanlar': Tuman.objects.all(),
                'mahallalar': Mahalla.objects.select_related('tuman').all(),
                'inspektorlar': Inspektor.objects.select_related('user', 'tuman').all(),
            })
        
        try:
            abonent = Abonent.objects.create(
                pinfl=pinfl,
                tuman_id=tuman_id,
                mahalla_id=mahalla_id,
                inspektor_id=inspektor_id,
                abonent_kod=abonent_kod,
                rasm=rasm,
            )
            messages.success(request, f"Abonent '{pinfl}' muvaffaqiyatli qo'shildi!")
            return redirect('admin-abonent-list')
        except IntegrityError:
            return render(request, 'admin_custom/abonent_form.html', {
                'error': f"'{abonent_kod}' raqami allaqachon mavjud!",
                'tumanlar': Tuman.objects.all(),
                'mahallalar': Mahalla.objects.select_related('tuman').all(),
                'inspektorlar': Inspektor.objects.select_related('user', 'tuman').all(),
            })
    
    return render(request, 'admin_custom/abonent_form.html', {
        'tumanlar': Tuman.objects.all(),
        'mahallalar': Mahalla.objects.select_related('tuman').all(),
        'inspektorlar': Inspektor.objects.select_related('user', 'tuman').all(),
    })


@admin_required
def admin_abonent_edit(request, pk):
    """Admin panel edit abonent."""
    from django.db import IntegrityError
    abonent = get_object_or_404(Abonent, pk=pk)
    
    if request.method == 'POST':
        abonent.pinfl = request.POST.get('pinfl')
        abonent.tuman_id = request.POST.get('tuman')
        abonent.mahalla_id = request.POST.get('mahalla')
        abonent.inspektor_id = request.POST.get('inspektor') or None
        abonent.abonent_kod = request.POST.get('abonent_kod', '').strip() or None
        
        if request.FILES.get('rasm'):
            abonent.rasm = request.FILES.get('rasm')
        
        try:
            abonent.save()
            messages.success(request, f"Abonent '{abonent.pinfl}' yangilandi!")
            return redirect('admin-abonent-list')
        except IntegrityError:
            return render(request, 'admin_custom/abonent_form.html', {
                'abonent': abonent,
                'tumanlar': Tuman.objects.all(),
                'mahallalar': Mahalla.objects.select_related('tuman').all(),
                'inspektorlar': Inspektor.objects.select_related('user', 'tuman').all(),
                'error': f"'{abonent.abonent_kod}' raqami allaqachon mavjud!"
            })
    
    return render(request, 'admin_custom/abonent_form.html', {
        'abonent': abonent,
        'tumanlar': Tuman.objects.all(),
        'mahallalar': Mahalla.objects.select_related('tuman').all(),
        'inspektorlar': Inspektor.objects.select_related('user', 'tuman').all(),
    })


@admin_required
def admin_abonent_delete(request, pk):
    """Admin panel delete abonent."""
    abonent = get_object_or_404(Abonent, pk=pk)
    if request.method == 'POST':
        pinfl = abonent.pinfl
        abonent.delete()
        messages.success(request, f"Abonent '{pinfl}' o'chirildi!")
        return redirect('admin-abonent-list')
    return render(request, 'admin_custom/abonent_delete.html', {'abonent': abonent})


@admin_required
def admin_pinfl_binding(request):
    """Admin page for binding abonent codes to abonents by tuman/mahalla."""
    tumanlar = Tuman.objects.all()
    
    selected_tuman = request.GET.get('tuman')
    selected_mahalla = request.GET.get('mahalla')
    selected_inspektor = request.GET.get('inspektor') # new filter
    
    abonentlar = []
    mahalla_nomi = ''
    filtered_mahallalar = []
    inspektorlar = [] 
    
    if selected_tuman:
        selected_tuman = int(selected_tuman)
        filtered_mahallalar = Mahalla.objects.filter(tuman_id=selected_tuman)
        inspektorlar = Inspektor.objects.filter(tuman_id=selected_tuman).select_related('user')
        
    if selected_mahalla:
        selected_mahalla = int(selected_mahalla)
        mahalla = Mahalla.objects.filter(pk=selected_mahalla).first()
        if mahalla:
            mahalla_nomi = mahalla.nomi
            # Only show abonents without abonent_kod (empty)
            queryset = Abonent.objects.filter(
                mahalla=mahalla
            ).filter(
                Q(abonent_kod__isnull=True) | Q(abonent_kod='')
            )
            
            # Apply inspector filter if selected
            if selected_inspektor:
                try:
                    selected_inspektor = int(selected_inspektor)
                    queryset = queryset.filter(inspektor_id=selected_inspektor)
                except (ValueError, TypeError):
                    pass
            
            abonentlar = queryset.order_by('id')
    
    if request.method == 'POST':
        abonent_ids = request.POST.get('abonent_ids', '')
        kodlar_text = request.POST.get('abonent_kodlar', '')
        mahalla_id = request.POST.get('mahalla_id')
        # inspektor_id removed from POST
        
        if abonent_ids and kodlar_text:
            from django.db import IntegrityError
            ids = [int(x) for x in abonent_ids.split(',') if x.strip()]
            kodlar = [k.strip() for k in kodlar_text.strip().split('\n')]
            
            updated = 0
            errors = []
            for i, abonent_id in enumerate(ids):
                if i < len(kodlar) and kodlar[i]:
                    try:
                        abonent = Abonent.objects.get(pk=abonent_id)
                        abonent.abonent_kod = kodlar[i]
                        abonent.save(update_fields=['abonent_kod'])
                        updated += 1
                    except Abonent.DoesNotExist:
                        pass
                    except IntegrityError:
                        errors.append(f"'{kodlar[i]}' raqami allaqachon mavjud!")
            
            if errors:
                messages.error(request, " ".join(errors))
            if updated > 0:
                messages.success(request, f"{updated} ta abonent raqami saqlandi!")
            
            # Preserve filters in redirect
            redirect_url = f"{request.path}?tuman={selected_tuman}&mahalla={mahalla_id}"
            if selected_inspektor:
                redirect_url += f"&inspektor={selected_inspektor}"
            return redirect(redirect_url)
    
    return render(request, 'admin_custom/pinfl_binding.html', {
        'tumanlar': tumanlar,
        'filtered_mahallalar': filtered_mahallalar,
        'selected_tuman': selected_tuman,
        'selected_mahalla': selected_mahalla,
        'abonentlar': abonentlar,
        'mahalla_nomi': mahalla_nomi,
        'inspektorlar': inspektorlar,
        'selected_inspektor': selected_inspektor,
    })
