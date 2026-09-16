"""
Script de test INTERACTIF pour envoyer des champs un par un.

Usage:
    python test_send_field.py
    
Vous verrez des prompts pour décider quand envoyer le champ suivant.
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
        print(f"\n📨 Envoi du champ: {field_data['type']}")
        print(f"   Question: {field_data['text']}")
        
        response = requests.post(
            WEBHOOK_URL,
            json=payload,
            timeout=5
        )
        
        if response.status_code == 200:
            print(f"✅ Champ envoyé avec succès!")
            print(f"   Allez regarder Streamlit à http://localhost:8501")
        else:
            print(f"❌ Erreur: Status {response.status_code}")
            print(f"   Réponse: {response.text}")
        
    except Exception as e:
        print(f"❌ Erreur de connexion: {str(e)}")
        print(f"   Vérifiez que le serveur webhook tourne: python webhook_server.py")


def wait_for_response(timeout=60):
    """Attend une réponse avec timeout."""
    print(f"\n⏳ En attente de réponse...")
    print(f"   Allez sur http://localhost:8501 et remplissez le formulaire")
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
                    response = data.get("response")
                    print(f"✅ Réponse reçue: '{response}'")
                    return True
            except:
                pass
        
        time.sleep(0.5)
    
    print(f"❌ Timeout - pas de réponse reçue")
    return False


def main():
    print("\n" + "="*60)
    print("🧪 TEST INTERACTIF - Envoi de champs")
    print("="*60)
    print("\nCe script vous permet de tester Streamlit en envoyant")
    print("des champs un par un via le webhook.")
    print("\n⚠️  Assurez-vous que les 2 services tournent:")
    print("   - Streamlit: streamlit run app.py")
    print("   - Webhook Server: python webhook_server.py")
    print("="*60)
    
    # Liste de champs de test
    test_fields = [
        {
            "type": "text",
            "text": "Quel est votre prénom ?",
            "placeholder": "Entrez votre prénom"
        },
        {
            "type": "text",
            "text": "Quel est votre nom de famille ?",
            "placeholder": "Entrez votre nom"
        },
        {
            "type": "date",
            "text": "Quelle est votre date de naissance ?",
            "placeholder": "JJ/MM/AAAA"
        },
        {
            "type": "text",
            "text": "Quelle est votre ville ?",
            "placeholder": "Entrez votre ville"
        },
    ]
    
    # Boucle de test
    for i, field in enumerate(test_fields, 1):
        print(f"\n\n📋 CHAMP {i}/{len(test_fields)}")
        print(f"{'='*60}")
        print(f"Type: {field['type']}")
        print(f"Texte: {field['text']}")
        
        # Demander à l'utilisateur s'il veut envoyer ce champ
        while True:
            user_input = input("\n▶️  Appuyez sur Enter pour ENVOYER ce champ (ou 'q' pour quitter): ").strip().lower()
            
            if user_input == 'q':
                print("\n✋ Test arrêté.")
                return
            elif user_input == '':
                # Envoyer le champ
                send_field(field)
                
                # Attendre la réponse
                if wait_for_response():
                    break
                else:
                    print("\n   Voulez-vous réessayer ce champ ? (appuyez sur Enter ou 'q')")
                    continue
            else:
                print("❌ Entrée invalide. Appuyez sur Enter ou tapez 'q'")
    
    print("\n" + "="*60)
    print("✅ Test terminé!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()


