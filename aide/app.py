"""Stable context and an action-led, private conversational form interface."""
import os
import base64
from pathlib import Path
import streamlit as st

ROOT = Path(__file__).parent
from aide.connected import ConnectedJourney
from aide.agent_browser import AgentBrowser
from aide.planner import plain_words

logo_path = ROOT / "assets" / "pazapa.png"
st.set_page_config(page_title="Pazapa — Les ateliers du quartier", page_icon=str(logo_path), layout="wide")
st.markdown((ROOT / "workspace.html").read_text(encoding="utf-8"), unsafe_allow_html=True)
logo_data = base64.b64encode(logo_path.read_bytes()).decode("ascii")
st.markdown(
    '<div class="pazapa-brand">'
    f'<img src="data:image/png;base64,{logo_data}" alt="Logo Pazapa : l’autonomie à portée de clic.">'
    '<h1>Pazapa</h1></div>',
    unsafe_allow_html=True,
)
st.write("Comprendre le site. Choisir une action. Avancer à ton rythme.")
st.caption("SITE DE DÉMONSTRATION · Utilise des informations fictives.")

PUBLIC_SITE = os.environ.get("SITE_PUBLIC_URL", "http://127.0.0.1:8000")
ticket = st.query_params.get("handoff")
if ticket:
    st.query_params.clear()
    for key in list(st.session_state):
        del st.session_state[key]
    try:
        browser = AgentBrowser(os.environ.get("SITE_BASE_URL", "http://site:8000"))
        browser.join_session(ticket)
        st.session_state.journey = ConnectedJourney(browser)
        st.session_state.linked = True
    except Exception:
        st.error("La liaison a expiré ou n’a pas abouti. Rouvre l’aide depuis le site d’origine.")
    finally:
        del ticket

if not st.session_state.get("linked"):
    st.info("Commence sur le site des ateliers, puis clique sur « M’aider avec ce site ». L’aide utilisera ainsi le même compte que ton onglet du site.")
    st.link_button("Ouvrir le site des ateliers", PUBLIC_SITE + "/")
    st.stop()

j = st.session_state.journey
if not j.homepage:
    with st.spinner("L’agent lit le site pour expliquer son contenu et repérer ses actions…"):
        j.discover_home()
    if not j.homepage:
        st.error(j.error or "L’agent n’a pas pu préparer l’accueil.")
        if st.button("Relire le site"):
            st.rerun()
        st.stop()
context = j.homepage
actions = {item["purpose"]: item for item in context["actions"]}


def clear_inputs():
    for key in list(st.session_state):
        if key.startswith("input_"):
            del st.session_state[key]


def begin(target):
    st.session_state.pending_ui = ("begin", target)


def perform_begin(target):
    clear_inputs()
    try:
        with st.spinner("Je lis le site et prépare tes questions…"):
            if "journey" not in st.session_state:
                st.session_state.journey = ConnectedJourney.start(os.environ.get("SITE_BASE_URL", "http://site:8000"), target)
            else:
                st.session_state.journey.begin_action(target)
        st.session_state.view = "conversation"
        st.session_state.notice = ""
    except Exception:
        st.session_state.notice = "Je n’arrive pas à préparer cette action. Vérifie que le site et l’accès à l’IA sont disponibles, puis réessaie."


def home():
    j = st.session_state.get("journey")
    if j:
        j.approval = None
        for secret in j.secrets.values():
            j.private_values.discard(str(secret))
        j.secrets.clear()
    clear_inputs()
    st.session_state.view = "home"
    st.session_state.notice = ""


def reserve():
    j = st.session_state.get("journey")
    if not j or not j.authenticated:
        st.session_state.notice = "Connecte-toi ou crée un compte pour réserver une activité."
        st.session_state.view = "home"
    else:
        begin("reservation")


def sync(field):
    j = st.session_state.journey
    j.set_answer(field["id"], st.session_state["input_" + field["id"]])
    for candidate in j.fields.values():
        if candidate.get("depends_on") == field["id"] and not j.value(candidate):
            st.session_state.pop("input_" + candidate["id"], None)


def advance():
    st.session_state.pending_ui = ("advance", None)


def perform_advance():
    j = st.session_state.journey
    with st.spinner("Je vérifie ta réponse…"):
        j.advance()
    for field in j.fields.values():
        if (field["kind"] == "secret" or field.get("depends_on")) and not j.value(field):
            st.session_state.pop("input_" + field["id"], None)


