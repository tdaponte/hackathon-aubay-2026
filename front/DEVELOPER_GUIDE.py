"""
GUIDE COMPLET POUR DÉVELOPPERS - Streamlit Form App

Ce document explique comment le système fonctionne et comment l'étendre.
"""

# ============================================================================
# 1. COMPRENDRE LE FLUX
# ============================================================================

"""
FLUX GLOBAL:

1. Autre App envoie webhooks
                    ↓
2. Webhook Server reçoit et stocke
                    ↓
3. Streamlit App affiche le champ
                    ↓
4. Utilisateur remplit
                    ↓
5. Streamlit envoie la réponse
                    ↓
6. Autre App reçoit la réponse et envoie le champ suivant
"""


# ============================================================================
# 2. LES 3 FICHIERS PRINCIPAUX
# ============================================================================

"""
app.py
------
L'interface utilisateur Streamlit.

Concepts clés:
- st.session_state : Mémorise les données entre les rechargements
- st.text_input() : Champ texte
- st.button() : Bouton
- st.rerun() : Recharge la page

Comment ça marche:
1. Streamlit recharge le fichier à chaque interactionde l'utilisateur
2. On utilise session_state pour ne pas perdre les données
3. Quand l'utilisateur clique, on met à jour session_state et on rerun()


webhook_server.py
-----------------
Serveur Flask qui reçoit les webhooks.

Concepts clés:
- @app.route() : Définit une URL à écouter
- request.get_json() : Reçoit les données JSON
- requests.post() : Envoie des requêtes HTTP

Endpoints:
- POST /receive_field : Reçoit un champ de la part de l'autre app
- POST /send_response : Envoie la réponse de l'utilisateur


test_send_field.py
------------------
Script pour tester sans l'autre application.
Simule l'envoi de champs.
"""


# ============================================================================
# 3. COMMENT AJOUTER UN NOUVEAU TYPE DE CHAMP
# ============================================================================

"""
Exemple: Ajouter un champ "checkbox" (case à cocher)

Étape 1: Dans app.py, dans la fonction display_field(), ajouter:

    elif field_type == "checkbox":
        user_input = st.checkbox(
            field.get("text", "Confirmez-vous ?"),
            key="checkbox_input"
        )
        if st.button("✓ Valider", use_container_width=True):
            send_response(str(user_input))  # True ou False


Étape 2: Tester avec test_send_field.py en ajoutant:

    def send_checkbox_test():
        field_data = {
            "field": {
                "type": "checkbox",
                "text": "Acceptez-vous ?",
            },
            "response_url": RESPONSE_URL
        }
        response = requests.post(WEBHOOK_URL, json=field_data)
        print(response.json())
"""


# ============================================================================
# 4. PERSONNALISER L'INTERFACE (CSS/Styling)
# ============================================================================

"""
Streamlit ne supporte pas HTML/CSS classique, mais voici comment le faire:

Option 1: Utiliser st.markdown() pour du texte formaté
---------
st.markdown("# Grand titre")
st.markdown("**Texte en gras**")
st.markdown(":red[Texte rouge]")
st.markdown(":blue[Texte bleu]")

Option 2: Changer le thème Streamlit
--------
Créer un fichier ~/.streamlit/config.toml :

[theme]
primaryColor = "#FF0000"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F0F0"
textColor = "#000000"
font = "sans serif"

Option 3: Utiliser st.columns() pour la mise en page
----
col1, col2 = st.columns(2)
with col1:
    st.write("Colonne 1")
with col2:
    st.write("Colonne 2")
"""


# ============================================================================
# 5. ERREURS COURANTES ET SOLUTIONS
# ============================================================================

