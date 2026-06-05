from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from datetime import date, datetime
from .models import (
    ProcesVerbalVillage, Chef, Utilisateur,
    Declarant, HistoriqueVillage, Lignage,
    Campement, SiteAdoration, LimiteVillage,
    ModeAccesTerre, Personne
)


def connexion(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            utilisateur = Utilisateur.objects.get(username=username)
            if utilisateur.est_actif:
                if utilisateur.password == password:
                    request.session['utilisateur_id'] = str(utilisateur.id)
                    request.session['username'] = utilisateur.username
                    request.session['role'] = utilisateur.role
                    request.session['nom'] = utilisateur.nom
                    request.session['prenom'] = utilisateur.prenom
                    utilisateur.deriere_connexion = date.today()
                    utilisateur.save()
                    return HttpResponseRedirect('/pv/creer/')
                else:
                    return render(request, 'registration/login.html', {
                        'error': 'Mot de passe incorrect',
                        'username': username
                    })
            else:
                return render(request, 'registration/login.html', {
                    'error': 'Compte désactivé',
                    'username': username
                })
        except Utilisateur.DoesNotExist:
            return render(request, 'registration/login.html', {
                'error': 'Nom d\'utilisateur incorrect',
                'username': username
            })
    return render(request, 'registration/login.html')


def logout_view(request):
    request.session.flush()
    return HttpResponseRedirect('/')


def dashboard(request):
    if 'utilisateur_id' not in request.session:
        return HttpResponseRedirect('/')
    context = {
        'username': request.session.get('username'),
        'nom': request.session.get('nom'),
        'prenom': request.session.get('prenom'),
        'role': request.session.get('role'),
    }
    return render(request, 'index.html', context)


def inscription(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        nom = request.POST.get('nom')
        prenom = request.POST.get('prenom')
        email = request.POST.get('email')
        if Utilisateur.objects(username=username).first():
            return render(request, 'registration/inscription.html', {
                'error': 'Ce nom d\'utilisateur existe déjà'
            })
        utilisateur = Utilisateur(
            username=username,
            password=password,
            nom=nom,
            prenom=prenom,
            email=email,
            role='utilisateur',
            est_actif=True,
            date_creation=date.today()
        )
        utilisateur.save()
        return redirect('connexion')
    return render(request, 'registration/inscription.html')


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



def creer_pv(request):
    if 'utilisateur_id' not in request.session:
        return HttpResponseRedirect('/')

    success = None
    error = None

    if request.method == 'POST':
        try:
            region = request.POST.get('region')
            departement = request.POST.get('departement')
            sous_prefecture = request.POST.get('sous_prefecture')
            village = request.POST.get('village')
            commissaire_enqueteur = request.POST.get('commissaire_enqueteur')

            date_enquete_str = request.POST.get('date_enquete')
            date_enquete = (
                datetime.strptime(date_enquete_str, '%Y-%m-%d').date()
                if date_enquete_str else None
            )

            # --- Déclarant ---
            declarant = None
            if request.POST.get('declarant_nom'):
                dd = request.POST.get('declarant_date_naissance')
                ddn = datetime.strptime(dd, '%Y-%m-%d').date() if dd else None
                declarant = Declarant(
                    nom=request.POST.get('declarant_nom'),
                    prenom=request.POST.get('declarant_prenom', ''),
                    date_naissance=ddn,
                    lieu_naissance=request.POST.get('declarant_lieu_naissance', ''),
                    qualite=request.POST.get('declarant_qualite', ''),
                    residence=request.POST.get('declarant_residence', ''),
                )

            # --- Lignages ---
            lignages = []
            l_noms = request.POST.getlist('lignage_nom[]')
            l_ordres = request.POST.getlist('lignage_ordre[]')
            for i, nom in enumerate(l_noms):
                nom = nom.strip()
                if nom:
                    ordre = l_ordres[i].strip() if i < len(l_ordres) else ''
                    lignages.append(Lignage(
                        nom_lignage=nom,
                        ordre_arrivee=int(ordre) if ordre.isdigit() else None
                    ))

            # --- Villages voisins / regroupement ---
            villages_voisins = [
                v.strip() for v in
                request.POST.get('villages_voisins', '').split(',')
                if v.strip()
            ]
            regroupement_villages = [
                v.strip() for v in
                request.POST.get('regroupement_villages', '').split(',')
                if v.strip()
            ]

            # --- Historique ---
            historique = None
            if request.POST.get('signification_nom'):
                historique = HistoriqueVillage(
                    signification_nom=request.POST.get('signification_nom', ''),
                    fondateur=request.POST.get('fondateur', ''),
                    activite_fondateur=request.POST.get('activite_fondateur', ''),
                    lieu_inhumation=request.POST.get('lieu_inhumation', ''),
                    origine_fondateur=request.POST.get('origine_fondateur', ''),
                    personnes_trouvees_sur_place=request.POST.get(
                        'personnes_trouvees', ''
                    ),
                    accords_avec_populations=request.POST.get(
                        'accords_populations', ''
                    ),
                    epoque_installation=request.POST.get('epoque_installation', ''),
                    lignages=lignages,
                    villages_voisins=villages_voisins,
                    regroupement_villages=regroupement_villages,
                )

            # --- Chefs ---
            chefs = []
            c_noms = request.POST.getlist('chef_nom[]')
            c_prenoms = request.POST.getlist('chef_prenom[]')
            c_debuts = request.POST.getlist('chef_debut_regne[]')
            c_fins = request.POST.getlist('chef_fin_regne[]')
            for i, nom in enumerate(c_noms):
                nom = nom.strip()
                if nom:
                    debut = (
                        datetime.strptime(c_debuts[i], '%Y-%m-%d').date()
                        if i < len(c_debuts) and c_debuts[i] else None
                    )
                    fin = (
                        datetime.strptime(c_fins[i], '%Y-%m-%d').date()
                        if i < len(c_fins) and c_fins[i] else None
                    )
                    chefs.append(Chef(
                        nom=nom,
                        prenom=c_prenoms[i].strip() if i < len(c_prenoms) else '',
                        debut_regne=debut,
                        fin_regne=fin,
                    ))

            # --- Campements ---
            campements = []
            cp_noms = request.POST.getlist('campement_nom[]')
            cp_orig = request.POST.getlist('campement_origine[]')
            for i, nom in enumerate(cp_noms):
                nom = nom.strip()
                if nom:
                    campements.append(Campement(
                        nom=nom,
                        origine_population=(
                            cp_orig[i].strip() if i < len(cp_orig) else ''
                        ),
                    ))

            # --- Sites d'adoration ---
            sites = []
            s_types = request.POST.getlist('site_type[]')
            s_loc = request.POST.getlist('site_localisation[]')
            for i, typ in enumerate(s_types):
                typ = typ.strip()
                if typ:
                    sites.append(SiteAdoration(
                        type_site=typ,
                        localisation=s_loc[i].strip() if i < len(s_loc) else '',
                    ))

            # --- Limites ---
            limites = []
            for desc in request.POST.getlist('limite_description[]'):
                desc = desc.strip()
                if desc:
                    limites.append(LimiteVillage(description=desc))

            # --- Mode accès terre ---
            mode_acces_value = request.POST.get('mode_acces_principal', '')
            mode_acces = ModeAccesTerre(
                heritage=mode_acces_value == 'heritage',
                don=mode_acces_value == 'don',
                pret=mode_acces_value == 'pret',
                achat=mode_acces_value == 'achat',
                location=mode_acces_value == 'location',
            )

            # --- Personnes présentes ---
            personnes = []
            p_noms = request.POST.getlist('personne_nom[]')
            p_prenoms = request.POST.getlist('personne_prenom[]')
            p_qualites = request.POST.getlist('personne_qualite[]')
            p_ages = request.POST.getlist('personne_age[]')
            p_residences = request.POST.getlist('personne_residence[]')
            p_signatures = request.POST.getlist('personne_signature[]')
            for i, nom in enumerate(p_noms):
                nom = nom.strip()
                if nom:
                    age = None
                    if i < len(p_ages) and p_ages[i].strip().isdigit():
                        age = int(p_ages[i])
                    personnes.append(Personne(
                        nom=nom,
                        prenom=p_prenoms[i].strip() if i < len(p_prenoms) else '',
                        qualite=p_qualites[i].strip() if i < len(p_qualites) else '',
                        age=age,
                        lieu_residence=(
                            p_residences[i].strip() if i < len(p_residences) else ''
                        ),
                        signature=(
                            p_signatures[i].strip() if i < len(p_signatures) else ''
                        ),
                    ))

            pv = ProcesVerbalVillage(
                region=region,
                departement=departement,
                sous_prefecture=sous_prefecture,
                village=village,
                commissaire_enqueteur=commissaire_enqueteur,
                date_enquete=date_enquete,
                declarant=declarant,
                historique=historique,
                chefs=chefs,
                campements=campements,
                sites_adoration=sites,
                limites=limites,
                modes_acces_terre=mode_acces,
                chef_de_terre=request.POST.get('chef_de_terre') == 'oui',
                zones_litigieuses=request.POST.get('zones_litigieuses') == 'oui',
                informations_complementaires=request.POST.get(
                    'informations_complementaires', ''
                ),
                personnes_presentes=personnes,
            )
            pv.save()
            success = 'Procès-verbal enregistré avec succès !'

        except Exception as e:
            error = f'Erreur lors de l\'enregistrement : {str(e)}'

    context = {
        'success': success,
        'error': error,
        'nom': request.session.get('nom'),
        'prenom': request.session.get('prenom'),
    }
    return render(request, 'pv/create.html', context)