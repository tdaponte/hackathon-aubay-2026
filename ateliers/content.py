"""Catalogue et textes visibles du site, indépendants de tout assistant IA."""

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
        "name": "Photographie avec échanges internationaux", "short_name": "Photographie",
        "category": "REGARDS & RENCONTRES",
        "description": "Découvrir la photographie et échanger avec des participants francophones et anglophones. Tous niveaux.",
        "number": "03", "slots": {
            "photo-10": "10 octobre 2026, 14 h–16 h",
            "photo-17": "17 octobre 2026, 14 h–16 h",
        },
    },
}
EXPERIENCES = {
    "aucune": "Aucune pratique",
    "occasionnelle": "Pratique occasionnelle",
    "reguliere": "Pratique régulière",
}
EXPECTATIONS = {
    "decouvrir": "Découvrir une activité",
    "apprendre": "Apprendre une technique",
    "rencontrer": "Rencontrer des personnes",
    "creer": "Créer quelque chose",
    "partager": "Partager mon expérience",
    "langue": "Pratiquer une langue",
}
CATALOG_TEXT = [
    "L’association Les ateliers du quartier propose un programme d’initiation et de pratique collective à destination des adultes. L’accès aux séances s’effectue après ouverture d’un espace personnel et transmission d’une demande d’inscription mentionnant l’activité sollicitée, la session retenue et les attentes du participant. La création de l’espace personnel ne vaut pas inscription à une activité. Chaque demande porte sur un atelier et un créneau ; son enregistrement est confirmé à l’issue de la procédure.",
    "Les séances ne donnent lieu à aucun paiement et le matériel nécessaire est mis à disposition sur place. Elles se déroulent à la Maison des ateliers — Bordeaux, lieu fictif. Pour permettre aux animateurs de préparer l’accueil, le formulaire sollicite un positionnement expérientiel, une expression de la finalité participative ainsi qu’une sélection des attentes associées à la participation. Une à trois attentes doivent être renseignées.",
    "Les séances de photographie avec échanges internationaux accueillent des participants francophones et anglophones. Une présentation succincte en français et sa version anglaise sont demandées pour cette activité. L’anglais n’est pas un prérequis pour participer : une aide à la traduction est autorisée. Pour les autres activités, seule la présentation française est nécessaire.",
    "Les personnes déjà adhérentes à l’association peuvent reporter le code à six chiffres figurant sur leur carte. Ce renseignement est facultatif et son absence ne fait pas obstacle à la création du compte. Les modalités relatives au compte, aux limites de saisie et à la participation sont précisées dans les formulaires suivants.",
]
TERMS = "Je confirme le choix de mon atelier et de mon créneau. Je comprends que l’activité est gratuite, que le matériel est fourni et que l’inscription concerne uniquement cette séance."
ACCOUNT_FIELDS = [
    ("first_name", "Prénom du titulaire", "text", 80, True, "given-name"),
    ("last_name", "Nom du titulaire", "text", 80, True, "family-name"),
    ("email", "Adresse électronique de correspondance", "email", 254, True, "email"),
    ("birth_date", "Date de naissance", "text", 10, True, "bday"),
    ("password", "Secret d’authentification", "password", 128, True, "new-password"),
    ("password_confirmation", "Réitération du secret", "password", 128, True, "new-password"),
    ("member_code", "Référence d’adhésion antérieure", "text", 6, False, "off"),
]
