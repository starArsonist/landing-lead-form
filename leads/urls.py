from django.urls import path

from . import views

urlpatterns = [
    path("", views.landing, name="landing"),
    path("lead/", views.submit, name="submit"),
    path("thanks/", views.thanks, name="thanks"),
]
