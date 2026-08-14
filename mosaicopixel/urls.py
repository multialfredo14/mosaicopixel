from django.conf import settings
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

from generator import views as generator_views


urlpatterns = [
    path("", generator_views.index, name="index"),
    path("preview", generator_views.preview, name="preview"),
    path("generate", generator_views.generate_pdf, name="generate_pdf"),
    path("mx-panel-2026", generator_views.stats_panel, name="stats_panel"),
    path("mx-panel-2026/inventario", generator_views.inventory_panel, name="inventory_panel"),
    path("mx-panel-2026/inventario/icono/<int:idx>.png", generator_views.inventory_icon, name="inventory_icon"),
    path("mx-panel-2026/inventario/agregar", generator_views.inventory_add, name="inventory_add"),
    path("mx-panel-2026/inventario/quitar", generator_views.inventory_remove, name="inventory_remove"),
    path("mx-panel-2026/inventario/fijar", generator_views.inventory_set, name="inventory_set"),
    path(
        "accounts/login/",
        auth_views.LoginView.as_view(
            template_name="registration/login.html",
            extra_context={"google_enabled": settings.GOOGLE_LOGIN_ENABLED},
        ),
        name="login",
    ),
    path("accounts/logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("oauth/", include("social_django.urls", namespace="social")),
    path("admin/", admin.site.urls),
]
