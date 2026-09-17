"""
bridge.py
=========

Relie le back-end conversationnel (form_backend.py) au front Streamlit
(interface_streamlit.py) SANS serveur web : la communication se fait
uniquement via deux fichiers JSON sur disque.

    current_field.json     : back-end -> front   (la question à afficher)
    current_response.json  : front -> back-end   (la réponse de l'utilisateur)

Chaque fichier porte un numéro de "version". Le front utilisait déjà ce
principe pour détecter un nouveau champ ; on applique exactement la même
logique côté back-end pour détecter une nouvelle réponse (polling simple).
"""

import json
import os
import time

CURRENT_FIELD_FILE = "current_field.json"
CURRENT_RESPONSE_FILE = "current_response.json"

# Traduction des types de champs back-end -> types compris par le front
BACKEND_TO_UI_TYPE = {
    "select": "dropdown",
    "check": "checkbox",
    "text": "text",
    "textarea": "textarea",
}

_version_counter = 0


def _map_field_to_ui_format(field_info: dict, question: str) -> dict:
    """
    Convertit un champ au format du back-end
        {label, type, values, description, placeholder, max_chars, optional}
    vers le format attendu par le front Streamlit
        {request, type, values, example, optional}
    """
    backend_type = field_info.get("type", "text")
    return {
        "request": question,
        "type": BACKEND_TO_UI_TYPE.get(backend_type, "text"),
        "values": field_info.get("values") or [],
        "example": field_info.get("placeholder", ""),
        "optional": bool(field_info.get("optional", False)),
    }


def _write_field(field_info: dict, question: str, version: int) -> None:
    ui_field = _map_field_to_ui_format(field_info, question)
    with open(CURRENT_FIELD_FILE, "w", encoding="utf-8") as f:
        json.dump({"field": ui_field, "version": version}, f, ensure_ascii=False, indent=2)
    print(f"➡️  Champ envoyé au front (version {version}) : {ui_field}")


def _read_response(expected_version: int, poll_interval: float = 0.3):
    """Attend que current_response.json contienne la version demandée."""
    while True:
        if os.path.exists(CURRENT_RESPONSE_FILE):
            try:
                with open(CURRENT_RESPONSE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if data.get("version") == expected_version:
                    print(f"⬅️  Réponse reçue du front : {data.get('response')!r}")
                    return data.get("response")
            except (json.JSONDecodeError, OSError):
                pass  # fichier en cours d'écriture côté front, on réessaie
        time.sleep(poll_interval)


def ask_user_via_streamlit(question: str, field_info: dict) -> str:
    """
    Remplace `input()` comme `ask_user_fn` dans collect_and_fill_form :
    écrit la question pour le front, attend la réponse de l'utilisateur
    (par polling fichier), et la renvoie.

    Signature volontairement différente de `ask_user_fn(question)` utilisée
    en CLI : il faut aussi `field_info` pour connaître le type/les valeurs
    du champ. Voir form_backend.py où l'appel devient
    `ask_user_fn(question, field_info)`.
    """
    global _version_counter
    _version_counter += 1
    _write_field(field_info, question, _version_counter)
    return _read_response(_version_counter)
