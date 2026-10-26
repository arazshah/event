import os

from django.conf import settings
from django.core.exceptions import ValidationError

ALLOWED_DOC_EXT = {".pdf", ".ppt", ".pptx", ".doc", ".docx", ".zip", ".png", ".jpg", ".jpeg"}


def validate_upload(f):
    ext = os.path.splitext(f.name)[1].lower()
    if ext not in ALLOWED_DOC_EXT:
        raise ValidationError("فرمت فایل مجاز نیست (pdf, pptx, docx, zip, png, jpg).")
    if f.size > settings.MAX_UPLOAD_MB * 1024 * 1024:
        raise ValidationError(f"حجم فایل نباید بیشتر از {settings.MAX_UPLOAD_MB} مگابایت باشد.")
