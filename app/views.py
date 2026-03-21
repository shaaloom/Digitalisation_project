from django.shortcuts import render
from django.http import HttpResponse
def connexion(request):
    return render(request,"index.html")
def Dashboard(request):
    return HttpResponse("<h1>Tableau de bord</h1>")
