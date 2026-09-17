"""Règles déterministes du site source. Aucune correction par IA."""
import re
from .content import ACTIVITIES


def text_length(value: str) -> int:
    return len(value.encode("utf-16-le")) // 2


def missing(label: str) -> str:
    return f"E100 — Valeur requise : {label}."


def email_valid(value: str) -> bool:
    if text_length(value) > 254 or value.count("@") != 1 or re.search(r"\s", value):
        return False
    local, domain = value.rsplit("@", 1)
    if not re.fullmatch(r"[a-zA-Z0-9.!#$%&'*+/=?^_\x60{|}~-]+", local):
        return False
    if len(local) > 64 or local.startswith(".") or local.endswith(".") or ".." in local:
        return False
    labels = domain.split(".")
    return len(labels) >= 2 and bool(re.fullmatch(r"[a-zA-Z]{2,}", labels[-1])) and all(
        re.fullmatch(r"[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?", label) for label in labels
    )


def validate_account(values: dict) -> list[str]:
    errors = []
    values["first_name"] = values.get("first_name", "").strip()
    if not values["first_name"]:
        errors.append(missing("Prénom du titulaire"))
    elif text_length(values["first_name"]) > 80:
        errors.append("E112 — Longueur maximale dépassée : Prénom du titulaire, 80 caractères.")
    values["email"] = values.get("email", "").strip()
    if not values["email"]:
        errors.append(missing("Adresse électronique de correspondance"))
    elif not email_valid(values["email"]):
        errors.append("E101 — Adresse électronique non conforme au format attendu.")
    password = values.get("password", "")
    if not password:
        errors.append(missing("Secret d’authentification"))
    elif not 12 <= text_length(password) <= 128:
        errors.append("E103 — Secret d’authentification : longueur attendue de 12 à 128 caractères.")
    return errors


def validate_registration(values: dict) -> list[str]:
    errors = []
    activity, slot = values.get("activity", ""), values.get("slot", "")
    if not activity:
        errors.append(missing("Activité sollicitée"))
    elif activity not in ACTIVITIES:
        errors.append("E109 — Sélection non reconnue : Activité sollicitée.")
    if not slot:
        errors.append(missing("Session de rattachement"))
    elif activity in ACTIVITIES and slot not in ACTIVITIES[activity]["slots"]:
        errors.append("E110 — Incompatibilité activité/session.")
    return errors
