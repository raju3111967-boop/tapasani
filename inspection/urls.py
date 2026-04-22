"""
URL patterns for inspection app
"""
from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Inspection CRUD
    path('inspection/', views.inspection_list, name='inspection_list'),
    path('inspection/create/', views.inspection_create, name='inspection_create'),
    path('inspection/<int:pk>/', views.inspection_detail, name='inspection_detail'),
    path('inspection/<int:pk>/edit/', views.inspection_edit, name='inspection_edit'),
    path('inspection/<int:pk>/delete/', views.inspection_delete, name='inspection_delete'),
    path('inspection/export/excel/', views.inspection_export_excel, name='inspection_export_excel'),

    # Master Tables
    path('masters/', views.master_dashboard, name='master_dashboard'),
    path('masters/<str:slug>/', views.master_list, name='master_list'),
    path('masters/<str:slug>/create/', views.master_create, name='master_create'),
    path('masters/<str:slug>/<int:pk>/edit/', views.master_edit, name='master_edit'),
    path('masters/<str:slug>/<int:pk>/toggle/', views.master_toggle, name='master_toggle'),

    # Reports
    path('reports/', views.reports_dashboard, name='reports_dashboard'),
    path('reports/pending/', views.report_pending, name='report_pending'),
    path('reports/recovered/', views.report_recovered, name='report_recovered'),
    path('reports/monthly/', views.report_monthly, name='report_monthly'),
    path('reports/yearly/', views.report_yearly, name='report_yearly'),
    path('reports/office-pending/', views.report_office_pending, name='report_office_pending'),
    path('reports/office-recovered/', views.report_office_recovered, name='report_office_recovered'),
    path('reports/office-month-pending/', views.report_office_month_pending, name='report_office_month_pending'),
    path('reports/office-year-recovery/', views.report_office_year_recovery, name='report_office_year_recovery'),

    # Office Information
    path('office-info/', views.office_info_list, name='office_info_list'),
    path('office-info/create/', views.office_info_create, name='office_info_create'),
    path('office-info/<int:pk>/edit/', views.office_info_edit, name='office_info_edit'),
    path('office-info/<int:pk>/delete/', views.office_info_delete, name='office_info_delete'),
    path('office-info/<int:pk>/toggle/', views.office_info_toggle, name='office_info_toggle'),

    # Notice and Letter Generation
    path('inspection/<int:pk>/notice/<str:notice_type>/', views.generate_notice, name='generate_notice'),
    path('inspection/<int:pk>/letter/<str:letter_type>/', views.generate_letter, name='generate_letter'),
    path('inspection/<int:pk>/notice/<str:notice_type>/download/', views.download_notice_word, name='download_notice_word'),
    path('inspection/<int:pk>/letter/<str:letter_type>/download/', views.download_letter_word, name='download_letter_word'),
    path('inspection/<int:pk>/notices/', views.notice_history, name='notice_history'),
    path('inspection/<int:pk>/final-order/', views.final_order_view, name='final_order'),
    path('inspection/<int:pk>/rrc-certificate/', views.rrc_certificate_view, name='rrc_certificate'),
    path('inspection/<int:pk>/boja-patra/', views.boja_patra_view, name='boja_patra'),

    # Notice Tracking
    path('inspection/<int:pk>/track/notice/<str:notice_type>/', views.track_notice, name='track_notice'),
    path('inspection/<int:pk>/track/letter/<str:letter_type>/', views.track_letter, name='track_letter'),
    path('notice/<int:pk>/edit/', views.edit_notice, name='edit_notice'),
    path('notice/<int:pk>/delete/', views.delete_notice, name='delete_notice'),

    # API
    path('api/calculate/', views.api_calculate, name='api_calculate'),
]
