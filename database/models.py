import sqlite3
from datetime import datetime
import os

DB_PATH = "database/viosense.db"

def init_db():
    """Initialize database with all tables"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Table 1: Violations
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS violations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            violation_id TEXT UNIQUE,
            vehicle_type TEXT,
            plate_number TEXT,
            violation_type TEXT,
            severity REAL,
            risk_level TEXT,
            confidence REAL,
            location TEXT,
            timestamp TEXT,
            image_path TEXT,
            pdf_path TEXT
        )
    ''')

    # Table 2: Vehicles (for repeat offender tracking)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vehicles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plate_number TEXT UNIQUE,
            total_violations INTEGER DEFAULT 0,
            risk_score REAL DEFAULT 0.0,
            first_seen TEXT,
            last_seen TEXT
        )
    ''')

    # Table 3: Locations (for safety index)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS locations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location_name TEXT UNIQUE,
            total_violations INTEGER DEFAULT 0,
            safety_score REAL DEFAULT 100.0,
            last_updated TEXT
        )
    ''')

    conn.commit()
    conn.close()
    print("✅ Database initialized successfully!")

def save_violation(data: dict):
    """Save a violation record to database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Generate violation ID
    timestamp = datetime.now()
    violation_id = f"V{timestamp.strftime('%Y%m%d%H%M%S')}"

    cursor.execute('''
        INSERT OR IGNORE INTO violations
        (violation_id, vehicle_type, plate_number,
         violation_type, severity, risk_level,
         confidence, location, timestamp,
         image_path, pdf_path)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        violation_id,
        data.get('vehicle_type', 'Unknown'),
        data.get('plate_number', 'Unknown'),
        data.get('violation_type', 'Unknown'),
        data.get('severity', 0.0),
        data.get('risk_level', 'MEDIUM'),
        data.get('confidence', 0.0),
        data.get('location', 'Unknown'),
        timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        data.get('image_path', ''),
        data.get('pdf_path', '')
    ))

    # Update vehicle record
    plate = data.get('plate_number', 'Unknown')
    cursor.execute('''
        INSERT INTO vehicles (plate_number, total_violations,
                            risk_score, first_seen, last_seen)
        VALUES (?, 1, ?, ?, ?)
        ON CONFLICT(plate_number) DO UPDATE SET
            total_violations = total_violations + 1,
            risk_score = MIN(10.0, risk_score + 0.5),
            last_seen = ?
    ''', (
        plate,
        data.get('severity', 5.0),
        timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        timestamp.strftime('%Y-%m-%d %H:%M:%S')
    ))

    conn.commit()
    conn.close()
    return violation_id

def get_repeat_offender(plate_number: str):
    """Check if vehicle is a repeat offender"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT total_violations, risk_score
        FROM vehicles
        WHERE plate_number = ?
    ''', (plate_number,))

    result = cursor.fetchone()
    conn.close()

    if result:
        total, risk = result
        is_repeat = total >= 3
        return {
            'plate': plate_number,
            'total_violations': total,
            'risk_score': round(risk, 1),
            'is_repeat_offender': is_repeat,
            'status': '🔴 HABITUAL OFFENDER' if is_repeat else '🟡 FIRST OFFENCE'
        }
    return None

def get_all_violations():
    """Get all violations for dashboard"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM violations ORDER BY timestamp DESC')
    rows = cursor.fetchall()
    conn.close()
    return rows

def update_location_safety(location: str, severity: float):
    """Update safety score for a location - realistic scoring"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Start from 100, deduct based on severity
    # Each violation deducts proportionally
    deduction = severity * 2  # max 20 points per violation

    cursor.execute('''
        INSERT INTO locations
        (location_name, total_violations, safety_score, last_updated)
        VALUES (?, 1, ?, ?)
        ON CONFLICT(location_name) DO UPDATE SET
            total_violations = total_violations + 1,
            safety_score = MAX(20, MIN(95,
                CASE
                    WHEN safety_score - ? < 20 THEN 20
                    ELSE safety_score - ?
                END
            )),
            last_updated = ?
    ''', (
        location,
        max(20, 95 - deduction),
        timestamp,
        deduction * 0.3,  # smaller deduction per violation
        deduction * 0.3,
        timestamp
    ))

    conn.commit()
    conn.close()

def get_safety_index():
    """Get safety scores for all locations"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT location_name, safety_score, total_violations
        FROM locations
        ORDER BY safety_score ASC
    ''')
    rows = cursor.fetchall()
    conn.close()
    return rows

if __name__ == "__main__":
    init_db()

    # Test save
    test_data = {
        'vehicle_type': 'Motorcycle',
        'plate_number': 'KA01AB1234',
        'violation_type': 'No Helmet',
        'severity': 7.2,
        'risk_level': 'HIGH',
        'confidence': 96.5,
        'location': 'MG Road'
    }

    vid = save_violation(test_data)
    print(f"✅ Violation saved: {vid}")

    # Test repeat offender
    offender = get_repeat_offender('KA01AB1234')
    print(f"✅ Offender check: {offender}")

    print("✅ Database module ready!")