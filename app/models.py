#from mongoengine import Document, EmbeddedDocument, StringField, EmbeddedDocumentField

#class Chef(EmbeddedDocument):
    #nom = StringField()
    #prenom = StringField()

#class Village(Document):
   # nom_village = StringField()
    #region = StringField()
   # departement = StringField()
   # chef = EmbeddedDocumentField(Chef)

from mongoengine import (
    Document, EmbeddedDocument,
    StringField, DateField, IntField,
    ListField, EmbeddedDocumentField, BooleanField
)

# -----------------------------
# PERSONNE
# -----------------------------
class Personne(EmbeddedDocument):
    nom = StringField(required=True)
    prenom = StringField()
    qualite = StringField()
    age = IntField()
    lieu_residence = StringField()
    signature = StringField()


# -----------------------------
# CHEF DU VILLAGE
# -----------------------------
class Chef(EmbeddedDocument):
    nom = StringField(required=True)
    prenom = StringField()
    debut_regne = DateField()
    fin_regne = DateField()


# -----------------------------
# LIGNAGE
# -----------------------------
class Lignage(EmbeddedDocument):
    nom_lignage = StringField()
    ordre_arrivee = IntField()


# -----------------------------
# CAMPMENT
# -----------------------------
class Campement(EmbeddedDocument):
    nom = StringField()
    origine_population = StringField()


# -----------------------------
# SITE SACRE
# -----------------------------
class SiteAdoration(EmbeddedDocument):
    type_site = StringField()  # foret, colline, rivière
    localisation = StringField()


# -----------------------------
# LIMITE TERRITORIALE
# -----------------------------
class LimiteVillage(EmbeddedDocument):
    description = StringField()  # rivière, arbre, colline


# -----------------------------
# MODE ACCES TERRE
# -----------------------------
class ModeAccesTerre(EmbeddedDocument):
    heritage = BooleanField()
    don = BooleanField()
    pret = BooleanField()
    achat = BooleanField()
    location = BooleanField()


# -----------------------------
# DECLARANT
# -----------------------------
class Declarant(EmbeddedDocument):
    nom = StringField()
    prenom = StringField()
    date_naissance = DateField()
    lieu_naissance = StringField()
    qualite = StringField()
    residence = StringField()


# -----------------------------
# HISTORIQUE DU VILLAGE
# -----------------------------
class HistoriqueVillage(EmbeddedDocument):

    signification_nom = StringField()

    fondateur = StringField()
    activite_fondateur = StringField()
    lieu_inhumation = StringField()

    origine_fondateur = StringField()
    personnes_trouvees_sur_place = StringField()
    accords_avec_populations = StringField()

    epoque_installation = StringField()

    lignages = ListField(EmbeddedDocumentField(Lignage))

    villages_voisins = ListField(StringField())

    regroupement_villages = ListField(StringField())


# -----------------------------
# DOCUMENT PV
# -----------------------------
class ProcesVerbalVillage(Document):

    # informations administratives
    departement = StringField(required=True)
    sous_prefecture = StringField()
    village = StringField(required=True)

    # enquête
    commissaire_enqueteur = StringField()
    date_enquete = DateField()

    declarant = EmbeddedDocumentField(Declarant)

    # historique
    historique = EmbeddedDocumentField(HistoriqueVillage)

    # chefs du village
    chefs = ListField(EmbeddedDocumentField(Chef))

    # campements
    campements = ListField(EmbeddedDocumentField(Campement))

    # sites sacrés
    sites_adoration = ListField(EmbeddedDocumentField(SiteAdoration))

    # limites du village
    limites = ListField(EmbeddedDocumentField(LimiteVillage))

    # accès à la terre
    modes_acces_terre = EmbeddedDocumentField(ModeAccesTerre)

    chef_de_terre = BooleanField()

    # conflits
    zones_litigieuses = BooleanField()

    # informations complémentaires
    informations_complementaires = StringField()

    # personnes présentes (annexe)
    personnes_presentes = ListField(EmbeddedDocumentField(Personne))

    meta = {
        "collection": "proces_verbaux_villages"
    }