import json
import statistics
from datetime import datetime, timedelta
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import os

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

def load_data():
    with open("donations.json", encoding="utf-8") as f:
        raw = json.load(f)
    arr = raw.get("data", raw) if isinstance(raw, dict) else raw
    out = []
    for d in arr:
        out.append({
            "id": d["id"],
            "donor": d.get("display_name", "Anonyme"),
            "amount": float(d["amount"]["value"]),
            "date": datetime.fromisoformat(d["created_at"].replace("Z", "+00:00")).isoformat().split("T")[0]
        })
    return out

donations = load_data()

@app.get("/donations")
def get_donations():
    return donations

@app.get("/stats/summary")
def summary():
    amounts = [d["amount"] for d in donations]
    return {
        "total": round(sum(amounts), 2),
        "mean": round(statistics.mean(amounts), 2),
        "median": round(statistics.median(amounts), 2),
        "count": len(amounts),
        "under1": len([a for a in amounts if a < 1])
    }

@app.get("/stats/top_donors")
def top_donors():
    agg = {}
    for d in donations:
        agg[d["donor"]] = agg.get(d["donor"], 0) + d["amount"]
    top = sorted(agg.items(), key=lambda x: x[1], reverse=True)[:10]
    return [{"donor": name, "amount": round(val, 2)} for name, val in top]

@app.get("/stats/evolution")
def evo():
    daily = {}
    for d in donations:
        daily[d["date"]] = daily.get(d["date"], 0) + d["amount"]
    return [{"date": day, "amount": round(daily[day], 2)} for day in sorted(daily)]

@app.get("/")
def index():
    with open("static/index.html", encoding="utf-8") as f:
        return HTMLResponse(f.read())
