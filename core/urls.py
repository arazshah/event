from django.urls import path

from . import views

app_name = "core"
urlpatterns = [
    path("", views.home, name="home"),
    path("call/", views.call, name="call"),
    path("register/", views.register, name="register"),
    path("sponsor/", views.sponsor, name="sponsor"),
    path("thanks/<str:what>/", views.thanks, name="thanks"),
    path("healthz", views.healthz, name="healthz"),
    path("private-files/<path:path>", views.private_file, name="private_file"),
]
