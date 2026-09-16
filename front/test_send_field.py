"""
Script de test INTERACTIF pour envoyer des champs un par un.
Vous pouvez entrer les valeurs du champ directement.

Usage:
    python test_send_field.py
    
Vous pouvez:
- Entrer une question et un exemple
- Envoyer le champ à Streamlit
- Attendre la réponse
- Envoyer un nouveau champ ou quitter
"""

import requests
import json
import os
import time

# URL du serveur webhook
WEBHOOK_URL = "http://localhost:8502/receive_field"
# URL où Streamlit enverra les réponses
RESPONSE_URL = "http://localhost:8502/mock_response"


def send_field(field_data):
    """Envoie un champ au serveur webhook."""
    
    payload = {
        "field": field_data,
        "response_url": RESPONSE_URL
    }
    
    try:
        print(f"\n📨 Envoi du champ...")
        print(f"   Question: {field_data['request']}")
        if field_data.get('example'):
            print(f"   Exemple: {field_data['example']}")
        if field_data.get('optional'):
            print(f"   Optionnel: Oui")
        
        response = requests.post(
            WEBHOOK_URL,
            json=payload,
            timeout=5
        )
        
        if response.status_code == 200:
            print(f"✅ Champ envoyé avec succès!")
            print(f"   👉 Allez regarder Streamlit à http://localhost:8501")
        else:
            print(f"❌ Erreur: Status {response.status_code}")
            print(f"   Réponse: {response.text}")
        
    except Exception as e:
        print(f"❌ Erreur de connexion: {str(e)}")
        print(f"   Vérifiez que le serveur webhook tourne: python webhook_server.py")


def wait_for_response(timeout=60):
    """Attend une réponse avec timeout."""
    print(f"\n⏳ En attente de réponse...")
    print(f"   Remplissez le formulaire sur http://localhost:8501")
    print(f"   Vous avez {timeout} secondes...\n")
    
    # Supprimer l'ancienne réponse pour détecter la nouvelle
    if os.path.exists("last_response.json"):
        os.remove("last_response.json")
    
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        # Vérifier si le fichier existe (= une nouvelle réponse)
        if os.path.exists("last_response.json"):
            try:
                with open("last_response.json", "r") as f:
                    data = json.load(f)
                    response_value = data.get("response")
                    print(f"\n✅ Réponse reçue:")
                    print(f"   {json.dumps({'response': response_value}, indent=4)}")
                    return True
            except:
                pass
        
        time.sleep(0.5)
    
    print(f"❌ Timeout - pas de réponse reçue")
    return False


def input_field():
    """Demande à l'utilisateur d'entrer un champ."""
    print("\n" + "="*60)
    print("📝 Créer un nouveau champ")
    print("="*60)
    
    # Question (obligatoire)
    while True:
        request = input("\n📌 Question à poser à l'utilisateur: ").strip()
        if request:
            break
        print("   ❌ La question est obligatoire")
    
    # Exemple (optionnel)
    example = input("📝 Exemple (optionnel, appuyez sur Enter pour passer): ").strip()
    
    # Optionnel (optionnel)
    optional_input = input("❓ Ce champ est optionnel ? (o/n, défaut: non): ").strip().lower()
    optional = optional_input == 'o'
    
    # Créer le champ
    field = {
        "type": "text",
        "request": request,
        "values": [],
        "example": example,
        "optional": optional
    }
    
    return field


def main():
    print("\n" + "="*60)
    print("🧪 TEST INTERACTIF - Créer et envoyer des champs")
    print("="*60)
    print("\nCe script vous permet de:")
    print("  • Créer des champs texte personnalisés")
    print("  • Les envoyer à Streamlit via webhook")
    print("  • Voir la réponse de l'utilisateur")
    print("\n⚠️  Assurez-vous que les services tournent:")
    print("   - Streamlit: streamlit run app.py")
    print("   - Webhook Server: python webhook_server.py")
    print("="*60)
    
    champ_count = 0
    
    while True:
        champ_count += 1
        
        # Créer un champ
        field = input_field()
        
        # Envoyer le champ
        send_field(field)
        
        # Attendre la réponse
        if not wait_for_response():
            print("\n   Pas de réponse reçue, continuons...")
        
        # Demander si on continue
        print("\n")
        continue_input = input("Voulez-vous envoyer un autre champ ? (oui/non): ").strip().lower()
        
        if continue_input not in ['oui', 'o', 'yes', 'y']:
            break
    
    print("\n" + "="*60)
    print(f"✅ Test terminé! ({champ_count} champ(s) envoyé(s))")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()


