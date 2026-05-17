from django.urls import path
from . import views

app_name = 'tracker'

urlpatterns = [
    # مسیر ورود دانش‌آموز
    path('login/', views.user_login, name='login'),
    
    # مسیر داشبورد دانش‌آموز
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # مسیر خروجی اکسل (فقط برای ادمین)
    path('export/excel/', views.export_study_sessions_excel, name='export_excel'),
]