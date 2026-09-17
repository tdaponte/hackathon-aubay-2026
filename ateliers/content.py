"""Catalogue visible du site source simplifié."""
LOCATION = "Maison des ateliers — Bordeaux, lieu fictif"
ACTIVITIES = {
    "peinture": {
        "name": "Peinture", "short_name": "Peinture", "category": "COULEURS & MATIÈRES",
        "description": "Découvrir la peinture et réaliser une création personnelle. Tous niveaux.",
        "number": "01", "slots": {
            "peinture-03": "3 octobre 2026, 10 h–12 h",
            "peinture-10": "10 octobre 2026, 10 h–12 h",
        },
    },
    "poterie": {
        "name": "Poterie", "short_name": "Poterie", "category": "GESTES & SAVOIR-FAIRE",
        "description": "Découvrir le modelage et fabriquer un petit objet. Tous niveaux.",
        "number": "02", "slots": {
            "poterie-07": "7 octobre 2026, 14 h–16 h",
            "poterie-14": "14 octobre 2026, 14 h–16 h",
        },
    },
    "photo": {
        "name": "Photographie", "short_name": "Photographie", "category": "REGARDS & RENCONTRES",
        "description": "Découvrir la photographie et apprendre à composer une image. Tous niveaux.",
        "number": "03", "slots": {
            "photo-10": "10 octobre 2026, 14 h–16 h",
            "photo-17": "17 octobre 2026, 14 h–16 h",
        },
    },
}
CATALOG_TEXT = [
    "L’association Les ateliers du quartier propose un programme d’initiation et de pratique collective. L’accès aux séances s’effectue après ouverture d’un espace personnel et transmission d’une demande mentionnant l’activité sollicitée et la session retenue. La création de l’espace personnel ne vaut pas réservation d’une activité.",
    "Les séances ne donnent lieu à aucun paiement et le matériel nécessaire est mis à disposition sur place. Elles se déroulent à la Maison des ateliers — Bordeaux, lieu fictif. Chaque réservation porte sur un atelier et un créneau ; son enregistrement est confirmé à l’issue de la procédure.",
    "Le titulaire est identifié par son prénom et son adresse électronique de correspondance. Le secret d’authentification est défini lors de l’ouverture de l’espace adhérent. Les modalités de saisie sont précisées dans le formulaire suivant. Une seule réservation par activité est admise pour un même compte.",
]
ACCOUNT_FIELDS = [
    ("first_name", "Prénom du titulaire", "text", 80, True, "given-name"),
    ("email", "Adresse électronique de correspondance", "email", 254, True, "email"),
    ("password", "Secret d’authentification", "password", 128, True, "new-password"),
]
