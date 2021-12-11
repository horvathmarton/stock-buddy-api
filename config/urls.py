"""api URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import os

from django.contrib import admin
from django.urls import include, path
from rest_framework.authtoken import views
from core.views import RootView

urlpatterns = [
    path("", RootView.as_view()),
    path("auth/", views.obtain_auth_token),
    path("admin/", admin.site.urls),
    path("raw-data/", include("apps.raw_data.urls")),
    path("stocks/", include("apps.stocks.urls")),
    path("transactions/", include("apps.transactions.urls")),
]

if os.getenv("DEBUG_MODE") == "true":
    urlpatterns += [path("auth-api/", include("rest_framework.urls"))]
