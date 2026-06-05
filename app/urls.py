from django.urls import path
from . import views

urlpatterns = [
    path("", views.connexion, name="connexion"),
    path("logout/", views.logout_view, name="logout"),
    path("Dashboard/", views.dashboard, name="Dashboard"),
    path("inscription/", views.inscription, name="inscription"),
    path("insert/", views.insert_data, name="insert_data"),
    path("pv/creer/", views.creer_pv, name="creer_pv"),
]