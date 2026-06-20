import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def get_violation_history():
    """Get historical violation data"""
    conn = sqlite3.connect("database/viosense.db")
    try:
        df = pd.read_sql_query(
            "SELECT * FROM violations", conn
        )
    except:
        df = pd.DataFrame()
    conn.close()
    return df

def predict_hotspots():
    """
    Predict tomorrow's violation hotspots
    Based on historical patterns
    """
    df = get_violation_history()

    locations = [
        "MG Road", "Silk Board", "Whitefield",
        "Koramangala", "Brigade Road", "Hebbal",
        "Electronic City", "Indiranagar"
    ]

    predictions = []

    for location in locations:
        if not df.empty and 'location' in df.columns:
            loc_data = df[df['location'] == location]
            violation_count = len(loc_data)
            avg_severity = loc_data['severity'].mean() if len(loc_data) > 0 else 5.0
        else:
            violation_count = 0
            avg_severity = 5.0

        # Predict risk score - guarantee a minimum baseline so it's never flat 0
        base_risk = (violation_count * 0.8) + (avg_severity * 0.4)
        risk_score = min(10, max(1.5, base_risk))
        risk_score = round(risk_score + random.uniform(-0.3, 0.5), 1)
        risk_score = max(1.0, min(10.0, risk_score))

        if risk_score >= 8:
            risk_level = "CRITICAL"
            officers = 5
            emoji = "🔴"
        elif risk_score >= 6:
            risk_level = "HIGH"
            officers = 3
            emoji = "🟠"
        elif risk_score >= 4:
            risk_level = "MEDIUM"
            officers = 2
            emoji = "🟡"
        else:
            risk_level = "LOW"
            officers = 1
            emoji = "🟢"

        # Expected violations tomorrow: based on today's count + small growth factor
        predicted_violations = violation_count + random.randint(0, 2) if violation_count > 0 else random.randint(0, 1)

        predictions.append({
            'location': location,
            'emoji': emoji,
            'predicted_violations': predicted_violations,
            'risk_score': risk_score,
            'risk_level': risk_level,
            'officers_needed': officers,
            'peak_time': '6PM - 8PM',
            'top_violation': 'No Helmet'
        })

    # Sort by risk score
    predictions.sort(key=lambda x: x['risk_score'], reverse=True)
    return predictions

if __name__ == "__main__":
    print("Predicting tomorrow's hotspots...")
    predictions = predict_hotspots()
    print("\nTOMORROW'S PREDICTED HOTSPOTS:")
    print("="*50)
    for p in predictions:
        print(f"{p['emoji']} {p['location']}")
        print(f"   Risk: {p['risk_level']} ({p['risk_score']}/10)")
        print(f"   Expected violations: {p['predicted_violations']}")
        print(f"   Officers needed: {p['officers_needed']}")
        print()