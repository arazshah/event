import re

from django import forms

from .models import Registration, SponsorInquiry, Submission


class HoneypotMixin(forms.Form):
    website_url = forms.CharField(required=False, widget=forms.TextInput(attrs={"tabindex": "-1", "autocomplete": "off"}))

    def clean_website_url(self):
        if self.cleaned_data.get("website_url"):
            raise forms.ValidationError("spam")
        return ""


def _clean_phone(value):
    value = value.translate(str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789"))
    digits = re.sub(r"[\s\-()]", "", value)
    if not re.fullmatch(r"\+?\d{8,15}", digits):
        raise forms.ValidationError("شماره موبایل معتبر نیست.")
    return digits


class SubmissionForm(HoneypotMixin, forms.ModelForm):
    class Meta:
        model = Submission
        fields = ["kind", "mode", "full_name", "email", "phone", "affiliation", "country_city", "title",
                  "abstract", "track", "duration", "bio", "link", "cv_file", "slides_file"]
        widgets = {"abstract": forms.Textarea(attrs={"rows": 6}), "bio": forms.Textarea(attrs={"rows": 3}),
                   "kind": forms.RadioSelect, "mode": forms.RadioSelect}

    def __init__(self, *args, tracks=(), **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["phone"].required = True
        self.fields["duration"].required = False
        self.fields["abstract"].label = "چکیده (حداکثر ۳۰۰ کلمه)"
        self.fields["kind"].choices = Submission.KINDS
        self.fields["mode"].choices = Submission.MODES
        if tracks:
            self.fields["track"] = forms.ChoiceField(
                label="زیرمحور", required=False, choices=[("", "---------")] + [(t, t) for t in tracks] + [("سایر", "سایر")]
            )

    def clean_phone(self):
        return _clean_phone(self.cleaned_data["phone"])

    def clean(self):
        data = super().clean()
        if data.get("kind") == Submission.KIND_ONLINE:
            data["mode"] = "online"
        return data


class RegistrationForm(HoneypotMixin, forms.ModelForm):
    class Meta:
        model = Registration
        fields = ["full_name", "phone", "email", "role", "organization", "attend", "interests"]
        widgets = {"interests": forms.Textarea(attrs={"rows": 3}), "role": forms.RadioSelect, "attend": forms.RadioSelect}

    def __init__(self, *args, is_final=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_final = is_final

    def clean_phone(self):
        return _clean_phone(self.cleaned_data["phone"])

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if Registration.objects.filter(email__iexact=email, is_final=self.is_final).exists():
            raise forms.ValidationError("با این ایمیل قبلاً ثبت‌نام شده است.")
        return email


class SponsorInquiryForm(HoneypotMixin, forms.ModelForm):
    class Meta:
        model = SponsorInquiry
        fields = ["company", "contact_name", "email", "phone", "level", "message"]
        widgets = {"message": forms.Textarea(attrs={"rows": 4})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from .models import SponsorLevel
        self.fields["level"].queryset = SponsorLevel.objects.filter(visible=True)
        self.fields["level"].empty_label = "هنوز مطمئن نیستم"