def conversation(j):
    if not j.pending_stage:
        st.button("Retour aux actions", on_click=home)
    if j.status != "ready":
        st.warning(plain_words(j.error or "La vérification est en cours."))
        if j.receipt:
            st.info("Réservation confirmée par le site : " + j.receipt["reference"])
        if st.button("Vérifier auprès du site" if j.pending_stage else "Reprendre l’analyse"):
            with st.spinner("Je vérifie sans renvoyer le formulaire…"):
                j.verify_submission() if j.pending_stage else j.retry_analysis()
            clear_inputs()
            st.rerun()
        return
    if j.step["kind"] == "done":
        with st.chat_message("assistant"):
            if j.target == "reservation":
                st.success("Le site a confirmé ta réservation.")
                st.write("Référence : " + j.receipt["reference"])
                st.write(j.receipt["activity"])
                st.write(j.receipt["slot"])
                with st.expander("Voir la confirmation du site"):
                    st.image(j.receipt["screenshot"])
            else:
                st.success("Ton compte est créé." if j.target == "account" else "Tu es connecté à ton compte.")
                st.write("Tu peux maintenant réserver une activité. Aucune nouvelle réservation n’a encore été faite.")
        if j.target != "reservation":
            st.button("Réserver une activité", type="primary", on_click=reserve, width="stretch")
        st.link_button("Voir mon compte et mes réservations sur le site", PUBLIC_SITE + "/inscription", width="stretch")
        st.caption("Ton onglet du site utilise la même session. Tu peux aussi y retourner et actualiser la page.")
        return

    stage = j.step["stage"]
    st.subheader("Ma connexion" if j.target == "login" else stage["title"])
    with st.container(height=300, key="conversation_history", border=False):
        for field in stage["fields"]:
            index = next(i for i, step in enumerate(j.steps) if step.get("field", {}).get("id") == field["id"])
            if index > j.current:
                break
            with st.chat_message("assistant"):
                st.write(field["question"])
            if index < j.current and j.value(field):
                with st.chat_message("user"):
                    st.text("Mot de passe renseigné — valeur masquée." if field["kind"] == "secret" else j.display_value(field))

    if j.step["kind"] == "field":
        field = j.step["field"]
        key = "input_" + field["id"]
        if key not in st.session_state:
            st.session_state[key] = j.value(field) or (None if field["kind"] == "choice" else "")
        if field["kind"] == "choice":
            labels = {o["value"]: o["label"] for o in j.options(field)}
            st.radio(field["ui_label"], list(labels), index=None, format_func=lambda v: labels[v], key=key, on_change=sync, args=(field,))
        else:
            st.text_input(field["ui_label"], type="password" if field["kind"] == "secret" else "default", key=key, on_change=sync, args=(field,), autocomplete="off")
        if field.get("instruction"):
            st.caption(field["instruction"])
        with st.expander("Explique-moi"):
            st.write(field["explanation"])
        if j.error:
            st.error(plain_words(j.error))
        back, forward = st.columns([1, 2])
        if j.current > 0 or j.editing_review is not None:
            back.button("Retour", on_click=j.back, width="stretch")
        forward.button("Enregistrer ma modification" if j.editing_review is not None else "Envoyer ma réponse", on_click=advance, type="primary", width="stretch")
    else:
        st.subheader(stage["review_title"])
        for field in stage["fields"]:
            value, edit = st.columns([3, 1])
            value.write(field["ui_label"])
            value.text(j.display_value(field))
            edit.button("Modifier", key="edit_" + field["id"], help="Modifier : " + field["ui_label"], on_click=j.edit, args=(field["id"],))
        st.write(stage["commitment"])
        if j.error:
            st.error(plain_words(j.error))
        st.button("Retour", on_click=j.back)
        st.button(stage["submit_label"], type="primary", on_click=advance, width="stretch")


with st.container(key="workspace"):
    left, right = st.columns([1, 1.25], gap="large")
    with left, st.container(key="context_panel", border=True):
        st.caption("CONTEXTE")
        st.header(context["title"])
        for paragraph in context["paragraphs"]:
            st.write(paragraph)
        st.divider()
        for fact in context["facts"]:
            st.write(fact)
    with right, st.container(key="action_panel"):
        st.header("Actions")
        pending = st.session_state.pop("pending_ui", None)
        if pending:
            # Render waiting feedback here, never above the immutable context.
            if pending[0] == "begin":
                perform_begin(pending[1])
            else:
                perform_advance()
            st.rerun()
        j = st.session_state.get("journey")
        view = st.session_state.get("view", "home")
        if st.session_state.get("notice"):
            st.info(st.session_state.notice)
        if view == "home":
            st.write("Que veux-tu faire ?")
            if j and j.authenticated:
                st.success("Tu es connecté à ton compte.")
            if "account" in actions or "login" in actions:
                label = " / ".join(actions[key]["label"] for key in ("account", "login") if key in actions)
                st.button(label, key="account_action", width="stretch", on_click=lambda: st.session_state.update(view="account", notice=""))
            if "reservation" in actions:
                st.button(actions["reservation"]["label"], key="reservation_action", width="stretch", on_click=reserve)
            st.caption("Tu choisis. Je t’aide une question à la fois.")
        elif view == "account":
            st.button("Retour aux actions", on_click=home)
            with st.chat_message("assistant"):
                st.write("As-tu déjà un compte sur ce site ?")
            if j and j.authenticated:
                st.success("Tu es déjà connecté. Tu peux réserver une activité.")
                st.button("Réserver une activité", on_click=reserve, type="primary")
            else:
                if "account" in actions:
                    st.button(actions["account"]["label"], key="choose_account", on_click=begin, args=("account",), width="stretch", type="primary")
                if "login" in actions:
                    st.button(actions["login"]["label"], key="choose_login", on_click=begin, args=("login",), width="stretch")
        elif j:
            conversation(j)

st.caption("Tu peux relire et modifier tes réponses. Rien n’est envoyé sans ta confirmation.")
if st.session_state.get("journey"):
    j = st.session_state.journey
    with st.expander("Vue technique — appels de l’agent"):
        st.caption("Appels réels. Les réponses personnelles et les mots de passe restent hors des messages du modèle.")
        st.write(f"{len(j.metrics)} appels au modèle · {sum(m['seconds'] for m in j.metrics):.1f} s d’attente IA cumulée")
        if j.trace:
            st.dataframe(j.trace, hide_index=True, width="stretch")
