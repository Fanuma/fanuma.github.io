from flask import Flask, render_template, request, redirect, url_for
import json
import os
from datetime import datetime
import requests

app = Flask(__name__)

def get_data_file(steam_id):
    return f"data_{steam_id}.json"

def load_data(steam_id):
    default = {"mmr_history": [], "matches": [], "initial_mmr": None}
    file_path = get_data_file(steam_id)
    if not os.path.exists(file_path):
        return default
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            for key in default:
                if key not in data:
                    data[key] = default[key]
            return data
    except (json.JSONDecodeError, KeyError):
        return default

def save_data(steam_id, data):
    with open(get_data_file(steam_id), 'w') as f:
        json.dump(data, f, indent=2)

def get_player_info(steam_id):
    account_id = str(int(steam_id) - 76561197960265728)
    profile_url = f"https://api.opendota.com/api/players/{account_id}"
    try:
        response = requests.get(profile_url)
        if response.status_code == 200:
            profile_data = response.json()
            return {
                "nickname": profile_data.get("profile", {}).get("personaname", "Неизвестно"),
                "avatar": profile_data.get("profile", {}).get("avatarfull", ""),
                "rank_tier": profile_data.get("rank_tier", 0)
            }
    except Exception:
        pass
    return {"nickname": "Неизвестно", "avatar": "", "rank_tier": 0}

@app.route("/", methods=["GET", "POST"])
def index():
    steam_id = request.args.get("steam_id", "76561198391350896")
    data = load_data(steam_id)

    if request.method == "POST":
        new_mmr = int(request.form["mmr"])
        last_mmr = data["mmr_history"][-1]["value"] if data["mmr_history"] else None
        diff = new_mmr - last_mmr if last_mmr is not None else 0
        data["mmr_history"].append({
            "value": new_mmr,
            "change": diff,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        save_data(steam_id, data)
        return redirect(url_for('index', steam_id=steam_id))

    player_info = get_player_info(steam_id)
    rank = player_info["rank_tier"] or 0
    rank_medal = rank // 10
    rank_star = rank % 10

    return render_template("index.html", data=data, steam_id=steam_id,
                           player_info=player_info, rank_medal=rank_medal, rank_star=rank_star)

@app.route("/update_matches")
def update_matches():
    steam_id = request.args.get("steam_id", "76561198391350896")
    data = load_data(steam_id)
    account_id = str(int(steam_id) - 76561197960265728)

    matches_url = f"https://api.opendota.com/api/players/{account_id}/recentMatches"
    heroes_url = "https://api.opendota.com/api/heroes"

    matches = requests.get(matches_url).json()
    heroes = {hero['id']: hero['localized_name'] for hero in requests.get(heroes_url).json()}

    match_list = []
    for match in matches[:15]:
        k = match.get('kills', 0)
        d = match.get('deaths', 1)
        a = match.get('assists', 0)
        kda = f"{k}/{d}/{a}"
        win = (match['player_slot'] < 128 and match['radiant_win']) or (match['player_slot'] >= 128 and not match['radiant_win'])
        duration = f"{match['duration'] // 60}:{match['duration'] % 60:02}"
        match_list.append({
            "hero": heroes.get(match['hero_id'], 'Unknown'),
            "win": "Победа" if win else "Поражение",
            "duration": duration,
            "kda": kda
        })

    data["matches"] = match_list
    save_data(steam_id, data)
    return redirect(url_for('index', steam_id=steam_id))

@app.route("/clear")
def clear():
    steam_id = request.args.get("steam_id", "76561198391350896")
    os.remove(get_data_file(steam_id))
    return redirect(url_for('index', steam_id=steam_id))

if __name__ == "__main__":
    app.run(debug=True)
