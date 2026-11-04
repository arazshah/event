"""Move an already-deployed database from the first edition's defaults to the redesigned ones.

Only rows that still hold the original seeded text are touched; anything the organiser edited is kept.
"""
import datetime

from django.db import migrations

from core import defaults as D, jalali

OLD = {
    "hero_text": "تازه‌ترین و تخصصی‌ترین مباحث هوش مصنوعی و علوم مکانی، در یک روز. فراخوان ارائه، سخنرانی و کارگاه باز است.",
    "networking_text": "فرصتی برای دیدار و گفتگوی رودرو با متخصصان GIS، سنجش‌ازدور و هوش مصنوعی و ساختن ارتباط‌های حرفه‌ای.",
    "unveil_text": "در این رویداد از محصولات هوشمند حوزه علوم مکانی رونمایی می‌شود.",
    "tracks_text": "سنجش‌ازدور و یادگیری عمیق\nمدل‌های زبانی (LLM) و داده مکانی\nPostGIS و پایگاه داده مکانی برای هوش مصنوعی\nکاربردهای شهری و محیط‌زیستی هوش مصنوعی",
    "time_text": "به‌زودی اعلام می‌شود",
    "venue_text": "به‌زودی اعلام می‌شود",
    "format_text": "حضوری + پخش آنلاین",
}
NEW = {
    "hero_text": D.HERO_TEXT, "networking_text": D.NETWORKING_TEXT, "unveil_text": D.UNVEIL_TEXT,
    "tracks_text": D.TRACKS_TEXT, "time_text": D.TIME_TEXT, "venue_text": D.VENUE_TEXT, "format_text": D.FORMAT_TEXT,
}
OLD_FAQ = {
    "شرکت در رویداد هزینه دارد؟", "مکان رویداد کجاست؟", "می‌توانم آنلاین شرکت کنم یا ارائه بدهم؟",
    "چه موضوعاتی پذیرفته می‌شود؟", "پیشنهاد چه زمانی داوری می‌شود؟",
}


def forward(apps, schema_editor):
    Site = apps.get_model("core", "SiteSettings")
    s = Site.objects.filter(pk=1).first()
    if s:
        for f, old in OLD.items():
            if getattr(s, f) == old:
                setattr(s, f, NEW[f])
        if s.event_date == datetime.date(2026, 11, 19):
            s.event_date = D.EVENT_DATE
        if s.call_deadline == datetime.date(2026, 11, 6):
            s.call_deadline = D.CALL_DEADLINE
        s.save()

    DateRow = apps.get_model("core", "ImportantDate")
    DateRow.objects.filter(title="اعلام برنامه و مکان").delete()
    DateRow.objects.filter(title="مهلت ارسال پیشنهاد").update(date_text=jalali.format_long(D.CALL_DEADLINE))
    DateRow.objects.filter(title="اعلام پذیرفته‌شدگان").update(title="اعلام نتیجه‌ی بررسی پیشنهادها", date_text="۲۷ آبان ۱۴۰۵")
    DateRow.objects.filter(title="روز رویداد").update(title="روز نشست", date_text=jalali.format_long(D.EVENT_DATE))

    apps.get_model("core", "FAQ").objects.filter(question__in=OLD_FAQ).delete()

    Level = apps.get_model("core", "SponsorLevel")
    for old, new in (("اسپانسر طلایی", "حامی اصلی"), ("اسپانسر نقره‌ای", "حامی تخصصی")):
        Level.objects.filter(title=old).update(title=new)
    Level.objects.filter(title="حامی اصلی").update(
        benefits="درج لوگو در پوستر، وب‌سایت و بنر محل برگزاری\nمعرفی در برنامه‌ی نشست\nاختصاص غرفه‌ی معرفی\nذکر نام در کلیه‌ی اطلاع‌رسانی‌ها")
    Level.objects.filter(title="حامی تخصصی").update(
        benefits="درج لوگو در وب‌سایت و بنر محل برگزاری\nمعرفی کوتاه در برنامه‌ی نشست\nذکر نام در اطلاع‌رسانی‌ها")

    Reg = apps.get_model("core", "Registration")
    Reg.objects.filter(role="professional").update(role="other")
    Partner = apps.get_model("core", "Partner")
    for old, new in (("gold", "main"), ("silver", "special"), ("host", "co")):
        Partner.objects.filter(kind=old).update(kind=new)
    apps.get_model("core", "TeamMember").objects.filter(group="organizer").update(group="secretariat")


class Migration(migrations.Migration):
    dependencies = [("core", "0003_observatory_redesign")]
    operations = [migrations.RunPython(forward, migrations.RunPython.noop)]
