"""
Views for तपासणी मेमो व्यवस्थापन प्रणाली
Dashboard, Login, Master CRUD, Inspection CRUD, Reports
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, Q, F
from django.db.models.functions import TruncMonth, TruncYear
from django.http import JsonResponse
from datetime import date, datetime
from decimal import Decimal

from .models import (
    InspectionMemo, OfficeName, InspectionYear, DocumentType,
    ApprovalStatus, Taluka, PropertyType, GroupSurvey, Unit,
    CompetentAuthority, Remark, LitigationStatus, OfficeInformation,
    NoticeTracking, PenaltyRate
)
from .forms import InspectionMemoForm, MasterForm


# ============================================================
# LOGIN / LOGOUT
# ============================================================

def login_view(request):
    """Professional login page with project info"""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'यशस्वीरित्या लॉगिन झाले!')
            return redirect('dashboard')
        else:
            messages.error(request, 'चुकीचे वापरकर्तानाव किंवा पासवर्ड!')

    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    messages.info(request, 'आपण यशस्वीरित्या लॉगआउट झालात.')
    return redirect('login')


# ============================================================
# DASHBOARD
# ============================================================

@login_required
def dashboard(request):
    """Main dashboard with summary statistics"""
    memos = InspectionMemo.objects.all()

    # Overall counts
    total_cases = memos.count()
    pending_cases = memos.filter(balance_amount__gt=0).count()
    recovered_cases = memos.filter(balance_amount__lte=0, total_amount__gt=0).count()

    # Total amounts
    total_short_sum = memos.aggregate(s=Sum('total_short'))['s'] or 0
    total_penalty_sum = memos.aggregate(s=Sum('penalty_amount'))['s'] or 0
    total_amount_sum = memos.aggregate(s=Sum('total_amount'))['s'] or 0
    recovered_sum = memos.aggregate(s=Sum('recovered_amount'))['s'] or 0
    balance_sum = memos.aggregate(s=Sum('balance_amount'))['s'] or 0

    # Type-wise breakdown
    type_summary = []
    for code, label in InspectionMemo.INSPECTION_TYPES:
        qs = memos.filter(inspection_type=code)
        type_summary.append({
            'code': code,
            'label': label,
            'total': qs.count(),
            'pending': qs.filter(balance_amount__gt=0).count(),
            'recovered': qs.filter(balance_amount__lte=0, total_amount__gt=0).count(),
            'total_amount': qs.aggregate(s=Sum('total_amount'))['s'] or 0,
            'recovered_amount': qs.aggregate(s=Sum('recovered_amount'))['s'] or 0,
            'balance': qs.aggregate(s=Sum('balance_amount'))['s'] or 0,
        })

    # Monthly summary (current year)
    current_year = date.today().year
    monthly_data = (
        memos
        .filter(created_at__year=current_year)
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(
            count=Count('id'),
            total=Sum('total_amount'),
            recovered=Sum('recovered_amount'),
        )
        .order_by('month')
    )

    # Yearly summary
    yearly_data = (
        memos
        .annotate(year=TruncYear('created_at'))
        .values('year')
        .annotate(
            count=Count('id'),
            total=Sum('total_amount'),
            recovered=Sum('recovered_amount'),
        )
        .order_by('-year')
    )

    context = {
        'total_cases': total_cases,
        'pending_cases': pending_cases,
        'recovered_cases': recovered_cases,
        'total_short_sum': total_short_sum,
        'total_penalty_sum': total_penalty_sum,
        'total_amount_sum': total_amount_sum,
        'recovered_sum': recovered_sum,
        'balance_sum': balance_sum,
        'type_summary': type_summary,
        'monthly_data': monthly_data,
        'yearly_data': yearly_data,
        'inspection_types': InspectionMemo.INSPECTION_TYPES,
    }
    return render(request, 'dashboard.html', context)


# ============================================================
# INSPECTION MEMO CRUD
# ============================================================

@login_required
def inspection_list(request):
    """List all inspection memos with search and type filter"""
    memos = InspectionMemo.objects.select_related(
        'office_name', 'inspection_year', 'approval_status', 'remark'
    ).all()

    # Filter by inspection type
    inspection_type = request.GET.get('type', '')
    if inspection_type:
        memos = memos.filter(inspection_type=inspection_type)

    # Filter by year
    year_id = request.GET.get('year', '')
    if year_id:
        memos = memos.filter(inspection_year_id=year_id)

    # Filter by office
    office_id = request.GET.get('office', '')
    if office_id:
        memos = memos.filter(office_name_id=office_id)

    # Search
    search = request.GET.get('search', '')
    if search:
        search_q = Q(deed_number__icontains=search) | \
                   Q(executant_name__icontains=search) | \
                   Q(claimant_name__icontains=search) | \
                   Q(memo_number__icontains=search) | \
                   Q(village__icontains=search)
        
        # Add paragraph search if numeric
        if search.isdigit():
            search_q |= Q(paragraph_number=search)
            
        memos = memos.filter(search_q)

    # Calculate totals
    total_stamp_duty = sum(memo.stamp_duty_short for memo in memos)
    total_reg_fee = sum(memo.reg_fee_short for memo in memos)
    total_amount = sum(memo.total_amount for memo in memos)
    total_balance = sum(memo.balance_amount for memo in memos)

    # Get selected labels
    selected_type_label = ''
    if inspection_type:
        for code, label in InspectionMemo.INSPECTION_TYPES:
            if code == inspection_type:
                selected_type_label = label
                break

    selected_year_label = ''
    if year_id:
        try:
            year_obj = InspectionYear.objects.get(id=year_id)
            selected_year_label = year_obj.year
        except:
            pass

    selected_office_name = ''
    if office_id:
        try:
            office_obj = OfficeName.objects.get(id=office_id)
            selected_office_name = office_obj.name
        except:
            pass

    context = {
        'memos': memos,
        'inspection_types': InspectionMemo.INSPECTION_TYPES,
        'offices': OfficeName.objects.filter(is_active=True),
        'years': InspectionYear.objects.filter(is_active=True),
        'selected_type': inspection_type,
        'selected_year': year_id,
        'selected_office': office_id,
        'search': search,
        'total_stamp_duty': total_stamp_duty,
        'total_reg_fee': total_reg_fee,
        'total_amount': total_amount,
        'total_balance': total_balance,
        'selected_type_label': selected_type_label,
        'selected_year_label': selected_year_label,
        'selected_office_name': selected_office_name,
    }
    return render(request, 'inspection/list.html', context)


@login_required
def inspection_create(request):
    """Create new inspection memo"""
    if request.method == 'POST':
        form = InspectionMemoForm(request.POST)
        if form.is_valid():
            memo = form.save()
            messages.success(request, 'माहिती यशस्वीरीत्या जतन झाली')
            return redirect('inspection_list')
        else:
            # Show detailed error message to user
            error_list = []
            for field, errors in form.errors.items():
                field_label = form.fields[field].label if field in form.fields else field
                error_list.append(f"{field_label}: {', '.join(errors)}")
            error_message = "कृपया सर्व आवश्यक माहिती भरा. " + " | ".join(error_list)
            messages.error(request, error_message)
    else:
        form = InspectionMemoForm()

    context = {
        'form': form,
        'title': 'नवीन तपासणी मेमो',
        'is_edit': False,
    }
    return render(request, 'inspection/form.html', context)


@login_required
def inspection_edit(request, pk):
    """Edit existing inspection memo"""
    memo = get_object_or_404(InspectionMemo, pk=pk)

    if request.method == 'POST':
        form = InspectionMemoForm(request.POST, instance=memo)
        if form.is_valid():
            form.save()
            messages.success(request, 'तपासणी मेमो यशस्वीरित्या अपडेट झाला!')
            return redirect('inspection_list')
        else:
            messages.error(request, 'कृपया सर्व आवश्यक माहिती भरा.')
    else:
        form = InspectionMemoForm(instance=memo)

    context = {
        'form': form,
        'title': 'तपासणी मेमो संपादन',
        'is_edit': True,
        'memo': memo,
    }
    return render(request, 'inspection/form.html', context)


@login_required
def inspection_detail(request, pk):
    """View inspection memo details"""
    memo = get_object_or_404(
        InspectionMemo.objects.select_related(
            'office_name', 'inspection_year', 'taluka', 'document_type',
            'property_type', 'group_survey', 'unit', 'approval_status',
            'competent_authority', 'litigation_status', 'remark'
        ), pk=pk
    )
    return render(request, 'inspection/detail.html', {'memo': memo})


@login_required
def inspection_delete(request, pk):
    """Delete inspection memo"""
    memo = get_object_or_404(InspectionMemo, pk=pk)
    if request.method == 'POST':
        deed = memo.deed_number
        memo.delete()
        messages.success(request, f'तपासणी मेमो हटवला! (दस्त क्र. {deed})')
        return redirect('inspection_list')
    return render(request, 'inspection/confirm_delete.html', {'memo': memo})


# ============================================================
# MASTER TABLE CRUD (Generic for all 11 tables)
# ============================================================

# Mapping of master table slugs to models
MASTER_MODELS = {
    'office': {'model': OfficeName, 'title': 'कार्यालयाचे नाव', 'icon': 'bi-building'},
    'year': {'model': InspectionYear, 'title': 'तपासणी वर्ष', 'icon': 'bi-calendar'},
    'doctype': {'model': DocumentType, 'title': 'दस्तऐवज प्रकार', 'icon': 'bi-file-earmark-text'},
    'approval': {'model': ApprovalStatus, 'title': 'मंजुरी स्थिती', 'icon': 'bi-check-circle'},
    'taluka': {'model': Taluka, 'title': 'तालुका', 'icon': 'bi-geo-alt'},
    'property': {'model': PropertyType, 'title': 'मालमत्ता प्रकार', 'icon': 'bi-house'},
    'groupsurvey': {'model': GroupSurvey, 'title': 'गट/सर्व्हे', 'icon': 'bi-map'},
    'unit': {'model': Unit, 'title': 'एकक', 'icon': 'bi-rulers'},
    'authority': {'model': CompetentAuthority, 'title': 'सक्षम प्राधिकारी', 'icon': 'bi-person-badge'},
    'remark': {'model': Remark, 'title': 'शेरा', 'icon': 'bi-chat-text'},
    'litigation': {'model': LitigationStatus, 'title': 'न्यायप्रविष्ट स्थिती', 'icon': 'bi-briefcase'},
    'penaltyrate': {'model': PenaltyRate, 'title': 'शास्तीचा दर', 'icon': 'bi-percent'},
}


@login_required
def master_dashboard(request):
    """Dashboard showing all master tables"""
    masters = []
    for slug, info in MASTER_MODELS.items():
        masters.append({
            'slug': slug,
            'title': info['title'],
            'icon': info['icon'],
            'count': info['model'].objects.filter(is_active=True).count(),
        })
    return render(request, 'masters/dashboard.html', {'masters': masters})


@login_required
def master_list(request, slug):
    """List entries for a master table"""
    if slug not in MASTER_MODELS:
        messages.error(request, 'अवैध मास्टर टेबल!')
        return redirect('master_dashboard')

    info = MASTER_MODELS[slug]
    model = info['model']
    items = model.objects.all().order_by('-is_active', 'name' if slug != 'year' else '-year')

    # For InspectionYear, the field is 'year' not 'name'
    field_name = 'year' if slug == 'year' else 'name'

    context = {
        'items': items,
        'slug': slug,
        'title': info['title'],
        'icon': info['icon'],
        'field_name': field_name,
    }
    return render(request, 'masters/list.html', context)


@login_required
def master_create(request, slug):
    """Create a new master entry"""
    if slug not in MASTER_MODELS:
        messages.error(request, 'अवैध मास्टर टेबल!')
        return redirect('master_dashboard')

    info = MASTER_MODELS[slug]
    model = info['model']
    field_name = 'year' if slug == 'year' else 'name'

    if request.method == 'POST':
        value = request.POST.get('value', '').strip()
        if value:
            kwargs = {field_name: value}
            obj, created = model.objects.get_or_create(**kwargs)
            if created:
                messages.success(request, f'"{value}" यशस्वीरित्या जोडले!')
            else:
                # Reactivate if was deactivated
                if not obj.is_active:
                    obj.is_active = True
                    obj.save()
                    messages.info(request, f'"{value}" पुन्हा सक्रिय केले.')
                else:
                    messages.warning(request, f'"{value}" आधीपासूनच अस्तित्वात आहे.')
        else:
            messages.error(request, 'कृपया नाव प्रविष्ट करा.')
        return redirect('master_list', slug=slug)

    context = {
        'slug': slug,
        'title': info['title'],
        'field_name': field_name,
        'is_edit': False,
    }
    return render(request, 'masters/form.html', context)


@login_required
def master_edit(request, slug, pk):
    """Edit a master entry"""
    if slug not in MASTER_MODELS:
        messages.error(request, 'अवैध मास्टर टेबल!')
        return redirect('master_dashboard')

    info = MASTER_MODELS[slug]
    model = info['model']
    item = get_object_or_404(model, pk=pk)
    field_name = 'year' if slug == 'year' else 'name'

    if request.method == 'POST':
        value = request.POST.get('value', '').strip()
        if value:
            setattr(item, field_name, value)
            item.save()
            messages.success(request, f'"{value}" यशस्वीरित्या अपडेट झाले!')
        else:
            messages.error(request, 'कृपया नाव प्रविष्ट करा.')
        return redirect('master_list', slug=slug)

    context = {
        'slug': slug,
        'title': info['title'],
        'field_name': field_name,
        'item': item,
        'is_edit': True,
        'current_value': getattr(item, field_name),
    }
    return render(request, 'masters/form.html', context)


@login_required
def master_toggle(request, slug, pk):
    """Toggle active/inactive for a master entry"""
    if slug not in MASTER_MODELS:
        return redirect('master_dashboard')

    info = MASTER_MODELS[slug]
    model = info['model']
    item = get_object_or_404(model, pk=pk)
    item.is_active = not item.is_active
    item.save()

    status = "सक्रिय" if item.is_active else "निष्क्रिय"
    messages.info(request, f'स्थिती बदलली: {status}')
    return redirect('master_list', slug=slug)


# ============================================================
# REPORTS
# ============================================================

@login_required
def reports_dashboard(request):
    """Reports landing page"""
    context = {
        'inspection_types': InspectionMemo.INSPECTION_TYPES,
        'offices': OfficeName.objects.filter(is_active=True),
        'years': InspectionYear.objects.filter(is_active=True),
    }
    return render(request, 'reports/dashboard.html', context)


def _apply_report_filters(queryset, request):
    """Common filter logic for all reports"""
    inspection_type = request.GET.get('type', '')
    year_id = request.GET.get('year', '')
    office_id = request.GET.get('office', '')

    if inspection_type:
        queryset = queryset.filter(inspection_type=inspection_type)
    if year_id:
        queryset = queryset.filter(inspection_year_id=year_id)
    if office_id:
        queryset = queryset.filter(office_name_id=office_id)

    return queryset, {
        'selected_type': inspection_type,
        'selected_year': year_id,
        'selected_office': office_id,
    }


@login_required
def report_pending(request):
    """Pending cases report (all + type wise)"""
    memos = InspectionMemo.objects.filter(balance_amount__gt=0).select_related(
        'office_name', 'inspection_year', 'approval_status', 'remark'
    )
    memos, filters = _apply_report_filters(memos, request)

    # Type-wise summary
    type_summary = []
    for code, label in InspectionMemo.INSPECTION_TYPES:
        qs = memos.filter(inspection_type=code)
        count = qs.count()
        if count > 0:
            type_summary.append({
                'label': label,
                'count': count,
                'total': qs.aggregate(s=Sum('total_amount'))['s'] or 0,
                'balance': qs.aggregate(s=Sum('balance_amount'))['s'] or 0,
            })

    totals = memos.aggregate(
        total_count=Count('id'),
        total_amount=Sum('total_amount'),
        total_balance=Sum('balance_amount'),
    )

    context = {
        'memos': memos,
        'type_summary': type_summary,
        'totals': totals,
        'report_title': 'प्रलंबित प्रकरणे अहवाल',
        'inspection_types': InspectionMemo.INSPECTION_TYPES,
        'offices': OfficeName.objects.filter(is_active=True),
        'years': InspectionYear.objects.filter(is_active=True),
        **filters,
    }
    return render(request, 'reports/pending.html', context)


@login_required
def report_recovered(request):
    """Recovered cases report"""
    memos = InspectionMemo.objects.filter(
        balance_amount__lte=0, total_amount__gt=0
    ).select_related(
        'office_name', 'inspection_year', 'approval_status', 'remark'
    )
    memos, filters = _apply_report_filters(memos, request)

    type_summary = []
    for code, label in InspectionMemo.INSPECTION_TYPES:
        qs = memos.filter(inspection_type=code)
        count = qs.count()
        if count > 0:
            type_summary.append({
                'label': label,
                'count': count,
                'total': qs.aggregate(s=Sum('total_amount'))['s'] or 0,
                'recovered': qs.aggregate(s=Sum('recovered_amount'))['s'] or 0,
            })

    totals = memos.aggregate(
        total_count=Count('id'),
        total_amount=Sum('total_amount'),
        total_recovered=Sum('recovered_amount'),
    )

    context = {
        'memos': memos,
        'type_summary': type_summary,
        'totals': totals,
        'report_title': 'वसुली झालेली प्रकरणे अहवाल',
        'inspection_types': InspectionMemo.INSPECTION_TYPES,
        'offices': OfficeName.objects.filter(is_active=True),
        'years': InspectionYear.objects.filter(is_active=True),
        **filters,
    }
    return render(request, 'reports/recovered.html', context)


@login_required
def report_monthly(request):
    """Monthly recovery report"""
    memos = InspectionMemo.objects.all()
    memos, filters = _apply_report_filters(memos, request)

    monthly = (
        memos
        .annotate(month=TruncMonth('execution_date'))
        .values('month')
        .annotate(
            count=Count('id'),
            total_short=Sum('total_short'),
            total_penalty=Sum('penalty_amount'),
            total_amount=Sum('total_amount'),
            total_recovered=Sum('recovered_amount'),
            total_balance=Sum('balance_amount'),
        )
        .order_by('-month')
    )

    context = {
        'monthly': monthly,
        'report_title': 'मासिक वसुली अहवाल',
        'inspection_types': InspectionMemo.INSPECTION_TYPES,
        'offices': OfficeName.objects.filter(is_active=True),
        'years': InspectionYear.objects.filter(is_active=True),
        **filters,
    }
    return render(request, 'reports/monthly.html', context)


@login_required
def report_yearly(request):
    """Yearly recovery report"""
    memos = InspectionMemo.objects.all()
    memos, filters = _apply_report_filters(memos, request)

    yearly = (
        memos
        .annotate(year=TruncYear('execution_date'))
        .values('year')
        .annotate(
            count=Count('id'),
            total_short=Sum('total_short'),
            total_penalty=Sum('penalty_amount'),
            total_amount=Sum('total_amount'),
            total_recovered=Sum('recovered_amount'),
            total_balance=Sum('balance_amount'),
        )
        .order_by('-year')
    )

    context = {
        'yearly': yearly,
        'report_title': 'वार्षिक वसुली अहवाल',
        'inspection_types': InspectionMemo.INSPECTION_TYPES,
        'offices': OfficeName.objects.filter(is_active=True),
        'years': InspectionYear.objects.filter(is_active=True),
        **filters,
    }
    return render(request, 'reports/yearly.html', context)


@login_required
def report_office_pending(request):
    """Office-wise pending report"""
    memos = InspectionMemo.objects.filter(balance_amount__gt=0)
    memos, filters = _apply_report_filters(memos, request)

    office_data = (
        memos
        .values('office_name__name')
        .annotate(
            count=Count('id'),
            total_amount=Sum('total_amount'),
            total_balance=Sum('balance_amount'),
        )
        .order_by('office_name__name')
    )

    context = {
        'office_data': office_data,
        'report_title': 'कार्यालयनिहाय प्रलंबित अहवाल',
        'inspection_types': InspectionMemo.INSPECTION_TYPES,
        'offices': OfficeName.objects.filter(is_active=True),
        'years': InspectionYear.objects.filter(is_active=True),
        **filters,
    }
    return render(request, 'reports/office_pending.html', context)


@login_required
def report_office_recovered(request):
    """Office-wise recovery report"""
    memos = InspectionMemo.objects.filter(balance_amount__lte=0, total_amount__gt=0)
    memos, filters = _apply_report_filters(memos, request)

    office_data = (
        memos
        .values('office_name__name')
        .annotate(
            count=Count('id'),
            total_amount=Sum('total_amount'),
            total_recovered=Sum('recovered_amount'),
        )
        .order_by('office_name__name')
    )

    context = {
        'office_data': office_data,
        'report_title': 'कार्यालयनिहाय वसुली अहवाल',
        'inspection_types': InspectionMemo.INSPECTION_TYPES,
        'offices': OfficeName.objects.filter(is_active=True),
        'years': InspectionYear.objects.filter(is_active=True),
        **filters,
    }
    return render(request, 'reports/office_recovered.html', context)


@login_required
def report_office_month_pending(request):
    """Office + Month wise pending report"""
    memos = InspectionMemo.objects.filter(balance_amount__gt=0)
    memos, filters = _apply_report_filters(memos, request)

    data = (
        memos
        .annotate(month=TruncMonth('execution_date'))
        .values('office_name__name', 'month')
        .annotate(
            count=Count('id'),
            total_amount=Sum('total_amount'),
            total_balance=Sum('balance_amount'),
        )
        .order_by('office_name__name', '-month')
    )

    context = {
        'data': data,
        'report_title': 'कार्यालय + मासिक प्रलंबित अहवाल',
        'inspection_types': InspectionMemo.INSPECTION_TYPES,
        'offices': OfficeName.objects.filter(is_active=True),
        'years': InspectionYear.objects.filter(is_active=True),
        **filters,
    }
    return render(request, 'reports/office_month_pending.html', context)


@login_required
def report_office_year_recovery(request):
    """Office + Year wise recovery report"""
    memos = InspectionMemo.objects.all()
    memos, filters = _apply_report_filters(memos, request)

    data = (
        memos
        .annotate(year=TruncYear('execution_date'))
        .values('office_name__name', 'year')
        .annotate(
            count=Count('id'),
            total_amount=Sum('total_amount'),
            total_recovered=Sum('recovered_amount'),
            total_balance=Sum('balance_amount'),
        )
        .order_by('office_name__name', '-year')
    )

    context = {
        'data': data,
        'report_title': 'कार्यालय + वार्षिक वसुली अहवाल',
        'inspection_types': InspectionMemo.INSPECTION_TYPES,
        'offices': OfficeName.objects.filter(is_active=True),
        'years': InspectionYear.objects.filter(is_active=True),
        **filters,
    }
    return render(request, 'reports/office_year_recovery.html', context)


# ============================================================
# API - Auto Calculation (AJAX)
# ============================================================

@login_required
def api_calculate(request):
    """AJAX endpoint for auto calculation"""
    try:
        stamp_duty_actual = Decimal(request.GET.get('stamp_duty_actual', '0') or '0')
        stamp_duty_collected = Decimal(request.GET.get('stamp_duty_collected', '0') or '0')
        reg_fee_actual = Decimal(request.GET.get('reg_fee_actual', '0') or '0')
        reg_fee_collected = Decimal(request.GET.get('reg_fee_collected', '0') or '0')
        recovered_stamp_duty = Decimal(request.GET.get('recovered_stamp_duty', '0') or '0')
        recovered_reg_fee = Decimal(request.GET.get('recovered_reg_fee', '0') or '0')
        recovered_penalty = Decimal(request.GET.get('recovered_penalty', '0') or '0')
        execution_date_str = request.GET.get('execution_date', '')

        stamp_duty_short = max(Decimal('0'), stamp_duty_actual - stamp_duty_collected)
        reg_fee_short = max(Decimal('0'), reg_fee_actual - reg_fee_collected)
        total_short = stamp_duty_short + reg_fee_short

        total_months = 0
        if execution_date_str:
            try:
                exec_date = datetime.strptime(execution_date_str, '%Y-%m-%d').date()
                diff = date.today() - exec_date
                days = max(0, diff.days)
                import math
                total_months = math.ceil(days / 30) if days > 0 else 0
            except ValueError:
                pass

        penalty = total_short * Decimal('0.02') * Decimal(str(total_months))
        total_amount = total_short + penalty

        # Individual balances
        balance_stamp_duty = max(Decimal('0'), stamp_duty_short - recovered_stamp_duty)
        balance_reg_fee = max(Decimal('0'), reg_fee_short - recovered_reg_fee)
        balance_penalty = max(Decimal('0'), penalty - recovered_penalty)

        # Total recovered and balance
        total_recovered = recovered_stamp_duty + recovered_reg_fee + recovered_penalty
        balance_amount = total_amount - total_recovered

        return JsonResponse({
            'stamp_duty_short': str(stamp_duty_short),
            'reg_fee_short': str(reg_fee_short),
            'total_short': str(total_short),
            'total_months': total_months,
            'penalty_amount': str(penalty),
            'total_amount': str(total_amount),
            'balance_stamp_duty': str(balance_stamp_duty),
            'balance_reg_fee': str(balance_reg_fee),
            'balance_penalty': str(balance_penalty),
            'balance_amount': str(balance_amount),
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


# ============================================================
# OFFICE INFORMATION CRUD
# ============================================================

@login_required
def office_info_list(request):
    """List all office information"""
    offices = OfficeInformation.objects.all().order_by('-is_active', '-created_at')
    return render(request, 'inspection/office_info_list.html', {'offices': offices})


@login_required
def office_info_create(request):
    """Create or edit office information"""
    # Get existing office info if available
    office = OfficeInformation.objects.first()
    
    if request.method == 'POST':
        office_name = request.POST.get('office_name')
        office_address = request.POST.get('office_address')
        office_email = request.POST.get('office_email')
        office_phone = request.POST.get('office_phone')
        district = request.POST.get('district')
        division_name = request.POST.get('division_name')
        divisional_office_name = request.POST.get('divisional_office_name')
        divisional_office_address = request.POST.get('divisional_office_address')
        designation_01 = request.POST.get('designation_01')
        designation_02 = request.POST.get('designation_02')
        working_officer_name = request.POST.get('working_officer_name')
        administrative_officer_name = request.POST.get('administrative_officer_name')
        senior_clerk_name = request.POST.get('senior_clerk_name')
        junior_clerk_name = request.POST.get('junior_clerk_name')

        if office_name:
            if office:
                # Update existing record
                office.office_name = office_name
                office.office_address = office_address
                office.office_email = office_email
                office.office_phone = office_phone
                office.district = district
                office.division_name = division_name
                office.divisional_office_name = divisional_office_name
                office.divisional_office_address = divisional_office_address
                office.designation_01 = designation_01
                office.designation_02 = designation_02
                office.working_officer_name = working_officer_name
                office.administrative_officer_name = administrative_officer_name
                office.senior_clerk_name = senior_clerk_name
                office.junior_clerk_name = junior_clerk_name
                office.save()
                messages.success(request, 'कार्यालयाची माहिती यशस्वीरित्या अपडेट केली गेली!')
            else:
                # Create new record
                OfficeInformation.objects.create(
                    office_name=office_name,
                    office_address=office_address,
                    office_email=office_email,
                    office_phone=office_phone,
                    district=district,
                    division_name=division_name,
                    divisional_office_name=divisional_office_name,
                    divisional_office_address=divisional_office_address,
                    designation_01=designation_01,
                    designation_02=designation_02,
                    working_officer_name=working_officer_name,
                    administrative_officer_name=administrative_officer_name,
                    senior_clerk_name=senior_clerk_name,
                    junior_clerk_name=junior_clerk_name
                )
                messages.success(request, 'कार्यालयाची माहिती यशस्वीरित्या जोडली गेली!')
            return redirect('office_info_list')
        else:
            messages.error(request, 'कार्यालयाचे नाव आवश्यक आहे!')

    # Pass office data to template for pre-filling form
    context = {'office': office}
    return render(request, 'inspection/office_info_form.html', context)


@login_required
def office_info_edit(request, pk):
    """Edit office information"""
    office = get_object_or_404(OfficeInformation, pk=pk)

    if request.method == 'POST':
        office.office_name = request.POST.get('office_name')
        office.office_address = request.POST.get('office_address')
        office.office_email = request.POST.get('office_email')
        office.office_phone = request.POST.get('office_phone')
        office.district = request.POST.get('district')
        office.division_name = request.POST.get('division_name')
        office.divisional_office_name = request.POST.get('divisional_office_name')
        office.divisional_office_address = request.POST.get('divisional_office_address')
        office.designation_01 = request.POST.get('designation_01')
        office.designation_02 = request.POST.get('designation_02')
        office.working_officer_name = request.POST.get('working_officer_name')
        office.administrative_officer_name = request.POST.get('administrative_officer_name')
        office.senior_clerk_name = request.POST.get('senior_clerk_name')
        office.junior_clerk_name = request.POST.get('junior_clerk_name')
        office.save()

        messages.success(request, 'कार्यालयाची माहिती यशस्वीरित्या अपडेट केली गेली!')
        return redirect('office_info_list')

    return render(request, 'inspection/office_info_form.html', {'office': office})


@login_required
def office_info_delete(request, pk):
    """Delete office information"""
    office = get_object_or_404(OfficeInformation, pk=pk)
    office.delete()
    messages.success(request, 'कार्यालयाची माहिती यशस्वीरित्या हटवली गेली!')
    return redirect('office_info_list')


@login_required
def office_info_toggle(request, pk):
    """Toggle active/inactive for office information"""
    office = get_object_or_404(OfficeInformation, pk=pk)
    office.is_active = not office.is_active
    office.save()
    status = 'सक्रिय' if office.is_active else 'निष्क्रिय'
    messages.success(request, f'कार्यालयाची माहिती {status} केली गेली!')
    return redirect('office_info_list')


# ============================================================
# NOTICE AND LETTER GENERATION
# ============================================================

@login_required
def generate_notice(request, pk, notice_type):
    """Generate notice HTML preview"""
    memo = get_object_or_404(InspectionMemo, pk=pk)

    # Get active office information
    office = OfficeInformation.objects.filter(is_active=True).first()
    if not office:
        messages.error(request, 'कृपया प्रथम कार्यालयाची माहिती टाका.')
        return redirect('inspection_detail', pk=pk)

    # Template mapping
    template_map = {
        'first': 'inspection/notice_templates/first_notice.html',
        'second': 'inspection/notice_templates/second_notice.html',
        'hearing': 'inspection/notice_templates/hearing_notice.html',
    }

    template = template_map.get(notice_type)
    if not template:
        messages.error(request, 'अवैध नोटीस प्रकार!')
        return redirect('inspection_detail', pk=pk)

    # Get notice date from tracking or use current date
    from datetime import date
    notice_date = date.today().strftime("%d/%m/%Y")
    
    # For final order, fetch second and hearing notice dates
    if notice_type == 'final_order':
        from django.utils import timezone
        second_notice = NoticeTracking.objects.filter(
            memo=memo, notice_type='SECOND'
        ).first()
        hearing_notice = NoticeTracking.objects.filter(
            memo=memo, notice_type='HEARING'
        ).first()
        
        context = {
            'memo': memo,
            'office': office,
            'second_notice_date': second_notice.issue_date if second_notice else None,
            'hearing_notice_date': hearing_notice.issue_date if hearing_notice else None,
            'today': timezone.now(),
        }
        return render(request, template, context)

    # Dynamic dates for notices from tracking
    first_notice_date = None
    second_notice_date = None
    
    if notice_type in ['second', 'hearing']:
        first_notice = memo.notices.filter(notice_type='FIRST').order_by('issue_date').first()
        if first_notice and first_notice.issue_date:
            first_notice_date = first_notice.issue_date.strftime("%d/%m/%Y")
            
    if notice_type == 'hearing':
        second_notice = memo.notices.filter(notice_type='SECOND').order_by('issue_date').first()
        if second_notice and second_notice.issue_date:
            second_notice_date = second_notice.issue_date.strftime("%d/%m/%Y")

    # Convert amount to words (digit by digit conversion)
    def number_to_marathi_digits(amount):
        digit_map = {
            '0': 'शून्य',
            '1': 'एक',
            '2': 'दोन',
            '3': 'तीन',
            '4': 'चार',
            '5': 'पाच',
            '6': 'सहा',
            '7': 'सात',
            '8': 'आठ',
            '9': 'नऊ'
        }
        amount_str = str(int(amount))
        marathi_digits = [digit_map.get(d, d) for d in amount_str]
        return ', '.join(marathi_digits) + ' मात्र'

    amount_in_words = number_to_marathi_digits(memo.total_short)

    context = {
        'memo': memo,
        'office': office,
        'notice_date': notice_date,
        'first_notice_date': first_notice_date,
        'second_notice_date': second_notice_date,
        'amount_in_words': amount_in_words,
    }

    return render(request, template, context)


@login_required
def generate_letter(request, pk, letter_type):
    """Generate letter HTML preview"""
    memo = get_object_or_404(InspectionMemo, pk=pk)
    
    # Get active office information
    office = OfficeInformation.objects.filter(is_active=True).first()
    if not office:
        messages.error(request, 'कृपया प्रथम कार्यालयाची माहिती टाका.')
        return redirect('inspection_detail', pk=pk)
    
    # Template mapping
    template_map = {
        'full_payment': 'inspection/letter_templates/full_payment_letter.html',
        'full_payment_note': 'inspection/letter_templates/full_payment_note.html',
        'partial_payment': 'inspection/letter_templates/partial_payment_letter.html',
        'partial_payment_note': 'inspection/letter_templates/partial_payment_note.html',
    }
    
    template = template_map.get(letter_type)
    if not template:
        messages.error(request, 'अवैध पत्र प्रकार!')
        return redirect('inspection_detail', pk=pk)
    
    def number_to_marathi_digits(amount):
        digit_map = {
            '0': 'शून्य', '1': 'एक', '2': 'दोन', '3': 'तीन', '4': 'चार',
            '5': 'पाच', '6': 'सहा', '7': 'सात', '8': 'आठ', '9': 'नऊ'
        }
        amount_str = str(int(amount))
        marathi_digits = [digit_map.get(d, d) for d in amount_str]
        return ', '.join(marathi_digits) + ' मात्र'

    from .forms import InspectionMemoForm
    from django.utils import timezone
    
    # Initialize form with memo instance to provide .value in template
    form_instance = InspectionMemoForm(instance=memo)
    
    context = {
        'memo': memo,
        'form': form_instance,
        'office': office,
        'display_stamp_duty_short': memo.stamp_duty_short,
        'display_reg_fee_short': memo.reg_fee_short,
        'display_penalty_amount': memo.penalty_amount,
        'id_balance_stamp_duty': memo.balance_stamp_duty,
        'id_balance_reg_fee': memo.balance_reg_fee,
        'id_balance_penalty': memo.balance_penalty,
        'amount_in_words': number_to_marathi_digits(memo.recovered_amount or memo.total_amount),
        'today': timezone.now(),
    }
    
    return render(request, template, context)


@login_required
def download_notice_word(request, pk, notice_type):
    """Download notice as Word document"""
    memo = get_object_or_404(InspectionMemo, pk=pk)
    
    # Get active office information
    office = OfficeInformation.objects.filter(is_active=True).first()
    if not office:
        messages.error(request, 'कृपया प्रथम कार्यालयाची माहिती टाका.')
        return redirect('inspection_detail', pk=pk)
    
    # Template mapping
    template_map = {
        'first': 'inspection/notice_templates/first_notice.html',
        'second': 'inspection/notice_templates/second_notice.html',
        'hearing': 'inspection/notice_templates/hearing_notice.html',
        'case_filing': 'inspection/notice_templates/case_filing_notice.html',
    }
    
    template = template_map.get(notice_type)
    if not template:
        messages.error(request, 'अवैध नोटीस प्रकार!')
        return redirect('inspection_detail', pk=pk)
    
    from .utils.word_generator import generate_word_from_template
    from django.http import HttpResponse
    import os
    from django.conf import settings
    
    # Generate Word document
    context = {
        'memo': memo,
        'office': office,
    }
    
    doc = generate_word_from_template(template, context)
    
    # Create tracking record
    notice_type_map = {
        'first': 'FIRST',
        'second': 'SECOND',
        'hearing': 'HEARING',
        'case_filing': 'CASE_FILING',
    }
    
    tracking = NoticeTracking.objects.create(
        memo=memo,
        notice_type=notice_type_map.get(notice_type),
        generated_by=request.user
    )
    
    # Save to temporary file
    filename = f"notice_{memo.deed_number}_{notice_type}_{tracking.id}.docx"
    temp_path = os.path.join(settings.MEDIA_ROOT, 'notices', 'temp', filename)
    os.makedirs(os.path.dirname(temp_path), exist_ok=True)
    doc.save(temp_path)
    
    # Save to tracking
    tracking.docx_file.name = f"notices/word/{filename}"
    tracking.save()
    
    # Return file as response
    with open(temp_path, 'rb') as f:
        response = HttpResponse(f.read(), content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    # Clean up temp file
    if os.path.exists(temp_path):
        os.remove(temp_path)
    
    messages.success(request, 'नोटीस Word फाइल यशस्वीरित्या डाउनलोड झाली!')
    return response


@login_required
def download_letter_word(request, pk, letter_type):
    """Download letter as Word document"""
    memo = get_object_or_404(InspectionMemo, pk=pk)
    
    # Get active office information
    office = OfficeInformation.objects.filter(is_active=True).first()
    if not office:
        messages.error(request, 'कृपया प्रथम कार्यालयाची माहिती टाका.')
        return redirect('inspection_detail', pk=pk)
    
    # Template mapping
    template_map = {
        'full_payment': 'inspection/letter_templates/full_payment_letter.html',
        'full_payment_note': 'inspection/letter_templates/full_payment_note.html',
        'partial_payment': 'inspection/letter_templates/partial_payment_letter.html',
        'partial_payment_note': 'inspection/letter_templates/partial_payment_note.html',
    }
    
    template = template_map.get(letter_type)
    if not template:
        messages.error(request, 'अवैध पत्र प्रकार!')
        return redirect('inspection_detail', pk=pk)
    
    from .utils.word_generator import generate_word_from_template
    from django.http import HttpResponse
    import os
    from django.conf import settings
    
    # Generate Word document
    context = {
        'memo': memo,
        'office': office,
    }
    
    doc = generate_word_from_template(template, context)
    
    # Create tracking record
    letter_type_map = {
        'full_payment': 'FULL_PAYMENT',
        'partial_payment': 'PARTIAL_PAYMENT',
    }
    
    tracking = NoticeTracking.objects.create(
        memo=memo,
        letter_type=letter_type_map.get(letter_type),
        generated_by=request.user
    )
    
    # Save to temporary file
    filename = f"letter_{memo.deed_number}_{letter_type}_{tracking.id}.docx"
    temp_path = os.path.join(settings.MEDIA_ROOT, 'notices', 'temp', filename)
    os.makedirs(os.path.dirname(temp_path), exist_ok=True)
    doc.save(temp_path)
    
    # Save to tracking
    tracking.docx_file.name = f"notices/word/{filename}"
    tracking.save()
    
    # Return file as response
    with open(temp_path, 'rb') as f:
        response = HttpResponse(f.read(), content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    # Clean up temp file
    if os.path.exists(temp_path):
        os.remove(temp_path)
    
    messages.success(request, 'पत्र Word फाइल यशस्वीरित्या डाउनलोड झाली!')
    return response


@login_required
def notice_history(request, pk):
    """View notice history for a memo"""
    memo = get_object_or_404(InspectionMemo, pk=pk)
    notices = memo.notices.all().order_by('-sent_date')

    return render(request, 'inspection/notice_history.html', {
        'memo': memo,
        'notices': notices,
    })


@login_required
def track_notice(request, pk, notice_type):
    """Track notice generation and create tracking record"""
    memo = get_object_or_404(InspectionMemo, pk=pk)

    # Create tracking record
    NoticeTracking.objects.create(
        memo=memo,
        notice_type=notice_type,
        status='GENERATED'
    )

    # Redirect to notice generation
    return redirect('generate_notice', pk=pk, notice_type=notice_type.lower())


@login_required
def track_letter(request, pk, letter_type):
    """Track letter generation and create tracking record"""
    memo = get_object_or_404(InspectionMemo, pk=pk)

    # Create tracking record
    NoticeTracking.objects.create(
        memo=memo,
        letter_type=letter_type.upper(),
        status='GENERATED'
    )

    # Redirect to letter generation
    return redirect('generate_letter', pk=pk, letter_type=letter_type)


@login_required
def edit_notice(request, pk):
    """Edit notice issue_date and status"""
    notice = get_object_or_404(NoticeTracking, pk=pk)

    if request.method == 'POST':
        issue_date = request.POST.get('issue_date')
        status = request.POST.get('status')

        if issue_date:
            from datetime import datetime
            notice.issue_date = datetime.strptime(issue_date, '%Y-%m-%d').date()
        if status:
            notice.status = status

        notice.save()
        messages.success(request, 'नोटीस यशस्वीरित्या अपडेट केले')

    return redirect('inspection_detail', pk=notice.memo.pk)


@login_required
def delete_notice(request, pk):
    """Delete notice tracking record"""
    notice = get_object_or_404(NoticeTracking, pk=pk)

    if request.method == 'POST':
        memo_pk = notice.memo.pk
        notice.delete()
        messages.success(request, 'नोटीस यशस्वीरित्या हटवले')
        return redirect('inspection_detail', pk=memo_pk)

    return redirect('inspection_detail', pk=notice.memo.pk)


@login_required
def inspection_export_excel(request):
    """Export inspection list to Excel (CSV)"""
    import csv
    from django.http import HttpResponse

    memos = InspectionMemo.objects.select_related(
        'office_name', 'inspection_year', 'approval_status', 'remark'
    ).all()

    # Apply same filters as list view
    inspection_type = request.GET.get('type', '')
    if inspection_type:
        memos = memos.filter(inspection_type=inspection_type)

    year_id = request.GET.get('year', '')
    if year_id:
        memos = memos.filter(inspection_year_id=year_id)

    office_id = request.GET.get('office', '')
    if office_id:
        memos = memos.filter(office_name_id=office_id)

    search = request.GET.get('search', '')
    if search:
        memos = memos.filter(
            Q(deed_number__icontains=search) |
            Q(executant_name__icontains=search) |
            Q(claimant_name__icontains=search) |
            Q(memo_number__icontains=search) |
            Q(village__icontains=search)
        )

    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="inspection_list.csv"'

    writer = csv.writer(response)

    # Write header
    writer.writerow([
        'अं.नं.',
        'प्रकार',
        'दस्त क्र',
        'परिच्छेद क्र',
        'निष्पादन दिनांक',
        'कार्यालय',
        'मंजुरी स्थिती',
        'कमी मु.शु',
        'कमी फी',
        'एकुण रक्कम',
        'शिल्लक',
        'शेरा'
    ])

    # Write data rows
    for idx, memo in enumerate(memos, 1):
        writer.writerow([
            idx,
            memo.get_inspection_type_display(),
            memo.deed_number,
            memo.paragraph_number or '',
            memo.execution_date.strftime('%d/%m/%Y') if memo.execution_date else '',
            memo.office_name.name if memo.office_name else '',
            memo.approval_status or '',
            memo.stamp_duty_short,
            memo.reg_fee_short,
            memo.total_amount,
            memo.balance_amount,
            memo.remark or ''
        ])

    return response


@login_required
def final_order_view(request, pk):
    """View to properly display the final order separately from generation"""
    memo = get_object_or_404(InspectionMemo, pk=pk)

    # Get active office information
    office = OfficeInformation.objects.filter(is_active=True).first()
    if not office:
        messages.error(request, 'कृपया प्रथम कार्यालयाची माहिती टाका.')
        return redirect('inspection_detail', pk=pk)

    from django.utils import timezone
    second_notice = NoticeTracking.objects.filter(
        memo=memo, notice_type='SECOND'
    ).first()
    hearing_notice = NoticeTracking.objects.filter(
        memo=memo, notice_type='HEARING'
    ).first()
    
    context = {
        'memo': memo,
        'office': office,
        'second_notice_date': second_notice.issue_date if second_notice else None,
        'hearing_notice_date': hearing_notice.issue_date if hearing_notice else None,
        'today': timezone.now(),
    }
    return render(request, 'inspection/final_order.html', context)


@login_required
def rrc_certificate_view(request, pk):
    """View to properly display the RRC Certificate"""
    memo = get_object_or_404(InspectionMemo, pk=pk)

    # Get active office information
    office = OfficeInformation.objects.filter(is_active=True).first()
    if not office:
        messages.error(request, 'कृपया प्रथम कार्यालयाची माहिती टाका.')
        return redirect('inspection_detail', pk=pk)

    from django.utils import timezone
    
    context = {
        'memo': memo,
        'office': office,
        'today': timezone.now(),
    }
    return render(request, 'inspection/rrc_certificate.html', context)


@login_required
def boja_patra_view(request, pk):
    """View to properly display the Boja Patra (Lien Order)"""
    memo = get_object_or_404(InspectionMemo, pk=pk)

    # Get active office information
    office = OfficeInformation.objects.filter(is_active=True).first()
    if not office:
        messages.error(request, 'कृपया प्रथम कार्यालयाची माहिती टाका.')
        return redirect('inspection_detail', pk=pk)

    # Fetch second and hearing notice dates from tracking
    second_notice = NoticeTracking.objects.filter(
        memo=memo, notice_type='SECOND'
    ).first()
    hearing_notice = NoticeTracking.objects.filter(
        memo=memo, notice_type='HEARING'
    ).first()

    from django.utils import timezone
    
    context = {
        'memo': memo,
        'office': office,
        'second_notice_date': second_notice.issue_date if second_notice else None,
        'hearing_notice_date': hearing_notice.issue_date if hearing_notice else None,
        'today': timezone.now(),
    }
    return render(request, 'inspection/boja_patra.html', context)
