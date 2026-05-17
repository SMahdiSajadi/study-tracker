from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Major, Subject, StudySession

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    # نمایش ستون رشته در لیست کاربران
    list_display = ('username', 'first_name', 'last_name', 'major', 'is_staff')
    search_fields = ('username', 'first_name', 'last_name')
    
    # اضافه کردن فیلد رشته به فرم ویرایش کاربر
    fieldsets = UserAdmin.fieldsets + (
        ('اطلاعات تحصیلی', {'fields': ('major',)}),
    )

@admin.register(Major)
class MajorAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'major')
    list_filter = ('major',)
    search_fields = ('name', 'major__name')

@admin.register(StudySession)
class StudySessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'subject', 'date', 'duration_minutes')
    list_filter = ('date', 'user', 'subject', 'subject__major')
    date_hierarchy = 'date'
    ordering = ('-date', '-id')