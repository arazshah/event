import os
import secrets

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from core import jalali
from core.models import FAQ, ImportantDate, ScheduleItem, SiteSettings, SponsorLevel

DEFAULT_LEVELS = [
    ("حامی اصلی", "درج لوگو در پوستر، وب‌سایت و بنر محل برگزاری\nمعرفی در برنامه‌ی نشست\nاختصاص غرفه‌ی معرفی\nذکر نام در کلیه‌ی اطلاع‌رسانی‌ها"),
    ("حامی تخصصی", "درج لوگو در وب‌سایت و بنر محل برگزاری\nمعرفی کوتاه در برنامه‌ی نشست\nذکر نام در اطلاع‌رسانی‌ها"),
    ("حامی رسانه‌ای", "درج لوگو در وب‌سایت و پوستر\nانتشار اخبار نشست در کانال‌های رسانه‌ای"),
]

DEFAULT_SCHEDULE = [
    ("۰۸:۰۰", "پذیرش و ثبت‌نام حضور", ""),
    ("۰۹:۰۰", "افتتاحیه و سخنرانی‌های کلیدی", "سخنرانی مسئولان و مدیران برگزارکننده"),
    ("۱۰:۱۵", "معرفی اطلس مخاطرات استان و رونمایی از محصولات هوشمند", ""),
    ("۱۱:۰۰", "پذیرایی و شبکه‌سازی", ""),
    ("۱۱:۳۰", "پنل هم‌اندیشی: چالش‌های داده‌ی مکانی در دستگاه‌های دولتی و بخش خصوصی", "با حضور مدیران و کارشناسان دستگاه‌های اجرایی"),
    ("۱۲:۳۰", "جمع‌بندی و اختتامیه", ""),
]

DEFAULT_FAQ = [
    ("آیا شرکت در نشست هزینه دارد؟", "خیر. شرکت در نشست رایگان است و ثبت‌نام قبلی الزامی است، زیرا ظرفیت سالن محدود است."),
    ("نشست در چه زمان و مکانی برگزار می‌شود؟", "دوشنبه ۲ آذر ۱۴۰۵، از ساعت ۸ تا ۱۳، در سالن آرتیمیا واقع در پردیس دانشگاه ارومیه."),
    ("چه کسانی می‌توانند در نشست شرکت کنند؟", "مدیران و کارشناسان دستگاه‌های اجرایی، اعضای هیئت علمی و پژوهشگران، دانشجویان تحصیلات تکمیلی، شرکت‌های دانش‌بنیان و فعالان بخش خصوصی."),
    ("چگونه می‌توانم تجربه یا پروژه‌ی خود را ارائه کنم؟", "از طریق صفحه‌ی فراخوان، پیشنهاد خود را تا پایان مهلت ثبت کنید. نتیجه‌ی بررسی توسط دبیرخانه به ایمیل شما اعلام می‌شود."),
    ("رصدخانه‌ی توسعه و تاب‌آوری چیست؟", "رصدخانه سکوی تحلیلی و تصمیم‌یار است که با شناسنامه‌دار کردن و اتصال استاندارد داده‌های دستگاه‌ها، شاخص‌های توسعه و تاب‌آوری استان را محاسبه و تحلیل می‌کند. توضیح بیشتر در همین صفحه آمده است."),
]


class Command(BaseCommand):
    help = "Create default settings, content and the initial admin user (idempotent)."

    def handle(self, *args, **opts):
        site = SiteSettings.load()
        if not ImportantDate.objects.exists():
            for i, (t, d, h) in enumerate([
                ("مهلت ارسال پیشنهاد", jalali.format_long(site.call_deadline), False),
                ("اعلام نتیجه‌ی بررسی پیشنهادها", "۲۷ آبان ۱۴۰۵", False),
                ("روز نشست", jalali.format_long(site.event_date), True),
            ]):
                ImportantDate.objects.create(title=t, date_text=d, order=i, highlight=h)
        if not ScheduleItem.objects.exists():
            for i, (t, ti, d) in enumerate(DEFAULT_SCHEDULE):
                ScheduleItem.objects.create(time_text=t, title=ti, description=d, order=i)
        if not FAQ.objects.exists():
            for i, (q, a) in enumerate(DEFAULT_FAQ):
                FAQ.objects.create(question=q, answer=a, order=i)
        if not SponsorLevel.objects.exists():
            for i, (t, b) in enumerate(DEFAULT_LEVELS):
                SponsorLevel.objects.create(title=t, benefits=b, order=i)
        User = get_user_model()
        if not User.objects.filter(is_superuser=True).exists():
            username = os.environ.get("ADMIN_USERNAME", "admin")
            password = os.environ.get("ADMIN_PASSWORD")
            generated = not password
            password = password or secrets.token_urlsafe(12)
            User.objects.create_superuser(username=username, email="", password=password)
            if generated:
                self.stdout.write(self.style.WARNING(f"Created admin '{username}' with random password: {password}"))
            else:
                self.stdout.write(f"Created admin '{username}' from ADMIN_PASSWORD.")
