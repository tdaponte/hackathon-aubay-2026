"""
App Streamlit pour afficher des champs de formulaire un à un.
Interface modernisée avec assistant conversationnel.
"""

import streamlit as st
import requests
from typing import Dict, Any
import json
import time
import os
from PIL import Image

# Configuration Streamlit
st.set_page_config(
    page_title="PAZAPA - Formulaire",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Styling personnalisé
st.markdown("""
<style>
    * {
        margin: 0;
        padding: 0;
    }
    
    .main {
        max-width: 1000px;
        margin: 0 auto;
    }
    
    [data-testid="stMainBlockContainer"] {
        max-width: 1000px;
        margin: 0 auto;
    }
    
    .header-container {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 30px;
        padding: 20px;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 12px;
    }
    
    .logo-section {
        display: flex;
        align-items: center;
        gap: 20px;
    }
    
    .logo-img {
        max-width: 80px;
        height: auto;
    }
    
    .title-section {
        flex: 1;
        text-align: center;
    }
    
    .title-section h1 {
        color: #2c3e50;
        font-size: 24px;
        margin-bottom: 5px;
    }
    
    .title-section p {
        color: #7f8c8d;
        font-size: 14px;
    }
    
    .buttons-section {
        display: flex;
        gap: 10px;
    }
    
    .conversation-container {
        background: white;
        border-radius: 12px;
        padding: 30px;
        margin-bottom: 30px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        min-height: 200px;
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
    }
    
    .assistant-message {
        display: flex;
        gap: 15px;
        flex: 1;
    }
    
    .assistant-icon {
        flex-shrink: 0;
        width: 50px;
        height: 50px;
        background: linear-gradient(135deg, #a8d5ff 0%, #7fa6d1 100%);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
    }
    
    .message-content {
        flex: 1;
    }
    
    .message-bubble {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        border: none;
        padding: 20px;
        border-radius: 20px;
        box-shadow: 0 4px 16px rgba(66, 133, 244, 0.15);
        min-height: auto;
        display: flex;
        flex-direction: column;
        justify-content: center;
        position: relative;
    }
    
    .message-bubble::before {
        content: '';
        position: absolute;
        left: -10px;
        top: 20px;
        width: 0;
        height: 0;
        border-top: 10px solid transparent;
        border-bottom: 10px solid transparent;
        border-right: 10px solid #e3f2fd;
        filter: drop-shadow(-2px 2px 2px rgba(66, 133, 244, 0.15));
    }
    
    .message-question {
        color: #1a237e;
        font-size: 18px;
        font-weight: 600;
        margin-bottom: 8px;
        line-height: 1.5;
    }
    
    .message-example {
        color: #424242;
        font-size: 15px;
        font-style: normal;
        margin-top: 10px;
        padding-top: 8px;
        border-top: 1px solid rgba(0, 0, 0, 0.1);
    }
    
    .input-section {
        display: flex;
        gap: 10px;
        margin-top: 20px;
    }
    
    .input-field {
        flex: 1;
    }
    
    .send-button {
        flex-shrink: 0;
    }
    
    .optional-badge {
        display: inline-block;
        background: #fff3cd;
        color: #856404;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 12px;
        margin-left: 10px;
    }
    
    .debug-section {
        margin-top: 50px;
        padding-top: 30px;
        border-top: 2px solid #ecf0f1;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# État de l'application
# ============================================================================

if "current_field" not in st.session_state:
    st.session_state.current_field = None

if "response_url" not in st.session_state:
    st.session_state.response_url = None

if "field_version" not in st.session_state:
    st.session_state.field_version = 0


# ============================================================================
# Fonctions utilitaires
# ============================================================================

def load_field_from_file():
    """
    Relit le fichier current_field.json pour voir s'il y a un nouveau champ.
    Utilise un versioning pour détecter les changements.
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


def get_logo():
    """Charge le logo PAZAPA."""
    logo_path = "images/logo.png"
    if os.path.exists(logo_path):
        try:
            return Image.open(logo_path)
        except:
            return None
    return None


# ============================================================================
# Interface - Header
# ============================================================================

def render_header():
    """Affiche le header avec logo et boutons."""
    
    col1, col2, col3 = st.columns([1, 3, 1])
    
    with col1:
        logo = get_logo()
        if logo:
            st.image(logo, width=80)
    
    with col2:
        st.markdown("""
        <div class="title-section">
            <h1>📋 Formulaire Inscription</h1>
            <p>Bienvenue ! Remplissez ce formulaire pour continuer</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        # Boutons pause et question
        button_col1, button_col2 = st.columns(2)
        
        with button_col1:
            if st.button("⏸️", key="pause_btn", help="Pause"):
                pass
        
        with button_col2:
            if st.button("❓", key="question_btn", help="Aide"):
                pass
    
    st.divider()


# ============================================================================
# Interface - Conversation
# ============================================================================

def render_conversation(field: Dict[str, Any]) -> None:
    """Affiche la conversation avec l'assistant."""
    
    # Question
    request = field.get("request", "")
    optional = field.get("optional", False)
    
    # Exemple
    example = field.get("example", "")
    
    # Construire le contenu de la bulle
    bubble_content = ""
    if request:
        if optional:
            bubble_content += f'<div class="message-question">{request} <span class="optional-badge">Optionnel</span></div>'
        else:
            bubble_content += f'<div class="message-question">{request}</div>'
        
        if example:
            bubble_content += f'<div class="message-example">Exemple : {example}</div>'
    
    # Afficher l'ensemble en une seule bulle
    st.markdown(f"""
    <div class="conversation-container">
        <div class="assistant-message">
            <div class="assistant-icon">🤖</div>
            <div class="message-content">
                <div class="message-bubble">
                    {bubble_content}
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ============================================================================
# Interface - Champs de formulaire
# ============================================================================

def render_field(field: Dict[str, Any]) -> None:
    """Affiche le champ de formulaire selon son type."""
    
    render_conversation(field)
    
    st.markdown('<div class="input-section">', unsafe_allow_html=True)
    
    field_type = field.get("type", "text")
    
    if field_type == "text":
        col1, col2 = st.columns([5, 1])
        
        with col1:
            user_input = st.text_input(
                label="",
                key=f"text_input_{st.session_state.field_version}",
                label_visibility="collapsed"
            )
        
        with col2:
            if st.button("➤", key=f"send_btn_{st.session_state.field_version}", use_container_width=True):
                if user_input:
                    send_response(user_input)
                else:
                    st.warning("Veuillez entrer une réponse")
    
    elif field_type == "checkbox":
        user_input = st.checkbox(
            field.get("request", "Confirmez-vous ?"),
            key=f"checkbox_input_{st.session_state.field_version}"
        )
        if st.button("➤ Envoyer", key=f"send_btn_{st.session_state.field_version}", use_container_width=True):
            send_response(str(user_input))
    
    elif field_type == "dropdown":
        values = field.get("values", [])
        user_input = st.selectbox(
            label="",
            options=values,
            key=f"dropdown_input_{st.session_state.field_version}",
            label_visibility="collapsed"
        )
        if st.button("➤ Envoyer", key=f"send_btn_{st.session_state.field_version}", use_container_width=True):
            send_response(user_input)
    
    else:
        st.error(f"Type de champ non supporté: {field_type}")
    
    st.markdown('</div>', unsafe_allow_html=True)


# ============================================================================
# Envoyer la réponse
# ============================================================================

def send_response(response: Any) -> None:
    """Envoie la réponse de l'utilisateur."""
    
    if not st.session_state.response_url:
        st.error("Erreur: pas d'URL de réponse définie")
        return
    
    try:
        print(f"\n📤 Envoi de la réponse: {response}")
        
        payload = {"response": response}
        
        response_obj = requests.post(
            st.session_state.response_url,
            json=payload,
            timeout=5
        )
        
        if response_obj.status_code == 200:
            st.success("✓ Réponse envoyée !")
            print(f"✅ Réponse envoyée au serveur")
            
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
    
    # Header
    render_header()
    
    # Afficher le champ ou attendre
    if st.session_state.current_field:
        render_field(st.session_state.current_field)
    else:
        # Écran d'attente - juste afficher une bulle vide
        st.markdown("""
        <div class="conversation-container">
            <div class="assistant-message">
                <div class="assistant-icon">🤖</div>
                <div class="message-content">
                    <div class="message-bubble">
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Debug - Afficher le format du webhook en bas
    st.markdown('<div class="debug-section">', unsafe_allow_html=True)
    with st.expander("📝 Format du webhook (debug)"):
        st.code("""{
    "field": {
        "request": "Est-ce que tu peux te présenter ?",
        "type": "text",
        "values": [],
        "example": "Je m'appelle...",
        "optional": false
    },
    "response_url": "http://localhost:8502/mock_response"
}""", language="json")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Auto-refresh
    time.sleep(0.5)
    st.rerun()


if __name__ == "__main__":
    main()





