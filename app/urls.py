from django.urls import path
from . import views

urlpatterns = [
    path("", views.connexion, name="connexion"),
    path("logout/", views.logout_view, name="logout"),
    path("Dashboard/", views.dashboard, name="Dashboard"),
    path("inscription/", views.inscription, name="inscription"),
    path("insert/", views.insert_data, name="insert_data"),
    path("pv/creer/", views.creer_pv, name="creer_pv"),
    path("tableau-de-bord/", views.tableau_de_bord, name="tableau_de_bord"),
    path("villages/", views.liste_villages, name="liste_villages"),
    path("villages/detail/<str:pk>/", views.detail_village, name="detail_village"),
    path("villages/modifier/<str:pk>/", views.modifier_village, name="modifier_village"),
    path("villages/supprimer/<str:pk>/", views.supprimer_village, name="supprimer_village"),
    path("villages/rapport/<str:pk>/", views.rapport_pdf, name="rapport_pdf"),
]