"""
Admin registration for all models
"""
from django.contrib import admin
from .models import (
    OfficeName, InspectionYear, DocumentType, ApprovalStatus,
    Taluka, PropertyType, GroupSurvey, Unit, CompetentAuthority,
    Remark, LitigationStatus, InspectionMemo
)

# Master Tables
admin.site.register(OfficeName)
admin.site.register(InspectionYear)
admin.site.register(DocumentType)
admin.site.register(ApprovalStatus)
admin.site.register(Taluka)
admin.site.register(PropertyType)
admin.site.register(GroupSurvey)
admin.site.register(Unit)
admin.site.register(CompetentAuthority)
admin.site.register(Remark)
admin.site.register(LitigationStatus)


@admin.register(InspectionMemo)
class InspectionMemoAdmin(admin.ModelAdmin):
    list_display = ['deed_number', 'inspection_type', 'office_name', 'execution_date', 'total_amount', 'balance_amount']
    list_filter = ['inspection_type', 'office_name', 'inspection_year']
    search_fields = ['deed_number', 'executant_name', 'claimant_name']
