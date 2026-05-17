from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('tracker/', include('tracker.urls', namespace='tracker')),
    path('', RedirectView.as_view(pattern_name='tracker:dashboard', permanent=False)),
]

# این خط جادویی در محیط لوکال فایل‌های CSS و گرافیکی را فعال می‌کند:
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)