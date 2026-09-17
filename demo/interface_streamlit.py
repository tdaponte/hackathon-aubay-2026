"""
App Streamlit pour afficher des champs de formulaire un à un.
Interface modernisée avec assistant conversationnel.

Communication avec le back-end (form_backend.py) via deux fichiers JSON,
sans webhook :
  - current_field.json    : lu ici, écrit par le back-end (la question)
  - current_response.json : écrit ici, lu par le back-end (la réponse)
"""

import streamlit as st
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

CURRENT_FIELD_FILE = "current_field.json"
CURRENT_RESPONSE_FILE = "current_response.json"

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
    
    .paused-overlay {
       opacity: 0.6;
       filter: grayscale(100%) brightness(0.9);
       pointer-events: none;
    }

</style>
""", unsafe_allow_html=True)

# ============================================================================
# État de l'application
# ============================================================================

if "current_field" not in st.session_state:
    st.session_state.current_field = None

if "field_version" not in st.session_state:
    st.session_state.field_version = 0

if "is_paused" not in st.session_state:
    st.session_state.is_paused = False


# ============================================================================
# Fonctions utilitaires
# ============================================================================

def load_field_from_file():
    """
    Relit le fichier current_field.json pour voir s'il y a un nouveau champ.
    Utilise un versioning pour détecter les changements.
    """
    if not os.path.exists(CURRENT_FIELD_FILE):
        return False

    try:
        with open(CURRENT_FIELD_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            field = data.get("field")
            version = data.get("version", 0)

            # Si la version est différente, c'est un nouveau champ
            if version > st.session_state.field_version:
                st.session_state.current_field = field
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
            <h1>Démo hackathon 2026</h1>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        # Boutons pause et question
        button_col1, button_col2 = st.columns(2)
        
        with button_col1:
            pause_icon = "▶️" if st.session_state.is_paused else "⏸️"
            if st.button(pause_icon, key="pause_btn", help="Pause/Reprendre"):
                st.session_state.is_paused = not st.session_state.is_paused
                st.rerun()
        
        with button_col2:
            if st.button("❓", key="question_btn", help="Aide"):
                pass


# ============================================================================
# Interface - Conversation
# ============================================================================

def render_conversation(field: Dict[str, Any], is_paused: bool = False) -> None:
    """Affiche la conversation avec l'assistant."""
    
    # Question
    request = field.get("request", "")
    optional = field.get("optional", False)
    
    # Exemple
    example = field.get("example", "")
    
    # Construire le contenu de la bulle
    bubble_content = ""
    if field.get("type") == "proposal":
        bubble_content += '<div class="message-question">Le texte est trop long. Voici une version raccourcie :</div>'
    elif request:
        bubble_content += f'<div class="message-question">{request}</div>'
        
        if example:
            bubble_content += f'<div class="message-example">Exemple : {example}</div>'
    
    # Appliquer le grisage si en pause
    paused_class = "paused-overlay" if is_paused else ""
    
    # Afficher l'ensemble en une seule bulle
    st.markdown(f"""
    <div class="conversation-container {paused_class}">
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
    
    render_conversation(field, st.session_state.is_paused)
    
    # Appliquer le grisage si en pause
    paused_class = "paused-overlay" if st.session_state.is_paused else ""
    
    st.markdown(f'<div class="input-section {paused_class}">', unsafe_allow_html=True)
    
    field_type = field.get("type", "text")
    
    # Désactiver les interactions si en pause
    is_disabled = st.session_state.is_paused
    
    if field_type == "proposal":
        proposal_default = field.get("request", "")
        user_input = st.text_area(
            label="",
            key=f"proposal_input_{st.session_state.field_version}",
            label_visibility="collapsed",
            value=proposal_default,
            disabled=is_disabled,
            height=180
        )
        if st.button("➤ Envoyer", key=f"send_btn_{st.session_state.field_version}", use_container_width=True, disabled=is_disabled):
            if user_input:
                send_response(user_input)
            else:
                st.warning("Veuillez entrer une réponse")
        return

    if field_type == "text":
        # st.form permet d'envoyer avec la touche Entrée : Streamlit
        # déclenche le form_submit_button dès qu'on valide un text_input
        # situé dans le même formulaire.
        with st.form(key=f"form_{st.session_state.field_version}", clear_on_submit=False):
            col1, col2 = st.columns([5, 1])
            with col1:
                user_input = st.text_input(
                    label="",
                    key=f"text_input_{st.session_state.field_version}",
                    label_visibility="collapsed",
                    disabled=is_disabled
                )
            with col2:
                submitted = st.form_submit_button("➤", use_container_width=True, disabled=is_disabled)

        if submitted:
            if user_input:
                send_response(user_input)
            else:
                st.warning("Veuillez entrer une réponse")

    elif field_type == "textarea":
        # Dans un text_area, Entrée insère un saut de ligne : l'envoi se
        # fait via Ctrl+Entrée (pour valider le champ) puis le bouton,
        # ou juste en cliquant le bouton.
        with st.form(key=f"form_{st.session_state.field_version}"):
            user_input = st.text_area(
                label="",
                key=f"textarea_input_{st.session_state.field_version}",
                label_visibility="collapsed",
                disabled=is_disabled
            )
            submitted = st.form_submit_button("➤ Envoyer", use_container_width=True, disabled=is_disabled)

        if submitted:
            if user_input:
                send_response(user_input)
            else:
                st.warning("Veuillez entrer une réponse")
    
    elif field_type in ("checkbox", "checkbow"):
        with st.form(key=f"form_{st.session_state.field_version}"):
            user_input = st.checkbox(
                field.get("request", "Confirmez-vous ?"),
                key=f"checkbox_input_{st.session_state.field_version}",
                disabled=is_disabled
            )
            submitted = st.form_submit_button("➤ Envoyer", use_container_width=True, disabled=is_disabled)

        if submitted:
            send_response(str(user_input))
    
    elif field_type in ("dropdown", "select"):
        values = field.get("values", [])
        selected_key = f"select_value_{st.session_state.field_version}"

        st.session_state.setdefault(selected_key, "")

        if values:
            chips_per_row = 3
            for i in range(0, len(values), chips_per_row):
                row_values = values[i:i + chips_per_row]
                cols = st.columns(len(row_values))
                for col, value in zip(cols, row_values):
                    with col:
                        is_selected = st.session_state.get(selected_key, "") == value
                        label = f"✓ {value}" if is_selected else value
                        if st.button(
                            label,
                            key=f"chip_{st.session_state.field_version}_{value}",
                            use_container_width=True,
                            disabled=is_disabled,
                        ):
                            st.session_state[selected_key] = "" if is_selected else value
                            st.rerun()

        if st.button("➤ Envoyer", key=f"send_btn_{st.session_state.field_version}", use_container_width=True, disabled=is_disabled):
            selected_value = st.session_state.get(selected_key, "")
            if selected_value:
                send_response(selected_value)
            else:
                st.warning("Choisis une valeur")
    
    else:
        st.error(f"Type de champ non supporté: {field_type}")
    
    st.markdown('</div>', unsafe_allow_html=True)


# ============================================================================
# Envoyer la réponse
# ============================================================================

def send_response(response: Any) -> None:
    """
    Envoie la réponse de l'utilisateur au back-end en l'écrivant dans
    current_response.json, avec le numéro de version du champ concerné.
    Le back-end (bridge.ask_user_via_streamlit) sonde ce fichier et
    reprend dès qu'il voit sa version.
    """
    try:
        print(f"\n📤 Écriture de la réponse: {response}")

        with open(CURRENT_RESPONSE_FILE, "w", encoding="utf-8") as f:
            json.dump(
                {"response": response, "version": st.session_state.field_version},
                f,
                ensure_ascii=False,
            )

        st.success("✓ Réponse envoyée !")
        print("✅ Réponse écrite dans current_response.json")

        field_version_key = f"select_value_{st.session_state.field_version}"
        if field_version_key in st.session_state:
            del st.session_state[field_version_key]

        for key in list(st.session_state.keys()):
            if key.startswith(f"chip_{st.session_state.field_version}_"):
                del st.session_state[key]

        st.session_state.current_field = None

        time.sleep(1)
        st.rerun()

    except Exception as e:
        st.error(f"Erreur lors de l'écriture de la réponse: {str(e)}")


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
        # Quand il n'y a rien à afficher, on garde seulement le robot avec son cadre vide.
        st.markdown("""
        <div class="conversation-container">
            <div class="assistant-message">
                <div class="assistant-icon">🤖</div>
                <div class="message-content">
                    <div class="message-bubble" style="visibility: hidden; min-height: 0; padding: 0; margin: 0; background: transparent; box-shadow: none; border: none;">
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Auto-refresh
    time.sleep(0.5)
    st.rerun()


if __name__ == "__main__":
    main()
