import csv

from django.contrib import admin
from django.db import models as dj_models
from django.http import HttpResponse
from django.utils.html import format_html

from . import jalali
from .models import (FAQ, ImportantDate, Partner, Registration, SiteSettings, SponsorInquiry, SponsorLevel, Submission, TeamMember)

admin.site.site_header = "پنل مدیریت رویداد روز GIS"
admin.site.site_title = "مدیریت رویداد"
admin.site.index_title = "مدیریت"


class JalaliDatesMixin:
    formfield_overrides = {dj_models.DateField: {"form_class": jalali.JalaliDateField}}


@admin.action(description="خروجی CSV از موارد انتخاب‌شده")
def export_csv(modeladmin, request, queryset):
    opts = modeladmin.model._meta
    fields = [f for f in opts.fields if f.get_internal_type() not in ("FileField", "ImageField")]
    resp = HttpResponse(content_type="text/csv; charset=utf-8")
    resp["Content-Disposition"] = f'attachment; filename="{opts.model_name}.csv"'
    resp.write("﻿")
    w = csv.writer(resp)
    w.writerow([f.verbose_name for f in fields])
    for obj in queryset:
        row = []
        for f in fields:
            v = getattr(obj, f.name)
            if f.choices:
                v = getattr(obj, f"get_{f.name}_display")()
            elif hasattr(v, "strftime"):
                v = v.strftime("%Y-%m-%d %H:%M")
            row.append(str(v) if v is not None else "")
        w.writerow(row)
    return resp


def _file_link(f):
    return format_html('<a href="{}">دانلود</a>', f.url) if f else "—"


@admin.register(SiteSettings)
class SiteSettingsAdmin(JalaliDatesMixin, admin.ModelAdmin):
    fieldsets = [
        ("اطلاعات اصلی", {"fields": ["event_name", "tagline", "hero_text", "tracks_text"]}),
        ("زمان و مکان", {"fields": ["event_date", "time_text", "city", "venue_text", "venue_url", "format_text"]}),
        ("فراخوان", {"fields": ["call_open", "call_deadline"]}),
        ("متن‌های تبلیغی", {"fields": ["networking_text", "unveil_text", "show_sponsors_section"]}),
        ("ثبت‌نام و پرداخت", {"fields": ["phase", "payment_link", "price_text", "registration_note"],
                              "description": "برای شروع ثبت‌نام واقعی: مرحله را روی «ثبت‌نام و پرداخت» بگذارید و لینک زرین‌پال را وارد کنید."}),
        ("تماس و شبکه‌های اجتماعی", {"fields": ["contact_email", "contact_phone", "telegram_url", "instagram_url"]}),
    ]

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        from django.shortcuts import redirect
        return redirect("admin:core_sitesettings_change", SiteSettings.load().pk)


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ["name", "role", "group", "order", "visible"]
    list_editable = ["order", "visible"]
    list_filter = ["group"]


@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display = ["name", "kind", "order", "visible"]
    list_editable = ["order", "visible"]
    list_filter = ["kind"]


@admin.register(SponsorLevel)
class SponsorLevelAdmin(admin.ModelAdmin):
    list_display = ["title", "order", "visible"]
    list_editable = ["order", "visible"]


@admin.register(ImportantDate)
class ImportantDateAdmin(admin.ModelAdmin):
    list_display = ["title", "date_text", "order", "highlight", "visible"]
    list_editable = ["order", "highlight", "visible"]


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ["question", "order", "visible"]
    list_editable = ["order", "visible"]


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ["full_name", "kind", "mode", "title", "affiliation", "status", "when", "cv", "slides"]
    list_filter = ["kind", "mode", "status", "track"]
    list_editable = ["status"]
    search_fields = ["full_name", "email", "title", "affiliation"]
    readonly_fields = ["created_at", "cv", "slides"]
    actions = [export_csv]

    @admin.display(description="زمان ثبت", ordering="created_at")
    def when(self, obj):
        return f"{jalali.format_short(obj.created_at)} {jalali.fa_digits(obj.created_at.astimezone().strftime('%H:%M'))}"

    @admin.display(description="رزومه")
    def cv(self, obj):
        return _file_link(obj.cv_file)

    @admin.display(description="اسلاید/ضمیمه")
    def slides(self, obj):
        return _file_link(obj.slides_file)


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ["full_name", "phone", "email", "role", "organization", "attend", "is_final", "paid", "when"]
    list_filter = ["is_final", "paid", "role", "attend"]
    list_editable = ["paid"]
    search_fields = ["full_name", "email", "phone", "organization"]
    readonly_fields = ["created_at", "is_final"]
    actions = [export_csv]

    @admin.display(description="زمان ثبت", ordering="created_at")
    def when(self, obj):
        return jalali.format_short(obj.created_at)


@admin.register(SponsorInquiry)
class SponsorInquiryAdmin(admin.ModelAdmin):
    list_display = ["company", "contact_name", "email", "phone", "level", "handled", "when"]
    list_editable = ["handled"]
    list_filter = ["handled", "level"]
    actions = [export_csv]

    @admin.display(description="زمان ثبت", ordering="created_at")
    def when(self, obj):
        return jalali.format_short(obj.created_at)


# Dashboard counters on the admin index page.
admin.site.index_template = "admin/dashboard_index.html"
_orig_index = admin.site.index


def _index(request, extra_context=None):
    ctx = dict(extra_context or {})
    kinds = {k: Submission.objects.filter(kind=k).count() for k, _ in Submission.KINDS}
    ctx["stats"] = [
        *[(label, kinds[k]) for k, label in Submission.KINDS],
        ("پیش‌ثبت‌نام", Registration.objects.filter(is_final=False).count()),
        ("ثبت‌نام قطعی", Registration.objects.filter(is_final=True).count()),
        ("پرداخت‌شده", Registration.objects.filter(paid=True).count()),
        ("درخواست اسپانسر", SponsorInquiry.objects.count()),
    ]
    return _orig_index(request, ctx)


admin.site.index = _index
