from fastapi import FastAPI
from datetime import datetime
from statistics import mean, median
import json
import os

app = FastAPI()

# Charger les dons depuis le fichier local donations.json
def load_data():
    with open("donations.json", encoding="utf-8") as f:
        raw = json.load(f)

    data = []
    for d in raw:  # On itère directement sur la liste
        try:
            data.append({
                "donation_id": d["id"],
                "donor_name": d.get("display_name", "Anonyme"),
                "amount": float(d.get("amount", 0)),
                "message": d.get("message", ""),
                "created_at": datetime.fromisoformat(d["created_at"].replace("Z", "+00:00")),
                "streamer_name": d.get("fundraiser", {}).get("display_name", "Inconnu")
            })
        except Exception as e:
            print("Erreur sur un don :", e)

    return data

# Charger une fois pour tous les endpoints
donations = load_data()

@app.get("/")
def home():
    return {"message": "API Streamlabs Charity prête 👋"}

@app.get("/donations")
def list_donations():
    return donations

@app.get("/stats/total")
def total_amount():
    return round(sum(d["amount"] for d in donations), 2)

@app.get("/stats/mean")
def mean_amount():
    return round(mean([d["amount"] for d in donations]), 2)

@app.get("/stats/median")
def median_amount():
    return round(median([d["amount"] for d in donations]), 2)

@app.get("/stats/top_donors")
def top_donors():
    from collections import defaultdict

    totals = defaultdict(float)
    for d in donations:
        name = d["donor_name"]
        totals[name] += d["amount"]

    sorted_donors = sorted(totals.items(), key=lambda x: x[1], reverse=True)
    return [{"name": name, "amount": round(amount, 2)} for name, amount in sorted_donors[:10]]

@app.get("/stats/graph")
def donation_graph():
    from collections import defaultdict

    graph = defaultdict(float)
    for d in donations:
        date = d["created_at"].date().isoformat()
        graph[date] += d["amount"]

    return [{"date": date, "amount": round(amount, 2)} for date, amount in sorted(graph.items())]

@app.get("/stats/under1euro")
def small_donations():
    return [d for d in donations if d["amount"] < 1.0]
