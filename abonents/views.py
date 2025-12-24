"""
Abonent views - API endpointlar uchun viewlar.
"""

from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404
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
    search_fields = ['abonent_kod', 'pinfl', 'ism', 'familiya']
    ordering_fields = ['id', 'yaratilgan_vaqt', 'familiya', 'ism']
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
    Rasm bilan birga yuborilishi kerak.
    
    Request body (form-data):
    - abonent_kod: string (required)
    - pasport_seriya: string (required)
    - pasport_raqam: string (required)
    - pinfl: string (required, 14 digits)
    - ism: string (required)
    - familiya: string (required)
    - otasining_ismi: string (optional)
    - tugilgan_sana: date (required, YYYY-MM-DD)
    - jins: string (required, 'erkak' or 'ayol')
    - rasm: file (required, image)
    - manzil: string (optional)
    - telefon: string (optional)
    
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


@api_view(['GET'])
def get_pinfl(request, abonent_kod):
    """
    GET /api/get-pinfl/<abonent_kod>/
    
    Berilgan abonent_kod bo'yicha PINFL ni qaytaradi.
    
    Response:
    - 200: {"pinfl": "12345678901234"}
    - 404: Abonent topilmadi
    """
    try:
        abonent = Abonent.objects.get(abonent_kod=abonent_kod)
        return Response(
            {'pinfl': abonent.pinfl},
            status=status.HTTP_200_OK
        )
    except Abonent.DoesNotExist:
        return Response(
            {
                'error': "Abonent topilmadi",
                'abonent_kod': abonent_kod
            },
            status=status.HTTP_404_NOT_FOUND
        )


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

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from django import forms


class AbonentForm(forms.ModelForm):
    """Abonent form for inspector frontend."""
    
    class Meta:
        model = Abonent
        fields = [
            'abonent_kod', 'pinfl', 'pasport_seriya', 'pasport_raqam',
            'familiya', 'ism', 'otasining_ismi', 'tugilgan_sana', 'jins',
            'telefon', 'manzil', 'rasm'
        ]
        widgets = {
            'tugilgan_sana': forms.DateInput(attrs={'type': 'date'}),
            'manzil': forms.Textarea(attrs={'rows': 3}),
        }


def inspector_login(request):
    """Inspector login view."""
    if request.user.is_authenticated:
        return redirect('inspector-dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f"Xush kelibsiz, {user.get_full_name() or user.username}!")
            return redirect('inspector-dashboard')
        else:
            messages.error(request, "Login yoki parol noto'g'ri!")
    
    return render(request, 'inspector/login.html')


def inspector_logout(request):
    """Inspector logout view."""
    logout(request)
    messages.info(request, "Tizimdan chiqdingiz.")
    return redirect('inspector-login')


@login_required(login_url='inspector-login')
def inspector_dashboard(request):
    """Inspector dashboard - stats and recent abonents."""
    today = timezone.now().date()
    
    context = {
        'today': today,
        'total_abonents': Abonent.objects.count(),
        'today_added': Abonent.objects.filter(yaratilgan_vaqt__date=today).count(),
        'recent_abonents': Abonent.objects.all()[:5],
    }
    return render(request, 'inspector/dashboard.html', context)


@login_required(login_url='inspector-login')
def inspector_abonent_list(request):
    """Abonent list with search and pagination."""
    search_query = request.GET.get('q', '')
    abonents = Abonent.objects.all()
    
    if search_query:
        abonents = abonents.filter(
            Q(abonent_kod__icontains=search_query) |
            Q(pinfl__icontains=search_query) |
            Q(ism__icontains=search_query) |
            Q(familiya__icontains=search_query) |
            Q(telefon__icontains=search_query)
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


@login_required(login_url='inspector-login')
def inspector_abonent_add(request):
    """Add new abonent."""
    if request.method == 'POST':
        form = AbonentForm(request.POST, request.FILES)
        if form.is_valid():
            abonent = form.save()
            messages.success(request, f"Abonent '{abonent.toliq_ism}' muvaffaqiyatli qo'shildi!")
            return redirect('inspector-abonent-list')
    else:
        form = AbonentForm()
    
    return render(request, 'inspector/abonent_form.html', {'form': form})


@login_required(login_url='inspector-login')
def inspector_abonent_edit(request, pk):
    """Edit existing abonent."""
    abonent = get_object_or_404(Abonent, pk=pk)
    
    if request.method == 'POST':
        form = AbonentForm(request.POST, request.FILES, instance=abonent)
        if form.is_valid():
            abonent = form.save()
            messages.success(request, f"Abonent '{abonent.toliq_ism}' yangilandi!")
            return redirect('inspector-abonent-list')
    else:
        form = AbonentForm(instance=abonent)
    
    return render(request, 'inspector/abonent_form.html', {'form': form})


@login_required(login_url='inspector-login')
def inspector_abonent_delete(request, pk):
    """Delete abonent confirmation."""
    abonent = get_object_or_404(Abonent, pk=pk)
    
    if request.method == 'POST':
        name = abonent.toliq_ism
        abonent.delete()
        messages.success(request, f"Abonent '{name}' o'chirildi!")
        return redirect('inspector-abonent-list')
    
    return render(request, 'inspector/abonent_delete.html', {'abonent': abonent})

