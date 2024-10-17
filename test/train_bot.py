import requests
import json

API_URL = "http://127.0.0.1:5000"

if __name__ == "__main__":
    # Paramètres d'entraînement
    games = 5000  # Nombre de parties pour l'entraînement
    learning_rate = 0.005  # Taux d'apprentissage

    print("Début de l'entraînement du bot...")
    response = requests.post(
        f"{API_URL}/bot/train",
        headers={"Content-Type": "application/json"},
        data=json.dumps({"games": games, "learning_rate": learning_rate}),
    )

    if response.status_code == 200:
        print("Bot entraîné avec succès !")
    else:
        print(f"Erreur : {response.json().get('message', 'Entraînement échoué.')}")
