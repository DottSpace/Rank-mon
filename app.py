from flask import Flask, request, jsonify, render_template
import json
import os

app = Flask(__name__)

CLASSIFICA_PATH = "data/classifica.json"

# Assicurati che la cartella 'data' esista
os.makedirs("data", exist_ok=True)

# Assicurati che il file classifica.json esista
if not os.path.exists(CLASSIFICA_PATH):
    with open(CLASSIFICA_PATH, "w") as f:
        json.dump([], f)

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

    with open(CLASSIFICA_PATH, "r+") as f:
        classifica = json.load(f)

        # Cerca se esiste già un record con lo stesso ID, aggiorna o aggiungi
        found = False
        for i, entry_in_list in enumerate(classifica):
            if entry_in_list["id"] == client_id:
                classifica[i] = entry
                found = True
                break
        if not found:
            classifica.append(entry)

        f.seek(0)
        f.truncate()
        json.dump(classifica, f, indent=4)

    return jsonify({"message": "Dati caricati!", "id": client_id}), 200

@app.route('/classifica', methods=['GET'])
def show_classifica():
    with open(CLASSIFICA_PATH) as f:
        classifica = json.load(f)
    
    # Aggiungiamo un punteggio basato su num_pokemon e somma livelli
    for entry in classifica:
        total_level = sum(p["level"] for p in entry["pokemon"])
        entry["score"] = entry["num_pokemon"] * 1000 + total_level  # Peso maggiore al numero di pokemon
    
    # Ordiniamo per score decrescente
    classifica.sort(key=lambda x: x["score"], reverse=True)
    
    return render_template("leaderboard.html", classifica=classifica)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
