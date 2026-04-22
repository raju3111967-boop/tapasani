"""
Models for तपासणी मेमो व्यवस्थापन प्रणाली
11 Master Tables + 1 Main Inspection Table
"""
from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from datetime import date
from decimal import Decimal
import math


# ============================================================
# MASTER TABLES (11)
# ============================================================

class OfficeName(models.Model):
    """कार्यालयाचे नाव"""
    name = models.CharField(max_length=255, verbose_name="कार्यालयाचे नाव")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "कार्यालय"
        verbose_name_plural = "कार्यालये"
        ordering = ['name']

    def __str__(self):
        return self.name


class InspectionYear(models.Model):
    """तपासणी वर्ष"""
    year = models.CharField(max_length=20, verbose_name="तपासणी वर्ष", unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "तपासणी वर्ष"
        verbose_name_plural = "तपासणी वर्षे"
        ordering = ['-year']

    def __str__(self):
        return self.year


class DocumentType(models.Model):
    """दस्तऐवज प्रकार"""
    name = models.CharField(max_length=255, verbose_name="दस्तऐवज प्रकार")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "दस्तऐवज प्रकार"
        verbose_name_plural = "दस्तऐवज प्रकार"
        ordering = ['name']

    def __str__(self):
        return self.name


class ApprovalStatus(models.Model):
    """मंजुरी स्थिती"""
    name = models.CharField(max_length=255, verbose_name="मंजुरी स्थिती")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "मंजुरी स्थिती"
        verbose_name_plural = "मंजुरी स्थिती"
        ordering = ['name']

    def __str__(self):
        return self.name


class Taluka(models.Model):
    """तालुका"""
    name = models.CharField(max_length=255, verbose_name="तालुका")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "तालुका"
        verbose_name_plural = "तालुके"
        ordering = ['name']

    def __str__(self):
        return self.name


class PropertyType(models.Model):
    """मालमत्ता प्रकार"""
    name = models.CharField(max_length=255, verbose_name="मालमत्ता प्रकार")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "मालमत्ता प्रकार"
        verbose_name_plural = "मालमत्ता प्रकार"
        ordering = ['name']

    def __str__(self):
        return self.name


class GroupSurvey(models.Model):
    """गट/सर्व्हे"""
    name = models.CharField(max_length=255, verbose_name="गट/सर्व्हे नंबर")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "गट/सर्व्हे"
        verbose_name_plural = "गट/सर्व्हे"
        ordering = ['name']

    def __str__(self):
        return self.name


class Unit(models.Model):
    """एकक"""
    name = models.CharField(max_length=255, verbose_name="एकक")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "एकक"
        verbose_name_plural = "एकके"
        ordering = ['name']

    def __str__(self):
        return self.name


class CompetentAuthority(models.Model):
    """सक्षम प्राधिकारी"""
    name = models.CharField(max_length=255, verbose_name="सक्षम प्राधिकारी")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "सक्षम प्राधिकारी"
        verbose_name_plural = "सक्षम प्राधिकारी"
        ordering = ['name']

    def __str__(self):
        return self.name


class Remark(models.Model):
    """शेरा"""
    name = models.CharField(max_length=500, verbose_name="शेरा")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "शेरा"
        verbose_name_plural = "शेरे"
        ordering = ['name']

    def __str__(self):
        return self.name


class LitigationStatus(models.Model):
    """न्यायप्रविष्ट स्थिती"""
    name = models.CharField(max_length=255, verbose_name="न्यायप्रविष्ट स्थिती")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "न्यायप्रविष्ट स्थिती"
        verbose_name_plural = "न्यायप्रविष्ट स्थिती"
        ordering = ['name']

    def __str__(self):
        return self.name


class PenaltyRate(models.Model):
    """शास्तीचा दर"""
    name = models.CharField(max_length=255, verbose_name="शास्तीचा दर")
    rate_value = models.DecimalField(max_digits=5, decimal_places=4, verbose_name="दर मूल्य")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "शास्तीचा दर"
        verbose_name_plural = "शास्तीचा दर"
        ordering = ['rate_value']

    def __str__(self):
        return self.name


class OfficeInformation(models.Model):
    """कार्यालयाची संपूर्ण माहिती"""
    office_name = models.CharField(max_length=255, verbose_name="कार्यालयाचे नांव")
    office_address = models.TextField(verbose_name="कार्यालयाचा पत्ता", blank=True, null=True)
    office_email = models.EmailField(verbose_name="कार्यालयाचा ई-मेल", blank=True, null=True)
    office_phone = models.CharField(max_length=20, verbose_name="कार्यालयाचा फोन नंबर", blank=True, null=True)
    district = models.CharField(max_length=100, verbose_name="जिल्हा", blank=True, null=True)
    division_name = models.CharField(max_length=255, verbose_name="विभागाचे नांव", blank=True, null=True)
    divisional_office_name = models.CharField(max_length=255, verbose_name="विभागीय कार्यालयाचे नांव", blank=True, null=True)
    divisional_office_address = models.TextField(verbose_name="विभागीय कार्यालयाचा पत्ता", blank=True, null=True)
    designation_01 = models.CharField(max_length=255, verbose_name="पदनाम 01", blank=True, null=True)
    designation_02 = models.CharField(max_length=255, verbose_name="पदनाम 02", blank=True, null=True)
    working_officer_name = models.CharField(max_length=255, verbose_name="कार्यरत अधिका-यांचे नांव", blank=True, null=True)
    administrative_officer_name = models.CharField(max_length=255, verbose_name="प्रशासकिय अधिकारी यांचे नांव", blank=True, null=True)
    senior_clerk_name = models.CharField(max_length=255, verbose_name="वरिष्ठ लिपीकांचे नांव", blank=True, null=True)
    junior_clerk_name = models.CharField(max_length=255, verbose_name="कनिष्ठ लिपीकांचे नांव", blank=True, null=True)

    is_active = models.BooleanField(default=True, verbose_name="सक्रिय")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "कार्यालयाची माहिती"
        verbose_name_plural = "कार्यालयाची माहिती"
        ordering = ['-created_at']

    def __str__(self):
        return self.office_name


# ============================================================
# MAIN INSPECTION TABLE
# ============================================================

class InspectionMemo(models.Model):
    """
    तपासणी मेमो - Main inspection record
    Single model for all 7 inspection types
    """

    # Inspection Type Choices
    INSPECTION_TYPES = [
        ('AG', 'मा. महालेखापाल'),
        ('IG', 'मा. नोंदणी महानिरीक्षक'),
        ('DIG', 'मा. नोंदणी उपमहानिरीक्षक'),
        ('SDO', 'सहजिल्हा निबंधक'),
        ('URGENT', 'तात्काळ तपासणी'),
        ('SPECIAL', 'विशेष तपासणी'),
        ('OTHER', 'इतर तपासणी'),
    ]

    # --- Core Fields ---
    inspection_type = models.CharField(
        max_length=10, choices=INSPECTION_TYPES,
        verbose_name="तपासणी प्रकार"
    )
    sr_no = models.PositiveIntegerField(
        verbose_name="अनुक्रमांक", null=True, blank=True
    )
    paragraph_number = models.PositiveIntegerField(
        verbose_name="परिच्छेद क्र", null=True, blank=True
    )
    office_name = models.ForeignKey(
        OfficeName, on_delete=models.PROTECT,
        verbose_name="कार्यालयाचे नाव"
    )
    inspection_year = models.ForeignKey(
        InspectionYear, on_delete=models.PROTECT,
        verbose_name="तपासणी वर्ष"
    )
    taluka = models.ForeignKey(
        Taluka, on_delete=models.PROTECT,
        verbose_name="तालुका", null=True, blank=True
    )

    # --- Document Details ---
    deed_number = models.CharField(
        max_length=50, verbose_name="दस्त क्रमांक"
    )
    execution_date = models.DateField(
        verbose_name="निष्पादन दिनांक"
    )
    registration_date = models.DateField(
        verbose_name="नोंदणी दिनांक", null=True, blank=True
    )
    document_type = models.ForeignKey(
        DocumentType, on_delete=models.PROTECT,
        verbose_name="दस्तऐवज प्रकार", null=True, blank=True
    )
    property_type = models.ForeignKey(
        PropertyType, on_delete=models.PROTECT,
        verbose_name="मालमत्ता प्रकार", null=True, blank=True
    )

    # --- Property Details ---
    group_survey = models.ForeignKey(
        GroupSurvey, on_delete=models.SET_NULL,
        verbose_name="गट/सर्व्हे", null=True, blank=True
    )
    survey_number = models.CharField(
        max_length=100,
        verbose_name="गट/सं.नं.क्रमांक",
        blank=True,
        null=True
    )
    area = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        verbose_name="एकुण क्षेत्रफळ"
    )
    sold_area = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        verbose_name="विक्री केलेले क्षेत्र"
    )
    built_up_area = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        verbose_name="बांधीव क्षेत्र"
    )
    unit = models.ForeignKey(
        Unit, on_delete=models.SET_NULL,
        verbose_name="एकक", null=True, blank=True
    )
    village = models.CharField(
        max_length=255, verbose_name="गाव/मौजे",
        blank=True, default=""
    )
    property_income_description = models.TextField(
        verbose_name="मिळकतीचे थोडक्यात वर्णन",
        blank=True, default=""
    )

    # --- Party Details ---
    executant_name = models.CharField(
        max_length=500, verbose_name="निष्पादकाचे नाव",
        blank=True, default=""
    )
    executant_address = models.TextField(
        verbose_name="निष्पादकाचा संपुर्ण पत्ता",
        blank=True, default=""
    )
    executant_mobile = models.CharField(
        max_length=15, verbose_name="निष्पादकाचा मोबाईल नंबर",
        blank=True, default=""
    )
    claimant_name = models.CharField(
        max_length=500, verbose_name="दावेदाराचे नाव",
        blank=True, default=""
    )

    # --- Value Details ---
    market_value = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        verbose_name="बाजार मूल्य", validators=[MinValueValidator(Decimal('0'))]
    )
    consideration_amount = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        verbose_name="मोबदला रक्कम", validators=[MinValueValidator(Decimal('0'))]
    )
    higher_value = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        verbose_name="जास्त रक्कम (मूल्यांकन)", validators=[MinValueValidator(Decimal('0'))]
    )
    valuation_difference = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        verbose_name="मुल्याकंनातील फरक"
    )
    objection_description = models.TextField(
        verbose_name="आक्षेपाचे थोडक्यात वर्णन",
        blank=True, default=""
    )

    # --- Stamp Duty ---
    stamp_duty_collected = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        verbose_name="वसूल केलेला मुद्रांक शुल्क", validators=[MinValueValidator(Decimal('0'))]
    )
    stamp_duty_actual = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        verbose_name="आवश्यक मुद्रांक शुल्क", validators=[MinValueValidator(Decimal('0'))]
    )
    stamp_duty_short = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        verbose_name="कमी पडलेला मुद्रांक शुल्क"
    )

    # --- Registration Fee ---
    reg_fee_collected = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        verbose_name="वसूल केलेली नोंदणी फी", validators=[MinValueValidator(Decimal('0'))]
    )
    reg_fee_actual = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        verbose_name="आवश्यक नोंदणी फी", validators=[MinValueValidator(Decimal('0'))]
    )
    reg_fee_short = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        verbose_name="कमी पडलेली नोंदणी फी"
    )

    # --- Calculated Totals ---
    total_short = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        verbose_name="एकुण कमी"
    )
    total_months = models.PositiveIntegerField(
        default=0, verbose_name="एकुण महिने"
    )
    penalty_date = models.DateField(
        verbose_name="शास्तीचा दिनांक", null=True, blank=True
    )
    penalty_rate = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal('0.02'),
        verbose_name="शास्तीचा दर"
    )
    penalty_amount = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        verbose_name="शास्ती रक्कम"
    )
    total_amount = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        verbose_name="एकुण रक्कम"
    )
    recovered_amount = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        verbose_name="वसूल रक्कम", validators=[MinValueValidator(Decimal('0'))]
    )
    balance_stamp_duty = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        verbose_name="शिल्लक मु.शु"
    )
    balance_reg_fee = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        verbose_name="शिल्लक नों.फी"
    )
    balance_penalty = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        verbose_name="शिल्लक शास्ती"
    )
    balance_amount = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        verbose_name="शिल्लक रक्कम"
    )

    # --- Status & Authority ---
    approval_status = models.ForeignKey(
        ApprovalStatus, on_delete=models.SET_NULL,
        verbose_name="मंजुरी स्थिती", null=True, blank=True
    )
    competent_authority = models.ForeignKey(
        CompetentAuthority, on_delete=models.SET_NULL,
        verbose_name="सक्षम प्राधिकारी", null=True, blank=True
    )
    litigation_status = models.ForeignKey(
        LitigationStatus, on_delete=models.SET_NULL,
        verbose_name="न्यायप्रविष्ट स्थिती", null=True, blank=True
    )
    court_name = models.CharField(
        max_length=255, verbose_name="न्यायालयाचे नाव",
        blank=True, default=""
    )
    petition_number = models.CharField(
        max_length=100, verbose_name="पिटीशन क्रमांक",
        blank=True, default=""
    )

    # --- Recovery Details ---
    recovery_date = models.DateField(
        verbose_name="वसुलीचा दिनांक", null=True, blank=True
    )
    challan_number = models.CharField(
        max_length=100, verbose_name="चलन क्रमांक",
        blank=True, default=""
    )

    # Individual Recovery Fields
    recovered_stamp_duty = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        verbose_name="वसुल मु.शु", validators=[MinValueValidator(Decimal('0'))]
    )
    recovered_stamp_duty_date = models.DateField(
        verbose_name="वसुली मु.शु.चा दिनांक", null=True, blank=True
    )
    recovered_stamp_duty_challan = models.CharField(
        max_length=100, verbose_name="वसुल मु.शु. चलन डिफेस क्रं.",
        blank=True, default=""
    )
    recovered_reg_fee = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        verbose_name="वसूल नों.फी", validators=[MinValueValidator(Decimal('0'))]
    )
    recovered_reg_fee_date = models.DateField(
        verbose_name="वसुली नों.फी चा दिनांक", null=True, blank=True
    )
    recovered_reg_fee_challan = models.CharField(
        max_length=100, verbose_name="वसूल नों.फी चलन डिफेस क्रं.",
        blank=True, default=""
    )
    recovered_penalty = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        verbose_name="वसूल शास्ती", validators=[MinValueValidator(Decimal('0'))]
    )
    recovered_penalty_date = models.DateField(
        verbose_name="वसुली शास्ती चा दिनांक", null=True, blank=True
    )
    recovered_penalty_challan = models.CharField(
        max_length=100, verbose_name="वसुल शास्ती चलन डिफेस क्रं.",
        blank=True, default=""
    )

    # --- Remarks ---
    remark = models.ForeignKey(
        Remark, on_delete=models.SET_NULL,
        verbose_name="शेरा", null=True, blank=True
    )
    additional_remark = models.TextField(
        verbose_name="अतिरिक्त शेरा", blank=True, default=""
    )

    # --- Memo Reference ---
    memo_number = models.CharField(
        max_length=100, verbose_name="मेमो क्रमांक",
        blank=True, default=""
    )
    memo_date = models.DateField(
        verbose_name="मेमो दिनांक", null=True, blank=True
    )
    inspection_date = models.DateField(
        verbose_name="तपासणी दिनांक", null=True, blank=True
    )

    # --- Timestamps ---
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "तपासणी मेमो"
        verbose_name_plural = "तपासणी मेमो"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_inspection_type_display()} - दस्त क्र. {self.deed_number}"

    def calculate_fields(self):
        """Auto-calculate derived fields"""
        # मुल्याकंनातील फरक = आक्षेपीत मुल्याकंन - दस्तातील मोबदला
        self.valuation_difference = max(
            Decimal('0'), self.market_value - self.consideration_amount
        )

        # कमी मु.शु = आवश्यक - वसूल केलेला
        self.stamp_duty_short = max(
            Decimal('0'), self.stamp_duty_actual - self.stamp_duty_collected
        )
        # कमी फी = आवश्यक - वसूल केलेली
        self.reg_fee_short = max(
            Decimal('0'), self.reg_fee_actual - self.reg_fee_collected
        )
        # एकुण कमी
        self.total_short = self.stamp_duty_short + self.reg_fee_short

        # एकुण महिने (round-up logic from execution_date to penalty_date or today)
        if self.execution_date:
            from datetime import date
            # Use penalty_date if available, otherwise use today
            if self.penalty_date:
                end_date = self.penalty_date
            else:
                end_date = date.today()
            diff = end_date - self.execution_date
            days = max(0, diff.days)
            self.total_months = math.ceil(days / 30) if days > 0 else 0
        else:
            self.total_months = 0

        # शास्ती = एकुण कमी × दर × महिने
        self.penalty_amount = (
            self.total_short * self.penalty_rate * Decimal(str(self.total_months))
        )

        # एकुण रक्कम = एकुण कमी + शास्ती
        self.total_amount = self.total_short + self.penalty_amount

        # शिल्लक = एकूण रक्कम - वसूल
        self.recovered_amount = self.recovered_stamp_duty + self.recovered_reg_fee + self.recovered_penalty
        self.balance_amount = self.total_amount - self.recovered_amount

        # Individual balances
        self.balance_stamp_duty = max(Decimal('0'), self.stamp_duty_short - self.recovered_stamp_duty)
        self.balance_reg_fee = max(Decimal('0'), self.reg_fee_short - self.recovered_reg_fee)
        self.balance_penalty = max(Decimal('0'), self.penalty_amount - self.recovered_penalty)

    def save(self, *args, **kwargs):
        self.calculate_fields()
        super().save(*args, **kwargs)

    @property
    def is_pending(self):
        """Check if case is pending (balance > 0)"""
        return self.balance_amount > 0

    @property
    def is_recovered(self):
        """Check if case is fully recovered"""
        return self.balance_amount <= 0 and self.total_amount > 0


