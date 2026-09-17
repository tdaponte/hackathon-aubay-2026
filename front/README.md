# 📋 Formulaire Simplifié - App Streamlit

Application Streamlit pour afficher des champs de formulaire de manière simple et progressive, conçue pour être accessible.

## 🎯 Objectif

- Afficher **un champ de formulaire à la fois**
- Communiquer avec une autre application via **webhooks HTTP**
- Recevoir les données des champs en JSON
- Renvoyer les réponses de l'utilisateur

## 🏗️ Architecture

```
Autre App (port 5000)
        ↓ POST /receive_field (champ + URL réponse)
    Webhook Server (port 8502) ← → Streamlit App (port 8501)
        ↓
Affiche le champ à l'utilisateur
        ↓
Utilisateur remplit
        ↓
POST → Autre App (avec la réponse)
```

## 🚀 Démarrage rapide

### Prérequis
- Python 3.8+
- pip (gestionnaire de paquets Python)

### Installation

1. **Clonez le repo** (ou utilisez le dossier existant)

2. **Installez les dépendances**

```bash
# Installez Streamlit et requests
pip install -r requirements.txt

# Si vous voulez utiliser le serveur webhook
pip install -r requirements-webhook.txt
```

### Lancement

Ouvrez **2-3 terminaux** différents :

#### Terminal 1: App Streamlit
```bash
streamlit run app.py
```
L'app s'ouvre sur `http://localhost:8501`

#### Terminal 2: Serveur Webhook (optionnel mais recommandé)
```bash
python webhook_server.py
```
Le serveur écoute sur `http://localhost:8502`

#### Terminal 3: Tests (optionnel)
```bash
python test_send_field.py
```

## 📨 Comment utiliser

### Option 1: Avec le serveur webhook (recommandé)

L'autre app envoie un POST à `http://localhost:8502/receive_field`:

```bash
curl -X POST http://localhost:8502/receive_field \
  -H "Content-Type: application/json" \
  -d '{
    "field": {
      "type": "text",
      "text": "Quel est votre nom ?",
      "placeholder": "Entrez votre réponse"
    },
    "response_url": "http://autre-app:5000/webhook/response"
  }'
```

### Option 2: Sans serveur webhook

Envoyez directement à Streamlit via une URL personnalisée. C'est plus compliqué, on verra ça plus tard si nécessaire.

## 📝 Format du JSON de champ

```json
{
  "field": {
    "type": "text",              // ou "date", "number", etc.
    "text": "Votre question ?",   // Le texte à afficher
    "placeholder": "..."         // Optionnel: texte gris d'aide
  },
  "response_url": "http://autre-app:5000/webhook/response"
}
```

## 📤 Format de la réponse

L'app envoie la réponse à `response_url`:

```json
{
  "response": "La réponse de l'utilisateur"
}
```

## 🧪 Tester sans l'autre application

Lancez `test_send_field.py` - il envoie des champs de test automatiquement.

## 📚 Concepts Python/Streamlit expliqués

### Session State
```python
if "current_field" not in st.session_state:
    st.session_state.current_field = None
```
**Quoi**: Streamlit recharge la page à chaque clic. `session_state` mémorise les données entre les recharges.
**Pourquoi**: Sans ça, le champ disparaîtrait quand l'utilisateur clique sur le bouton.

### Rerun (recharge)
```python
st.rerun()
```
Force Streamlit à recharger la page. Utile après une action importante.

### Widgets (champs)
```python
st.text_input("Label", placeholder="Aide")  # Champ texte
st.date_input("Label")                      # Champ date
st.number_input("Label")                    # Champ nombre
```

## 🐛 Dépannage

**"Erreur de connexion"**
- Vérifiez que le serveur webhook tourne: `python webhook_server.py`
- Vérifiez les URLs (localhost:8502, localhost:8501)

**"Pas de champ affiché"**
- Vérifiez que le JSON a été bien envoyé au serveur
- Regardez les logs du serveur (`webhook_server.py`)

**Streamlit très lent**
- C'est normal au démarrage. Il compile les changements.

## 🎨 Prochaines étapes

- [ ] Ajouter d'autres types de champs (date, nombre, sélection, etc.)
- [ ] Rendre l'interface plus grande et colorée
- [ ] Ajouter des images/icônes pour l'accessibilité
- [ ] Gérer plusieurs formulaires en parallèle
- [ ] Ajouter des validations personnalisées

## 📞 Besoin d'aide ?

Consultez:
- [Docs Streamlit](https://docs.streamlit.io/)
- [Docs Flask](https://flask.palletsprojects.com/)
- [Requêtes HTTP avec requests](https://docs.python-requests.org/)