"""
Erreur: "AttributeError: 'NoneType' object has no attribute 'get'"
-----------
Cause: current_field est None et on essaie d'appeler .get()
Solution: Toujours vérifier que current_field n'est pas None avant utilisation

    if st.session_state.current_field:
        field = st.session_state.current_field
        # Utiliser field...


Erreur: "ConnectionRefusedError" ou "requests.exceptions.ConnectionError"
----------
Cause: Webhook server n'est pas lancé ou URL incorrecte
Solution: 
    1. Vérifiez que webhook_server.py tourne: python webhook_server.py
    2. Vérifiez les URLs (localhost:8502, 8501, etc.)
    3. Vérifiez les ports dans webhook_server.py


Erreur: Le champ ne s'affiche pas
-----------
Cause: current_field.json n'existe pas ou est mal formaté
Solution:
    1. Regardez les logs du serveur webhook
    2. Vérifiez le format du JSON envoyé
    3. Relancez Streamlit: Ctrl+C et streamlit run app.py


Erreur: "Streamlit very slow" ou "100% CPU"
-----------
Cause: Boucle de rerun infinie ou code dans le main qui execute à chaque reload
Solution:
    1. Utilisez des fonctions (pas de code direct dans main())
    2. Évitez les rerun() inutiles
    3. Utilisez @st.cache_data pour les opérations lentes
"""


# ============================================================================
# 6. PASSER À LA PRODUCTION
# ============================================================================

"""
Pour deployer cette app en ligne:

Option 1: Streamlit Cloud (gratuit pour les repos publics)
---------
1. Push le code sur GitHub
2. Allez sur https://streamlit.io/cloud
3. Connectez votre repo
4. Sélectionnez app.py comme app principale
5. C'est déployé!

Attention: Le webhook_server.py doit être sur le même serveur.

Option 2: Docker
---------
Créer un Dockerfile:

FROM python:3.9
WORKDIR /app
COPY requirements.txt requirements-webhook.txt ./
RUN pip install -r requirements.txt -r requirements-webhook.txt
COPY . .
CMD ["sh", "-c", "python webhook_server.py & streamlit run app.py"]

Puis:
docker build -t form-app .
docker run -p 8501:8501 -p 8502:8502 form-app
"""


# ============================================================================
# 7. VARIABLES D'ENVIRONNEMENT
# ============================================================================

"""
Pour éviter de hardcoder les URLs et ports, utilisez des .env:

.env:
-----
STREAMLIT_PORT=8501
WEBHOOK_PORT=8502
OTHER_APP_URL=http://localhost:5000
RESPONSE_ENDPOINT=/webhook/response

app.py:
-------
from dotenv import load_dotenv
import os

load_dotenv()
WEBHOOK_PORT = os.getenv("WEBHOOK_PORT", 8502)
OTHER_APP_URL = os.getenv("OTHER_APP_URL", "http://localhost:5000")
"""


# ============================================================================
# 8. STRUCTURE DU PROJET (SI VOUS GRANDISSEZ)
# ============================================================================

"""
Quand le projet devient plus gros:

project/
├── app.py                    # App Streamlit principale
├── webhook_server.py         # Serveur webhook Flask
├── test_send_field.py        # Tests
├── requirements.txt
├── requirements-webhook.txt
├── .env                      # Variables d'environnement
├── .env.example              # Copie sans secrets
└── src/                      # Code réutilisable
    ├── utils.py              # Fonctions utilitaires
    ├── field_handler.py      # Logique pour afficher les champs
    ├── webhook_handler.py    # Logique pour les webhooks
    └── models.py             # Structures de données (dataclasses)

Exemple models.py:
------------------
from dataclasses import dataclass
from typing import Optional

@dataclass
class Field:
    type: str
    text: str
    placeholder: Optional[str] = None

@dataclass
class WebhookPayload:
    field: Field
    response_url: str
"""


# ============================================================================
# 9. RESSOURCES
# ============================================================================

"""
Documentation:
- Streamlit: https://docs.streamlit.io/
- Flask: https://flask.palletsprojects.com/
- Requests: https://docs.python-requests.org/
- Webhooks: https://en.wikipedia.org/wiki/Webhook

Tutoriels vidéo:
- Streamlit basics: https://www.youtube.com/results?search_query=streamlit+tutorial
- Flask webhooks: https://www.youtube.com/results?search_query=flask+webhook+tutorial

Communautés:
- Streamlit Forum: https://discuss.streamlit.io/
- Stack Overflow: https://stackoverflow.com/questions/tagged/streamlit
"""
