"""Règles déterministes du site source. Aucune correction par IA."""
import re
from datetime import date, datetime
from zoneinfo import ZoneInfo

from .content import ACTIVITIES, EXPERIENCES, EXPECTATIONS


def normalize_lines(value: str) -> str:
    return value.replace("\r\n", "\n").replace("\r", "\n")


def text_length(value: str) -> int:
    return len(normalize_lines(value).encode("utf-16-le")) // 2


def missing(label: str) -> str:
    return f"E100 — Valeur requise : {label}."


def too_long(label: str, limit: int) -> str:
    return f"E112 — Longueur maximale dépassée : {label}, {limit} caractères."


def email_valid(value: str) -> bool:
    if text_length(value) > 254 or value.count("@") != 1 or re.search(r"\s", value):
        return False
    local, domain = value.rsplit("@", 1)
    if not re.fullmatch(r"[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+", local):
        return False
    if len(local) > 64 or local.startswith(".") or local.endswith(".") or ".." in local:
        return False
    labels = domain.split(".")
    return len(labels) >= 2 and bool(re.fullmatch(r"[a-zA-Z]{2,}", labels[-1])) and all(
        re.fullmatch(r"[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?", label)
        for label in labels
    )


def validate_account(values: dict, today: date | None = None) -> list[str]:
    errors = []
    for key, label in [("first_name", "Prénom du titulaire"), ("last_name", "Nom du titulaire")]:
        values[key] = values.get(key, "").strip()
        if not values[key]:
            errors.append(missing(label))
        elif text_length(values[key]) > 80:
            errors.append(too_long(label, 80))
    values["email"] = values.get("email", "").strip()
    if not values["email"]:
        errors.append(missing("Adresse électronique de correspondance"))
    elif not email_valid(values["email"]):
        errors.append("E101 — Adresse électronique non conforme au format attendu.")

    # Order follows the form: identity, date, credentials, optional membership.
    raw_date = values.get("birth_date", "")
    if not raw_date:
        errors.append(missing("Date de naissance"))
    else:
        try:
            if not re.fullmatch(r"[0-9]{2}/[0-9]{2}/[0-9]{4}", raw_date):
                raise ValueError
            born = datetime.strptime(raw_date, "%d/%m/%Y").date()
            today = today or datetime.now(ZoneInfo("Europe/Paris")).date()
            if born > today:
                errors.append("E106 — Date de naissance postérieure à la date courante.")
            elif today.year - born.year - ((today.month, today.day) < (born.month, born.day)) < 18:
                errors.append("E107 — Condition de majorité non satisfaite.")
        except ValueError:
            errors.append("E105 — Date non conforme. Format attendu : JJ/MM/AAAA.")
    password = values.get("password", "")
    if not password:
        errors.append(missing("Secret d’authentification"))
    elif not 12 <= text_length(password) <= 128:
        errors.append("E103 — Secret d’authentification : longueur attendue de 12 à 128 caractères.")
    confirmation = values.get("password_confirmation", "")
    if not confirmation:
        errors.append(missing("Réitération du secret"))
    elif confirmation != password:
        errors.append("E104 — Discordance des secrets d’authentification.")
    if values.get("member_code") and not re.fullmatch(r"[0-9]{6}", values["member_code"]):
        errors.append("E108 — Référence attendue : six caractères numériques.")
    return errors


def validate_registration(values: dict) -> list[str]:
    errors = []
    activity = values.get("activity", "")
    slot = values.get("slot", "")
    if not activity:
        errors.append(missing("Activité sollicitée"))
    elif activity not in ACTIVITIES:
        errors.append("E109 — Sélection non reconnue : Activité sollicitée.")
    if not slot:
        errors.append(missing("Session de rattachement"))
    elif activity in ACTIVITIES and slot not in ACTIVITIES[activity]["slots"]:
        errors.append("E110 — Incompatibilité activité/session.")
    experience = values.get("experience", "")
    if not experience:
        errors.append(missing("Positionnement expérientiel"))
    elif experience not in EXPERIENCES:
        errors.append("E109 — Sélection non reconnue : Positionnement expérientiel.")
    selections = values.get("expectations", [])
    if any(item not in EXPECTATIONS for item in selections):
        errors.append("E109 — Sélection non reconnue : Attentes associées à la participation.")
    elif not 1 <= len(selections) <= 3 or len(set(selections)) != len(selections):
        errors.append("E111 — Cardinalité des attentes non conforme : de 1 à 3 valeurs.")
    fields = [("presentation_fr", "Finalité participative — version française")]
    if activity == "photo":
        fields.append(("presentation_en", "Finalité participative — version anglaise"))
    else:
        values["presentation_en"] = ""
    for key, label in fields:
        values[key] = normalize_lines(values.get(key, ""))
        if not values[key].strip():
            errors.append(missing(label))
        elif text_length(values[key]) > 200:
            errors.append(too_long(label, 200))
    if values.get("terms_accepted") != "on":
        errors.append("E113 — Acceptation des conditions requise.")
    if values.get("newsletter", "") not in ("", "on"):
        errors.append("E109 — Sélection non reconnue : Réception des actualités associatives.")
    return errors
