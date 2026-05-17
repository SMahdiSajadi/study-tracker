from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

class Major(models.Model):
    """مدل رشته تحصیلی"""
    name = models.CharField(max_length=150, unique=True, verbose_name=_("نام رشته"))

    class Meta:
        verbose_name = _("رشته تحصیلی")
        verbose_name_plural = _("رشته‌های تحصیلی")
        ordering = ['name']

    def __str__(self) -> str:
        return self.name

class CustomUser(AbstractUser):
    """مدل کاربر سفارشی با قابلیت انتخاب رشته"""
    # این خط را برای اتصال کاربر به رشته اضافه کردیم
    major = models.ForeignKey(
        Major, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name=_("رشته تحصیلی")
    )

    class Meta:
        verbose_name = _("کاربر")
        verbose_name_plural = _("کاربران")

    def __str__(self) -> str:
        return self.get_full_name() or self.username

class Subject(models.Model):
    """مدل دروس"""
    name = models.CharField(max_length=150, verbose_name=_("نام درس"))
    major = models.ForeignKey(
        Major, 
        on_delete=models.CASCADE, 
        related_name="subjects", 
        verbose_name=_("رشته تحصیلی")
    )

    class Meta:
        verbose_name = _("درس")
        verbose_name_plural = _("دروس")
        unique_together = [['name', 'major']]

    def __str__(self) -> str:
        return f"{self.name} ({self.major.name})"

class StudySession(models.Model):
    """مدل جلسه مطالعه"""
    user = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name="study_sessions", 
        verbose_name=_("دانش‌آموز")
    )
    date = models.DateField(
        default=timezone.now, 
        verbose_name=_("تاریخ مطالعه")
    )
    subject = models.ForeignKey(
        Subject, 
        on_delete=models.CASCADE, 
        related_name="study_sessions", 
        verbose_name=_("درس مطالعه شده")
    )
    duration_minutes = models.PositiveIntegerField(
        verbose_name=_("مدت زمان (دقیقه)")
    )

    class Meta:
        verbose_name = _("جلسه مطالعه")
        verbose_name_plural = _("جلسات مطالعه")
        ordering = ['-date', '-id']

    def __str__(self) -> str:
        return f"{self.user.username} - {self.subject.name} - {self.duration_minutes} دقیقه"