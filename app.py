from flask import Flask, request, jsonify, render_template
import requests

app = Flask(__name__)

API_KEY = '$2a$10$hazJKeTX19uYe/C8hmrEVeJSfbBh94NdWVshdehPNFRSrhWxQS4wq'
BIN_ID = '6874d2216063391d31ad4b68'

HEADERS = {
    'Content-Type': 'application/json',
    'X-Master-Key': API_KEY
}

def get_classifica():
    url = f'https://api.jsonbin.io/v3/b/{BIN_ID}/latest'
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        data = response.json()
        # La struttura di jsonbin ha i dati in data['record']
        return data.get('record', [])
    else:
        return []

def save_classifica(classifica):
    url = f'https://api.jsonbin.io/v3/b/{BIN_ID}'
    response = requests.put(url, headers=HEADERS, json=classifica)
    return response.status_code == 200

@app.route('/upload', methods=['POST'])
def upload_data():
    data = request.get_json()
    client_id = data.get("id")
    if not client_id:
        return jsonify({"error": "ID mancante"}), 400

    entry = {
        "id": client_id,
        "trainer_name": data["trainer"]["name"],
        "num_pokemon": data["num_pokemon"],
        "play_time": data["play_time"],
        "pokemon": [
            {
                "name": p["name"],
                "level": p["level"]
            } for p in data["pokemon"]
        ]
    }

    classifica = get_classifica()

    found = False
    for i, entry_in_list in enumerate(classifica):
        if entry_in_list.get("id") == client_id:
            classifica[i] = entry
            found = True
            break
    if not found:
        classifica.append(entry)

    success = save_classifica(classifica)
    if success:
        return jsonify({"message": "Dati caricati!", "id": client_id}), 200
    else:
        return jsonify({"error": "Errore nel salvataggio"}), 500

@app.route('/classifica', methods=['GET'])
def show_classifica():
    classifica = get_classifica()

    # Calcola punteggio
    for entry in classifica:
        total_level = sum(p.get("level", 0) for p in entry.get("pokemon", []))
        entry["score"] = entry.get("num_pokemon", 0) * 1000 + total_level

    classifica.sort(key=lambda x: x["score"], reverse=True)

    return render_template("leaderboard.html", classifica=classifica)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
