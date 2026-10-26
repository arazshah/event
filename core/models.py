import datetime
import uuid

from django.db import models

from .storage import private_storage
from .validators import validate_upload


def _upload_to(instance, filename):
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "bin"
    return f"{uuid.uuid4().hex}.{ext}"


class SiteSettings(models.Model):
    """Single row holding everything the organiser may want to edit."""

    PHASE_PREREG = "prereg"
    PHASE_REG = "registration"
    PHASES = [(PHASE_PREREG, "پیش‌ثبت‌نام"), (PHASE_REG, "ثبت‌نام و پرداخت")]

    event_name = models.CharField("نام رویداد", max_length=120, default="روز جهانی GIS ارومیه")
    tagline = models.CharField("محور / زیرعنوان", max_length=200, default="GeoAI | هوش مصنوعی در علوم مکانی")
    hero_text = models.TextField(
        "متن معرفی",
        default="تازه‌ترین و تخصصی‌ترین مباحث هوش مصنوعی و علوم مکانی، در یک روز. "
        "فراخوان ارائه، سخنرانی و کارگاه باز است.",
    )
    event_date = models.DateField("تاریخ برگزاری (شمسی، مثل ۱۴۰۵/۰۸/۲۸)", default=datetime.date(2026, 11, 19))
    time_text = models.CharField("ساعت", max_length=100, default="به‌زودی اعلام می‌شود", blank=True)
    city = models.CharField("شهر", max_length=60, default="ارومیه")
    venue_text = models.CharField("مکان", max_length=200, default="به‌زودی اعلام می‌شود", blank=True)
    venue_url = models.URLField("لینک نقشه مکان", blank=True)
    format_text = models.CharField("نحوه برگزاری", max_length=120, default="حضوری + پخش آنلاین", blank=True)

    call_open = models.BooleanField("فراخوان باز است", default=True)
    call_deadline = models.DateField("مهلت ارسال پیشنهاد (شمسی)", default=datetime.date(2026, 11, 6))

    networking_text = models.TextField(
        "متن شبکه‌سازی",
        default="فرصتی برای دیدار و گفتگوی رودررو با متخصصان GIS، سنجش‌ازدور و هوش مصنوعی و ساختن ارتباط‌های حرفه‌ای.",
        blank=True,
    )
    unveil_text = models.TextField(
        "متن رونمایی محصول",
        default="در این رویداد از محصولات هوشمند حوزه علوم مکانی رونمایی می‌شود.",
        blank=True,
    )
    tracks_text = models.TextField(
        "زیرمحورها (هر خط یک مورد)",
        default="سنجش‌ازدور و یادگیری عمیق\nمدل‌های زبانی (LLM) و داده مکانی\nPostGIS و پایگاه داده مکانی برای هوش مصنوعی\nکاربردهای شهری و محیط‌زیستی هوش مصنوعی",
        blank=True,
    )

    phase = models.CharField("مرحله ثبت‌نام", max_length=20, choices=PHASES, default=PHASE_PREREG)
    payment_link = models.URLField("لینک پرداخت زرین‌پال", blank=True)
    price_text = models.CharField("مبلغ / توضیح هزینه", max_length=120, blank=True, help_text="مثلاً «۲۰۰٬۰۰۰ تومان» یا «رایگان»")
    registration_note = models.TextField("توضیح بعد از ثبت‌نام", blank=True)

    contact_email = models.EmailField("ایمیل تماس", blank=True)
    contact_phone = models.CharField("تلفن / واتساپ", max_length=40, blank=True)
    telegram_url = models.URLField("لینک تلگرام", blank=True)
    instagram_url = models.URLField("لینک اینستاگرام", blank=True)
    show_sponsors_section = models.BooleanField("نمایش بخش اسپانسرها", default=True)

    class Meta:
        verbose_name = "تنظیمات رویداد"
        verbose_name_plural = "تنظیمات رویداد"

    def __str__(self):
        return "تنظیمات رویداد"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    @property
    def track_list(self):
        return [t.strip() for t in self.tracks_text.splitlines() if t.strip()]

    @property
    def is_registration(self):
        return self.phase == self.PHASE_REG


class TeamMember(models.Model):
    GROUPS = [("organizer", "تیم برگزاری"), ("scientific", "کمیته علمی")]
    name = models.CharField("نام", max_length=120)
    role = models.CharField("سمت", max_length=120, blank=True)
    group = models.CharField("گروه", max_length=20, choices=GROUPS, default="organizer")
    photo = models.ImageField("عکس", upload_to="team/", blank=True)
    order = models.PositiveIntegerField("ترتیب", default=0)
    visible = models.BooleanField("نمایش", default=True)

    class Meta:
        ordering = ["group", "order", "id"]
        verbose_name = "عضو تیم"
        verbose_name_plural = "تیم و کمیته علمی"

    def __str__(self):
        return self.name


class Partner(models.Model):
    KINDS = [
        ("host", "میزبان"),
        ("co", "همکار برگزاری"),
        ("gold", "اسپانسر طلایی"),
        ("silver", "اسپانسر نقره‌ای"),
        ("media", "حامی رسانه‌ای"),
    ]
    name = models.CharField("نام", max_length=120)
    kind = models.CharField("نوع", max_length=10, choices=KINDS, default="co")
    logo = models.ImageField("لوگو", upload_to="partners/", blank=True)
    url = models.URLField("وب‌سایت", blank=True)
    order = models.PositiveIntegerField("ترتیب", default=0)
    visible = models.BooleanField("نمایش", default=True)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "همکار / اسپانسر"
        verbose_name_plural = "همکاران و اسپانسرها"

    def __str__(self):
        return f"{self.name} ({self.get_kind_display()})"


