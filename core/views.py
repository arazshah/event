from django.conf import settings
from django.core.exceptions import SuspiciousFileOperation
from django.contrib.admin.views.decorators import staff_member_required
from django.core.cache import cache
from django.http import FileResponse, Http404, HttpResponse
from django.shortcuts import redirect, render
from django.utils._os import safe_join

from .forms import RegistrationForm, SponsorInquiryForm, SubmissionForm
from .models import FAQ, ImportantDate, Partner, SiteSettings, SponsorLevel, Submission, TeamMember

PARTNER_GROUPS = [("host", "میزبان"), ("co", "همکاران برگزاری"), ("gold", "اسپانسر طلایی"),
                  ("silver", "اسپانسر نقره‌ای"), ("media", "حامیان رسانه‌ای")]


def _throttled(request, key, limit=8, window=3600):
    ip = request.META.get("HTTP_X_FORWARDED_FOR", request.META.get("REMOTE_ADDR", "")).split(",")[0].strip()
    k = f"thr:{key}:{ip}"
    n = cache.get(k, 0)
    if n >= limit:
        return True
    cache.set(k, n + 1, window)
    return False


def healthz(request):
    return HttpResponse("ok")


def home(request):
    partners = Partner.objects.filter(visible=True)
    groups = [(title, [p for p in partners if p.kind == k]) for k, title in PARTNER_GROUPS]
    groups = [(t, ps) for t, ps in groups if ps]
    team = TeamMember.objects.filter(visible=True)
    return render(request, "core/home.html", {
        "kinds": Submission.KINDS,
        "partner_groups": groups,
        "organizers": [m for m in team if m.group == "organizer"],
        "scientific": [m for m in team if m.group == "scientific"],
        "levels": SponsorLevel.objects.filter(visible=True),
        "dates": ImportantDate.objects.filter(visible=True),
        "faqs": FAQ.objects.filter(visible=True),
    })


def call(request):
    s = SiteSettings.load()
    initial = {"kind": request.GET.get("type", Submission.KIND_SPEAKER), "mode": "inperson"}
    if request.method == "POST":
        form = SubmissionForm(request.POST, request.FILES, tracks=s.track_list)
        if not s.call_open:
            form.add_error(None, "فراخوان بسته شده است.")
        elif form.is_valid():
            if _throttled(request, "call"):
                form.add_error(None, "تعداد درخواست‌ها زیاد است؛ کمی بعد دوباره تلاش کنید.")
            else:
                form.save()
                return redirect("core:thanks", what="call")
    else:
        form = SubmissionForm(initial=initial, tracks=s.track_list)
    return render(request, "core/call.html", {"form": form})


def register(request):
    s = SiteSettings.load()
    final = s.is_registration
    if request.method == "POST":
        form = RegistrationForm(request.POST, is_final=final)
        if form.is_valid():
            if _throttled(request, "reg"):
                form.add_error(None, "تعداد درخواست‌ها زیاد است؛ کمی بعد دوباره تلاش کنید.")
            else:
                obj = form.save(commit=False)
                obj.is_final = final
                obj.save()
                return redirect("core:thanks", what="register-final" if final else "register")
    else:
        form = RegistrationForm(is_final=final)
    return render(request, "core/register.html", {"form": form})


def sponsor(request):
    levels = SponsorLevel.objects.filter(visible=True)
    if request.method == "POST":
        form = SponsorInquiryForm(request.POST)
        if form.is_valid():
            if _throttled(request, "spon", limit=5):
                form.add_error(None, "تعداد درخواست‌ها زیاد است؛ کمی بعد دوباره تلاش کنید.")
            else:
                form.save()
                return redirect("core:thanks", what="sponsor")
    else:
        form = SponsorInquiryForm()
    return render(request, "core/sponsor.html", {"form": form, "levels": levels})


def thanks(request, what):
    if what not in {"call", "register", "register-final", "sponsor"}:
        raise Http404
    return render(request, "core/thanks.html", {"what": what})


@staff_member_required
def private_file(request, path):
    try:
        full = safe_join(settings.PRIVATE_ROOT, path)
        return FileResponse(open(full, "rb"), as_attachment=True)
    except (ValueError, SuspiciousFileOperation, FileNotFoundError, IsADirectoryError):
        raise Http404
