import cv2
import os
import random
from datetime import datetime

from preprocessing.enhance import preprocess
from detection.yolo_detect import detect_vehicles, draw_detections
from ocr.plate_reader import read_plate, _mock_plate
from violation.classifier import VIOLATIONS, get_severity, get_risk_emoji
from evidence.pdf_generator import generate_pdf
from database.models import (
    init_db, save_violation,
    get_repeat_offender, update_location_safety
)

# Bengaluru locations for demo
DEMO_LOCATIONS = [
    "MG Road", "Silk Board", "Whitefield",
    "Koramangala", "Brigade Road", "Hebbal",
    "Electronic City", "Indiranagar"
]

def simulate_violations(detections):
    """
    Simulate violation detection based on detected vehicles
    In real system: this comes from trained violation model
    """
    violations_found = []

    for det in detections:
        vehicle = det['class_name']

        # Randomly assign violations for demo
        if vehicle in ['motorcycle', 'bicycle']:
            possible = ['no_helmet', 'triple_riding', 'wrong_side']
        elif vehicle in ['car', 'truck', 'bus']:
            possible = ['no_seatbelt', 'wrong_side',
                       'stop_line', 'red_light', 'illegal_parking']
        else:
            possible = ['stop_line', 'wrong_side']

        # Pick 1-2 violations
        num_violations = random.randint(1, 2)
        selected = random.sample(
            possible,
            min(num_violations, len(possible))
        )

        for v_type in selected:
            severity_info = get_severity(v_type)
            violations_found.append({
                'vehicle_type': vehicle,
                'violation_type': VIOLATIONS[v_type]['name'],
                'violation_key': v_type,
                'severity': severity_info['severity'],
                'risk_level': severity_info['risk'],
                'confidence': round(random.uniform(85, 99), 1),
                'bbox': det['bbox']
            })

    return violations_found

def process_image(image_path, location=None):
    """
    Full VioSense Pipeline:
    Image -> Preprocess -> Detect -> Violations -> OCR -> Evidence -> DB
    """
    print("\n" + "="*50)
    print("VIOSENSE AI TRAFFIC ENFORCEMENT")
    print("="*50)

    if location is None:
        location = random.choice(DEMO_LOCATIONS)

    print(f"Processing: {image_path}")
    print(f"Location: {location}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-"*50)

    # Step 1: Preprocessing
    print("\n[1/6] Preprocessing image...")
    try:
        img, is_night = preprocess(image_path)
    except Exception as e:
        print(f"Using original image: {e}")
        img = cv2.imread(image_path)
        is_night = False

    if img is None:
        print("ERROR: Could not load image!")
        return None

    # Step 2: Vehicle Detection
    print("\n[2/6] Detecting vehicles...")
    try:
        detections, _ = detect_vehicles(image_path)
        print(f"Found {len(detections)} vehicles/persons")
        for d in detections:
            print(f"  - {d['class_name']} ({d['confidence']}%)")
    except Exception as e:
        print(f"Detection note: {e}")
        detections = [{'class_name': 'motorcycle',
                      'confidence': 92.0,
                      'bbox': [100, 100, 300, 300]}]

    # Step 3: Violation Detection
    print("\n[3/6] Detecting violations...")
    violations = simulate_violations(detections)

    if not violations:
        # Always show at least one for demo
        violations = [{
            'vehicle_type': 'motorcycle',
            'violation_type': 'No Helmet',
            'violation_key': 'no_helmet',
            'severity': 7.2,
            'risk_level': 'HIGH',
            'confidence': 94.5,
            'bbox': [100, 100, 300, 300]
        }]

    print(f"Found {len(violations)} violations:")
    for v in violations:
        emoji = get_risk_emoji(v['risk_level'])
        print(f"  {emoji} {v['violation_type']} | "
              f"Severity: {v['severity']}/10 | "
              f"Confidence: {v['confidence']}%")

    # Step 4: License Plate OCR
    print("\n[4/6] Reading license plate...")
    plate_result = _mock_plate()
    print(f"  Plate: {plate_result['plate_number']}")
    print(f"  Confidence: {plate_result['confidence']}%")

    # Step 5: Check Repeat Offender
    print("\n[5/6] Checking repeat offender database...")
    plate = plate_result['plate_number']
    offender_info = get_repeat_offender(plate)

    if offender_info:
        print(f"  Status: {offender_info['status']}")
        print(f"  Total violations: {offender_info['total_violations']}")
        print(f"  Risk score: {offender_info['risk_score']}/10")
    else:
        print("  Status: First time offender")

    # Step 6: Generate Evidence for each violation
    print("\n[6/6] Generating evidence reports...")
    results = []

    for i, violation in enumerate(violations):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        violation_id = f"V{datetime.now().strftime('%Y%m%d%H%M%S')}{i}"

        # Save to database
        db_data = {
            'vehicle_type': violation['vehicle_type'],
            'plate_number': plate,
            'violation_type': violation['violation_type'],
            'severity': violation['severity'],
            'risk_level': violation['risk_level'],
            'confidence': violation['confidence'],
            'location': location,
            'image_path': image_path
        }
        saved_id = save_violation(db_data)

        # Update location safety
        update_location_safety(location, violation['severity'])

        # Generate PDF
        pdf_data = {
            'violation_id': saved_id,
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
        }
        pdf_path = generate_pdf(pdf_data)

        results.append({
            'violation_id': saved_id,
            'violation': violation['violation_type'],
            'plate': plate,
            'pdf': pdf_path
        })

    # Summary
    print("\n" + "="*50)
    print("PROCESSING COMPLETE")
    print("="*50)
    print(f"Total violations found: {len(violations)}")
    print(f"Location: {location}")
    print(f"Vehicle plate: {plate}")
    print(f"Evidence PDFs generated: {len(results)}")
    print("\nViolation Summary:")
    for r in results:
        print(f"  ID: {r['violation_id']}")
        print(f"  Violation: {r['violation']}")
        print(f"  PDF: {r['pdf']}")

    return results


if __name__ == "__main__":
    init_db()

    # Test with a sample image
    # Download any traffic image for testing
    test_image = "test_image.jpg"

    # Create a blank test image if none exists
    if not os.path.exists(test_image):
        import numpy as np
        blank = np.zeros((480, 640, 3), dtype=np.uint8)
        blank[:] = (100, 100, 100)
        cv2.imwrite(test_image, blank)
        print("Created test image for demo")

    results = process_image(test_image, "MG Road")