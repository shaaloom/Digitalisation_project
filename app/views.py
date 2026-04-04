from django.http import JsonResponse
from django.shortcuts import render
from django.http import HttpResponse
from .models import Village, Chef

def connexion(request):
    return render(request,"index.html")
def Dashboard(request):
    return HttpResponse("<h1>Tableau de bord</h1>")

def insert_data(request):

    chef = Chef(
        nom="Diarrassouba",
        prenom="Kolotieloma"
    )

    village = Village(
        nom_village="Zouan",
        region="Guemon",
        departement="Duekoue",
        chef=chef
    )

    village.save()

    return JsonResponse({"message": "Village enregistré avec succès"})
