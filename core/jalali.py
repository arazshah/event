import datetime

import jdatetime
from django import forms

MONTHS = ["فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور", "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"]
WEEKDAYS = ["دوشنبه", "سه‌شنبه", "چهارشنبه", "پنجشنبه", "جمعه", "شنبه", "یکشنبه"]  # Monday=0
_FA = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")
_EN = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")


def fa_digits(value):
    return str(value).translate(_FA)


def to_jalali(d):
    if isinstance(d, datetime.datetime):
        d = d.date()
    return jdatetime.date.fromgregorian(date=d)


def format_long(d):
    j = to_jalali(d)
    return f"{WEEKDAYS[d.weekday()]} {fa_digits(j.day)} {MONTHS[j.month - 1]} {fa_digits(j.year)}"


def format_short(d):
    j = to_jalali(d)
    return fa_digits(f"{j.year:04d}/{j.month:02d}/{j.day:02d}")


class JalaliDateField(forms.DateField):
    """Accepts/edits dates as 1405/08/28 and stores a Gregorian date."""

    widget = forms.TextInput(attrs={"dir": "ltr", "placeholder": "1405/08/28", "size": 12})

    def prepare_value(self, value):
        if isinstance(value, (datetime.date, datetime.datetime)):
            j = to_jalali(value)
            return f"{j.year:04d}/{j.month:02d}/{j.day:02d}"
        return value

    def to_python(self, value):
        if value in self.empty_values:
            return None
        s = str(value).strip().translate(_EN).replace("-", "/").replace(".", "/")
        try:
            y, m, d = (int(p) for p in s.split("/"))
            return jdatetime.date(y, m, d).togregorian()
        except (ValueError, TypeError):
            raise forms.ValidationError("تاریخ شمسی را به شکل ۱۴۰۵/۰۸/۲۸ وارد کنید.")
