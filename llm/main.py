from llm.scraping import form_scraping, fill_form
from llm import init_llm
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser

import requests


history = {}

class FormConversationState: 
    def __init__(self, schema: dict):
        self.schema = schema
        self.answers = {}
 
    @property
    def missing_fields(self) -> dict:
        """Champs du schéma pas encore renseignés."""
        return {k: v for k, v in self.schema.items() if k not in self.answers}
 
    @property
    def is_complete(self) -> bool:
        """True uniquement quand TOUS les champs du schéma ont une réponse."""
        return len(self.missing_fields) == 0
 
    def set_answer(self, field: str, value) -> None:
        self.answers[field] = value
 

def extract_single_answer(llm, field: str, field_type: str, user_message: str):
    parser = JsonOutputParser()
 
    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "Extrait la valeur du champ '{field}' à partir du message de "
         "l'utilisateur. Type de réponse attendu : {field_type}.\n\n"
         "Réponds UNIQUEMENT avec un JSON de la forme "
         '{{"value": <la valeur extraite>}}.\n'
         "Si le message ne contient pas d'information exploitable pour ce "
         'champ, demande une nouvelle fois à l\'utilisateur et réponds {{"value": null}}.'),
        ("human", "{user_message}"),
    ])
 
    chain = prompt | llm | parser
    result = chain.invoke({
        "field": field,
        "field_type": field_type,
        "user_message": user_message,
    })
    
    return result.get("value")
 

def generate_next_question(llm, state: FormConversationState) -> str:
    next_field, field_type = next(iter(state.missing_fields.items()))
 
    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "Tu aides un utilisateur à remplir un formulaire, un champ à la "
         "fois. Pose UNE seule question claire et naturelle en français"
         "pour obtenir la valeur du champ suivant.\n\n"
         "Nom du champ : {field}\n"
         "Type de réponse attendu : {field_type}\n\n"
         "Réponds uniquement avec la question, sans préambule."),
    ])
 
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({"field": next_field, "field_type": field_type})

def collect_and_fill_form(
    llm,
    form_url: str,
    ask_user_fn,
    form_selector: str = "form",
    submit: bool = False,
) -> dict:
    """
    :param ask_user_fn: fonction qui prend une question (str) et retourne
        la réponse de l'utilisateur (str). Ex: `input` en CLI, ou une
        fonction qui envoie le message dans ton chat et attend la réponse.
    """
    BASE_URL = "127.0.0.1"
    data = {}
    response = requests.post(f"{BASE_URL}", json=data)
    
    print(response.json())
    schema = response.json()
    state = FormConversationState(schema)
 
    # 1. Boucle : une question par champ manquant, jusqu'à couverture totale
    while not state.is_complete:
        field, field_type = next(iter(state.missing_fields.items()))
 
        question = generate_next_question(llm, state)
        user_reply = ask_user_fn(question)
 
        value = extract_single_answer(llm, field, field_type, user_reply)
 
        if value is None:
            print(f"La valeur de '{field}' n'est pas cohérente, "
                  f"la question sera reposée.")
            continue  # on ne marque PAS le champ comme répondu -> reposé
 
        state.set_answer(field, value)
 
   
    assert state.is_complete 
 
    final_answers = state.answers
 
    fill_form(form_url, final_answers, form_selector=form_selector, submit=submit)
    return final_answers

def get_session_history(session_id):
    if session_id not in history:
        history[session_id] = InMemoryChatMessageHistory()
    return history[session_id]

llm = init_llm()

if __name__ == "__main__": 
    FORM_URL = "file:///C:/Users/Hackathon_user/Documents/GitHub/hackathon-aubay-2026/forms.html"
  
    def ask_user(question: str) -> str:
        print(f"Assistant: {question}")
        return input("Vous: ")
 
    answers = collect_and_fill_form(llm, FORM_URL, ask_user_fn=ask_user, submit=False)
    print("Formulaire rempli avec :", answers)
