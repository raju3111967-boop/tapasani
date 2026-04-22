"""
Forms for तपासणी  व्यवस्थापन प्रणाली
"""
from django import forms
from .models import (
    InspectionMemo, OfficeName, InspectionYear, DocumentType,
    ApprovalStatus, Taluka, PropertyType, GroupSurvey, Unit,
    CompetentAuthority, Remark, LitigationStatus, PenaltyRate
)


class InspectionMemoForm(forms.ModelForm):
    """
    Single common form for all 7 inspection types.
    inspection_type dropdown at top, rest common fields.
    """

    class Meta:
        model = InspectionMemo
        fields = [
            'inspection_type', 'office_name', 'inspection_year',
            'taluka', 'deed_number', 'paragraph_number', 'execution_date', 'registration_date',
            'document_type', 'property_type', 'group_survey', 'survey_number', 'area', 'sold_area', 'built_up_area', 'unit',
            'village', 'property_income_description',
            'executant_name', 'executant_address', 'executant_mobile',
            'market_value', 'consideration_amount', 'higher_value', 'valuation_difference', 'objection_description',
            'stamp_duty_collected', 'stamp_duty_actual',
            'reg_fee_collected', 'reg_fee_actual',
            'penalty_date', 'penalty_rate',
            'approval_status', 'competent_authority', 'litigation_status',
            'court_name', 'petition_number',
            'recovered_stamp_duty', 'recovered_stamp_duty_date', 'recovered_stamp_duty_challan',
            'recovered_reg_fee', 'recovered_reg_fee_date', 'recovered_reg_fee_challan',
            'recovered_penalty', 'recovered_penalty_date', 'recovered_penalty_challan',
            'remark', 'additional_remark',
            'memo_number', 'memo_date',
        ]
        widgets = {
            'inspection_type': forms.Select(attrs={
                'class': 'form-select form-select-lg',
                'id': 'id_inspection_type',
            }),
            'office_name': forms.Select(attrs={'class': 'form-select'}),
            'inspection_year': forms.Select(attrs={'class': 'form-select'}),
            'taluka': forms.Select(attrs={'class': 'form-select'}),
            'deed_number': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'दस्त क्रमांक',
            }),
            'paragraph_number': forms.NumberInput(attrs={
                'class': 'form-control', 'placeholder': 'परिच्छेद क्र',
            }),
            'execution_date': forms.DateInput(attrs={
                'class': 'form-control', 'type': 'date',
            }),
            'registration_date': forms.DateInput(attrs={
                'class': 'form-control', 'type': 'date',
            }),
            'document_type': forms.Select(attrs={'class': 'form-select'}),
            'property_type': forms.Select(attrs={'class': 'form-select'}),
            'group_survey': forms.Select(attrs={'class': 'form-select'}),
            'survey_number': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'गट/सं.नं.क्रमांक',
            }),
            'area': forms.NumberInput(attrs={
                'class': 'form-control', 'step': '0.01', 'placeholder': 'एकुण क्षेत्रफळ',
            }),
            'sold_area': forms.NumberInput(attrs={
                'class': 'form-control', 'step': '0.01', 'placeholder': 'विक्री केलेले क्षेत्र',
            }),
            'built_up_area': forms.NumberInput(attrs={
                'class': 'form-control', 'step': '0.01', 'placeholder': 'बांधीव क्षेत्र',
            }),
            'unit': forms.Select(attrs={'class': 'form-select'}),
            'village': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'गाव/मौजे',
            }),
            'property_income_description': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 2, 'placeholder': 'मिळकतीचे थोडक्यात वर्णन',
            }),
            'executant_name': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'निष्पादकाचे नाव',
            }),
            'executant_address': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 2, 'placeholder': 'निष्पादकाचा संपुर्ण पत्ता',
            }),
            'executant_mobile': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'निष्पादकाचा मोबाईल नंबर',
            }),
            'claimant_name': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'दावेदाराचे नाव',
            }),
            'market_value': forms.NumberInput(attrs={
                'class': 'form-control calc-field', 'step': '0.01',
                'placeholder': '0.00', 'id': 'id_market_value',
            }),
            'consideration_amount': forms.NumberInput(attrs={
                'class': 'form-control calc-field', 'step': '0.01',
                'placeholder': '0.00', 'id': 'id_consideration_amount',
            }),
            'higher_value': forms.NumberInput(attrs={
                'class': 'form-control calc-field', 'step': '0.01',
                'placeholder': '0.00', 'id': 'id_higher_value',
            }),
            'valuation_difference': forms.NumberInput(attrs={
                'class': 'form-control', 'step': '0.01', 'readonly': True,
                'placeholder': '0.00', 'id': 'id_valuation_difference',
            }),
            'objection_description': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 2, 'placeholder': 'आक्षेपाचे थोडक्यात वर्णन',
            }),
            'stamp_duty_collected': forms.NumberInput(attrs={
                'class': 'form-control calc-field', 'step': '0.01',
                'placeholder': '0.00', 'id': 'id_stamp_duty_collected',
            }),
            'stamp_duty_actual': forms.NumberInput(attrs={
                'class': 'form-control calc-field', 'step': '0.01',
                'placeholder': '0.00', 'id': 'id_stamp_duty_actual',
            }),
            'reg_fee_collected': forms.NumberInput(attrs={
                'class': 'form-control calc-field', 'step': '0.01',
                'placeholder': '0.00', 'id': 'id_reg_fee_collected',
            }),
            'reg_fee_actual': forms.NumberInput(attrs={
                'class': 'form-control calc-field', 'step': '0.01',
                'placeholder': '0.00', 'id': 'id_reg_fee_actual',
            }),
            'penalty_date': forms.DateInput(attrs={
                'class': 'form-control', 'type': 'date',
            }),
            'penalty_rate': forms.NumberInput(attrs={
                'class': 'form-control', 'step': '0.01', 'placeholder': '0.02',
            }),
            'approval_status': forms.Select(attrs={'class': 'form-select'}),
            'competent_authority': forms.Select(attrs={'class': 'form-select'}),
            'litigation_status': forms.Select(attrs={'class': 'form-select'}),
            'court_name': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'न्यायालयाचे नाव',
            }),
            'petition_number': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'पिटीशन क्रमांक',
            }),
            'recovered_stamp_duty': forms.NumberInput(attrs={
                'class': 'form-control calc-field', 'step': '0.01',
                'placeholder': '0.00',
            }),
            'recovered_stamp_duty_date': forms.DateInput(attrs={
                'class': 'form-control', 'type': 'date',
            }),
            'recovered_stamp_duty_challan': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'चलन क्रमांक',
            }),
            'recovered_reg_fee': forms.NumberInput(attrs={
                'class': 'form-control calc-field', 'step': '0.01',
                'placeholder': '0.00',
            }),
            'recovered_reg_fee_date': forms.DateInput(attrs={
                'class': 'form-control', 'type': 'date',
            }),
            'recovered_reg_fee_challan': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'चलन क्रमांक',
            }),
            'recovered_penalty': forms.NumberInput(attrs={
                'class': 'form-control calc-field', 'step': '0.01',
                'placeholder': '0.00',
            }),
            'recovered_penalty_date': forms.DateInput(attrs={
                'class': 'form-control', 'type': 'date',
            }),
            'recovered_penalty_challan': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'चलन क्रमांक',
            }),
            'remark': forms.Select(attrs={'class': 'form-select'}),
            'additional_remark': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 2,
                'placeholder': 'अतिरिक्त शेरा',
            }),
            'memo_number': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'मेमो क्रमांक',
            }),
            'memo_date': forms.DateInput(attrs={
                'class': 'form-control', 'type': 'date',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set initial value for remark to प्रलंबीत
        try:
            pending_remark = Remark.objects.get(name='प्रलंबीत')
            self.fields['remark'].initial = pending_remark
        except Remark.DoesNotExist:
            pass

        # Make recovery fields optional (not required)
        recovery_fields = [
            'recovered_stamp_duty', 'recovered_stamp_duty_date', 'recovered_stamp_duty_challan',
            'recovered_reg_fee', 'recovered_reg_fee_date', 'recovered_reg_fee_challan',
            'recovered_penalty', 'recovered_penalty_date', 'recovered_penalty_challan',
        ]
        for field in recovery_fields:
            self.fields[field].required = False

        # Make value fields optional (not required)
        value_fields = ['higher_value', 'valuation_difference']
        for field in value_fields:
            self.fields[field].required = False

        # Filter only active items in FK dropdowns
        self.fields['office_name'].queryset = OfficeName.objects.filter(is_active=True)
        self.fields['inspection_year'].queryset = InspectionYear.objects.filter(is_active=True)
        self.fields['document_type'].queryset = DocumentType.objects.filter(is_active=True)
        self.fields['approval_status'].queryset = ApprovalStatus.objects.filter(is_active=True)
        self.fields['taluka'].queryset = Taluka.objects.filter(is_active=True)
        self.fields['property_type'].queryset = PropertyType.objects.filter(is_active=True)
        self.fields['group_survey'].queryset = GroupSurvey.objects.filter(is_active=True)
        self.fields['unit'].queryset = Unit.objects.filter(is_active=True)
        self.fields['competent_authority'].queryset = CompetentAuthority.objects.filter(is_active=True)
        self.fields['remark'].queryset = Remark.objects.filter(is_active=True)
        self.fields['litigation_status'].queryset = LitigationStatus.objects.filter(is_active=True)

        # Set empty labels for FK selects
        for field_name in [
            'office_name', 'inspection_year', 'document_type', 'approval_status',
            'taluka', 'property_type', 'group_survey', 'unit',
            'competent_authority', 'remark', 'litigation_status',
        ]:
            self.fields[field_name].empty_label = "--- निवडा ---"


# ============================================================
# Generic Master Form (used by master CRUD views)
# ============================================================

class MasterForm(forms.ModelForm):
    """Generic form for all master tables"""

    class Meta:
        model = OfficeName  # placeholder, overridden in view
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'नाव प्रविष्ट करा',
                'autofocus': True,
            }),
        }
