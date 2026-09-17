from llm import init_llm
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser

import requests


history = {}


class FormConversationState:
    def __init__(self, form_fields: list[dict]):
        """
        :param form_fields: liste de dicts au format renvoyé par l'API
            (label, type, values, description, placeholder, max_chars, optional)
        """
        # On ne garde que les champs obligatoires (optional == "false")
        self.fields = {
            f["id"]: f
            for f in form_fields
            if str(f.get("optional", "false")).lower() != "true"
        }
        self.answers = {}

    @property
    def missing_fields(self) -> dict:
        """Champs du schéma pas encore renseignés (id -> infos du champ)."""
        return {k: v for k, v in self.fields.items() if k not in self.answers}

    @property
    def is_complete(self) -> bool:
        """True uniquement quand TOUS les champs obligatoires ont une réponse."""
        return len(self.missing_fields) == 0

    def set_answer(self, field_id: str, value) -> None:
        self.answers[field_id] = value


def _describe_constraints(field_info: dict) -> str:
    """Construit une phrase décrivant les contraintes du champ (type, options, longueur)."""
    field_type = field_info.get("type")
    values = field_info.get("values") or []
    max_chars = field_info.get("max_chars") or 0

    if field_type == "select":
        options = [v for v in values if v.lower() != "select an option..."]
        return f"La valeur doit être EXACTEMENT une des options suivantes : {options}."

    if field_type == "check":
        return "La valeur doit être un booléen : true si l'utilisateur accepte/consent, false sinon."

    if max_chars:
        return f"La valeur ne doit pas dépasser {max_chars} caractères."

    return ""


def extract_single_answer(llm, field_info: dict, user_message: str):
    label = field_info.get("label", field_info["id"])
    field_type = field_info.get("type", "text")
    description = field_info.get("description", "")
    constraints = _describe_constraints(field_info)

    parser = JsonOutputParser()

    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "Extrait la valeur du champ '{label}' à partir du message de "
         "l'utilisateur.\n"
         "Description du champ : {description}\n"
         "Type de champ : {field_type}\n"
         "{constraints}\n\n"
         "Réponds UNIQUEMENT avec un JSON de la forme "
         '{{"value": <la valeur extraite>}}.\n'
         "Si le message ne contient pas d'information exploitable pour ce "
         'champ, réponds {{"value": null}}.'),
        ("human", "{user_message}"),
    ])

    chain = prompt | llm | parser
    result = chain.invoke({
        "label": label,
        "description": description,
        "field_type": field_type,
        "constraints": constraints,
        "user_message": user_message,
    })

    return result.get("value")


def generate_next_question(llm, state: FormConversationState) -> str:
    field_id, field_info = next(iter(state.missing_fields.items()))
    label = field_info.get("label", field_id)
    field_type = field_info.get("type", "text")
    description = field_info.get("description", "")
    placeholder = field_info.get("placeholder", "")
    values = field_info.get("values") or []

    extra = ""
    if field_type == "select":
        options = [v for v in values if v.lower() != "select an option..."]
        extra = f"Les options possibles sont : {', '.join(options)}."
    elif field_type == "check":
        extra = "Il s'agit d'une case à cocher : demande une confirmation oui/non."
    elif placeholder:
        extra = f"Exemple de réponse attendue : {placeholder}"

    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "Tu aides un utilisateur à remplir un formulaire, un champ à la "
         "fois. Pose UNE seule question claire et naturelle en français "
         "pour obtenir la valeur du champ suivant.\n\n"
         "Nom du champ : {label}\n"
         "Description : {description}\n"
         "{extra}\n\n"
         "Réponds uniquement avec la question, sans préambule."),
    ])

    chain = prompt | llm | StrOutputParser()
    return chain.invoke({"label": label, "description": description, "extra": extra})


def collect_and_fill_form(llm, ask_user_fn) -> dict:
    """
    :param ask_user_fn: fonction qui prend une question (str) et retourne
        la réponse de l'utilisateur (str). Ex: `input` en CLI, ou une
        fonction qui envoie le message dans ton chat et attend la réponse.
    """

    response = requests.get(
        "http://127.0.0.1:8000/extract",
        headers={"accept": "*/*"},
    )
    response.raise_for_status()
    data = response.json()
    print(f"réponse du scraping: {data}")

    if data.get("status") != "success":
        raise RuntimeError(f"L'API a renvoyé une erreur : {data}")

    form_fields = data["form_fields"]
    state = FormConversationState(form_fields)

    # 1. Boucle : une question par champ manquant, jusqu'à couverture totale
    while not state.is_complete:
        field_id, field_info = next(iter(state.missing_fields.items()))
        label = field_info.get("label", field_id)

        question = generate_next_question(llm, state)
        user_reply = ask_user_fn(question)

        value = extract_single_answer(llm, field_info, user_reply)

        if value is None:
            print(f"La valeur de '{label}' n'est pas cohérente, "
                  f"la question sera reposée.")
            continue  # on ne marque PAS le champ comme répondu -> reposé

        state.set_answer(field_id, value)

    assert state.is_complete

    final_answers = state.answers

    # Construction du payload attendu par l'API :
    # { "responses": { <id>: [(value, type)], ... } }
    responses_payload = {
        field_id: [value, state.fields[field_id]["type"]]
        for field_id, value in final_answers.items()
    }

    fill_response = requests.post(
        "http://127.0.0.1:8000/fill",
        json={"responses": responses_payload},
    )
    fill_response.raise_for_status()
    print(f"réponse du fill: {fill_response.json()}")

    return final_answers

def get_session_history(session_id):
    if session_id not in history:
        history[session_id] = InMemoryChatMessageHistory()
    return history[session_id]

llm = init_llm()

if __name__ == "__main__":
    def ask_user(question: str) -> str:
        print(f"Assistant: {question}")
        return input("Vous: ")

    answers = collect_and_fill_form(llm, ask_user_fn=ask_user)
    print("Formulaire rempli avec :", answers)