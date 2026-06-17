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



def tableau_de_bord(request):
    if 'utilisateur_id' not in request.session:
        return HttpResponseRedirect('/')

    pvs = list(ProcesVerbalVillage.objects.all())
    total = len(pvs)

    regions = list(set(pv.region for pv in pvs if pv.region))
    nrg = len(regions)
    ndp = len(set(pv.departement for pv in pvs if pv.departement))
    nsp = len(set(pv.sous_prefecture for pv in pvs if pv.sous_prefecture))

    with_litige = sum(1 for pv in pvs if pv.zones_litigieuses)
    chef_terre = sum(1 for pv in pvs if pv.chef_de_terre)

    # Villages sans acte de création (sans historique)
    sans_acte = sum(1 for pv in pvs if not pv.historique)
    actp = round((sans_acte / total * 100), 1) if total else 0

    # Fondateurs sans accord avec populations trouvées
    lien_persone_non_count = sum(
        1 for pv in pvs
        if pv.historique and not pv.historique.accords_avec_populations
    )
    lien_persone_non = round((lien_persone_non_count / total * 100), 1) if total else 0

    # Fondateurs sans lien avec personnes trouvées (pas de personnes_trouvees_sur_place)
    lien = sum(
        1 for pv in pvs
        if pv.historique and not pv.historique.personnes_trouvees_sur_place
    )
    liennul = round((lien / total * 100), 1) if total else 0

    chefoui = round((chef_terre / total * 100), 1) if total else 0

    # Modes d'accès à la terre
    heritage_count = sum(1 for pv in pvs if pv.modes_acces_terre and pv.modes_acces_terre.heritage)
    don_count = sum(1 for pv in pvs if pv.modes_acces_terre and pv.modes_acces_terre.don)
    achat_count = sum(1 for pv in pvs if pv.modes_acces_terre and pv.modes_acces_terre.achat)
    location_count = sum(1 for pv in pvs if pv.modes_acces_terre and pv.modes_acces_terre.location)

    context = {
        'histoire': pvs,
        'nrg': nrg,
        'ndp': ndp,
        'nsp': nsp,
        'actp': actp,
        'lien_persone_non': lien_persone_non,
        'lien': lien,
        'liennul': liennul,
        'chef_terre': chef_terre,
        'chefoui': chefoui,
        'total_villages': total,
        'with_litige': with_litige,
        'heritage_count': heritage_count,
        'don_count': don_count,
        'achat_count': achat_count,
        'location_count': location_count,
        'nom': request.session.get('nom'),
        'prenom': request.session.get('prenom'),
        'regions': regions,
    }
    return render(request, 'tableau-de-bord.html', context)


def liste_villages(request):
    if 'utilisateur_id' not in request.session:
        return HttpResponseRedirect('/')
    pvs = ProcesVerbalVillage.objects.all()
    context = {
        'pvs': pvs,
        'nom': request.session.get('nom'),
        'prenom': request.session.get('prenom'),
    }
    return render(request, 'village/liste.html', context)


def detail_village(request, pk):
    if 'utilisateur_id' not in request.session:
        return HttpResponseRedirect('/')
    pv = ProcesVerbalVillage.objects.get(id=pk)
    context = {
        'pv': pv,
        'nom': request.session.get('nom'),
        'prenom': request.session.get('prenom'),
    }
    return render(request, 'village/detail.html', context)


