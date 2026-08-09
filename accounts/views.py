from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect, render


def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Hay dos backends configurados (Google y usuario/contrasena), asi
            # que hay que decirle a Django con cual quedo autenticado; si no,
            # login() lanza ValueError y el registro truena.
            login(request, user, backend="django.contrib.auth.backends.ModelBackend")
            return redirect("index")
    else:
        form = UserCreationForm()
    return render(
        request,
        "registration/signup.html",
        {"form": form, "google_enabled": settings.GOOGLE_LOGIN_ENABLED},
    )
