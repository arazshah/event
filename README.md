# event.postgis.ir — سایت روز جهانی GIS ارومیه

Django + SQLite. فراخوان (۴ نوع)، پیش‌ثبت‌نام/ثبت‌نام با لینک زرین‌پال، اسپانسر، و پنل مدیریت فارسی با تاریخ شمسی.

## استقرار روی Coolify
1. New Resource → Repository → `arazshah/event`، Build Pack: **Dockerfile**، پورت **8000**.
2. Domain: `https://event.postgis.ir`
3. **Persistent Storage**: یک volume با مسیر مقصد `/data` (دیتابیس و فایل‌های آپلودی اینجا ذخیره می‌شود؛ بدون آن با هر استقرار پاک می‌شود).
4. Environment Variables:
   | نام | توضیح |
   |---|---|
   | `SECRET_KEY` | **الزامی**، رشته تصادفی بلند |
   | `ADMIN_PASSWORD` | رمز اولیه ادمین (فقط وقتی هنوز ادمینی نیست استفاده می‌شود) |
   | `ADMIN_USERNAME` | پیش‌فرض `admin` |
   | `ALLOWED_HOSTS` | پیش‌فرض `event.postgis.ir,localhost,127.0.0.1` (localhost برای healthcheck لازم است) |
   | `CSRF_TRUSTED_ORIGINS` | پیش‌فرض `https://event.postgis.ir` |
5. Deploy. پنل: `/admin/`. بعد از اولین ورود رمز را از «تغییر گذرواژه» عوض کنید.

اگر `ADMIN_PASSWORD` ندهید، رمز تصادفی در لاگ اولین اجرا چاپ می‌شود.

## شروع ثبت‌نام واقعی
پنل ← تنظیمات رویداد ← مرحله را روی «ثبت‌نام و پرداخت» بگذارید و لینک زرین‌پال و مبلغ را وارد کنید.
کاربر بعد از ثبت‌نام صفحه‌ای با دکمه پرداخت می‌بیند. تیک «پرداخت تأیید شد» را خودتان در لیست ثبت‌نام‌ها می‌زنید.

## اجرای محلی
```
pip install -r requirements.txt
export DJANGO_DEBUG=1
python manage.py migrate && python manage.py bootstrap_site && python manage.py runserver
```
فایل‌های رزومه/اسلاید فقط برای کاربر staff قابل دانلود است (`/private-files/`). لوگو و عکس تیم عمومی است.
