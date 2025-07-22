from fastapi import FastAPI
from datetime import datetime
import json

app = FastAPI()

def load_data():
    with open("donations.json", encoding="utf-8") as f:
        raw = json.load(f)

    data = []
    for d in raw:
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

donations_data = load_data()

@app.get("/donations")
def get_donations():
    return donations_data

@app.get("/stats/total")
def get_total():
    return round(sum(d["amount"] for d in donations_data), 2)

@app.get("/stats/top_donors")
def top_donors():
    from collections import defaultdict
    donors = defaultdict(float)
    for d in donations_data:
        donors[d["donor_name"]] += d["amount"]
    sorted_donors = sorted(donors.items(), key=lambda x: x[1], reverse=True)
    return [{"name": name, "amount": round(amount, 2)} for name, amount in sorted_donors[:10]]

@app.get("/stats/by_streamer")
def by_streamer():
    from collections import defaultdict
    streamers = defaultdict(float)
    for d in donations_data:
        streamers[d["streamer_name"]] += d["amount"]
    sorted_streamers = sorted(streamers.items(), key=lambda x: x[1], reverse=True)
    return [{"streamer": name, "amount": round(amount, 2)} for name, amount in sorted_streamers]

@app.get("/stats/graph")
def donation_graph():
    from collections import defaultdict
    import datetime

    timeline = defaultdict(float)
    for d in donations_data:
        day = d["created_at"].date().isoformat()
        timeline[day] += d["amount"]

    return sorted(
        [{"date": day, "total": round(amount, 2)} for day, amount in timeline.items()],
        key=lambda x: x["date"]
    )
