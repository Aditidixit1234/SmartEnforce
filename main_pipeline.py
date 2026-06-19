import cv2
import os
import random
from datetime import datetime
import time

from preprocessing.enhance import preprocess
from detection.yolo_detect import detect_vehicles, apply_violation_logic, draw_violations
from ocr.plate_reader import _mock_plate
from violation.classifier import get_severity, get_risk_emoji
from evidence.pdf_generator import generate_pdf
from database.models import (
    init_db, save_violation,
    get_repeat_offender, update_location_safety
)

DEMO_LOCATIONS = [
    "MG Road", "Silk Board", "Whitefield",
    "Koramangala", "Brigade Road", "Hebbal",
    "Electronic City", "Indiranagar"
]

def generate_unique_id(index):
    """Generate truly unique violation ID using timestamp + index"""
    ts = datetime.now().strftime('%Y%m%d%H%M%S')
    return f"V{ts}{index:03d}"

def process_image(image_path, location=None):
    print("\n" + "="*50)
    print("VIOSENSE AI TRAFFIC ENFORCEMENT")
    print("="*50)

    if location is None:
        location = random.choice(DEMO_LOCATIONS)

    print(f"Processing: {image_path}")
    print(f"Location: {location}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Step 1: Preprocessing
    print("\n[1/5] Preprocessing image...")
    try:
        img, is_night = preprocess(image_path)
    except Exception as e:
        print(f"Using original: {e}")
        img = cv2.imread(image_path)

    if img is None:
        print("ERROR: Could not load image!")
        return None

    # Step 2: Vehicle Detection
    print("\n[2/5] Detecting vehicles...")
    try:
        detections, _ = detect_vehicles(image_path)
        print(f"Found {len(detections)} vehicles/persons")
    except Exception as e:
        print(f"Detection error: {e}")
        detections = []

    # Step 3: Violation Detection
    print("\n[3/5] Detecting violations...")
    violations = apply_violation_logic(detections)

    if not violations:
        print("No violations detected in this image.")
        print("Note: Only motorcycles with No Helmet or Triple Riding are detected.")
        return []

    print(f"Found {len(violations)} violations")

    # Draw annotated image
    annotated = draw_violations(img.copy(), detections, violations)
    os.makedirs("static", exist_ok=True)
    cv2.imwrite('static/annotated_result.jpg', annotated)

    # Step 4: Process each violation with UNIQUE IDs
    print("\n[4/5] Generating evidence...")
    results = []
    seen_plates = set()

    for i, violation in enumerate(violations):
        # Small delay to ensure unique timestamps
        time.sleep(0.01)

        # Generate unique ID with index
        unique_id = generate_unique_id(i)

        # Generate unique plate per vehicle
        plate_result = _mock_plate()
        plate = plate_result['plate_number']
        attempts = 0
        while plate in seen_plates and attempts < 10:
            plate_result = _mock_plate()
            plate = plate_result['plate_number']
            attempts += 1
        seen_plates.add(plate)

        offender_info = get_repeat_offender(plate)
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Save to database
        save_violation({
            'vehicle_type': violation['vehicle_type'],
            'plate_number': plate,
            'violation_type': violation['violation_type'],
            'severity': violation['severity'],
            'risk_level': violation['risk_level'],
            'confidence': violation['confidence'],
            'location': location,
            'image_path': image_path
        })

        update_location_safety(location, violation['severity'])

        # Generate PDF with unique ID
        pdf_path = generate_pdf({
            'violation_id': unique_id,
            'vehicle_type': violation['vehicle_type'].title(),
            'plate_number': plate,
            'violation_type': violation['violation_type'],
            'severity': violation['severity'],
            'risk_level': violation['risk_level'],
            'confidence': violation['confidence'],
            'location': location,
            'timestamp': timestamp,
            'action': 'Issue Challan',
            'repeat_offender': offender_info
        })

        results.append({
            'violation_id': unique_id,
            'violation': violation['violation_type'],
            'plate': plate,
            'pdf': pdf_path
        })

        print(f"  [{i+1}] ID: {unique_id} | {violation['violation_type']} | Plate: {plate}")

    print(f"\nDone! {len(results)} violations processed")
    return results


if __name__ == "__main__":
    init_db()
    test_image = "test_traffic.jpg"
    if not os.path.exists(test_image):
        import numpy as np
        blank = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.imwrite(test_image, blank)
    results = process_image(test_image, "MG Road")
    if results:
        for r in results:
            print(f"ID: {r['violation_id']} | {r['violation']} | {r['plate']}")