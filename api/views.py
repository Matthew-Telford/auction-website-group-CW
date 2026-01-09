from django.contrib.auth import authenticate, login
from django.http import HttpResponse, HttpRequest, JsonResponse
from django.shortcuts import render


def main_spa(request: HttpRequest) -> HttpResponse:
    return render(request, "api/spa/index.html", {})


def user_login(request):
    email = request.POST["email"]
    password = request.POST["password"]
    user = authenticate(request, username=email, password=password)
    if user is not None:
        login(request, user)
