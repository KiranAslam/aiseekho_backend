# Agent 3 — Operational Intelligence Agent
# Analyzes hospital availability, congestion, and emergency readiness
from config import settings
import json

try:
    from services.gemini_service import analyze_with_gemini
except Exception:
    analyze_with_gemini = None


def run(hospitals: list) -> dict:
    if not hospitals:
        return {
            "agent": "OpsIntelAgent",
            "insights": [],
            "reason": "No hospital data available for analysis."
        }

    # If live and Gemini configured, ask LLM to produce concise insights
    if settings.APP_MODE == "live" and analyze_with_gemini and settings.GEMINI_API_KEY:
        try:
            summary = []
            for h in hospitals:
                summary.append(f"{h.get('hospital_name')} (rating: {h.get('hospital_rating')}, eta: {h.get('eta')}, wait: {h.get('wait_time')})")
            prompt = (
                "Given the following hospitals and their stats, produce a JSON array of 3 short insights about which hospital to pick and why. "
                "Return only JSON.\n\nHospitals:\n" + "\n".join(summary)
            )
            resp = analyze_with_gemini(prompt)
            insights = json.loads(resp)
            top = insights[0] if insights else hospitals[0].get("hospital_name")
            return {
                "agent": "OpsIntelAgent",
                "insights": insights,
                "top_hospital": top,
                "reason": "Operational intelligence completed via Gemini."
            }
        except Exception:
            pass

    best_rating = max(hospitals, key=lambda item: item.get("hospital_rating", 0))
    fastest_eta = min(hospitals, key=lambda item: int(item.get("eta", "999 mins").split()[0]))

    insights = [
        f"Best-rated hospital is {best_rating['hospital_name']} with rating {best_rating['hospital_rating']}.",
        f"Fastest arrival estimate is {fastest_eta['hospital_name']} at {fastest_eta['eta']}.",
        "Recommend the hospital with the best balance of rating, wait time, and emergency readiness.",
    ]

    return {
        "agent": "OpsIntelAgent",
        "insights": insights,
        "top_hospital": best_rating["hospital_name"],
        "reason": "Operational intelligence completed."
    }
