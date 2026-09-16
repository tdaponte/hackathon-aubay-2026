"""
App Streamlit simple pour afficher des champs de formulaire un à un.
Elle reçoit les champs via webhook d'une autre application.
"""

import streamlit as st
import requests
from typing import Dict, Any
import json
import time
import os

# Configuration Streamlit
st.set_page_config(
    page_title="Formulaire Simplifié",
    page_icon="📋",
    layout="centered"
)

# ============================================================================
# État de l'application (Streamlit Session State)
# ============================================================================

if "current_field" not in st.session_state:
    st.session_state.current_field = None

if "response_url" not in st.session_state:
    st.session_state.response_url = None

if "field_version" not in st.session_state:
    st.session_state.field_version = 0


# ============================================================================
# Fonction pour charger un champ depuis le fichier
# ============================================================================

def load_field_from_file():
    """
    Relit le fichier current_field.json pour voir s'il y a un nouveau champ.
    Utilise un versioning pour détecter les changements.
    Retourne True si un nouveau champ a été détecté.
    """
    if not os.path.exists("current_field.json"):
        return False
    
    try:
        with open("current_field.json", "r") as f:
            data = json.load(f)
            field = data.get("field")
            response_url = data.get("response_url")
            version = data.get("version", 0)
            
            # Si la version est différente, c'est un nouveau champ
            if version > st.session_state.field_version:
                st.session_state.current_field = field
                st.session_state.response_url = response_url
                st.session_state.field_version = version
                print(f"✅ Nouveau champ détecté (version {version})")
                return True
    
    except Exception as e:
        print(f"Erreur en relisant le fichier: {str(e)}")
    
    return False


# ============================================================================
# Fonction pour afficher le champ
# ============================================================================

def display_field(field: Dict[str, Any]) -> None:
    """
    Affiche un champ de formulaire en fonction de son type.
    
    Args:
        field: Dictionnaire avec {type, text, placeholder, ...}
    """
    st.title("Formulaire")
    
    # Afficher le texte/question du champ
    if "text" in field:
        st.markdown(f"### {field['text']}")
    
    # Afficher le champ selon son type
    field_type = field.get("type", "text")
    
    if field_type == "text" or field_type == "string":
        placeholder = field.get("placeholder", "Entrez votre réponse")
        user_input = st.text_input(
            label="Réponse",
            placeholder=placeholder,
            key=f"text_input_{st.session_state.field_version}"
        )
        
        # Bouton pour valider et envoyer la réponse
        if st.button("✓ Valider", use_container_width=True):
            if user_input:
                send_response(user_input)
            else:
                st.warning("Veuillez entrer une réponse")
    
    elif field_type == "date":
        user_input = st.date_input(
            "Sélectionnez une date",
            key=f"date_input_{st.session_state.field_version}"
        )
        if st.button("✓ Valider", use_container_width=True):
            send_response(user_input.isoformat())
    
    elif field_type == "number":
        user_input = st.number_input(
            "Entrez un nombre",
            key=f"number_input_{st.session_state.field_version}"
        )
        if st.button("✓ Valider", use_container_width=True):
            send_response(str(user_input))
    
    else:
        st.error(f"Type de champ non supporté: {field_type}")


# ============================================================================
# Fonction pour envoyer la réponse
# ============================================================================

def send_response(response: Any) -> None:
    """
    Envoie la réponse de l'utilisateur à l'application qui a envoyé le webhook.
    """
    if not st.session_state.response_url:
        st.error("Erreur: pas d'URL de réponse définie")
        return
    
    try:
        print(f"\n📤 Envoi de la réponse: {response}")
        
        # Préparer la réponse
        payload = {"response": response}
        
        # Envoyer la réponse
        response_obj = requests.post(
            st.session_state.response_url,
            json=payload,
            timeout=5
        )
        
        if response_obj.status_code == 200:
            st.success("✓ Réponse envoyée avec succès!")
            print(f"✅ Réponse envoyée au serveur")
            
            # Réinitialiser pour attendre le prochain champ
            st.session_state.current_field = None
            
            time.sleep(1)
            st.rerun()
        else:
            st.error(f"Erreur lors de l'envoi: {response_obj.status_code}")
    
    except Exception as e:
        st.error(f"Erreur de connexion: {str(e)}")


# ============================================================================
# Interface principale
# ============================================================================

def main():
    # Vérifier si un nouveau champ est arrivé
    has_new_field = load_field_from_file()
    
    # Afficher le champ ou attendre
    if st.session_state.current_field:
        display_field(st.session_state.current_field)
    else:
        # Écran d'attente
        st.title("Formulaire")
        st.info("⏳ En attente d'un champ à afficher...")
        st.write("L'autre application doit envoyer un champ via webhook")
        
        # Afficher les instructions pour les développeurs
        with st.expander("📝 Instructions pour les développeurs"):
            st.write("""
            Pour envoyer un champ, faites une requête POST à :
            
            ```
            POST http://localhost:8502/receive_field
            ```
            
            Avec le corps JSON :
            ```json
            {
                "field": {
                    "type": "text",
                    "text": "Quel est votre nom ?",
                    "placeholder": "Entrez votre prénom et nom"
                },
                "response_url": "http://localhost:8502/mock_response"
            }
            ```
            """)
    
    # Auto-refresh rapide pour détecter les changements
    # mais pas trop souvent pour ne pas surcharger Streamlit
    time.sleep(0.5)
    st.rerun()


if __name__ == "__main__":
    main()



