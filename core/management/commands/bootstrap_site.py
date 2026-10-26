import os
import secrets

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from core import jalali
from core.models import FAQ, ImportantDate, SiteSettings, SponsorLevel

DEFAULT_LEVELS = [
    ("اسپانسر طلایی", "لوگو روی پوستر، سایت و بنر سالن\nغرفه معرفی در محل رویداد\nزمان معرفی ۱۰ دقیقه‌ای روی سن\nنام در تمام اطلاع‌رسانی‌ها"),
    ("اسپانسر نقره‌ای", "لوگو روی سایت و بنر سالن\nمعرفی کوتاه ۳ دقیقه‌ای\nنام در اطلاع‌رسانی‌ها"),
    ("حامی رسانه‌ای", "لوگو روی سایت و پوستر\nانتشار اخبار رویداد در کانال‌های شما"),
]


DEFAULT_FAQ = [
    ("شرکت در رویداد هزینه دارد؟", "اطلاعیه‌ی هزینه همراه با شروع ثبت‌نام اصلی اعلام می‌شود. پیش‌ثبت‌نام رایگان و بدون تعهد است."),
    ("مکان رویداد کجاست؟", "رویداد در ارومیه برگزار می‌شود و مکان دقیق به‌زودی اعلام می‌شود. افراد پیش‌ثبت‌نام‌شده اولین نفراتی هستند که مطلع می‌شوند."),
    ("می‌توانم آنلاین شرکت کنم یا ارائه بدهم؟", "بله، رویداد حضوری است و پخش آنلاین هم دارد. متخصصان خارج از کشور می‌توانند به‌صورت آنلاین ارائه دهند."),
    ("چه موضوعاتی پذیرفته می‌شود؟", "هر موضوعی در محور هوش مصنوعی در علوم مکانی: سنجش‌ازدور، مدل‌های زبانی و داده مکانی، PostGIS برای AI و کاربردهای شهری و محیط‌زیستی."),
    ("پیشنهاد چه زمانی داوری می‌شود؟", "پس از پایان مهلت فراخوان، کمیته علمی پیشنهادها را بررسی می‌کند و نتیجه به ایمیل شما اعلام می‌شود."),
]


class Command(BaseCommand):
    help = "Create default settings, sponsor levels and the initial admin user (idempotent)."

    def handle(self, *args, **opts):
        site = SiteSettings.load()
        if not ImportantDate.objects.exists():
            for i, (t, d, h) in enumerate([
                ("مهلت ارسال پیشنهاد", jalali.format_long(site.call_deadline), False),
                ("اعلام پذیرفته‌شدگان", "۱۹ آبان ۱۴۰۵", False),
                ("اعلام برنامه و مکان", "۲۱ آبان ۱۴۰۵", False),
                ("روز رویداد", jalali.format_long(site.event_date), True),
            ]):
                ImportantDate.objects.create(title=t, date_text=d, order=i, highlight=h)
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
