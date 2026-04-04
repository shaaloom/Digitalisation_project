#from django.urls import path

#from .views import insert_data
#from . import views

#urlpatterns = [
    #path("", views.connection, name="connection"),
    #path("", views.connexion, name="connexion"),
    #path('Dashboard/', views.Dashboard, name='Dashboard'),
    #path('insert/', insert_data, name='insert_data'),

from django.urls import path
from . import views

urlpatterns = [
    path("", views.connexion, name="connexion"),
    path("Dashboard/", views.dashboard, name="Dashboard"),
    path("insert/", views.insert_data, name="insert_data"),
]
    #path('formulairemanuscrit/',views.formulairemanuscrit,name='formulairemanuscrit'),
   # path("datah", views.datatables, name="datah"),
    #path('logout', views.logout_view, name='logout'),
    #path('detail<str:pk>', views.detaille, name='detail'),
    #path('rapport<str:pk>', views.rapport_pdf, name='rapport'),
    #path('visualisation', views.visualisationt, name='visualisation'),
    #path('modifier<str:pk>', views.modifier, name='modifier'),
    #]


