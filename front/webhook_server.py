"""
Serveur webhook Flask pour recevoir les champs du formulaire.
Ce serveur communique avec l'app Streamlit.

Instructions:
1. Démarrer ce serveur: python webhook_server.py
2. Dans un autre terminal: streamlit run app.py
3. Dans un troisième terminal: python test_send_field.py (pour tester)
"""

from flask import Flask, request, jsonify
import requests
import json
import os

app = Flask(__name__)

# Configuration
STREAMLIT_URL = "http://localhost:8501"
STREAMLIT_WEBHOOK_PORT = 8502

# Compteur de version pour les champs
def get_next_version():
    """Récupère et incrémente la version du champ."""
    version_file = "field_version.txt"
    try:
        if os.path.exists(version_file):
            with open(version_file, "r") as f:
                version = int(f.read().strip())
        else:
            version = 0
        
        # Incrémenter
        new_version = version + 1
        
        # Sauvegarder
        with open(version_file, "w") as f:
            f.write(str(new_version))
        
        return new_version
    except:
        return 1


# ============================================================================
# Endpoint pour recevoir les webhooks
# ============================================================================

@app.route('/receive_field', methods=['POST'])
def receive_field():
    """
    Reçoit un champ depuis l'autre application.
    
    Corps attendu:
    {
        "field": {
            "type": "text",
            "request": "La question",
            "example": "L'exemple",
            "optional": false,
            "values": []
        },
        "response_url": "http://autre-app:PORT/webhook/response"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "Pas de JSON reçu"}), 400
        
        field = data.get("field")
        response_url = data.get("response_url")
        
        if not field:
            return jsonify({"error": "Le champ 'field' est requis"}), 400
        
        # Valider le champ
        if "type" not in field or "request" not in field:
            return jsonify({"error": "Le champ doit avoir 'type' et 'request'"}), 400

        # Le type "proposal" reste un vrai champ envoyable par le formulaire.
        if not response_url:
            return jsonify({"error": "Le champ 'response_url' est requis"}), 400
        
        # Obtenir la version du champ
        version = get_next_version()
        
        print(f"\n✅ Champ reçu (v{version}): {field['type']}")
        print(f"   Question: {field['request']}")
        print(f"   URL réponse: {response_url}")
        
        # Sauvegarder le champ avec sa version
        with open("current_field.json", "w") as f:
            json.dump({
                "field": field,
                "response_url": response_url,
                "version": version
            }, f)
        
        return jsonify({
            "status": "success",
            "message": "Champ reçu et affiché",
            "version": version
        }), 200
    
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        return jsonify({"error": str(e)}), 500


# ============================================================================
# Endpoint pour recevoir les réponses de Streamlit
# ============================================================================

@app.route('/send_response', methods=['POST'])
def send_response():
    """
    Reçoit la réponse de Streamlit et l'envoie à l'autre application.
    """
    try:
        data = request.get_json()
        response_value = data.get("response")
        
        # Charger l'URL de réponse depuis le fichier
        with open("current_field.json", "r") as f:
            stored_data = json.load(f)
            response_url = stored_data.get("response_url")
        
        if not response_url:
            return jsonify({"error": "Pas d'URL de réponse"}), 400
        
        # Envoyer la réponse à l'autre application
        response_obj = requests.post(
            response_url,
            json={"response": response_value},
            timeout=5
        )
        
        print(f"\n📤 Réponse envoyée: {response_value}")
        print(f"   À: {response_url}")
        print(f"   Status: {response_obj.status_code}")
        
        return jsonify({
            "status": "success",
            "message": "Réponse envoyée"
        }), 200
    
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        return jsonify({"error": str(e)}), 500


# ============================================================================
# Endpoint mock pour tester avec test_send_field.py
# ============================================================================

@app.route('/mock_response', methods=['POST'])
def mock_response():
    """
    Endpoint mock qui reçoit les réponses du test.
    Utilisé pour simuler l'autre application.
    """
    try:
        data = request.get_json()
        response_value = data.get("response")
        
        print(f"\n✅ Réponse reçue: '{response_value}'")
        print(f"   (Ceci vient de Streamlit)")
        
        # Sauvegarder la réponse dans un fichier pour que le test puisse la lire
        with open("last_response.json", "w") as f:
            json.dump({
                "response": response_value
            }, f)
        
        return jsonify({
            "status": "success",
            "message": "Réponse reçue (mock)"
        }), 200
    
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        return jsonify({"error": str(e)}), 500


# ============================================================================
# Endpoint de santé
# ============================================================================

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    print(f"\n{'='*60}")
    print(f"🚀 Serveur webhook démarré")
    print(f"{'='*60}")
    print(f"Port: {STREAMLIT_WEBHOOK_PORT}")
    print(f"URL: http://localhost:{STREAMLIT_WEBHOOK_PORT}")
    print(f"\nEndpoints:")
    print(f"  POST /receive_field     ← Reçoit les champs")
    print(f"  POST /send_response     ← Envoie les réponses")
    print(f"  POST /mock_response     ← Mock pour les tests")
    print(f"  GET  /health            ← Santé du serveur")
    print(f"{'='*60}\n")
    
    app.run(
        host="localhost",
        port=STREAMLIT_WEBHOOK_PORT,
        debug=False
    )

