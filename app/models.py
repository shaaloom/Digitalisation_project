from mongoengine import Document, EmbeddedDocument, StringField, EmbeddedDocumentField

class Chef(EmbeddedDocument):
    nom = StringField()
    prenom = StringField()

class Village(Document):
    nom_village = StringField()
    region = StringField()
    departement = StringField()
    chef = EmbeddedDocumentField(Chef)