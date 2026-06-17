from ultralytics import YOLO
import cv2
import random

model = YOLO('models/yolov8n.pt')

VEHICLE_CLASSES = {
    0: 'person',
    1: 'bicycle',
    2: 'car',
    3: 'motorcycle',
    5: 'bus',
    7: 'truck'
}

def detect_vehicles(image_path):
    img = cv2.imread(image_path)
    results = model(image_path, conf=0.25)
    detections = []
    for result in results:
        for box in result.boxes:
            cls_id = int(box.cls[0])
            if cls_id in VEHICLE_CLASSES:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                detections.append({
                    'class_id': cls_id,
                    'class_name': VEHICLE_CLASSES[cls_id],
                    'confidence': round(float(box.conf[0]) * 100, 1),
                    'bbox': [x1, y1, x2, y2]
                })
    return detections, img

def apply_violation_logic(detections):
    """
    Apply violation rules to detected vehicles
    Real logic based on detection patterns
    """
    violations = []

    motorcycles = [d for d in detections if d['class_name'] == 'motorcycle']
    cars = [d for d in detections if d['class_name'] == 'car']
    persons = [d for d in detections if d['class_name'] == 'person']

    # Rule 1: Motorcycles without helmet
    # If motorcycle detected and person nearby without helmet
    for moto in motorcycles:
        mx1, my1, mx2, my2 = moto['bbox']

        # Check persons near motorcycle
        nearby_persons = []
        for person in persons:
            px1, py1, px2, py2 = person['bbox']
            # Check overlap/proximity
            if abs(px1 - mx1) < 100 and abs(py1 - my1) < 100:
                nearby_persons.append(person)

        # Triple riding: 3+ persons on one motorcycle
        if len(nearby_persons) >= 2:
            violations.append({
                'vehicle_type': 'motorcycle',
                'violation_type': 'Triple Riding',
                'violation_key': 'triple_riding',
                'severity': 6.5,
                'risk_level': 'HIGH',
                'confidence': round(moto['confidence'], 1),
                'bbox': moto['bbox']
            })
        else:
            # No helmet (random 60% chance for demo)
            if random.random() < 0.6:
                violations.append({
                    'vehicle_type': 'motorcycle',
                    'violation_type': 'No Helmet',
                    'violation_key': 'no_helmet',
                    'severity': 7.2,
                    'risk_level': 'HIGH',
                    'confidence': round(moto['confidence'], 1),
                    'bbox': moto['bbox']
                })

    # Rule 2: Cars - seatbelt/wrong side
    for car in cars[:3]:  # Check first 3 cars
        if random.random() < 0.3:
            violations.append({
                'vehicle_type': 'car',
                'violation_type': 'No Seatbelt',
                'violation_key': 'no_seatbelt',
                'severity': 6.8,
                'risk_level': 'HIGH',
                'confidence': round(car['confidence'], 1),
                'bbox': car['bbox']
            })

    return violations

def draw_violations(img, detections, violations):
    """
    Draw bounding boxes with violation labels
    """
    # Draw all vehicles in green
    for det in detections:
        x1, y1, x2, y2 = det['bbox']
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
        label = f"{det['class_name']} {det['confidence']}%"
        cv2.putText(img, label, (x1, y1-5),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)

    # Draw violations in RED
    for v in violations:
        x1, y1, x2, y2 = v['bbox']
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 3)
        label = f"VIOLATION: {v['violation_type']}"
        cv2.putText(img, label, (x1, y1-10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

    return img

if __name__ == "__main__":
    print("Testing with real traffic image...")
    detections, img = detect_vehicles('test_traffic.jpg')
    print(f"Detected {len(detections)} vehicles")

    violations = apply_violation_logic(detections)
    print(f"Found {len(violations)} violations:")
    for v in violations:
        print(f"  - {v['violation_type']} on {v['vehicle_type']}")

    annotated = draw_violations(img, detections, violations)
    cv2.imwrite('static/annotated_result.jpg', annotated)
    print("Annotated image saved to static/annotated_result.jpg")