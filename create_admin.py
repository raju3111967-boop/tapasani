"""
Script to create admin superuser for तपासणी मेमो व्यवस्थापन प्रणाली
Run: python create_admin.py
"""
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tapasani.settings')

import django
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', '123')
    print("✅ Admin user created: username=admin, password=123")
else:
    print("ℹ️  Admin user already exists.")
