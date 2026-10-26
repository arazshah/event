from .models import SiteSettings


def site_settings(request):
    return {"S": SiteSettings.load()}
