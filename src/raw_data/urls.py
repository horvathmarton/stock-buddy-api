from django.urls import path
from django.urls.resolvers import URLPattern
from .views import StockViews

urlpatterns = [
    path('stocks', StockViews.as_view()),
]