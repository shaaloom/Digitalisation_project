#from django.http import JsonResponse
#from django.shortcuts import render
#from django.http import HttpResponse
#from .models import Village, Chef

#def connexion(request):
 #   return render(request,"index.html")
#def Dashboard(request):
 #   return HttpResponse("<h1>Tableau de bord</h1>")

#def insert_data(request):

 #   chef = Chef(
  #      nom="Diarrassouba",
   #     prenom="Kolotieloma"
    #)

    #village = Village(
     #   nom_village="Zouan",
      #  region="Guemon",
       # departement="Duekoue",
        #chef=chef
    #)

    #village.save()

    #return JsonResponse({"message": "Village enregistré avec succès"})
from django.http import JsonResponse
from django.shortcuts import render
from django.http import HttpResponse
from datetime import date

from .models import ProcesVerbalVillage, Chef


def connexion(request):
    return render(request, "index.html")


def dashboard(request):
    return HttpResponse("<h1>Tableau de bord</h1>")


def insert_data(request):

    chef = Chef(
        nom="Diarrassouba",
        prenom="Kolotieloma"
    )

    pv = ProcesVerbalVillage(
        departement="Guemon",
        sous_prefecture="Duekoue",
        village="Zouan",
        date_enquete=date.today(),
        chefs=[chef]
    )

    pv.save()

    return JsonResponse({"message": "PV enregistré avec succès"})
