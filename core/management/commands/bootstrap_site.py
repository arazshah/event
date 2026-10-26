import os
import secrets

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from core.models import SiteSettings, SponsorLevel, TeamMember

DEFAULT_LEVELS = [
    ("اسپانسر طلایی", "لوگو روی پوستر، سایت و بنر سالن\nغرفه معرفی در محل رویداد\nزمان معرفی ۱۰ دقیقه‌ای روی سن\nنام در تمام اطلاع‌رسانی‌ها"),
    ("اسپانسر نقره‌ای", "لوگو روی سایت و بنر سالن\nمعرفی کوتاه ۳ دقیقه‌ای\nنام در اطلاع‌رسانی‌ها"),
    ("حامی رسانه‌ای", "لوگو روی سایت و پوستر\nانتشار اخبار رویداد در کانال‌های شما"),
]


class Command(BaseCommand):
    help = "Create default settings, sponsor levels and the initial admin user (idempotent)."

    def handle(self, *args, **opts):
        SiteSettings.load()
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