def modifier_village(request, pk):
    if 'utilisateur_id' not in request.session:
        return HttpResponseRedirect('/')
    pv = ProcesVerbalVillage.objects.get(id=pk)

    success = None
    error = None

    if request.method == 'POST':
        try:
            pv.region = request.POST.get('region')
            pv.departement = request.POST.get('departement')
            pv.sous_prefecture = request.POST.get('sous_prefecture')
            pv.village = request.POST.get('village')
            pv.commissaire_enqueteur = request.POST.get('commissaire_enqueteur')
            date_enquete_str = request.POST.get('date_enquete')
            if date_enquete_str:
                pv.date_enquete = datetime.strptime(date_enquete_str, '%Y-%m-%d').date()

            if request.POST.get('declarant_nom'):
                dd = request.POST.get('declarant_date_naissance')
                ddn = datetime.strptime(dd, '%Y-%m-%d').date() if dd else None
                pv.declarant = Declarant(
                    nom=request.POST.get('declarant_nom'),
                    prenom=request.POST.get('declarant_prenom', ''),
                    date_naissance=ddn,
                    lieu_naissance=request.POST.get('declarant_lieu_naissance', ''),
                    qualite=request.POST.get('declarant_qualite', ''),
                    residence=request.POST.get('declarant_residence', ''),
                )

            if request.POST.get('signification_nom'):
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
                villages_voisins = [v.strip() for v in request.POST.get('villages_voisins', '').split(',') if v.strip()]
                regroupement_villages = [v.strip() for v in request.POST.get('regroupement_villages', '').split(',') if v.strip()]
                pv.historique = HistoriqueVillage(
                    signification_nom=request.POST.get('signification_nom', ''),
                    fondateur=request.POST.get('fondateur', ''),
                    activite_fondateur=request.POST.get('activite_fondateur', ''),
                    lieu_inhumation=request.POST.get('lieu_inhumation', ''),
                    origine_fondateur=request.POST.get('origine_fondateur', ''),
                    personnes_trouvees_sur_place=request.POST.get('personnes_trouvees', ''),
                    accords_avec_populations=request.POST.get('accords_populations', ''),
                    epoque_installation=request.POST.get('epoque_installation', ''),
                    lignages=lignages,
                    villages_voisins=villages_voisins,
                    regroupement_villages=regroupement_villages,
                )

            chefs = []
            c_noms = request.POST.getlist('chef_nom[]')
            c_prenoms = request.POST.getlist('chef_prenom[]')
            c_debuts = request.POST.getlist('chef_debut_regne[]')
            c_fins = request.POST.getlist('chef_fin_regne[]')
            for i, nom in enumerate(c_noms):
                nom = nom.strip()
                if nom:
                    debut = datetime.strptime(c_debuts[i], '%Y-%m-%d').date() if i < len(c_debuts) and c_debuts[i] else None
                    fin = datetime.strptime(c_fins[i], '%Y-%m-%d').date() if i < len(c_fins) and c_fins[i] else None
                    chefs.append(Chef(nom=nom, prenom=c_prenoms[i].strip() if i < len(c_prenoms) else '', debut_regne=debut, fin_regne=fin))
            pv.chefs = chefs

            campements = []
            cp_noms = request.POST.getlist('campement_nom[]')
            cp_orig = request.POST.getlist('campement_origine[]')
            for i, nom in enumerate(cp_noms):
                nom = nom.strip()
                if nom:
                    campements.append(Campement(nom=nom, origine_population=cp_orig[i].strip() if i < len(cp_orig) else ''))
            pv.campements = campements

            sites = []
            s_types = request.POST.getlist('site_type[]')
            s_loc = request.POST.getlist('site_localisation[]')
            for i, typ in enumerate(s_types):
                typ = typ.strip()
                if typ:
                    sites.append(SiteAdoration(type_site=typ, localisation=s_loc[i].strip() if i < len(s_loc) else ''))
            pv.sites_adoration = sites

            limites = []
            for desc in request.POST.getlist('limite_description[]'):
                desc = desc.strip()
                if desc:
                    limites.append(LimiteVillage(description=desc))
            pv.limites = limites

            mode_acces_value = request.POST.get('mode_acces_principal', '')
            pv.modes_acces_terre = ModeAccesTerre(
                heritage=mode_acces_value == 'heritage',
                don=mode_acces_value == 'don',
                pret=mode_acces_value == 'pret',
                achat=mode_acces_value == 'achat',
                location=mode_acces_value == 'location',
            )

            pv.chef_de_terre = request.POST.get('chef_de_terre') == 'oui'
            pv.zones_litigieuses = request.POST.get('zones_litigieuses') == 'oui'
            pv.informations_complementaires = request.POST.get('informations_complementaires', '')

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
                    age = int(p_ages[i]) if i < len(p_ages) and p_ages[i].strip().isdigit() else None
                    personnes.append(Personne(nom=nom, prenom=p_prenoms[i].strip() if i < len(p_prenoms) else '',
                        qualite=p_qualites[i].strip() if i < len(p_qualites) else '', age=age,
                        lieu_residence=p_residences[i].strip() if i < len(p_residences) else '',
                        signature=p_signatures[i].strip() if i < len(p_signatures) else ''))
            pv.personnes_presentes = personnes

            pv.save()
            success = 'Village modifié avec succès !'
        except Exception as e:
            error = f'Erreur : {str(e)}'

    context = {
        'pv': pv,
        'success': success,
        'error': error,
        'nom': request.session.get('nom'),
        'prenom': request.session.get('prenom'),
    }
    return render(request, 'village/modifier.html', context)


