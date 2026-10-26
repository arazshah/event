from django.conf import settings
from django.core.files.storage import FileSystemStorage


class PrivateStorage(FileSystemStorage):
    """Uploads that only staff may download (CVs, slides)."""

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("location", settings.PRIVATE_ROOT)
        kwargs.setdefault("base_url", settings.PRIVATE_URL)
        super().__init__(*args, **kwargs)


def private_storage():
    return PrivateStorage()
