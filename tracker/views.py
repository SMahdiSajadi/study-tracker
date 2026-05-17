import openpyxl
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpRequest, HttpResponse
from django.utils import timezone
from django.db.models import Sum
from .models import StudySession, Subject

def user_login(request: HttpRequest) -> HttpResponse:
    """ویوی ورود کاربران (دانش‌آموزان)"""
    if request.user.is_authenticated:
        return redirect('tracker:dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('tracker:dashboard')
    else:
        form = AuthenticationForm()

    return render(request, 'tracker/login.html', {'form': form})


@login_required(login_url='tracker:login')
def dashboard(request: HttpRequest) -> HttpResponse:
    """
    داشبورد اصلی دانش‌آموز به همراه پردازش فرم چندگانه (Dynamic Form)
    """
    user = request.user
    today = timezone.now().date()

    # --- بخش پردازش داده‌های ارسالی فرم (POST) ---
    if request.method == 'POST':
        # دریافت لیست دروس و زمان‌ها از فرم HTML
        subject_ids = request.POST.getlist('subjects[]')
        durations = request.POST.getlist('durations[]')

        sessions_to_create = []
        
        # استفاده از zip برای پیمایش همزمان دو لیست
        for subject_id, duration in zip(subject_ids, durations):
            try:
                sub_id = int(subject_id)
                dur = int(duration)
                
                # فقط زمان‌های معتبر (بیشتر از صفر) ثبت شوند
                if dur > 0:
                    sessions_to_create.append(
                        StudySession(
                            user=user,
                            subject_id=sub_id,
                            duration_minutes=dur,
                            date=today
                        )
                    )
            except (ValueError, TypeError):
                # اگر کاربر داده نامعتبری وارد کرد، آن ردیف نادیده گرفته می‌شود
                pass

        # استفاده از bulk_create برای ذخیره تمام رکوردها در یک کوئری (پرفورمنس بالا)
        if sessions_to_create:
            StudySession.objects.bulk_create(sessions_to_create)

        return redirect('tracker:dashboard')

    # --- بخش نمایش اطلاعات داشبورد (GET) ---
    if hasattr(user, 'major') and user.major:
        subjects = Subject.objects.filter(major=user.major)
    else:
        subjects = Subject.objects.none()

    today_sessions = StudySession.objects.filter(user=user, date=today)
    total_minutes_dict = today_sessions.aggregate(total=Sum('duration_minutes'))
    total_minutes_today = total_minutes_dict['total'] or 0

    context = {
        'student_name': user.get_full_name() or user.username,
        'major_name': user.major.name if hasattr(user, 'major') and user.major else "نامشخص",
        'subjects': subjects,
        'today_sessions': today_sessions,
        'total_minutes_today': total_minutes_today,
    }
    
    return render(request, 'tracker/dashboard.html', context)


# دکوراتور برای اطمینان از اینکه فقط ادمین می‌تواند به این ویو دسترسی داشته باشد
@user_passes_test(lambda u: u.is_staff)
def export_study_sessions_excel(request: HttpRequest) -> HttpResponse:
    """
    تولید فایل اکسل پیشرفته از ساعات مطالعه برای مدیران با استفاده از openpyxl.
    """
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "گزارش مطالعه دانش‌آموزان"

    # تنظیم هدرهای فایل اکسل
    headers = [
        'نام دانش‌آموز', 
        'رشته تحصیلی', 
        'تاریخ', 
        'نام درس', 
        'دقیقه مطالعه', 
        'مجموع مطالعه روزانه شخص'
    ]
    ws.append(headers)

    # واکشی تمام جلسات به همراه جداول مرتبط برای جلوگیری از مشکل N+1
    sessions = StudySession.objects.select_related(
        'user', 'subject', 'subject__major'
    ).order_by('-date', 'user__username')

    # پیش‌محاسبه مجموع مطالعه روزانه هر شخص
    daily_totals_query = StudySession.objects.values(
        'user_id', 'date'
    ).annotate(total=Sum('duration_minutes'))
    
    daily_totals = {
        (item['user_id'], item['date']): item['total'] 
        for item in daily_totals_query
    }

    # پر کردن ردیف‌های فایل اکسل
    for session in sessions:
        user_name = session.user.get_full_name() or session.user.username
        
        major_name = "نامشخص"
        if hasattr(session.user, 'major') and session.user.major:
            major_name = session.user.major.name
            
        date_str = session.date.strftime('%Y/%m/%d')
        subject_name = session.subject.name
        duration = session.duration_minutes
        
        total_daily = daily_totals.get((session.user_id, session.date), 0)

        ws.append([
            user_name,
            major_name,
            date_str,
            subject_name,
            duration,
            total_daily
        ])

    # تنظیم ریسپانس برای دانلود فایل
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="study_report.xlsx"'
    
    wb.save(response)
    return response