def supprimer_village(request, pk):
    if 'utilisateur_id' not in request.session:
        return HttpResponseRedirect('/')
    pv = ProcesVerbalVillage.objects.get(id=pk)
    if request.method == 'POST':
        pv.delete()
        return redirect('liste_villages')
    context = {
        'pv': pv,
        'nom': request.session.get('nom'),
        'prenom': request.session.get('prenom'),
    }
    return render(request, 'village/confirmer-suppression.html', context)


def rapport_pdf(request, pk):
    from io import BytesIO
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import cm, mm
    from reportlab.lib.colors import HexColor
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
    from reportlab.lib import colors

    if 'utilisateur_id' not in request.session:
        return HttpResponseRedirect('/')

    pv = ProcesVerbalVillage.objects.get(id=pk)

    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            topMargin=2*cm, bottomMargin=2*cm,
                            leftMargin=2*cm, rightMargin=2*cm)

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle('Title2', parent=styles['Title'],
                                  fontSize=18, leading=22, alignment=TA_CENTER,
                                  textColor=HexColor('#1C3A5E'), spaceAfter=6)
    sub_style = ParagraphStyle('Sub2', parent=styles['Normal'],
                                fontSize=11, leading=14, alignment=TA_CENTER,
                                textColor=HexColor('#555555'), spaceAfter=20)
    section_style = ParagraphStyle('Section', parent=styles['Heading2'],
                                    fontSize=13, leading=16, textColor=HexColor('#1C3A5E'),
                                    spaceBefore=16, spaceAfter=6)
    field_style = ParagraphStyle('Field', parent=styles['Normal'],
                                  fontSize=10, leading=13, spaceAfter=2)
    label_style = ParagraphStyle('Label', parent=styles['Normal'],
                                  fontSize=10, leading=13, textColor=HexColor('#888888'),
                                  spaceAfter=1)

    elements = []

    elements.append(Paragraph("RÉPUBLIQUE DE CÔTE D'IVOIRE", title_style))
    elements.append(Paragraph("Agence Foncière Rurale (AFOR)", sub_style))
    elements.append(HRFlowable(width="100%", thickness=2, color=HexColor('#1C3A5E')))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph("PROCÈS-VERBAL DE VILLAGE", ParagraphStyle('MainTitle',
        parent=styles['Title'], fontSize=16, leading=20, alignment=TA_CENTER,
        textColor=HexColor('#2D5F8A'), spaceAfter=20)))

    # Infos administratives
    elements.append(Paragraph("1. INFORMATIONS ADMINISTRATIVES", section_style))
    admin_data = [
        ['Région', pv.region or '—'],
        ['Département', pv.departement or '—'],
        ['Sous-Préfecture', pv.sous_prefecture or '—'],
        ['Village', pv.village or '—'],
        ['Commissaire Enquêteur', pv.commissaire_enqueteur or '—'],
        ["Date d'enquête", str(pv.date_enquete) if pv.date_enquete else '—'],
    ]
    t = Table(admin_data, colWidths=[5*cm, 10*cm])
    t.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('TEXTCOLOR', (0, 0), (0, -1), HexColor('#1C3A5E')),
        ('BACKGROUND', (0, 0), (0, -1), HexColor('#F0F4F8')),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#CCCCCC')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 10))

    # Déclarant
    if pv.declarant:
        elements.append(Paragraph("2. DÉCLARANT", section_style))
        d = pv.declarant
        dec_data = [
            ['Nom', d.nom or '—'],
            ['Prénom', d.prenom or '—'],
            ['Date de naissance', str(d.date_naissance) if d.date_naissance else '—'],
            ['Lieu de naissance', d.lieu_naissance or '—'],
            ['Qualité', d.qualite or '—'],
            ['Résidence', d.residence or '—'],
        ]
        t = Table(dec_data, colWidths=[5*cm, 10*cm])
        t.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('TEXTCOLOR', (0, 0), (0, -1), HexColor('#1C3A5E')),
            ('BACKGROUND', (0, 0), (0, -1), HexColor('#F0F4F8')),
            ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#CCCCCC')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 10))

    # Historique
    if pv.historique:
        elements.append(Paragraph("3. HISTORIQUE DU VILLAGE", section_style))
        h = pv.historique
        hist_labels = [
            ('Signification du nom', h.signification_nom),
            ('Fondateur', h.fondateur),
            ('Activité du fondateur', h.activite_fondateur),
            ("Lieu d'inhumation", h.lieu_inhumation),
            ('Origine du fondateur', h.origine_fondateur),
            ('Personnes trouvées sur place', h.personnes_trouvees_sur_place),
            ('Accords avec populations', h.accords_avec_populations),
            ("Époque d'installation", h.epoque_installation),
        ]
        hist_data = [[Paragraph(f'<b>{lbl}</b>', field_style), Paragraph(val or '—', field_style)] for lbl, val in hist_labels]
        t = Table(hist_data, colWidths=[5*cm, 10*cm])
        t.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 0.3, HexColor('#DDDDDD')),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(t)

        if h.lignages:
            elements.append(Paragraph("Lignages :", styles['Heading3']))
            lign_data = [['N°', 'Nom du lignage', "Ordre d'arrivée"]]
            for i, lig in enumerate(h.lignages, 1):
                lign_data.append([str(i), lig.nom_lignage or '—', str(lig.ordre_arrivee) if lig.ordre_arrivee else '—'])
            t = Table(lign_data, colWidths=[1*cm, 8*cm, 6*cm])
            t.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1C3A5E')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#CCCCCC')),
                ('TOPPADDING', (0, 0), (-1, -1), 3),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                ('ALIGN', (0, 0), (0, -1), 'CENTER'),
            ]))
            elements.append(t)
        elements.append(Spacer(1, 10))

    # Chefs
    if pv.chefs:
        elements.append(Paragraph("4. CHEFS DU VILLAGE", section_style))
        chef_data = [['N°', 'Nom', 'Prénom', 'Début règne', 'Fin règne']]
        for i, c in enumerate(pv.chefs, 1):
            chef_data.append([str(i), c.nom or '—', c.prenom or '—',
                              str(c.debut_regne) if c.debut_regne else '—',
                              str(c.fin_regne) if c.fin_regne else '—'])
        t = Table(chef_data, colWidths=[1*cm, 4*cm, 4*cm, 3*cm, 3*cm])
        t.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1C3A5E')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#CCCCCC')),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 10))

    # Campements
    if pv.campements:
        elements.append(Paragraph("5. CAMPEMENTS", section_style))
        camp_data = [['N°', 'Nom', 'Origine population']]
        for i, c in enumerate(pv.campements, 1):
            camp_data.append([str(i), c.nom or '—', c.origine_population or '—'])
        t = Table(camp_data, colWidths=[1*cm, 6*cm, 8*cm])
        t.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1C3A5E')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#CCCCCC')),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 10))

    # Sites d'adoration
    if pv.sites_adoration:
        elements.append(Paragraph("6. SITES SACRÉS", section_style))
        site_data = [['N°', 'Type', 'Localisation']]
        for i, s in enumerate(pv.sites_adoration, 1):
            site_data.append([str(i), s.type_site or '—', s.localisation or '—'])
        t = Table(site_data, colWidths=[1*cm, 6*cm, 8*cm])
        t.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1C3A5E')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#CCCCCC')),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 10))

    # Limites
    if pv.limites:
        elements.append(Paragraph("7. LIMITES TERRITORIALES", section_style))
        lim_data = [['N°', 'Description']]
        for i, l in enumerate(pv.limites, 1):
            lim_data.append([str(i), l.description or '—'])
        t = Table(lim_data, colWidths=[1*cm, 14*cm])
        t.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1C3A5E')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#CCCCCC')),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 10))

    # Mode accès terre
    if pv.modes_acces_terre:
        elements.append(Paragraph("8. MODE D'ACCÈS À LA TERRE", section_style))
        m = pv.modes_acces_terre
        acces_data = [
            ['Héritage', 'Oui' if m.heritage else 'Non'],
            ['Don', 'Oui' if m.don else 'Non'],
            ['Prêt', 'Oui' if m.pret else 'Non'],
            ['Achat', 'Oui' if m.achat else 'Non'],
            ['Location', 'Oui' if m.location else 'Non'],
        ]
        t = Table(acces_data, colWidths=[5*cm, 10*cm])
        t.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('TEXTCOLOR', (0, 0), (0, -1), HexColor('#1C3A5E')),
            ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#CCCCCC')),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 6))

    # Chef de terre / litige
    info_data = [
        ['Chef de terre', 'Oui' if pv.chef_de_terre else 'Non'],
        ['Zones litigieuses', 'Oui' if pv.zones_litigieuses else 'Non'],
    ]
    t = Table(info_data, colWidths=[5*cm, 10*cm])
    t.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('TEXTCOLOR', (0, 0), (0, -1), HexColor('#1C3A5E')),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#CCCCCC')),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 6))

    # Infos complémentaires
    if pv.informations_complementaires:
        elements.append(Paragraph("9. INFORMATIONS COMPLÉMENTAIRES", section_style))
        elements.append(Paragraph(pv.informations_complementaires, field_style))
        elements.append(Spacer(1, 10))

    # Personnes présentes
    if pv.personnes_presentes:
        elements.append(Paragraph("10. PERSONNES PRÉSENTES", section_style))
        pers_data = [['N°', 'Nom', 'Prénom', 'Qualité', 'Âge', 'Résidence']]
        for i, p in enumerate(pv.personnes_presentes, 1):
            pers_data.append([str(i), p.nom or '—', p.prenom or '—', p.qualite or '—',
                              str(p.age) if p.age else '—', p.lieu_residence or '—'])
        t = Table(pers_data, colWidths=[1*cm, 3*cm, 3*cm, 3*cm, 1.5*cm, 3.5*cm])
        t.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1C3A5E')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#CCCCCC')),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('ALIGN', (3, 0), (4, -1), 'CENTER'),
        ]))
        elements.append(t)

    elements.append(Spacer(1, 20))
    elements.append(HRFlowable(width="100%", thickness=1, color=HexColor('#CCCCCC')))
    elements.append(Spacer(1, 8))
    elements.append(Paragraph("Document généré par le système de digitalisation AFOR", ParagraphStyle('Footer',
        parent=styles['Normal'], fontSize=8, alignment=TA_CENTER, textColor=HexColor('#999999'))))

    doc.build(elements)
    pdf_bytes = buf.getvalue()
    buf.close()

    from django.http import HttpResponse
    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    filename = f"PV_{pv.village or 'village'}_{pv.departement or 'inconnu'}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


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