class SponsorLevel(models.Model):
    title = models.CharField("عنوان سطح", max_length=80)
    benefits = models.TextField("مزایا (هر خط یک مورد)")
    order = models.PositiveIntegerField("ترتیب", default=0)
    visible = models.BooleanField("نمایش", default=True)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "سطح حمایت"
        verbose_name_plural = "سطوح حمایت"

    def __str__(self):
        return self.title

    @property
    def benefit_list(self):
        return [b.strip() for b in self.benefits.splitlines() if b.strip()]


class Submission(models.Model):
    KIND_SPEAKER, KIND_PRESENT, KIND_WORKSHOP, KIND_ONLINE = "speaker", "presentation", "workshop", "online_abroad"
    KINDS = [
        (KIND_SPEAKER, "سخنران"),
        (KIND_PRESENT, "ارائه"),
        (KIND_WORKSHOP, "کارگاه"),
        (KIND_ONLINE, "ارائه آنلاین از خارج از کشور"),
    ]
    MODES = [("inperson", "حضوری"), ("online", "آنلاین"), ("either", "هر دو / فرقی ندارد")]
    STATUS = [("new", "جدید"), ("review", "در داوری"), ("accepted", "پذیرفته"), ("rejected", "رد شده")]

    kind = models.CharField("نوع", max_length=20, choices=KINDS)
    mode = models.CharField("شیوه حضور", max_length=10, choices=MODES, default="inperson")
    full_name = models.CharField("نام و نام خانوادگی", max_length=120)
    email = models.EmailField("ایمیل")
    phone = models.CharField("موبایل", max_length=30, blank=True)
    affiliation = models.CharField("دانشگاه / سازمان", max_length=160, blank=True)
    country_city = models.CharField("کشور / شهر", max_length=100, blank=True)
    title = models.CharField("عنوان", max_length=200)
    abstract = models.TextField("چکیده")
    track = models.CharField("زیرمحور", max_length=200, blank=True)
    duration = models.CharField("مدت پیشنهادی", max_length=60, blank=True)
    bio = models.TextField("معرفی کوتاه", blank=True)
    link = models.URLField("لینک (وب‌سایت، گیت‌هاب، لینکدین...)", blank=True)
    cv_file = models.FileField("رزومه", upload_to=_upload_to, storage=private_storage, blank=True, validators=[validate_upload])
    slides_file = models.FileField("اسلاید / فایل ضمیمه", upload_to=_upload_to, storage=private_storage, blank=True, validators=[validate_upload])
    status = models.CharField("وضعیت", max_length=10, choices=STATUS, default="new")
    admin_note = models.TextField("یادداشت داخلی", blank=True)
    created_at = models.DateTimeField("زمان ثبت", auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "پیشنهاد ارائه"
        verbose_name_plural = "پیشنهادهای فراخوان"

    def __str__(self):
        return f"{self.get_kind_display()} - {self.full_name}"


class Registration(models.Model):
    ATTEND = [("inperson", "حضوری"), ("online", "آنلاین")]
    ROLES = [("student", "دانشجو"), ("professional", "شاغل / پژوهشگر"), ("other", "سایر")]

    full_name = models.CharField("نام و نام خانوادگی", max_length=120)
    phone = models.CharField("موبایل", max_length=30)
    email = models.EmailField("ایمیل")
    role = models.CharField("وضعیت", max_length=15, choices=ROLES, default="student")
    organization = models.CharField("دانشگاه / سازمان", max_length=160, blank=True)
    attend = models.CharField("نحوه شرکت", max_length=10, choices=ATTEND, default="inperson")
    interests = models.TextField("علاقه‌مندی‌ها / توضیحات", blank=True)
    is_final = models.BooleanField("ثبت‌نام قطعی (مرحله پرداخت)", default=False, editable=False)
    paid = models.BooleanField("پرداخت تأیید شد", default=False)
    created_at = models.DateTimeField("زمان ثبت", auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "ثبت‌نام"
        verbose_name_plural = "پیش‌ثبت‌نام و ثبت‌نام‌ها"
        constraints = [
            models.UniqueConstraint(fields=["email", "is_final"], name="uniq_registration_email_stage"),
        ]

    def __str__(self):
        return self.full_name


class SponsorInquiry(models.Model):
    company = models.CharField("شرکت / سازمان", max_length=160)
    contact_name = models.CharField("نام رابط", max_length=120)
    email = models.EmailField("ایمیل")
    phone = models.CharField("تلفن", max_length=30, blank=True)
    level = models.ForeignKey(SponsorLevel, verbose_name="سطح موردنظر", null=True, blank=True, on_delete=models.SET_NULL)
    message = models.TextField("پیام", blank=True)
    handled = models.BooleanField("پیگیری شد", default=False)
    created_at = models.DateTimeField("زمان ثبت", auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "درخواست حمایت"
        verbose_name_plural = "درخواست‌های اسپانسر"

    def __str__(self):
        return self.company


class ImportantDate(models.Model):
    title = models.CharField("عنوان", max_length=120)
    date_text = models.CharField("تاریخ (متن آزاد)", max_length=80)
    order = models.PositiveIntegerField("ترتیب", default=0)
    highlight = models.BooleanField("پررنگ (مثلاً روز رویداد)", default=False)
    visible = models.BooleanField("نمایش", default=True)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "تاریخ مهم"
        verbose_name_plural = "تاریخ‌های مهم"

    def __str__(self):
        return self.title


class FAQ(models.Model):
    question = models.CharField("پرسش", max_length=200)
    answer = models.TextField("پاسخ")
    order = models.PositiveIntegerField("ترتیب", default=0)
    visible = models.BooleanField("نمایش", default=True)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "پرسش متداول"
        verbose_name_plural = "پرسش‌های متداول"

    def __str__(self):
        return self.question