# ============================================================
# NOTICE TRACKING
# ============================================================

class NoticeTracking(models.Model):
    """नोटीस व पत्र ट्रॅकिंग"""
    NOTICE_TYPES = [
        ('FIRST', 'प्रथम नोटीस'),
        ('SECOND', 'दुसरी नोटीस'),
        ('HEARING', 'सुनावणी नोटीस'),
        ('CASE_FILING', 'बोजा नोटीस'),
    ]

    LETTER_TYPES = [
        ('FULL_PAYMENT', 'पूर्ण रक्कम भरल्यानंतर पत्र'),
        ('PARTIAL_PAYMENT', 'कमी रक्कम भरल्यानंतर पत्र'),
    ]

    STATUS_CHOICES = [
        ('GENERATED', 'तयार झाले'),
        ('SENT', 'पाठविले'),
        ('CLOSED', 'बंद'),
    ]

    memo = models.ForeignKey(
        InspectionMemo,
        on_delete=models.CASCADE,
        related_name='notices',
        verbose_name="तपासणी मेमो"
    )
    notice_type = models.CharField(
        max_length=20,
        choices=NOTICE_TYPES,
        blank=True,
        null=True,
        verbose_name="नोटीस प्रकार"
    )
    letter_type = models.CharField(
        max_length=20,
        choices=LETTER_TYPES,
        blank=True,
        null=True,
        verbose_name="पत्र प्रकार"
    )
    issue_date = models.DateField(
        verbose_name="इश्यु दिनांक",
        default=date.today,
        blank=True,
        null=True
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='GENERATED',
        verbose_name="स्थिती"
    )
    sent_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="पाठवलेली दिनांक"
    )
    generated_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="जनरेट केले आहे"
    )
    docx_file = models.FileField(
        upload_to='notices/word/',
        blank=True,
        null=True,
        verbose_name="Word फाइल"
    )

    class Meta:
        verbose_name = "नोटीस ट्रॅकिंग"
        verbose_name_plural = "नोटीस ट्रॅकिंग"
        ordering = ['-sent_date']

    def __str__(self):
        if self.notice_type:
            return f"{self.get_notice_type_display()} - {self.memo.deed_number}"
        elif self.letter_type:
            return f"{self.get_letter_type_display()} - {self.memo.deed_number}"
        return f"Notice - {self.memo.deed_number}"
